"""Exception hierarchy, HRESULT mapping, and COM error mapping tests."""

import pytest

from natlink_compat._exceptions import (
    NatError, InvalidWord, UnknownName, OutOfRange, MimicFailed,
    BadGrammar, WrongState, BadWindow,
    SyntaxError as NlSyntaxError,
    UserExists,
    ValueError as NlValueError,
    DataMissing, WrongType,
    _raise_for_hresult, _raise_for_com_error,
)


class TestExceptionHierarchy:

    ALL_SUBCLASSES = [
        InvalidWord, UnknownName, OutOfRange, MimicFailed,
        BadGrammar, WrongState, BadWindow, NlSyntaxError,
        UserExists, NlValueError, DataMissing, WrongType,
    ]

    @pytest.mark.parametrize("cls", ALL_SUBCLASSES, ids=lambda c: c.__name__)
    def test_inherits_from_NatError(self, cls):
        assert issubclass(cls, NatError)
        assert issubclass(cls, Exception)
        exc = cls("test message")
        assert isinstance(exc, NatError)

    def test_NatError_is_base(self):
        assert issubclass(NatError, Exception)
        assert not issubclass(NatError, RuntimeError)


class TestHresultMapping:

    HRESULT_CASES = [
        (0x80040032, InvalidWord),    # SRERR_INVALIDWORD
        (0x80040034, UnknownName),    # SRERR_RULENAMEDOESNOTEXIST
        (0x8004001A, OutOfRange),     # SRERR_VALUEOUTOFRANGE
        (0x80040016, MimicFailed),    # E_RECOGNIZER_BUSY
        (0x8004002D, BadGrammar),     # SRERR_GRAMMARERROR
        (0x80040010, WrongState),     # SRERR_INVALIDMODE
        (0x80040039, BadWindow),      # SRERR_INVALIDWINDOW
        (0x80040035, NlSyntaxError),  # SRERR_SYNTAXERROR
        (0x8004006A, UserExists),     # SRERR_SPEAKEREXISTS
        (0x80070057, NlValueError),   # E_INVALIDARG
        (0x80004005, NatError),       # E_FAIL
        (0x80040036, DataMissing),    # SRERR_GRAMMARTOOCOMPLEX
        (0x8004003B, WrongType),      # SRERR_INVALIDINTERFACE
    ]

    @pytest.mark.parametrize(
        "hresult,exc_class",
        HRESULT_CASES,
        ids=[c.__name__ for _, c in HRESULT_CASES],
    )
    def test_hresult_maps_to_exception(self, hresult, exc_class):
        signed = hresult - 0x100000000  # convert to signed
        with pytest.raises(exc_class):
            _raise_for_hresult(signed)

    def test_success_does_not_raise(self):
        _raise_for_hresult(0)   # S_OK
        _raise_for_hresult(1)   # S_FALSE

    def test_unknown_hresult_raises_NatError(self):
        with pytest.raises(NatError):
            _raise_for_hresult(-1)

    def test_context_appears_in_message(self):
        try:
            _raise_for_hresult(-1, "myFunction")
        except NatError as e:
            assert "myFunction" in str(e)


class TestCOMErrorMapping:

    COM_ERROR_CASES = [
        (0,  NatError),
        (1,  InvalidWord),
        (2,  UnknownName),
        (3,  BadGrammar),
        (4,  UserExists),
        (5,  WrongState),
        (6,  OutOfRange),
        (7,  MimicFailed),
        (8,  BadWindow),
        (9,  NlSyntaxError),
        (10, NlValueError),
        (11, DataMissing),
        (12, WrongType),
    ]

    @pytest.mark.parametrize(
        "error_type,exc_class",
        COM_ERROR_CASES,
        ids=[c.__name__ for _, c in COM_ERROR_CASES],
    )
    def test_com_error_type_maps(self, error_type, exc_class):
        with pytest.raises(exc_class):
            _raise_for_com_error(error_type)
