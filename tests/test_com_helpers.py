"""Tests for _com_helpers: get_dragon_error_message and vtable call logic."""

import ctypes
from ctypes import c_long, c_ulong, c_void_p, c_wchar, POINTER, byref
import struct

import pytest

from natlink_com._com_helpers import (
    get_dragon_error_message,
    _call_error_message_get,
)
from natlink_com._guids import IID_IDgnErrorW


# ---------------------------------------------------------------------------
# Fake COM object builder
# ---------------------------------------------------------------------------

def iid_to_bytes(iid):
    """Convert a GUID struct to 16 raw bytes."""
    return bytes(ctypes.cast(
        byref(iid), ctypes.POINTER(ctypes.c_ubyte * 16)).contents)


class FakeCOMObject:
    """Minimal in-memory COM object with a working vtable.

    Layout: [ptr_to_vtable] -> [slot0, slot1, slot2, ...]
    qi_raw does: vtbl = cast(punk, PTR(PTR(c_void_p))).contents -> vtbl[0]
    This means punk must point to a memory location that itself points to
    the function pointer array.
    """

    def __init__(self, slots):
        """slots: dict of {index: ctypes_callback}"""
        n = max(slots.keys()) + 1
        self._fn_ptrs = (c_void_p * n)()
        self._prevent_gc = list(slots.values())
        for idx, fn in slots.items():
            self._fn_ptrs[idx] = ctypes.cast(fn, c_void_p).value

        # vtable_ptr points to the function pointer array
        self._vtbl_ptr = ctypes.cast(self._fn_ptrs, c_void_p)
        # The COM object is a pointer-to-vtable-pointer
        self._obj_mem = c_void_p(self._vtbl_ptr.value)

    @property
    def ptr(self):
        """Raw COM pointer (address of the object)."""
        return ctypes.addressof(self._obj_mem)


def _make_qi(match_iid_bytes, result_ptr):
    """QI callback: returns result_ptr if IID matches, else E_NOINTERFACE."""
    @ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(ctypes.c_ubyte * 16),
                        POINTER(c_void_p))
    def qi(this, riid, ppv):
        actual = bytes(riid.contents)
        if actual == match_iid_bytes:
            ppv[0] = result_ptr
            return 0  # S_OK
        ppv[0] = 0
        return -2147467262  # E_NOINTERFACE
    return qi


def _make_qi_fail():
    """QI callback that always returns E_NOINTERFACE."""
    @ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(ctypes.c_ubyte * 16),
                        POINTER(c_void_p))
    def qi(this, riid, ppv):
        ppv[0] = 0
        return -2147467262
    return qi


def _make_addref():
    @ctypes.WINFUNCTYPE(c_ulong, c_void_p)
    def addref(this):
        return 1
    return addref


def _make_release():
    @ctypes.WINFUNCTYPE(c_ulong, c_void_p)
    def release(this):
        return 0
    return release


def _make_last_error_get():
    @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p)
    def last_error_get(this, perror):
        return 0
    return last_error_get


def _make_error_message_get(message):
    """ErrorMessageGet that writes `message` into the buffer."""
    @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_ulong,
                        POINTER(c_ulong))
    def fn(this, pbuf, buf_size, pneeded):
        full = message + '\0'
        pneeded[0] = len(full)
        if buf_size < len(full):
            # Write truncated
            dst = (c_wchar * buf_size).from_address(pbuf)
            for i in range(min(buf_size - 1, len(message))):
                dst[i] = message[i]
            dst[min(buf_size - 1, len(message))] = '\0'
            return -2147220978  # E_BUFFERTOOSMALL (0x8004020E signed)
        dst = (c_wchar * buf_size).from_address(pbuf)
        for i, ch in enumerate(full):
            dst[i] = ch
        return 0  # S_OK
    return fn


def _make_error_message_get_fail(hresult):
    """ErrorMessageGet that always returns a failure HRESULT."""
    @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_ulong,
                        POINTER(c_ulong))
    def fn(this, pbuf, buf_size, pneeded):
        return hresult
    return fn


def _build_error_obj(message_fn):
    """Build a fake IDgnErrorW COM object."""
    return FakeCOMObject({
        0: _make_qi_fail(),
        1: _make_addref(),
        2: _make_release(),
        3: _make_last_error_get(),
        4: message_fn,
    })


def _build_source_obj(error_obj_ptr):
    """Build a fake IUnknown that QIs to error_obj_ptr for IDgnErrorW."""
    iid_bytes = iid_to_bytes(IID_IDgnErrorW)
    return FakeCOMObject({
        0: _make_qi(iid_bytes, error_obj_ptr),
        1: _make_addref(),
        2: _make_release(),
    })


# ---------------------------------------------------------------------------
# Tests: get_dragon_error_message
# ---------------------------------------------------------------------------

class TestGetDragonErrorMessage:

    def test_returns_none_for_null(self):
        assert get_dragon_error_message(None) is None
        assert get_dragon_error_message(0) is None

    def test_returns_none_when_qi_fails(self):
        """QI for IDgnErrorW fails -> returns None."""
        obj = FakeCOMObject({
            0: _make_qi_fail(),
            1: _make_addref(),
            2: _make_release(),
        })
        assert get_dragon_error_message(obj.ptr) is None

    def test_returns_message_on_success(self):
        """Full round-trip: QI succeeds, ErrorMessageGet writes a string."""
        msg = "Dragon error: microphone not paused"
        err_obj = _build_error_obj(_make_error_message_get(msg))
        src_obj = _build_source_obj(err_obj.ptr)
        result = get_dragon_error_message(src_obj.ptr)
        assert result == msg

    def test_retries_on_buffer_too_small(self):
        """E_BUFFERTOOSMALL with needed > 512 triggers retry."""
        msg = "X" * 600
        err_obj = _build_error_obj(_make_error_message_get(msg))
        src_obj = _build_source_obj(err_obj.ptr)
        result = get_dragon_error_message(src_obj.ptr)
        assert result == msg

    def test_returns_none_on_other_failure(self):
        """Non-E_BUFFERTOOSMALL failure -> returns None."""
        err_obj = _build_error_obj(
            _make_error_message_get_fail(-2147467259))  # E_FAIL
        src_obj = _build_source_obj(err_obj.ptr)
        assert get_dragon_error_message(src_obj.ptr) is None


# ---------------------------------------------------------------------------
# Tests: _call_error_message_get directly
# ---------------------------------------------------------------------------

class TestCallErrorMessageGet:

    def test_correct_vtable_slot(self):
        """Calls slot 4 (ErrorMessageGet), not slot 3 (LastErrorGet)."""
        calls = []

        @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p)
        def last_error_get(this, perror):
            calls.append('LastErrorGet')
            return 0

        @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_ulong,
                            POINTER(c_ulong))
        def error_message_get(this, pbuf, buf_size, pneeded):
            calls.append('ErrorMessageGet')
            dst = (c_wchar * buf_size).from_address(pbuf)
            dst[0] = 'A'
            dst[1] = '\0'
            pneeded[0] = 2
            return 0

        obj = FakeCOMObject({
            0: _make_qi_fail(),
            1: _make_addref(),
            2: _make_release(),
            3: last_error_get,
            4: error_message_get,
        })
        result = _call_error_message_get(obj.ptr)
        assert result == "A"
        assert calls == ['ErrorMessageGet']

    def test_passes_512_char_count(self):
        """Buffer size passed to ErrorMessageGet is 512 (chars, not bytes)."""
        received = []

        @ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_ulong,
                            POINTER(c_ulong))
        def error_message_get(this, pbuf, buf_size, pneeded):
            received.append(buf_size)
            dst = (c_wchar * buf_size).from_address(pbuf)
            dst[0] = '\0'
            pneeded[0] = 1
            return 0

        obj = FakeCOMObject({
            0: _make_qi_fail(),
            1: _make_addref(),
            2: _make_release(),
            3: _make_last_error_get(),
            4: error_message_get,
        })
        _call_error_message_get(obj.ptr)
        assert received == [512]
