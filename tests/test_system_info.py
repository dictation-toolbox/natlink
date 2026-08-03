"""System info queries and mic state control tests."""

import pytest

import natlink_compat as natlink


@pytest.mark.online
class TestLiveSystemInfo:

    def test_getCurrentUser(self, live_connection):
        result = natlink.getCurrentUser()
        assert isinstance(result, tuple)
        assert len(result) == 2
        name, directory = result
        assert isinstance(name, str)
        assert len(name) > 0
        assert isinstance(directory, str)
        assert len(directory) > 0, "directory must not be empty"
        assert directory.endswith("\\current"), (
            f"directory should end with \\current, got: {directory!r}"
        )

    def test_getCurrentModule(self, live_connection):
        result = natlink.getCurrentModule()
        assert isinstance(result, tuple)
        assert len(result) == 3
        path, title, hwnd = result
        assert isinstance(path, str)
        assert isinstance(title, str)
        assert isinstance(hwnd, int)

    def test_getMicState(self, live_connection):
        state = natlink.getMicState()
        assert state in ("on", "off", "sleeping", "disabled")

    def test_getScreenSize(self, live_connection):
        width, height = natlink.getScreenSize()
        assert isinstance(width, int) and width > 0
        assert isinstance(height, int) and height > 0

    def test_getCursorPos(self, live_connection):
        x, y = natlink.getCursorPos()
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_getClipboard(self, live_connection):
        result = natlink.getClipboard()
        assert isinstance(result, str)

    def test_getCallbackDepth_zero(self, live_connection):
        assert natlink.getCallbackDepth() == 0


@pytest.mark.online
class TestLiveMicState:

    @pytest.mark.parametrize("target", ["off", "sleeping", "on"])
    def test_set_mic_state(self, live_connection, target):
        original = natlink.getMicState()
        try:
            natlink.setMicState(target)
            assert natlink.getMicState() == target
        finally:
            natlink.setMicState(original)
