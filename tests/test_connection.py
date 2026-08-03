"""Connection lifecycle and state machine tests."""

import pytest

import natlink_compat as natlink
from natlink_compat._state import _state
from natlink_compat._exceptions import WrongState


class TestState:

    def test_reset_clears_everything(self):
        class _Sentinel:
            pass

        fake_grammar = _Sentinel()
        fake_dict = _Sentinel()
        _state.backend = object()  # fake backend — makes connected=True
        _state.callback_depth = 5
        _state.begin_callbacks.append(lambda: None)
        _state.change_callbacks.append(lambda: None)
        _state.grammar_registry[1] = fake_grammar
        _state.dict_registry[2] = fake_dict

        _state.reset()

        assert not _state.connected
        assert _state.backend is None
        assert _state.callback_depth == 0
        assert len(_state.begin_callbacks) == 0
        assert len(_state.change_callbacks) == 0
        assert len(_state.grammar_registry) == 0
        assert len(_state.dict_registry) == 0
        from natlink_com._win32 import kernel32 as _k32
        assert _k32.WaitForSingleObject(_state._disconnect_event_handle, 0) != 0  # not signaled


class TestPreConnection:
    """Every connection-dependent function must raise WrongState before natConnect."""

    def setup_method(self):
        _state.reset()

    FUNCTIONS = [
        ("playString",       lambda: natlink.playString("")),
        ("playEvents",       lambda: natlink.playEvents([])),
        ("execScript",       lambda: natlink.execScript("")),
        ("recognitionMimic", lambda: natlink.recognitionMimic([""])),
        ("getClipboard",     lambda: natlink.getClipboard()),
        ("getCursorPos",     lambda: natlink.getCursorPos()),
        ("getScreenSize",    lambda: natlink.getScreenSize()),
        ("getCurrentModule", lambda: natlink.getCurrentModule()),
        ("getCurrentUser",   lambda: natlink.getCurrentUser()),
        ("getMicState",      lambda: natlink.getMicState()),
        ("setMicState",      lambda: natlink.setMicState("off")),
        ("inputFromFile",    lambda: natlink.inputFromFile("test.wav")),
        ("getAllUsers",       lambda: natlink.getAllUsers()),
        ("createUser",       lambda: natlink.createUser("__test__")),
        ("openUser",         lambda: natlink.openUser("test")),
        ("saveUser",         lambda: natlink.saveUser()),
        ("getUserTraining",  lambda: natlink.getUserTraining()),
        ("getTrainingMode",  lambda: natlink.getTrainingMode()),
        ("startTraining",    lambda: natlink.startTraining("calibrate")),
        ("finishTraining",   lambda: natlink.finishTraining(True)),
        ("getWordInfo",      lambda: natlink.getWordInfo("test")),
        ("addWord",          lambda: natlink.addWord("test")),
        ("deleteWord",       lambda: natlink.deleteWord("test")),
        ("setWordInfo",      lambda: natlink.setWordInfo("test", 0)),
        ("getWordProns",     lambda: natlink.getWordProns("test")),
    ]

    @pytest.mark.parametrize(
        "name,func", FUNCTIONS, ids=[x[0] for x in FUNCTIONS]
    )
    def test_raises_wrong_state(self, name, func):
        with pytest.raises(WrongState):
            func()


class TestPreConnectionSafe:

    def setup_method(self):
        _state.reset()

    def test_getCallbackDepth_returns_zero(self):
        assert natlink.getCallbackDepth() == 0

    def test_setBeginCallback_stores_and_clears(self):
        cb = lambda info: None
        natlink.setBeginCallback(cb)
        assert any(e.fn is cb for e in _state.begin_callbacks)
        natlink.setBeginCallback(None)
        assert len(_state.begin_callbacks) == 0

    def test_setChangeCallback_stores_and_clears(self):
        cb = lambda t, v: None
        natlink.setChangeCallback(cb)
        assert any(e.fn is cb for e in _state.change_callbacks)
        natlink.setChangeCallback(None)
        assert len(_state.change_callbacks) == 0

    def test_isNatSpeakRunning_returns_int(self):
        result = natlink.isNatSpeakRunning()
        assert isinstance(result, int)
        assert result in (0, 1)

    def test_natDisconnect_when_not_connected(self):
        natlink.natDisconnect()  # should not raise


@pytest.mark.online
class TestLiveConnection:

    def teardown_method(self):
        if _state.connected:
            try:
                natlink.natDisconnect()
            except Exception:
                _state.reset()

    def test_connect_and_disconnect(self, live_connection):
        natlink.natConnect()
        assert _state.connected
        assert _state.backend is not None
        natlink.natDisconnect()
        assert not _state.connected

    def test_connect_as_context_manager(self, live_connection):
        with natlink.natConnect():
            assert _state.connected
        assert not _state.connected

    def test_connect_idempotent(self, live_connection):
        natlink.natConnect()
        natlink.natConnect()  # should reconnect, not raise
        assert _state.connected

    def test_double_disconnect_is_safe(self, live_connection):
        natlink.natConnect()
        natlink.natDisconnect()
        natlink.natDisconnect()  # should not raise

    def test_isNatSpeakRunning_when_connected(self, live_connection):
        natlink.natConnect()
        assert natlink.isNatSpeakRunning() == 1
