"""Lexicon helpers — raw COM vtable calls for vocabulary operations.

Uses IDgnLexWordW (dd10midl) for the reliable cross-bitness baseline.
ILexPronounceW is still attempted for C++-close paths, but pronunciation
retrieval is not currently dependable cross-process.

comtypes stores raw (no-HRESULT-raising) COM method callables under the
mangled name _InterfaceName__com_MethodName.  Python's name-mangling only
applies when the attribute is accessed from a method defined *inside*
that class.  Module-level code requires explicit getattr() with the
mangled name.
"""

import ctypes
import logging
import struct
from typing import List, Optional

from ._errors import (NatlinkCOMError,
                      ERR_INVALID_WORD,
                      ERR_UNKNOWN_NAME)
from ._dspeech_constants import (
    DGNWORDTESTFLAG_CASESENSITIVE,
    DGNWORDTESTFLAG_DICTONLY,
    DGNWORDTESTFLAG_ACTIVEVOCONLY,
)
from ._speech_constants import (
    CHARSET_ENGINEPHONETIC,
    VPS_UNKNOWN,
    E_BUFFERTOOSMALL as _E_BUFFERTOOSMALL,
    LEXERR_INVALIDTEXTCHAR as _LEXERR_INVALIDTEXTCHAR,
    LEXERR_INVALIDSENSE as _LEXERR_INVALIDSENSE,
    LEXERR_ALREADYINLEX as _LEXERR_ALREADYINLEX,
    LEXERR_ENGBUFTOOSMALL as _LEXERR_ENGBUFTOOSMALL,
)

log = logging.getLogger("natlink.com.lexicon")

_DGNENGINEINFO_SIZE = 8  # DgnEngineInfo = { DWORD dwFlags; DWORD dwWordNum; }


# --- Raw COM vtable helpers ---

def _word_test(lex, dwFlags, word):
    """IDgnSRLexiconW::WordTest — raw call, returns (hr, exists_bool)."""
    exists = ctypes.c_long(0)
    hr = getattr(lex, "_IDgnSRLexiconW__com_WordTest")(
        dwFlags, word, ctypes.byref(exists))
    return hr, bool(exists.value)


_POSINFO_SIZE = 24  # DWORD POS_Type + DWORD SAPI_POS + BYTE[16] Dgn_POS


def _get_posinfo_type():
    """Get the comtypes-generated POSINFO type from the TLB."""
    tlb = __import__('natlink_com._tlb', fromlist=['get_tlb']).get_tlb()
    return tlb.POSINFO

_POSINFO = None
_posinfo_lock = __import__("threading").Lock()

def _lex_word_get(lw, word):
    """IDgnLexWordW::Get — raw call.

    Get(word, POSINFO*, BYTE* enginfo, DWORD enginfo_size, DWORD* actual)
    Returns (hr, posinfo, enginfo_bytes).
    """
    global _POSINFO
    if _POSINFO is None:
        with _posinfo_lock:
            if _POSINFO is None:
                _POSINFO = _get_posinfo_type()
    posinfo = _POSINFO()
    actual = ctypes.c_ulong(0)
    # First call with NULL buffer to get required size
    hr = getattr(lw, "_IDgnLexWordW__com_Get")(
        word, ctypes.byref(posinfo), None, 0, ctypes.byref(actual))
    if hr < 0 or hr == 1:  # error or S_FALSE (word not found)
        return hr, posinfo, b""
    if actual.value == 0:
        return hr, posinfo, b""
    # Second call with properly sized buffer
    info_buf = (ctypes.c_ubyte * actual.value)()
    hr = getattr(lw, "_IDgnLexWordW__com_Get")(
        word, ctypes.byref(posinfo),
        info_buf, actual.value,
        ctypes.byref(actual))
    return hr, posinfo, bytes(info_buf[:actual.value])


def _lex_word_add(lw, word, posinfo_ptr=None, info_buf=None, info_size=0):
    """IDgnLexWordW::Add — raw call. Returns raw HRESULT.

    Add(word, POSINFO*, BYTE* enginfo, DWORD enginfo_size)
    posinfo and enginfo are [in, unique] — can be NULL.
    """
    return getattr(lw, "_IDgnLexWordW__com_Add")(
        word, posinfo_ptr, info_buf, info_size)


def _lex_pron_get(lex_pron, word, sense=0, pron_buf_size=64):
    """ILexPronounceW::Get — raw call.

    Matches C++ ILexPronounce::Get(CHARSET_ENGINEPHONETIC, word, sense,
    pronBuf, sizeof(pronBuf), &pronSize, &partSpeech,
    (BYTE*)&info, sizeof(DgnEngineInfo), &infoSize)

    Returns (hr, pron_buf, pron_size, part_speech, eng_info, info_size).
    """
    import ctypes
    pron_buf = ctypes.create_unicode_buffer(pron_buf_size)
    pron_ptr = ctypes.cast(pron_buf, ctypes.POINTER(ctypes.c_ushort))
    pron_size = ctypes.c_ulong(0)
    part_speech = ctypes.c_ulong(0)
    eng_info = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)()
    info_size = ctypes.c_ulong(0)
    # Zero-init — Dragon may return S_OK without writing
    ctypes.memset(eng_info, 0, _DGNENGINEINFO_SIZE)

    hr = getattr(lex_pron, "_ILexPronounceW__com_Get")(
        CHARSET_ENGINEPHONETIC, word, sense,
        pron_ptr, pron_buf_size * 2,  # buffer size in bytes
        ctypes.byref(pron_size),
        ctypes.byref(part_speech),
        eng_info, _DGNENGINEINFO_SIZE,
        ctypes.byref(info_size))
    return (hr, pron_buf, pron_size.value, part_speech.value,
            eng_info, info_size.value)


def _enum_next(enum_iface, requested=64, buffer_size=8192):
    """Fetch the next SRWORDW batch from a word enumerator.

    Returns `(hr, words)` where `words` is a parsed `[(text, word_num), ...]`
    SRWORDW array batch.
    """
    from ._res_obj import _parse_srwordw_array

    method = getattr(enum_iface, "_IDgnSRWordEnumW__com_Next", None)
    if method is None:
        method = getattr(enum_iface, "_IDgnSRWordPrefixEnumW__com_Next")

    _MAX_BUFFER = 16 * 1024 * 1024  # 16 MB safety cap
    while True:
        buf = (ctypes.c_ubyte * buffer_size)()
        actual = ctypes.c_ulong(0)
        fetched = ctypes.c_ulong(0)
        hr = method(requested, buf, ctypes.byref(actual), buffer_size,
                    ctypes.byref(fetched))
        hr_unsigned = hr & 0xFFFFFFFF
        if hr_unsigned in (_E_BUFFERTOOSMALL, _LEXERR_ENGBUFTOOSMALL):
            buffer_size = max(buffer_size * 2, actual.value or 0)
            if buffer_size > _MAX_BUFFER:
                raise NatlinkCOMError("WordEnum.Next",
                    error_message="Buffer growth exceeded 16 MB limit")
            continue
        if hr < 0:
            raise NatlinkCOMError("WordEnum.Next", hr=hr)
        return hr, _parse_srwordw_array(bytes(buf[:actual.value]))


def _collect_enum_words(enum_iface, reset_arg=None):
    """Collect all words from IDgnSRWordEnumW / IDgnSRWordPrefixEnumW."""
    if reset_arg is None:
        enum_iface.Reset()
    else:
        enum_iface.Reset(reset_arg)

    words = []
    while True:
        hr, batch = _enum_next(enum_iface)
        words.extend(batch)
        if hr == 1 or not batch:
            break
    return words


def _word_lookup(lex, method_name, query, flags=0, initial_chars=256):
    """Call WordFromPrefix / WordFromPron with automatic buffer growth.

    dspeech.h: WordFromPrefix(prefix, flags, bufSizeChars, buffer, actualSize)
    dd10midl:  p2 is the conformance for the output string (C_WSTRING sized).

    Uses the raw __com_ method to bypass comtypes's [out,string] handling,
    passing the buffer and size manually.
    """
    buf_chars = max(2, initial_chars)
    _MAX_CHARS = 4 * 1024 * 1024  # 4M chars safety cap
    method = getattr(lex, method_name)
    while True:
        buf = ctypes.create_unicode_buffer(buf_chars)
        buf_ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ushort))
        size_bytes = ctypes.c_ulong(buf_chars * 2)
        hr = method(query, flags, buf_chars, buf_ptr, ctypes.byref(size_bytes))
        hr_unsigned = hr & 0xFFFFFFFF
        if hr_unsigned in (_E_BUFFERTOOSMALL, _LEXERR_ENGBUFTOOSMALL):
            needed_chars = max(buf_chars * 2, (size_bytes.value // 2) + 1)
            if needed_chars > _MAX_CHARS:
                raise NatlinkCOMError(method_name,
                    error_message="Buffer growth exceeded limit")
            buf_chars = needed_chars
            continue
        if hr < 0:
            raise NatlinkCOMError(method_name, hr=hr)
        raw = ctypes.string_at(buf, size_bytes.value)
        return raw.decode("utf-16-le", errors="ignore").rstrip("\x00")


# --- Shared validation helpers ---

_STRICT_TEST_FLAGS = (DGNWORDTESTFLAG_ACTIVEVOCONLY |
                      DGNWORDTESTFLAG_DICTONLY |
                      DGNWORDTESTFLAG_CASESENSITIVE)


def _require_lex(conn, caller):
    """Return (lexicon, lex_word) or raise."""
    lex, lw = conn.lexicon, conn.lex_word
    if lex is None or lw is None:
        raise NatlinkCOMError(caller,
                              error_message="No lexicon/vocabulary interface")
    return lex, lw


def _map_flags(flags):
    """Map Python getWordInfo flags to Dragon WordTest flags (inverted logic)."""
    dw = 0
    if not (flags & 0x01):
        dw |= DGNWORDTESTFLAG_ACTIVEVOCONLY
    if not (flags & 0x02):
        dw |= DGNWORDTESTFLAG_DICTONLY
    if not (flags & 0x04):
        dw |= DGNWORDTESTFLAG_CASESENSITIVE
    return dw


def _check_word_exists(lex, word, caller, dw_flags=None):
    """WordTest — raises on COM error or invalid word, returns bool for exists.

    C++ distinguishes three outcomes:
      - hr < 0          → COM error (exception)
      - hr == S_FALSE(1) → invalid word (errInvalidWord exception)
      - !bExists         → word not in vocabulary (return False)
      - bExists          → word found (return True)
    — Joel Gould, DragonCode.cpp (getWordInfo, setWordInfo, getWordProns)
    """
    hr, exists = _word_test(lex, dw_flags or _STRICT_TEST_FLAGS, word)
    if hr < 0:
        raise NatlinkCOMError(f"{caller}::WordTest", hr=hr)
    if hr == 1:  # S_FALSE — word is invalid (Dragon rejects the spelling)
        raise NatlinkCOMError(caller, error_type=ERR_INVALID_WORD,
                              error_message=f"The word '{word}' is invalid "
                              "(NatSpeak does not allow that spelling)")
    return bool(exists)


# --- High-level vocabulary operations ---

def get_word_info(conn, word: str, flags: int = 0) -> Optional[int]:
    """Get word properties. Returns bit flags, or None if not in vocab.

    Matches C++ CDragonCode::getWordInfo:
      flags bits: 1 = consider inactive words (backup dictionary)
                  2 = consider active non-dictation words
                  4 = case insensitive match
      WordTest → S_FALSE means invalid word, !bExists means not found.
      Then ILexPronounce::Get for engine info (dwFlags).

    "If we got here then the word exists and is valid.  Look up the
    engine specific information (formatting flags)."
    — Joel Gould, DragonCode.cpp (getWordInfo)

    Tries ILexPronounceW::Get first (matching C++). Falls back to
    IDgnLexWordW::Get if the cross-process ILexPronounceW path is unavailable
    or unreliable.
    """
    # C++: if( flags & ~0x07 ) → "Unknown flags passed to getWordInfo"
    if flags & ~0x07:
        raise NatlinkCOMError("get_word_info",
                              error_message="Unknown flags passed to getWordInfo")
    lex, lw = _require_lex(conn, "get_word_info")
    if not _check_word_exists(lex, word, "get_word_info", _map_flags(flags)):
        return None

    # Try ILexPronounceW::Get first (C++ path)
    info_flags = _get_word_info_via_lex_pron(conn, word)
    if info_flags is not None:
        return info_flags

    # Fallback: IDgnLexWordW::Get
    hr, _, enginfo = _lex_word_get(lw, word)
    if hr < 0:
        raise NatlinkCOMError("IDgnLexWordW::Get", hr=hr)
    if len(enginfo) >= 4:
        return struct.unpack_from("<I", enginfo, 0)[0]
    return 0


def _get_word_info_via_lex_pron(conn, word):
    """Try ILexPronounceW::Get for engine info, matching C++ getWordInfo.

    C++ calls ILexPronounce::Get with pronBuf size=0 (only wants engine info).
    Returns dwFlags or None if the ILexPronounceW path is unavailable or
    unreliable.
    """
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        return None
    try:
        lex_pron = central.QueryInterface(tlb.ILexPronounceW)
    except Exception:
        return None
    try:
        # C++: pronBuf[1], size=0 — we only want engine info, not pronunciation
        pron_buf = ctypes.create_unicode_buffer(1)
        pron_ptr = ctypes.cast(pron_buf, ctypes.POINTER(ctypes.c_ushort))
        pron_size = ctypes.c_ulong(0)
        part_speech = ctypes.c_ulong(0)
        eng_info = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)()
        info_size = ctypes.c_ulong(0)
        # Zero-init engine info — Dragon may return S_OK without writing
        ctypes.memset(eng_info, 0, _DGNENGINEINFO_SIZE)

        hr = getattr(lex_pron, "_ILexPronounceW__com_Get")(
            CHARSET_ENGINEPHONETIC, word, 0,
            pron_ptr, 0,  # C++: pronBuf size = 0 (don't need pronunciation)
            ctypes.byref(pron_size),
            ctypes.byref(part_speech),
            eng_info, _DGNENGINEINFO_SIZE,
            ctypes.byref(info_size))
        if hr < 0:
            log.debug("ILexPronounceW::Get failed: 0x%08X — falling back",
                      hr & 0xFFFFFFFF)
            return None
        return struct.unpack_from("<I", bytes(eng_info), 0)[0]
    except Exception:
        log.debug("ILexPronounceW::Get exception — falling back",
                  exc_info=True)
        return None


def add_word(conn, word: str, pron: str = "", word_info: int = 0) -> bool:
    """Add a word. Returns True if added, False if already exists.

    Matches C++ CDragonCode::addWord:
      DgnEngineInfo: dwFlags = wordInfo, dwWordNum = wordInfo ? 1 : 0
      ILexPronounce::Add(CHARSET_ENGINEPHONETIC, word, pron, VPS_UNKNOWN, info)
      LEXERR_ALREADYINLEX → return 0 (not added)
      LEXERR_INVALIDTEXTCHAR → "The word '%s' is invalid"
    — Joel Gould, DragonCode.cpp (addWord)

    Tries ILexPronounceW::Add first (matching C++). Falls back to
    IDgnLexWordW::Add only when no explicit pronunciation is requested,
    because that fallback cannot preserve pronunciation payloads.
    """
    # C++: info.dwFlags = wordInfo; info.dwWordNum = wordInfo ? 1 : 0;
    info_bytes = struct.pack("<II", word_info, 1 if word_info else 0)
    info = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)(*info_bytes)

    # Try C++ path: ILexPronounceW::Add
    result = _add_word_via_lex_pron(conn, word, pron, info)
    if result is not None:
        return result

    if pron:
        raise NatlinkCOMError(
            "add_word",
            error_message=(
                "Adding a word with an explicit pronunciation requires "
                "ILexPronounceW; the fallback path would drop pronunciation "
                "data"
            ),
        )

    # Fallback: IDgnLexWordW::Add
    lw = conn.lex_word
    if lw is None:
        raise NatlinkCOMError("add_word", error_message="No vocabulary interface")
    hr = _lex_word_add(lw, word, None, info, _DGNENGINEINFO_SIZE)
    return _check_add_result(hr, word)


def _add_word_via_lex_pron(conn, word, pron, info):
    """Try ILexPronounceW::Add matching C++ addWord.

    C++: pLexPron->Add(CHARSET_ENGINEPHONETIC, word, pron,
         VPS_UNKNOWN, (BYTE*)&info, sizeof(DgnEngineInfo))

    Returns True/False or None to fall back.
    """
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        return None
    try:
        lex_pron = central.QueryInterface(tlb.ILexPronounceW)
    except Exception:
        return None
    try:
        # C++: pron is "" when no pronunciation specified, not NULL
        pron_str = pron if pron else ""
        hr = getattr(lex_pron, "_ILexPronounceW__com_Add")(
            CHARSET_ENGINEPHONETIC, word, pron_str,
            VPS_UNKNOWN, info, _DGNENGINEINFO_SIZE)
        return _check_add_result(hr, word)
    except NatlinkCOMError:
        raise
    except Exception:
        log.debug("ILexPronounceW::Add failed — falling back", exc_info=True)
        return None


def _check_add_result(hr, word):
    """Check HRESULT from Add, matching C++ error handling."""
    if hr == _LEXERR_ALREADYINLEX:
        # C++: "word was not added because it already exists" → return 0
        log.debug("Word '%s' already in lexicon", word)
        return False
    hr_unsigned = hr & 0xFFFFFFFF
    if hr_unsigned == _LEXERR_INVALIDTEXTCHAR:
        # C++: "The word '%s' is invalid (NatSpeak does not allow that spelling)"
        raise NatlinkCOMError("add_word", error_type=ERR_INVALID_WORD,
                              error_message=f"The word '{word}' is invalid "
                              "(NatSpeak does not allow that spelling)")
    if hr < 0:
        raise NatlinkCOMError("add_word", hr=hr)
    log.debug("Added word: %s", word)
    return True


def delete_word(conn, word: str) -> None:
    """Delete a word from vocabulary.

    Matches C++ CDragonCode::deleteWord:
      IDgnLexWord::Remove(word)
      LEXERR_INVALIDTEXTCHAR → "The word '%s' is invalid"
      S_FALSE → "The word '%s' is not in the active vocabulary"
    """
    lw = conn.lex_word
    if lw is None:
        raise NatlinkCOMError("delete_word", error_message="No lex word interface")
    hr = getattr(lw, "_IDgnLexWordW__com_Remove")(word)
    hr_unsigned = hr & 0xFFFFFFFF
    if hr_unsigned == _LEXERR_INVALIDTEXTCHAR:
        # C++: "The word '%s' is invalid (NatSpeak does not allow that spelling)"
        raise NatlinkCOMError("delete_word", error_type=ERR_INVALID_WORD,
                              error_message=f"The word '{word}' is invalid "
                              "(NatSpeak does not allow that spelling)")
    if hr == 1:  # S_FALSE
        # C++: "The word '%s' is not in the active vocabulary"
        raise NatlinkCOMError("delete_word", error_type=ERR_UNKNOWN_NAME,
                              error_message=f"The word '{word}' is not in "
                              "the active vocabulary")
    if hr < 0:
        raise NatlinkCOMError("IDgnLexWordW::Remove", hr=hr)
    log.debug("Deleted word: %s", word)


def set_word_info(conn, word: str, flags: int = 0) -> None:
    """Set word properties (fetch current info, re-add with new flags).

    Matches C++ CDragonCode::setWordInfo:
      1. WordTest with strict flags (ACTIVEVOCONLY | DICTONLY | CASESENSITIVE)
         - S_FALSE → invalid word
         - !bExists → word not in vocabulary
      2. ILexPronounce::Get to fetch current pronunciation + engine info
      3. Update info.dwFlags, info.dwWordNum
      4. ILexPronounce::Add with same pronunciation and new info

    "The way Draqgon [sic] NaturallySpeaking is coded, the wordInfo data
    will not be changed for an existing word unless you add the word back
    to the system with a pronunciation.  Therefore, we use a trick.  We
    first get all the word information then we write back that same
    information except that we include the new wordInfo."
    — Joel Gould, DragonCode.cpp (setWordInfo)  [typo is in original C++]

    NOTE: C++ uses ILexPronounce::Get to fetch and preserve the current
    pronunciation. That exact cross-process path is not currently reliable
    here, so we fall back to IDgnLexWordW::Add with NULL pronunciation.
    This assumes Dragon preserves the existing pronunciation when pron is NULL.
    """
    lex, lw = _require_lex(conn, "set_word_info")
    if not _check_word_exists(lex, word, "set_word_info"):
        # C++: "The word '%s' is not in the active vocabulary"
        raise NatlinkCOMError("set_word_info", error_type=ERR_UNKNOWN_NAME,
                              error_message=f"The word '{word}' is not in "
                              "the active vocabulary")

    # Try C++ path: ILexPronounceW::Get + ILexPronounceW::Add
    if _set_word_info_via_lex_pron(conn, word, flags):
        log.debug("Set word info (ILexPronounceW): %s -> 0x%X", word, flags)
        return

    # Fallback: IDgnLexWordW::Add with NULL pronunciation
    # C++: info.dwFlags = wordInfo; info.dwWordNum = wordInfo ? 1 : 0;
    new_info = struct.pack("<II", flags, 1 if flags else 0)
    new_info_buf = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)(*new_info)
    hr = _lex_word_add(lw, word, None, new_info_buf, _DGNENGINEINFO_SIZE)
    if hr < 0:
        raise NatlinkCOMError("IDgnLexWordW::Add", hr=hr)
    log.debug("Set word info (IDgnLexWordW fallback): %s -> 0x%X", word, flags)


def _set_word_info_via_lex_pron(conn, word, new_flags):
    """Try C++ setWordInfo path: Get current pron, re-Add with new flags.

    C++: ILexPronounce::Get(CHARSET_ENGINEPHONETIC, word, 0,
         pronBuf, 64, &pronSize, &partSpeech,
         (BYTE*)&info, sizeof(DgnEngineInfo), &infoSize)
    Then: info.dwFlags = wordInfo; info.dwWordNum = wordInfo ? 1 : 0;
    Then: ILexPronounce::Add(CHARSET_ENGINEPHONETIC, word, pronBuf,
         partSpeech, (BYTE*)&info, sizeof(DgnEngineInfo))

    Returns True if successful, False to fall back to IDgnLexWordW.
    """
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        return False
    try:
        lex_pron = central.QueryInterface(tlb.ILexPronounceW)
    except Exception:
        return False
    try:
        # Get current pronunciation + engine info
        pron_buf = ctypes.create_unicode_buffer(64)
        pron_ptr = ctypes.cast(pron_buf, ctypes.POINTER(ctypes.c_ushort))
        pron_size = ctypes.c_ulong(0)
        part_speech = ctypes.c_ulong(0)
        eng_info = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)()
        info_size = ctypes.c_ulong(0)
        ctypes.memset(eng_info, 0, _DGNENGINEINFO_SIZE)

        hr = getattr(lex_pron, "_ILexPronounceW__com_Get")(
            CHARSET_ENGINEPHONETIC, word, 0,
            pron_ptr, 64 * 2,  # buffer size in bytes (sizeof(pronBuf))
            ctypes.byref(pron_size),
            ctypes.byref(part_speech),
            eng_info, _DGNENGINEINFO_SIZE,
            ctypes.byref(info_size))
        if hr < 0:
            log.debug("ILexPronounceW::Get failed: 0x%08X", hr & 0xFFFFFFFF)
            return False

        # Update flags, re-Add with same pronunciation
        # C++: info.dwFlags = wordInfo; info.dwWordNum = wordInfo ? 1 : 0;
        struct.pack_into("<II", eng_info, 0, new_flags, 1 if new_flags else 0)

        hr = getattr(lex_pron, "_ILexPronounceW__com_Add")(
            CHARSET_ENGINEPHONETIC, word, pron_ptr,
            part_speech.value,
            eng_info, _DGNENGINEINFO_SIZE)
        if hr < 0:
            log.debug("ILexPronounceW::Add failed: 0x%08X", hr & 0xFFFFFFFF)
            return False
        return True
    except Exception:
        log.debug("ILexPronounceW set_word_info failed — falling back",
                  exc_info=True)
        return False


def get_word_prons(conn, word: str) -> Optional[List[str]]:
    """Get pronunciations. Returns list, None if word not found.

    Matches C++ CDragonCode::getWordProns:
      1. WordTest with strict flags — invalid → error, !exists → None
      2. Iterate ILexPronounceW::Get with sense 0..99 until INVALIDSENSE
      3. Collect pronunciation strings into a list

    "There is no SAPI call which gets all the word prons, we have to
    iterate over all the possible pronunciations."
    — Joel Gould, DragonCode.cpp (getWordProns)

    Falls back to empty list if the ILexPronounceW pronunciation path is
    unavailable or unreliable cross-process.
    """
    lex = conn.lexicon
    if lex is None:
        return None
    if not _check_word_exists(lex, word, "get_word_prons"):
        return None

    # Try ILexPronounceW — may fail cross-bitness
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        return []
    try:
        lex_pron = central.QueryInterface(tlb.ILexPronounceW)
    except Exception:
        log.debug("QI(ILexPronounceW) failed — pronunciations not available")
        return []

    # Iterate senses 0..99 collecting pronunciations
    prons = []
    for sense in range(100):
        try:
            pron_buf = ctypes.create_unicode_buffer(64)
            pron_ptr = ctypes.cast(pron_buf, ctypes.POINTER(ctypes.c_ushort))
            pron_size = ctypes.c_ulong(0)
            part_speech = ctypes.c_ulong(0)
            eng_info = (ctypes.c_ubyte * _DGNENGINEINFO_SIZE)()
            info_size = ctypes.c_ulong(0)

            hr = getattr(lex_pron, "_ILexPronounceW__com_Get")(
                CHARSET_ENGINEPHONETIC, word, sense,
                pron_ptr, 64 * 2,  # buffer size in bytes
                ctypes.byref(pron_size),
                ctypes.byref(part_speech),
                eng_info, _DGNENGINEINFO_SIZE,
                ctypes.byref(info_size))

            hr_unsigned = hr & 0xFFFFFFFF
            if hr_unsigned == _LEXERR_INVALIDSENSE:
                break  # no more pronunciations
            if hr_unsigned == _LEXERR_INVALIDTEXTCHAR:
                raise NatlinkCOMError("get_word_prons", error_type=ERR_INVALID_WORD,
                    error_message=f"The word '{word}' is invalid "
                    "(NatSpeak does not allow that spelling)")
            if hr < 0:
                log.debug("ILexPronounceW::Get(sense=%d) failed: 0x%08X — "
                          "falling back to empty list", sense, hr_unsigned)
                return []
            prons.append(pron_buf.value)
        except NatlinkCOMError:
            raise
        except Exception:
            log.debug("ILexPronounceW::Get failed (sense=%d) — "
                      "pronunciations not available cross-bitness",
                      sense, exc_info=True)
            return []
    return prons


def enumerate_words(conn) -> List[str]:
    """Enumerate lexicon words exposed by IDgnSRLexiconW::WordEnum."""
    lex = conn.lexicon
    if lex is None:
        raise NatlinkCOMError("enumerate_words",
                              error_message="No lexicon interface")
    enum_iface = lex.WordEnum()
    return [text for text, _word_num in _collect_enum_words(enum_iface)]


def enumerate_prefix_words(conn, prefix: str) -> List[str]:
    """Enumerate words for a prefix via IDgnSRLexiconW::WordPrefixEnum."""
    lex = conn.lexicon
    if lex is None:
        raise NatlinkCOMError("enumerate_prefix_words",
                              error_message="No lexicon interface")
    enum_iface = lex.WordPrefixEnum()
    return [text for text, _word_num in _collect_enum_words(enum_iface, prefix)]


def get_word_from_prefix(conn, prefix: str, flags: int = 0, **_kw) -> str:
    """Single-result wrapper for IDgnSRLexiconW::WordFromPrefix.

    dspeech.h: WordFromPrefix(prefix, flags, bufSizeChars, buffer, actualSize)
    The COM method has no 'index' parameter — that was a Python wrapper
    invention.  Extra kwargs are accepted and ignored for backwards compat.
    """
    lex = conn.lexicon
    if lex is None:
        raise NatlinkCOMError("get_word_from_prefix",
                              error_message="No lexicon interface")
    return _word_lookup(lex, "_IDgnSRLexiconW__com_WordFromPrefix",
                        prefix, flags)


def get_word_from_pron(conn, pronunciation: str,
                       flags: int = 0, **_kw) -> str:
    """Single-result wrapper for IDgnSRLexiconW::WordFromPron.

    Same parameter layout as WordFromPrefix.
    """
    lex = conn.lexicon
    if lex is None:
        raise NatlinkCOMError("get_word_from_pron",
                              error_message="No lexicon interface")
    return _word_lookup(lex, "_IDgnSRLexiconW__com_WordFromPron",
                        pronunciation, flags)
