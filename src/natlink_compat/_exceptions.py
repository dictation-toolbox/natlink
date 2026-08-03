"""_exceptions.py - NatError hierarchy and HRESULT-to-exception mapping."""


class NatError(Exception):
    """Base exception for all natlink errors."""
    pass


class InvalidWord(NatError):
    pass


class UnknownName(NatError):
    pass


class OutOfRange(NatError):
    pass


class MimicFailed(NatError):
    pass


class BadGrammar(NatError):
    pass


class WrongState(NatError):
    pass


class ConnectionInUse(NatError):
    """Another process already holds the single Dragon connection.

    Natlink permits one active connection at a time, guarded by the
    ``NatlinkConnectionActive`` named mutex. The current owner must release
    it (natlink tray menu > Configure > Release Dragon, or
    ``natDisconnect()``) before another
    process can connect. See issue #228.
    """
    pass


class BadWindow(NatError):
    pass


class SyntaxError(NatError):
    pass


class UserExists(NatError):
    pass


class ValueError(NatError):
    pass


class DataMissing(NatError):
    pass


class WrongType(NatError):
    pass


# HRESULT codes from Dragon / SAPI 4 that map to specific exceptions.
# SRCERR constants come from speech.h; DGNERR from dspeech.h.
_HRESULT_MAP = {
    0x80040032: InvalidWord,     # SRERR_INVALIDWORD
    0x80040034: UnknownName,     # SRERR_RULENAMEDOESNOTEXIST
    0x80040207: UnknownName,     # SRERR_INVALIDLIST
    0x8004001A: OutOfRange,      # SRERR_VALUEOUTOFRANGE
    0x80040016: MimicFailed,     # E_RECOGNIZER_BUSY (mimic)
    0x8004002D: BadGrammar,      # SRERR_GRAMMARERROR
    0x80040010: WrongState,      # SRERR_INVALIDMODE
    0x80040039: BadWindow,       # SRERR_INVALIDWINDOW
    0x80040035: SyntaxError,     # SRERR_SYNTAXERROR
    0x8004006A: UserExists,      # SRERR_SPEAKEREXISTS
    0x80070057: ValueError,      # E_INVALIDARG
    0x80004005: NatError,        # E_FAIL (generic)
    0x80040036: DataMissing,     # SRERR_GRAMMARTOOCOMPLEX (overloaded)
    0x8004003B: WrongType,       # SRERR_INVALIDINTERFACE
}


# Error-type codes from NatlinkCOMError.error_type (matches original C++ enum).
_ERROR_TYPE_MAP = {
    0: NatError,
    1: InvalidWord,
    2: UnknownName,
    3: BadGrammar,
    4: UserExists,
    5: WrongState,
    6: OutOfRange,
    7: MimicFailed,
    8: BadWindow,
    9: SyntaxError,
    10: ValueError,
    11: DataMissing,
    12: WrongType,
}


def _raise_for_hresult(hr, context=""):
    """Raise the appropriate NatError subclass for a negative HRESULT.

    Does nothing if hr >= 0 (success).
    """
    if hr >= 0:
        return
    unsigned = hr & 0xFFFFFFFF
    exc_class = _HRESULT_MAP.get(unsigned, NatError)
    msg = f"HRESULT 0x{unsigned:08X}"
    if context:
        msg = f"{context}: {msg}"
    raise exc_class(msg)


def _raise_for_com_error(error_type, hr=None, context="", detail=""):
    """Raise a NatError subclass using error_type as the primary signal.

    Falls back to HRESULT mapping when error_type is None (e.g. when the
    COM call returns only an HRESULT without error details).
    """
    exc_class = _ERROR_TYPE_MAP.get(error_type)
    if exc_class is None and hr is not None:
        exc_class = _HRESULT_MAP.get(hr & 0xFFFFFFFF, NatError)
    elif exc_class is None:
        exc_class = NatError
    parts = []
    if context:
        parts.append(context)
    if hr is not None:
        parts.append(f"HRESULT 0x{(hr & 0xFFFFFFFF):08X}")
    if error_type is not None:
        parts.append(f"error_type {error_type}")
    msg = ": ".join(parts) if parts else "natlink COM error"
    if detail:
        msg += f" — {detail}"
    raise exc_class(msg)


def com_call(context, fn, *args, **kwargs):
    """Call a natlink_com API and map all errors to NatError classes.

    Handles NatlinkCOMError (our wrapper), _ctypes.COMError (comtypes),
    and connection errors.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        # NatlinkCOMError — our wrapper with error_type + hr
        if hasattr(exc, 'error_type') and hasattr(exc, 'hr'):
            _raise_for_com_error(
                exc.error_type, hr=exc.hr, context=context,
                detail=getattr(exc, 'error_message', ''))
        # _ctypes.COMError — comtypes raises this for failed COM calls
        if hasattr(exc, 'hresult'):
            _raise_for_hresult(exc.hresult, context=context)
        # Connection errors
        if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
            raise NatError(f"{context}: connection lost: {exc}") from exc
        raise NatError(f"{context}: {exc}") from exc
