"""ComResObj — wraps a Dragon recognition result.

Provides the ResObj interface that natlink_compat wraps to present
the original natlink C extension API.
"""

import ctypes
import logging
import struct
import threading
import weakref

from ._errors import (NatlinkCOMError,
                      ERR_BAD_GRAMMAR,
                      ERR_DATA_MISSING,
                      ERR_INVALID_WORD,
                      ERR_OUT_OF_RANGE,
                      ERR_WRONG_TYPE)
from ._gram_obj import _pack_srword_list
from ._dspeech_constants import (
    DGNERR_NOTASELECTGRAMMAR as _DGNERR_NOTASELECTGRAMMAR,
    DGNERR_DOESNOTMATCHGRAMMAR as _DGNERR_DOESNOTMATCHGRAMMAR,
)
from ._speech_constants import (
    CHARSET_ENGINEPHONETIC,
    SRCORCONFIDENCE_VERY,
    SRERR_VALUEOUTOFRANGE as _E_UNEXPECTED,
    SRERR_NOTENOUGHDATA as _SRERR_NOTENOUGHDATA,
    SRERR_INVALIDCHAR as _SRERR_INVALIDCHAR,
)

log = logging.getLogger("natlink.com.results")
_SRWORDW_BUF_SIZE = 280        # 140 WCHAR max

# Track live ComResObj instances for cleanup before disconnect.
_live_res_objs = set()
_live_res_objs_lock = threading.Lock()


def _remove_ref(ref):
    with _live_res_objs_lock:
        _live_res_objs.discard(ref)


def release_all_res_objs():
    """Release all outstanding ComResObj instances.

    Called by natDisconnect before tearing down the COM connection.
    """
    with _live_res_objs_lock:
        refs = list(_live_res_objs)
        _live_res_objs.clear()
    for ref in refs:
        obj = ref()
        if obj is not None:
            obj.release()


class ComResObj:
    """Wraps a Dragon recognition result."""

    def __init__(self, results_unknown, words=None, tlb=None, connection=None):
        self._words = words or []
        self._tlb = tlb
        self._connection = connection
        # Own the IUnknown for the lifetime of this object — callers hand us a
        # reference they no longer manage (an AddRef'd RPC pointer in the
        # PhraseFinish sink, or a freshly wrapped raw pointer in ResultsGet).
        # Released in release() so the Dragon refcount drains on teardown.
        self._unknown = results_unknown
        # QI ISRResBasicW immediately (matches C++ pattern).
        self._res_basic = None
        if results_unknown is not None and tlb is not None:
            try:
                self._res_basic = results_unknown.QueryInterface(tlb.ISRResBasicW)
            except Exception:
                log.debug("QI(ISRResBasicW) failed", exc_info=True)
            # "The following code is necessary to preserve the wave information so
            # that we could use this utterance for playback and/or enrollment.  It
            # is inefficient to save this information for every utterance but in
            # the initial version of this module, I find it easier to save this
            # information by default."
            # — Joel Gould, ResultObject.cpp (CResultObject::create)
            # Dragon's dd10midl.dll has no proxy for ISRResMemory, but our
            # marshal DLL does — registered via CoRegisterPSClsid.
            try:
                res_mem = results_unknown.QueryInterface(tlb.ISRResMemory)
                res_mem.LockSet(True)
                log.debug("ISRResMemory::LockSet(True) — wave data preserved")
            except Exception:
                log.debug("ISRResMemory::LockSet not available", exc_info=True)
        ref = weakref.ref(self, lambda r: _remove_ref(r))
        with _live_res_objs_lock:
            _live_res_objs.add(ref)

    def _mustbe_inited(self, func):
        """C++ MUSTBETINITED macro — check result object is still usable."""
        if self._res_basic is None:
            raise NatlinkCOMError(func,
                error_message=f"This results object is no longer usable "
                              f"(calling {func})")

    def get_results(self, choice=0):
        """Get recognized words for a given choice.

        Matches C++ CResultObject::getResults: ISRResGraphW::BestPathWord +
        GetWordNode per word, for *every* choice including 0.

        The cached SRPHRASEW words cannot serve choice 0: the number in an
        SRPHRASEW word is ``dwWordNum``, a word-table id, while callers expect
        ``dwCFGParse``, the CFG rule number. Measured on Dragon 13 and 14 with
        a two-rule grammar sharing a word — the cached number was identical
        under both rules, which a rule number cannot be. ``GrammarBase`` maps
        these onto ``gotResults_<rule>``, so the wrong source silently
        misdispatches every rule-based grammar.
        """
        self._mustbe_inited("ResObj.getResults")
        graph = self._qi("ISRResGraphW")
        if graph is None:
            if choice == 0 and self._words:
                # No results graph (e.g. a ResObj vended by DictObj). The
                # words are still correct; the rule number is simply not
                # recoverable here, so report 0 rather than a word id that
                # would be mistaken for a rule.
                return [{"word": w, "cfg_parse": 0} for w, _ in self._words]
            raise NatlinkCOMError("get_results",
                                  error_message="No ISRResGraphW interface")
        try:
            path, count = _best_path_word(graph, choice)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _E_UNEXPECTED:
                raise NatlinkCOMError("get_results", error_type=ERR_OUT_OF_RANGE,
                    error_message=f"There is no result number {choice}") from exc
            raise
        results = []
        for i in range(count):
            node, word_text = _get_word_node(graph, path[i], self._tlb)
            if node is None or not word_text:
                continue
            results.append({"word": word_text, "cfg_parse": node.dwCFGParse})
        return results

    def get_word_info(self, choice=0):
        """Get detailed word info for a given choice.

        Matches C++ CResultObject::getWordInfo:
          ISRResGraphW::BestPathWord → IDgnSRResGraphW::GetWordNode per word
          ILexPronounceW::Get for pronunciation + engine flags
          ISRResBasicW::TimeGet for relative timestamps

        Returns list of (word, cfgParse, wordScore, startTime, endTime,
        engineFlags, pronunciation) tuples — matching C++ Py_BuildValue
        "(siiiiis)" format.
        """
        self._mustbe_inited("ResObj.getWordInfo")
        graph = self._qi("ISRResGraphW")
        if graph is None:
            raise NatlinkCOMError("get_word_info",
                                  error_message="No ISRResGraphW interface")
        try:
            path, count = _best_path_word(graph, choice)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _E_UNEXPECTED:
                raise NatlinkCOMError("get_word_info", error_type=ERR_OUT_OF_RANGE,
                    error_message=f"There is no result number {choice}") from exc
            raise
        if count == 0:
            return []

        gwn = self._qi("IDgnSRResGraphW") or graph
        utt_start = self._get_utterance_start_time()
        # C++ QIs ILexPronounce from ISRCentral for pronunciation + engine flags.
        # Try ILexPronounceW — may fail cross-bitness (vcmshl /Oi stubs).
        lex_pron = None
        conn = self._connection
        if conn and conn.central and conn.tlb:
            try:
                lex_pron = conn.central.QueryInterface(conn.tlb.ILexPronounceW)
            except Exception:
                log.debug("QI(ILexPronounceW) failed — pronunciation not available")

        results = []
        for i in range(count):
            node, word_text = _get_word_node(gwn, path[i], self._tlb)
            if node is None or not word_text:
                continue
            rel_start = int(node.qwStartTime - utt_start) if utt_start else int(node.qwStartTime)
            rel_end = int(node.qwEndTime - utt_start) if utt_start else int(node.qwEndTime)
            pron, eng_flags = _get_pronunciation(conn, lex_pron, word_text)
            results.append({
                "word": word_text,
                "cfg_parse": node.dwCFGParse,
                "word_score": node.dwWordScore,
                "start_time": rel_start,
                "end_time": rel_end,
                "engine_flags": eng_flags,
                "pronunciation": pron,
            })
        return results

    def get_wave(self):
        """Get audio waveform data as raw bytes.

        Matches C++ CResultObject::getWave:
          QI(ISRResAudio) → GetWAV(&sData) → CoTaskMemFree
          SRERR_NOTENOUGHDATA → "The wave data is no longer available"
        """
        from ._sdata import sdata_to_bytes
        audio = self._qi("ISRResAudio")
        if audio is None:
            raise NatlinkCOMError("get_wave",
                                  error_message="No ISRResAudio interface")
        try:
            sdata = audio.GetWAV()
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _SRERR_NOTENOUGHDATA:
                # C++: "The wave data is no longer available for this result"
                raise NatlinkCOMError("get_wave", error_type=ERR_DATA_MISSING,
                    error_message="The wave data is no longer available "
                                  "for this result") from exc
            raise
        raw = sdata_to_bytes(sdata)
        if not raw:
            raise NatlinkCOMError("get_wave",
                error_message="The wave data is no longer available "
                              "for this result")
        return raw

    def correction(self, words):
        """Submit a correction. Returns True if training succeeded.

        Matches C++ CResultObject::correction:
          makePhrase(ppWords) → ISRResCorrectionW::Correction(phrase, SRCORCONFIDENCE_VERY)
          SRERR_INVALIDCHAR → "Invalid word in ResObj.correction transcript"
          "returns S_OK if training succeeds and S_FALSE otherwise."
        — Joel Gould, ResultObject.cpp (CResultObject::correction)

        Note: The original C++ has MUSTBETINITED("ResObj.getResults") here —
        a copy-paste error; the function name should be "ResObj.correction".
        """
        self._mustbe_inited("ResObj.correction")
        corr = self._qi("ISRResCorrectionW")
        if corr is None:
            raise NatlinkCOMError("correction",
                                  error_message="No ISRResCorrectionW interface")
        phrase_data = _pack_srword_list(words)
        tlb = self._tlb
        phrase = tlb.SRPHRASEW()
        phrase.dwSize = len(phrase_data) + 4
        buf = None
        if phrase_data:
            buf = (ctypes.c_ubyte * len(phrase_data))(*phrase_data)
            phrase.abWords = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
        try:
            hr = corr.Correction(phrase, SRCORCONFIDENCE_VERY)
        except Exception as exc:
            hr_val = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr_val == _SRERR_INVALIDCHAR:
                # C++: "Invalid word in ResObj.correction transcript"
                raise NatlinkCOMError("correction", error_type=ERR_INVALID_WORD,
                    error_message="Invalid word in ResObj.correction "
                                  "transcript") from exc
            raise
        finally:
            del buf
        # "returns S_OK if training succeeds and S_FALSE otherwise"
        return hr == 0

    def get_select_info(self, gram_handle, choice=0):
        """Get selection info relative to a grammar. Returns (start, end).

        Matches C++ CResultObject::getSelectInfo:
          MUSTBETINITED + grammar GUID + IDgnSRResSelect::GetInfo
          SRERR_VALUEOUTOFRANGE → "There is no result number %d"
          DGNERR_NOTASELECTGRAMMAR → "Result was not from a Select grammar"
          DGNERR_DOESNOTMATCHGRAMMAR → "Result was not from the indicated grammar"

        "The recognizer call to the select information requires that you pass
        in the GUID of the grammar.  We go to the grammar to get the GUID.
        The Python programmer will have passed in the grammar pointer."
        — Joel Gould, ResultObject.cpp (CResultObject::getSelectInfo)

        Note: The original C++ has MUSTBETINITED("getWordInfo") here —
        a copy-paste error; the function name should be "getSelectInfo".
        """
        self._mustbe_inited("ResObj.getSelectInfo")
        select = self._qi("IDgnSRResSelect")
        if select is None:
            raise NatlinkCOMError("get_select_info",
                                  error_message="No IDgnSRResSelect interface")
        conn = self._connection
        lookup = conn.lookup_com_grammar if conn else None
        com_gram = lookup(gram_handle) if lookup else None
        if com_gram is None:
            raise NatlinkCOMError("get_select_info",
                                  error_message="Grammar not found in registry")
        grammar_guid = com_gram.get_grammar_guid()
        try:
            start, end, word_num = select.GetInfo(grammar_guid, choice)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _E_UNEXPECTED:
                raise NatlinkCOMError("get_select_info", error_type=ERR_OUT_OF_RANGE,
                    error_message=f"There is no result number "
                                  f"{choice}") from exc
            if hr == _DGNERR_NOTASELECTGRAMMAR:
                # C++: "Result number %d was not from a Select grammar"
                raise NatlinkCOMError("get_select_info", error_type=ERR_WRONG_TYPE,
                    error_message=f"Result number {choice} was not from "
                                  f"a Select grammar") from exc
            if hr == _DGNERR_DOESNOTMATCHGRAMMAR:
                # C++: "Result number %d was not from the indicated grammar"
                raise NatlinkCOMError("get_select_info", error_type=ERR_BAD_GRAMMAR,
                    error_message=f"Result number {choice} was not from "
                                  f"the indicated grammar") from exc
            raise
        return (start, end)

    def release(self):
        """Release ISRResBasicW and the owned IUnknown — matching C++
        CResultObject::destroy plus the IUnknown reference this object owns."""
        from ._com_helpers import force_release
        try:
            force_release(self._res_basic)
            force_release(self._unknown)
        finally:
            self._res_basic = None
            self._unknown = None
            self._connection = None

    def _qi(self, iface_name):
        """QI for an interface, returning a temporary (not cached)."""
        if self._res_basic is None or self._tlb is None:
            return None
        try:
            return self._res_basic.QueryInterface(getattr(self._tlb, iface_name))
        except Exception as e:
            log.debug("QI(%s) failed: %s %s", iface_name, type(e).__name__, e)
            return None

    def _get_utterance_start_time(self):
        """Get utterance start time via ISRResBasicW::TimeGet."""
        basic = self._res_basic
        if basic is None:
            return 0
        try:
            start = ctypes.c_ulonglong(0)
            end = ctypes.c_ulonglong(0)
            hr = basic._ISRResBasicW__com_TimeGet(
                ctypes.byref(start), ctypes.byref(end))
            return start.value if hr >= 0 else 0
        except Exception:
            log.debug("TimeGet failed", exc_info=True)
            return 0


# --- Module-level helpers ---

def _best_path_word(graph, choice):
    """ISRResGraphW::BestPathWord via comtypes. Returns (path_list, count).

    "we preallocate 512 words for the best path and hope the grammar does
    not include something larger"
    — Joel Gould, ResultObject.cpp (CResultObject::getResults)

    The returned pathSize is a byte count, not a word count — divide by
    sizeof(DWORD) to get the actual number of word node IDs.
    """
    path_buf = (ctypes.c_ulong * 512)()
    needed = ctypes.c_ulong(0)
    hr = graph._ISRResGraphW__com_BestPathWord(
        choice, path_buf, ctypes.sizeof(path_buf), ctypes.byref(needed))
    if hr < 0:
        raise NatlinkCOMError("BestPathWord", hr=hr)
    count = needed.value // 4
    return [path_buf[i] for i in range(count)], count


def _get_word_node(graph_iface, node_id, tlb):
    """GetWordNode via comtypes. Returns (node_struct, word_text) or (None, '').

    C++: "we support a maximum word size of 128 plus overhead" — uses a
    140-byte buffer (BYTE aBuffer[140]).  We use 280 bytes (_SRWORDW_BUF_SIZE)
    to account for WCHAR (2 bytes per character).
    """
    word_buf = (ctypes.c_ubyte * _SRWORDW_BUF_SIZE)()
    needed = ctypes.c_ulong(0)
    try:
        if hasattr(graph_iface, '_IDgnSRResGraphW__com_GetWordNode'):
            node = tlb.DGNSRRESWORDNODE()
            hr = graph_iface._IDgnSRResGraphW__com_GetWordNode(
                node_id, ctypes.byref(node), word_buf,
                _SRWORDW_BUF_SIZE, ctypes.byref(needed))
        else:
            node = tlb.SRRESWORDNODE()
            hr = graph_iface._ISRResGraphW__com_GetWordNode(
                node_id, ctypes.byref(node), word_buf,
                _SRWORDW_BUF_SIZE, ctypes.byref(needed))
    except Exception:
        return None, ""
    if hr < 0:
        return None, ""
    return node, _parse_srwordw_buf(bytes(word_buf))


def _parse_srwordw_buf(word_bytes):
    """Parse word text from an SRWORDW byte buffer."""
    if len(word_bytes) < 10:
        return ""
    entry_size = struct.unpack_from("<I", word_bytes, 0)[0]
    text_data = word_bytes[8:min(entry_size, len(word_bytes))]
    try:
        return text_data.decode("utf-16-le").rstrip("\x00")
    except UnicodeDecodeError:
        return ""


def _get_pronunciation(conn, lex_pron, word_text):
    """Get pronunciation and engine flags.

    Prefer the original ILexPronounceW path. If that fails, preserve as much
    metadata as possible by falling back to the lexicon engine-flags lookup.
    """
    if lex_pron is None:
        return ("", _get_engine_flags_fallback(conn, word_text))
    try:
        from ._lexicon import _lex_pron_get
        hr, pron_buf, pron_size, _, info, info_size = _lex_pron_get(
            lex_pron, word_text, pron_buf_size=64)
        if hr < 0:
            return ("", _get_engine_flags_fallback(conn, word_text))
        pron = pron_buf.value if pron_size > 0 else ""
        eng_flags = 0
        if info_size >= 4:
            eng_flags = struct.unpack_from("<I", bytes(info), 0)[0]
        return (pron, eng_flags)
    except Exception:
        return ("", _get_engine_flags_fallback(conn, word_text))


def _get_engine_flags_fallback(conn, word_text):
    """Best-effort fallback for engine flags when pronunciation lookup fails."""
    if conn is None:
        return 0
    try:
        from ._lexicon import get_word_info
        flags = get_word_info(conn, word_text, 0)
    except Exception:
        return 0
    return 0 if flags is None else int(flags)


def parse_srphrasew(phrase_struct):
    """Parse SRPHRASEW struct into list of (word, cfgInfo) tuples.

    This is used for PhraseFinish's inline SRPHRASEW (choice 0) — more
    efficient than per-word BestPathWord+GetWordNode calls: "ISRResBasic::
    PhraseGet is a more efficient way of getting the results information
    because we only have to make one COM call instead one COM call per
    word in the results." — Joel Gould, ResultObject.cpp (getWords)
    """
    if phrase_struct is None:
        return []
    try:
        raw_ptr = ctypes.cast(phrase_struct, ctypes.c_void_p).value
        if not raw_ptr:
            return []
        dw_buf = (ctypes.c_ubyte * 4)()
        ctypes.memmove(dw_buf, raw_ptr, 4)
        total_size = struct.unpack_from("<I", bytes(dw_buf), 0)[0]
        if total_size <= 4:
            return []
        data_size = total_size - 4
        raw = (ctypes.c_ubyte * data_size)()
        ctypes.memmove(raw, raw_ptr + 4, data_size)
        data = bytes(raw)
    except Exception:
        log.exception("Failed to read SRPHRASEW data")
        return []
    return _parse_srwordw_array(data)


def _parse_srwordw_array(data):
    """Parse a flat byte buffer of consecutive SRWORDW entries."""
    words = []
    offset = 0
    while offset + 8 <= len(data):
        entry_size, word_num = struct.unpack_from("<II", data, offset)
        if entry_size < 10:
            break
        text_bytes = data[offset + 8 : offset + entry_size]
        try:
            text = text_bytes.decode("utf-16-le").rstrip("\x00")
        except UnicodeDecodeError:
            text = ""
        if text:
            words.append((text, word_num))
        offset += entry_size
    return words
