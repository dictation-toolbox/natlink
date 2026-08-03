"""Error handling: HRESULT -> exception mapping."""

import logging

log = logging.getLogger("natlink.com")

# Error-type codes, ordinal-identical to the C++ enum in
# Reference/natlink-master/NatlinkSource/Exceptions.h:14-33.  natlink_compat's
# _ERROR_TYPE_MAP indexes this same ordering to pick a NatError subclass, so a
# wrong value here silently raises the wrong exception class at the API surface.
# Always use these names — never a bare integer.
ERR_NAT_ERROR = 0
ERR_INVALID_WORD = 1
ERR_UNKNOWN_NAME = 2
ERR_BAD_GRAMMAR = 3
ERR_USER_EXISTS = 4
ERR_WRONG_STATE = 5
ERR_OUT_OF_RANGE = 6
ERR_MIMIC_FAILED = 7
ERR_BAD_WINDOW = 8
ERR_SYNTAX_ERROR = 9
ERR_VALUE_ERROR = 10
ERR_DATA_MISSING = 11
ERR_WRONG_TYPE = 12


class NatlinkCOMError(Exception):
    """COM operation error with .error_type, .hr, and .error_message.

    natlink_compat uses these attributes for exception mapping to
    the original natlink NatError hierarchy.
    """
    def __init__(self, operation: str, hr: int = 0,
                 error_type: int = 0, error_message: str = ""):
        self.error_type = error_type
        self.hr = hr
        self.error_message = error_message or f"HRESULT 0x{hr & 0xFFFFFFFF:08X}"
        super().__init__(f"{operation}: {self.error_message}")


def check_hresult(hr: int, operation: str) -> None:
    """Raise NatlinkCOMError if HRESULT indicates failure (hr < 0)."""
    if hr < 0:
        raise NatlinkCOMError(operation, hr=hr)
