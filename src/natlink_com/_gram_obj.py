"""ComGramObj — wraps ISRGramCommonW + ISRGramCFGW.

Provides the GramObj interface that natlink_compat wraps to present
the original natlink C extension API.
"""

import ctypes
import logging
import struct

from ._com_helpers import next_object_handle
from ._errors import (NatlinkCOMError,
                      ERR_BAD_GRAMMAR,
                      ERR_INVALID_WORD,
                      ERR_UNKNOWN_NAME,
                      ERR_WRONG_STATE,
                      ERR_WRONG_TYPE)
from ._sdata import build_sdata as _build_sdata, sdata_to_bytes

from ._dspeech_constants import DGNSRHDRTYPE_SELECT
from ._speech_constants import (
    SRHDRTYPE_CFG, SRHDRTYPE_DICTATION,
    SRGRMFMT_CFG, SRGRMFMT_DICTATION, SRGRMFMT_DRAGONNATIVE1,
    SRERR_INVALIDCHAR as _SRERR_INVALIDCHAR,
    SRERR_GRAMMARERROR as _SRERR_GRAMMARERROR,
    SRERR_GRAMMARTOOCOMPLEX as _SRERR_GRAMMARTOOCOMPLEX,
    SRERR_INVALIDRULE as _SRERR_INVALIDRULE,
    SRERR_RULEALREADYACTIVE as _SRERR_RULEALREADYACTIVE,
    SRERR_RULENOTACTIVE as _SRERR_RULENOTACTIVE,
    SRERR_INVALIDLIST as _SRERR_INVALIDLIST,
    SRCKCFG_RULES as _SRCKCFG_RULES,
    SRCKCFG_EXPORTRULES as _SRCKCFG_EXPORTRULES,
    SRCKCFG_LISTS as _SRCKCFG_LISTS,
    SRCFG_STARTOPERATION as _SRCFG_STARTOPERATION,
    SRCFG_ENDOPERATION as _SRCFG_ENDOPERATION,
    SRCFG_LIST as _SRCFG_LIST,
    SRCFGO_SEQUENCE as _SRCFGO_SEQUENCE,
)

log = logging.getLogger("natlink.com.grammar")


def make_empty_grammar():
    """Build an ANSI SAPI 4.0 CFG grammar that can never be recognized.

    Matches C++ makeEmptyGrammar (DragonCode.cpp) byte-for-byte:

    "This returns an allocated datablock which holds a standard SAPI
    command and control grammar.  The specific grammar returned by thus
    function contins an empty list so it will never be recognized."
    — Joel Gould, DragonCode.cpp (makeEmptyGrammar)
    [sic: "thus" and "contins" are typos in the original C++ source]

    Structure (ANSI, dwFlags=0):
      SRHEADER { dwType=CFG(0), dwFlags=0 }
      SRCHUNK  { SRCKCFG_RULES, <rules> }
        SRCFGRULE { dwSize, dwUniqueID=1 }
          SRCFGSYMBOL { STARTOPERATION, 0, SEQUENCE }
          SRCFGSYMBOL { LIST, 0, 1 }
          SRCFGSYMBOL { ENDOPERATION, 0, SEQUENCE }
      SRCHUNK  { SRCKCFG_EXPORTRULES, <export> }
        SRCFGXRULE { dwSize, dwRuleNum=1, "Start\\0" padded }
      SRCHUNK  { SRCKCFG_LISTS, <list> }
        SRCFGLIST { dwSize, dwListNum=1, "Empty\\0" padded }
    """
    # String sizes — ANSI, null-terminated, padded to 4-byte boundary
    # C++: dwStartWordSize = (strlen("Start") + 1 + 3) & ~3 = 8
    start_word = b"Start\x00"
    start_padded = len(start_word)
    start_padded = (start_padded + 3) & ~3  # 8

    # C++: dwEmptyWordSize = (strlen("Empty") + 1 + 3) & ~3 = 8
    empty_word = b"Empty\x00"
    empty_padded = len(empty_word)
    empty_padded = (empty_padded + 3) & ~3  # 8

    # Struct sizes (all DWORD-based, no alignment issues)
    # SRCFGRULE = 2 DWORDs (dwSize, dwUniqueID) = 8 bytes header
    # SRCFGSYMBOL = WORD + WORD + DWORD = 8 bytes each
    # SRCFGXRULE = 2 DWORDs (dwSize, dwRuleNum) + string
    # SRCFGLIST = 2 DWORDs (dwSize, dwListNum) + string

    rule_chunk_size = 8 + 3 * 8          # SRCFGRULE(8) + 3 * SRCFGSYMBOL(8) = 32
    export_chunk_size = 8 + start_padded  # SRCFGXRULE(8) + "Start\0.." = 16
    list_chunk_size = 8 + empty_padded    # SRCFGLIST(8) + "Empty\0.." = 16

    buf = bytearray()

    # SRHEADER { dwType=SRHDRTYPE_CFG(0), dwFlags=0 }
    buf += struct.pack("<II", SRHDRTYPE_CFG, 0)

    # SRCHUNK { dwChunkID=SRCKCFG_RULES(3), dwChunkSize }
    buf += struct.pack("<II", _SRCKCFG_RULES, rule_chunk_size)
    # SRCFGRULE { dwSize=rule_chunk_size, dwUniqueID=1 }
    buf += struct.pack("<II", rule_chunk_size, 1)
    # 3 x SRCFGSYMBOL { wType, wProbability=0, dwValue }
    buf += struct.pack("<HHI", _SRCFG_STARTOPERATION, 0, _SRCFGO_SEQUENCE)
    buf += struct.pack("<HHI", _SRCFG_LIST, 0, 1)
    buf += struct.pack("<HHI", _SRCFG_ENDOPERATION, 0, _SRCFGO_SEQUENCE)

    # SRCHUNK { dwChunkID=SRCKCFG_EXPORTRULES(4), dwChunkSize }
    buf += struct.pack("<II", _SRCKCFG_EXPORTRULES, export_chunk_size)
    # SRCFGXRULE { dwSize, dwRuleNum=1, szString="Start" }
    buf += struct.pack("<II", export_chunk_size, 1)
    buf += start_word.ljust(start_padded, b"\x00")

    # SRCHUNK { dwChunkID=SRCKCFG_LISTS(6), dwChunkSize }
    buf += struct.pack("<II", _SRCKCFG_LISTS, list_chunk_size)
    # SRCFGLIST { dwSize, dwListNum=1, szString="Empty" }
    # NOTE: C++ has a bug here: pList->dwSize = dwExportChunkSize (should be
    # dwListChunkSize). We reproduce the bug for byte-exact compatibility.
    # If a future Dragon version fixes this, gate on version and use
    # list_chunk_size instead.
    buf += struct.pack("<II", export_chunk_size, 1)
    buf += empty_word.ljust(empty_padded, b"\x00")

    return bytes(buf)


def load_grammar(conn, data, all_results=False, hypothesis=False):
    """Load a binary grammar into Dragon.

    1. Detect grammar type from first DWORD
    2. Create grammar sink (ISRGramNotifySinkW + IDgnGetSinkFlags)
    3. ISRCentralW::GrammarLoad -> IUnknown
    4. QI for ISRGramCommonW, ISRGramCFGW
    5. Return ComGramObj wrapping everything

    "The grammar format must match the type of grammar in the binary data
    block's header.  The grammar type is the first DWORD in the header."
    — Joel Gould, GrammarObject.cpp (CGrammarObject::load)

    After loading, C++ adds the grammar to a linked list so "all the
    grammars can be freed when we disconnect" (GrammarObject.cpp:296-297).
    The Python equivalent is connection.register_grammar_sink().

    The grammar sink implements ISRGramNotifySink + IDgnGetSinkFlags:
    "This is a grammar notification sink.  This sink detect PhraseFinish
    and pass the information to the parent class."
    — Joel Gould, GrammarObject.cpp (CSRGramNotifySink class comment)
    [sic: "detect" and "pass" should be "detects" and "passes"]
    """
    from ._grammar_sink import create_grammar_sink

    central = conn.central
    tlb = conn.tlb
    if central is None:
        raise NatlinkCOMError("grammar_load", error_message="Not connected")

    if len(data) < 4:
        raise NatlinkCOMError("grammar_load", error_message="Grammar data too short")
    hdr_type = struct.unpack_from("<I", data, 0)[0]
    gram_fmt = {
        SRHDRTYPE_CFG: SRGRMFMT_CFG,
        SRHDRTYPE_DICTATION: SRGRMFMT_DICTATION,
        DGNSRHDRTYPE_SELECT: SRGRMFMT_DRAGONNATIVE1,
    }.get(hdr_type)
    if gram_fmt is None:
        raise NatlinkCOMError("grammar_load",
                              error_message=f"Unknown grammar header type: {hdr_type}")

    sink = create_grammar_sink(0, all_results, hypothesis, connection=conn)
    sdata, _buf = _build_sdata(tlb, data)

    iid = tlb.ISRGramNotifySinkW._iid_
    try:
        punk = central.GrammarLoad(gram_fmt, sdata, sink, iid)
    except Exception as exc:
        hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
        if hr == _SRERR_INVALIDCHAR:
            # C++: "Invalid word in grammar"
            raise NatlinkCOMError("grammar_load", error_type=ERR_INVALID_WORD,
                error_message="Invalid word in grammar") from exc
        if hr == _SRERR_GRAMMARERROR:
            # C++: "The grammar specification is in error"
            raise NatlinkCOMError("grammar_load", error_type=ERR_BAD_GRAMMAR,
                error_message="The grammar specification is in error") from exc
        raise

    gram_common = punk.QueryInterface(tlb.ISRGramCommonW)

    gram_cfg = None
    try:
        gram_cfg = punk.QueryInterface(tlb.ISRGramCFGW)
    except Exception:
        log.debug("Grammar does not support ISRGramCFGW (no list operations)")

    gram = ComGramObj(gram_common, gram_cfg, sink, all_results, hypothesis,
                      sdata_cls=tlb.SDATA, punk=punk, tlb=tlb)

    sink._gram_handle = gram.handle
    conn.register_grammar_sink(gram.handle, sink)

    log.debug("Loaded grammar (handle=%d, fmt=0x%X, cfg=%s)",
               gram.handle, gram_fmt, gram_cfg is not None)
    return gram


class ComGramObj:
    """Wraps a loaded Dragon grammar (ISRGramCommonW + ISRGramCFGW)."""

    def __init__(self, gram_common, gram_cfg, sink, all_results, hypothesis,
                 sdata_cls=None, punk=None, tlb=None):
        """
        Args:
            gram_common: comtypes ISRGramCommonW pointer.
            gram_cfg: comtypes ISRGramCFGW pointer (or None if not a CFG grammar).
            sink: GrammarSink COMObject (prevent GC).
            all_results: If True, receive results from all grammars.
            hypothesis: If True, receive hypothesis callbacks.
            sdata_cls: comtypes SDATA struct class (for list operations).
            punk: comtypes IUnknown from GrammarLoad (for lazy QI).
            tlb: Dragon type library module (interface definitions).
        """
        self._handle = next_object_handle()
        self._gram_common = gram_common
        self._gram_cfg = gram_cfg
        self._sink = sink
        self._all_results = all_results
        self._hypothesis = hypothesis
        self._sdata_cls = sdata_cls
        self._punk = punk
        self._tlb = tlb
        # Lazy-initialized interfaces
        self._dgn_gram_common = None   # IDgnSRGramCommon (SpecialGrammar)
        self._gram_dictation = None    # ISRGramDictationW (Context)
        self._gram_select = None       # IDgnSRGramSelectW (WordsSet/Get)

    @property
    def handle(self):
        return self._handle

    def activate(self, rule_name="", window_handle=0):
        """Activate a grammar rule.

        ISRGramCommonW::Activate(HWND, BOOL autoPause, PCWSTR ruleName)

        "An empty rule name is the same as a NULL rule name for CFG grammars
        and a NULL rull name is required for dictation grammars."
        — Joel Gould, GrammarObject.cpp (CGrammarObject::activate)
        [sic: "rull" is a typo in the original C++ source]
        """
        if self._gram_common is None:
            raise NatlinkCOMError("activate", error_message="Grammar not loaded")
        hwnd = window_handle or 0
        if hwnd and not ctypes.windll.user32.IsWindow(hwnd):
            raise NatlinkCOMError("activate",
                                  error_message=f"Invalid window handle: {hwnd}")
        # "An empty rule name is the same as a NULL rule name for CFG grammars
        # and a NULL rull name is required for dictation grammars." [sic]
        rule = rule_name if rule_name else None
        try:
            self._gram_common.Activate(hwnd, False, rule)
            log.debug("activate(handle=%d, rule=%r, hwnd=0x%X)",
                      self._handle, rule_name, hwnd)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _SRERR_INVALIDRULE:
                # C++: "The rule %s is not defined in the grammar"
                raise NatlinkCOMError("activate", error_type=ERR_UNKNOWN_NAME,
                    error_message=f"The rule {rule_name} is not defined "
                                  f"in the grammar") from exc
            if hr == _SRERR_GRAMMARTOOCOMPLEX:
                # C++: "The grammar is too complex to be recognized"
                raise NatlinkCOMError("activate", error_type=ERR_BAD_GRAMMAR,
                    error_message="The grammar is too complex to be "
                                  "recognized") from exc
            if hr == _SRERR_RULEALREADYACTIVE:
                # C++: "The rule %s is already active"
                raise NatlinkCOMError("activate", error_type=ERR_WRONG_STATE,
                    error_message=f"The rule {rule_name} is already "
                                  f"active") from exc
            raise

    def deactivate(self, rule_name=""):
        """Deactivate a grammar rule.

        ISRGramCommonW::Deactivate(PCWSTR ruleName)

        Unlike activate(), C++ does NOT convert empty rule name to NULL
        for deactivate — it passes the name through CComBSTR directly.
        """
        if self._gram_common is None:
            raise NatlinkCOMError("deactivate", error_message="Grammar not loaded")
        try:
            self._gram_common.Deactivate(rule_name)
            log.debug("deactivate(handle=%d, rule=%r)",
                      self._handle, rule_name)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _SRERR_RULENOTACTIVE:
                # C++: "The rule %s is not active"
                raise NatlinkCOMError("deactivate", error_type=ERR_WRONG_STATE,
                    error_message=f"The rule {rule_name} is not "
                                  f"active") from exc
            raise

    def unload(self, connection=None):
        """Release all COM references for this grammar."""
        from ._com_helpers import force_release
        if connection is not None:
            connection.unregister_grammar_sink(self._handle)
        try:
            force_release(self._gram_select)
            force_release(self._gram_dictation)
            force_release(self._dgn_gram_common)
            force_release(self._gram_cfg)
            force_release(self._gram_common)
            force_release(self._punk)
        finally:
            self._gram_select = None
            self._gram_dictation = None
            self._dgn_gram_common = None
            self._gram_cfg = None
            self._gram_common = None
            self._punk = None
            self._sink = None

    def _lazy_qi(self, attr, iface_name):
        """Lazy QI: cache the result of punk.QueryInterface on first access."""
        cached = getattr(self, attr)
        if cached is not None:
            return cached
        if self._punk is None or self._tlb is None:
            return None
        try:
            result = self._punk.QueryInterface(getattr(self._tlb, iface_name))
        except Exception:
            return None
        setattr(self, attr, result)
        return result

    def set_exclusive(self, state):
        """Set grammar exclusivity.

        Matches C++ CGrammarObject::setExclusive:
          QI(IDgnSRGramCommon) → SpecialGrammar(bState != 0)
        """
        if self._gram_common is None:
            raise NatlinkCOMError("set_exclusive",
                                  error_message="Grammar not loaded")
        iface = self._lazy_qi("_dgn_gram_common", "IDgnSRGramCommon")
        if iface is None:
            raise NatlinkCOMError("set_exclusive",
                error_message="QI(IDgnSRGramCommon) failed")
        iface.SpecialGrammar(bool(state))
        log.debug("set_exclusive(%s)", state)

    def get_grammar_guid(self):
        """Get the grammar's GUID via IDgnSRGramCommon::Identify.

        Used by ResObj.get_select_info to match results to grammars.
        Returns a comtypes GUID or raises NatlinkCOMError.

        "Note this is not called from Python directly but as a side effect
        of calling getSelectText from CResultObject."
        — Joel Gould, GrammarObject.cpp (CGrammarObject::getGrammarGuid)
        [Note: original says "getSelectText" but means getSelectInfo]
        """
        iface = self._lazy_qi("_dgn_gram_common", "IDgnSRGramCommon")
        if iface is None:
            raise NatlinkCOMError("get_grammar_guid",
                                  error_message="QI(IDgnSRGramCommon) failed")
        return iface.Identify()

    # --- List operations (ISRGramCFGW) ---

    def list_set(self, list_name, words):
        """Set (replace) a grammar list with given words.

        ISRGramCFGW::ListSet(PCWSTR name, SDATA data)

        To empty a list, pass an empty word list -- this creates an SDATA
        with dwSize=0, matching the C++:

        "to empty the list, we will set the list to be a set of no words"
        — Joel Gould, GrammarObject.cpp (CGrammarObject::emptyList)

        C++ sets sData.pData = "\\0" with sData.dwSize = 0, so the data
        pointer is non-NULL but zero-length.  We pass b"" for the same
        effect.
        """
        if self._gram_cfg is None:
            # C++: onINVALIDINTERFACE "emptyList not support for this type of grammar"
            raise NatlinkCOMError("list_set", error_type=ERR_WRONG_TYPE,
                                  error_message="emptyList not supported for this type of grammar")
        sdata, _buf = self._make_sdata(_pack_srword_list(words))
        try:
            self._gram_cfg.ListSet(list_name, sdata)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _SRERR_INVALIDLIST:
                # C++: onUNKNOWNNAME "The list %s is not defined in the grammar"
                raise NatlinkCOMError("list_set", error_type=ERR_UNKNOWN_NAME,
                    error_message=f"The list {list_name} is not defined "
                                  f"in the grammar") from exc
            raise

    def list_append(self, list_name, word):
        """Append a word to a grammar list.

        ISRGramCFGW::ListAppend(PCWSTR name, SDATA data)
        """
        if self._gram_cfg is None:
            # C++: onINVALIDINTERFACE "appendList not support for this type of grammar"
            raise NatlinkCOMError("list_append", error_type=ERR_WRONG_TYPE,
                                  error_message="appendList not supported for this type of grammar")
        sdata, _buf = self._make_sdata(_pack_srword_list([word]))
        try:
            self._gram_cfg.ListAppend(list_name, sdata)
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _SRERR_INVALIDCHAR:
                # C++: "Invalid word in word list"
                raise NatlinkCOMError("list_append", error_type=ERR_INVALID_WORD,
                    error_message="Invalid word in word list") from exc
            if hr == _SRERR_INVALIDLIST:
                # C++: onUNKNOWNNAME "The list %s is not defined in the grammar"
                raise NatlinkCOMError("list_append", error_type=ERR_UNKNOWN_NAME,
                    error_message=f"The list {list_name} is not defined "
                                  f"in the grammar") from exc
            raise

    def list_get(self, list_name):
        """Get raw SDATA bytes for a grammar list.

        ISRGramCFGW::ListGet(PCWSTR name, PSDATA data)
        Returns raw bytes (SRWORDW array) — parsed by natlink_compat.GramObj.getList.
        """
        if self._gram_cfg is None:
            raise NatlinkCOMError("list_get", error_message="Grammar does not support lists")
        sdata = self._gram_cfg.ListGet(list_name)
        return sdata_to_bytes(sdata)

    def list_query(self, list_name):
        """Check if a grammar list exists.

        ISRGramCFGW::ListQuery(PCWSTR name, BOOL* exists)
        """
        if self._gram_cfg is None:
            return False
        return bool(self._gram_cfg.ListQuery(list_name))

    def list_remove(self, list_name, words):
        """Remove words from a grammar list.

        ISRGramCFGW::ListRemove(PCWSTR name, SDATA data)
        """
        if self._gram_cfg is None:
            raise NatlinkCOMError("list_remove", error_message="Grammar does not support lists")
        sdata, _buf = self._make_sdata(_pack_srword_list(words))
        self._gram_cfg.ListRemove(list_name, sdata)

    def link_query(self, link_name):
        """Check if a grammar link exists.

        ISRGramCFGW::LinkQuery(PCWSTR name, BOOL* exists)
        """
        if self._gram_cfg is None:
            return False
        return bool(self._gram_cfg.LinkQuery(link_name))

    def _make_sdata(self, raw_bytes):
        """Wrap raw bytes in a comtypes SDATA struct.

        Returns (sdata, buf) — caller MUST keep buf reference alive until
        the COM call completes.  Delegates to the shared _build_sdata helper.
        """
        return _build_sdata(self._tlb, raw_bytes or b"")

    def set_context(self, before_text="", after_text=""):
        """Set dictation context for better recognition.

        Matches C++ CGrammarObject::setContext:
          NEEDGRAMMAR + QI(ISRGramDictation) + Context(before, after)
          onINVALIDINTERFACE → "setContext not support for this type of grammar"
        """
        if self._gram_common is None:
            raise NatlinkCOMError("set_context",
                                  error_message="Grammar not loaded")
        iface = self._lazy_qi("_gram_dictation", "ISRGramDictationW")
        if iface is None:
            # C++: onINVALIDINTERFACE "setContext not support for this type of grammar"
            raise NatlinkCOMError("set_context", error_type=ERR_WRONG_TYPE,
                                  error_message="setContext not supported "
                                  "for this type of grammar")
        # C++ passes CComBSTR(beforeText), CComBSTR(afterText) — empty strings
        # become empty BSTRs, NOT NULL.  Dragon may treat NULL differently.
        iface.Context(before_text, after_text)
        log.debug("set_context(before=%r, after=%r)", before_text, after_text)

    def _require_select(self, caller):
        """Return IDgnSRGramSelectW or raise — shared guard for select-text methods."""
        if self._gram_common is None:
            raise NatlinkCOMError(caller, error_message="Grammar not loaded")
        iface = self._lazy_qi("_gram_select", "IDgnSRGramSelectW")
        if iface is None:
            raise NatlinkCOMError(caller, error_type=ERR_WRONG_TYPE,
                                  error_message=f"{caller} not supported "
                                  "for this type of grammar")
        return iface

    def set_select_text(self, text):
        """Set select-and-say text buffer.

        Matches C++ CGrammarObject::setSelectText:
          NEEDGRAMMAR + QI(IDgnSRGramSelect) + WordsSet(SDATA)
          onINVALIDINTERFACE → "setSelectText not support for this type of grammar"
        """
        iface = self._require_select("setSelectText")
        raw = text.encode("utf-16-le") + b"\x00\x00" if text else b""
        sdata, _buf = self._make_sdata(raw)
        iface.WordsSet(sdata)
        log.debug("set_select_text(%d chars)", len(text))

    def get_select_text(self):
        """Get select-and-say text buffer.

        Matches C++ CGrammarObject::getSelectText:
          NEEDGRAMMAR + QI(IDgnSRGramSelect) + WordsGet(&SDATA)
          onINVALIDINTERFACE → "setSelectText not support for this type of grammar"
          (Note: C++ error message says "setSelectText" even for getSelectText — reproduced)
        """
        # C++ uses "setSelectText" in error msg even for getSelectText (reproduced)
        iface = self._require_select("setSelectText")
        sdata = iface.WordsGet()
        raw = sdata_to_bytes(sdata)
        return raw.decode("utf-16-le").rstrip("\x00") if raw else ""

    def change_select_text(self, start, end, text):
        """Replace a range in the select-and-say text buffer.

        IDgnSRGramSelectW::WordsChange(DWORD start, DWORD count, SDATA data)

        Declared in C++ GrammarObject.h as changeSelectText(char*, int, int)
        but never implemented in GrammarObject.cpp.  The COM interface
        IDgnSRGramSelectW::WordsChange exists, so we implement it here.
        """
        iface = self._require_select("changeSelectText")
        raw = text.encode("utf-16-le") + b"\x00\x00" if text else b""
        sdata, _buf = self._make_sdata(raw)
        count = max(0, end - start)
        iface.WordsChange(start, count, sdata)
        log.debug("change_select_text(start=%d, end=%d, chars=%d)",
                  start, end, len(text))

    def delete_select_text(self, start, end):
        """Delete a range from the select-and-say text buffer."""
        iface = self._require_select("deleteSelectText")
        count = max(0, end - start)
        iface.WordsDelete(start, count)
        log.debug("delete_select_text(start=%d, end=%d)", start, end)

    def insert_select_text(self, start, text):
        """Insert text into the select-and-say buffer at an offset."""
        iface = self._require_select("insertSelectText")
        raw = text.encode("utf-16-le") + b"\x00\x00" if text else b""
        sdata, _buf = self._make_sdata(raw)
        iface.WordsInsert(start, sdata)
        log.debug("insert_select_text(start=%d, chars=%d)", start, len(text))


def _pack_srword_list(words):
    """Pack a list of strings into SRWORDW SDATA format.

    Each SRWORDW entry:
      DWORD dwSize     — total size of this entry (4-byte aligned)
      DWORD dwWordNum  — word number (0)
      WCHAR szWord[]   — null-terminated UTF-16LE string
    """
    if not words:
        return b""
    parts = []
    for word in words:
        encoded = (word + "\x00").encode("utf-16-le")
        entry_size = 8 + len(encoded)
        # Align to 4-byte boundary
        padded = (entry_size + 3) & ~3
        entry = struct.pack("<II", padded, 0) + encoded
        entry += b"\x00" * (padded - len(entry))
        parts.append(entry)
    return b"".join(parts)
