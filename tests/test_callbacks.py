"""Callback system tests (timer, change, begin, results, hypothesis)."""

import time

import pytest

import natlink_compat as natlink
from natlink_compat._exceptions import MimicFailed

from _helpers import compile_grammar, extract_words, do_mimic


@pytest.mark.online
class TestLiveCallbacks:
    """Live callback tests verifying callbacks fire with correct types and values."""

    # --- Timer callback ---

    def test_timer_callback_fires(self, live_connection):
        """Timer callback fires repeatedly at the requested interval."""
        from conftest import wait_for_callback
        hits = []
        natlink.setTimerCallback(lambda: hits.append(time.monotonic()), 50)
        wait_for_callback(lambda: len(hits) >= 3, timeout=5.0)
        natlink.setTimerCallback(None, 0)
        assert len(hits) >= 3, f"Expected >=3 timer hits, got {len(hits)}"

    # --- Change callback ---

    def test_change_callback_fires_on_mic_toggle(self, live_connection):
        """Toggle mic state fires change callback with ("mic", new_state)."""
        received = []
        natlink.setChangeCallback(lambda t, info: received.append((t, info)))
        try:
            original = natlink.getMicState()
            target = "on" if original != "on" else "off"
            natlink.setMicState(target)
            from conftest import wait_for_callback
            wait_for_callback(
                lambda: any(r[0] == "mic" for r in received), timeout=2.0)

            mic_events = [r for r in received if r[0] == "mic"]
            assert len(mic_events) >= 1, \
                f"No mic change callback after setMicState({target!r}). Got: {received}"
            _, mic_info = mic_events[-1]
            assert isinstance(mic_info, str) and mic_info == target, \
                f"Expected mic state {target!r}, got {mic_info!r}"
        finally:
            natlink.setChangeCallback(None)
            try:
                natlink.setMicState(original)
                wait_for_callback(lambda: True, timeout=0.3)
            except Exception:
                pass

    # --- Begin callback ---

    def test_begin_callback_fires_on_mimic(self, live_connection):
        """Begin callback fires before recognition with (path, title, hwnd) tuple."""
        begin_received = []
        binary = compile_grammar("<rule> exported = test begin callback;")
        gram = natlink.GramObj()

        try:
            natlink.setBeginCallback(lambda info: begin_received.append(info))
            gram.setResultsCallBack(lambda w, r: None)
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "begin", "callback"])

            assert len(begin_received) >= 1, \
                "Global begin callback never fired during mimic"
            mod_info = begin_received[0]
            assert isinstance(mod_info, tuple) and len(mod_info) == 3, \
                f"module_info should be (path, title, hwnd), got {mod_info!r}"
            path, title, hwnd = mod_info
            assert isinstance(path, str)
            assert isinstance(title, str)
            assert isinstance(hwnd, int)
        finally:
            natlink.setBeginCallback(None)
            gram.unload()

    def test_begin_callback_before_results_callback(self, live_connection):
        """Begin callback fires BEFORE results callback."""
        order = []
        binary = compile_grammar("<rule> exported = test callback order;")
        gram = natlink.GramObj()

        try:
            natlink.setBeginCallback(lambda info: order.append("begin"))
            gram.setResultsCallBack(lambda w, r: order.append("results"))
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "callback", "order"])

            assert "begin" in order and "results" in order, \
                f"Expected begin+results, got {order}"
            assert order.index("begin") < order.index("results"), \
                f"Begin should fire before results: {order}"
        finally:
            natlink.setBeginCallback(None)
            gram.unload()

    # --- Results callback ---

    def test_results_callback_word_tuples_and_resobj(self, live_connection):
        """Results callback receives (word, ruleNumber) tuples and a usable ResObj."""
        received = []
        binary = compile_grammar("<rule> exported = hello world;")
        gram = natlink.GramObj()

        try:
            gram.setResultsCallBack(lambda w, r: received.append((w, r)))
            gram.load(binary)
            gram.activate("rule", 0)
            try:
                gram.setExclusive(1)
            except Exception:
                pass

            do_mimic(["hello", "world"])

            assert len(received) >= 1, "Results callback never fired"
            words, res_obj = received[0]
            assert isinstance(words, list)
            for item in words:
                assert isinstance(item, tuple) and len(item) == 2
                assert isinstance(item[0], str)
                assert isinstance(item[1], int)

            word_strs = extract_words(words)
            assert "hello" in word_strs and "world" in word_strs

            # ResObj usable
            assert isinstance(res_obj, natlink.ResObj)
            results = res_obj.getResults(0)
            assert results is not None and isinstance(results, list)
            flat_words = res_obj.getWords(0)
            assert isinstance(flat_words, list) and len(flat_words) >= 2
        finally:
            gram.unload()

    def test_allResults_other_string(self, live_connection):
        """With allResults=1, non-matching recognition passes "other" string."""
        caught = []
        binary_listener = compile_grammar("<rule> exported = very specific unused;")
        binary_matcher = compile_grammar("<rule> exported = hello world;")
        gram_listener = natlink.GramObj()
        gram_matcher = natlink.GramObj()

        try:
            gram_listener.setResultsCallBack(
                lambda w, r: caught.append(("listener", w, r)))
            gram_listener.load(binary_listener, allResults=1)
            gram_listener.activate("rule", 0)

            gram_matcher.load(binary_matcher)
            gram_matcher.activate("rule", 0)

            do_mimic(["hello", "world"])

            other_results = [c for c in caught if c[1] == "other"]
            assert len(other_results) >= 1, \
                f"Expected 'other' result, got: {[c[1] for c in caught]}"
            assert isinstance(other_results[0][2], natlink.ResObj)
        finally:
            gram_listener.unload()
            gram_matcher.unload()

    def test_allResults_reject_string(self, live_connection):
        """With allResults=1 and exclusive mode, unmatched mimic gives "reject"."""
        caught = []
        binary = compile_grammar("<rule> exported = very specific command only;")
        gram = natlink.GramObj()

        try:
            gram.setResultsCallBack(lambda w, r: caught.append((w, r)))
            gram.load(binary, allResults=1)
            gram.activate("rule", 0)
            gram.setExclusive(1)

            try:
                natlink.recognitionMimic(["completely", "random", "phrase"])
            except MimicFailed:
                pass
            time.sleep(1.0)

            reject_results = [c for c in caught if c[0] == "reject"]
            assert len(reject_results) >= 1, \
                f"Expected 'reject' in callback, got: {[c[0] for c in caught]}"
            assert isinstance(reject_results[0][1], natlink.ResObj)
        finally:
            gram.setExclusive(0)
            gram.unload()

    # --- Hypothesis callback ---

    def test_hypothesis_callback_fires(self, live_connection):
        """Hypothesis callback fires during recognition when hypothesis=1."""
        hypotheses = []
        binary = compile_grammar("<rule> exported = hello world;")
        gram = natlink.GramObj()
        try:
            gram.setHypothesisCallBack(lambda words: hypotheses.append(words))
            gram.setResultsCallBack(lambda w, r: None)
            gram.load(binary, hypothesis=1)
            gram.activate("rule", 0)
            do_mimic(["hello", "world"])
            for h in hypotheses:
                assert isinstance(h, list)
        finally:
            gram.unload()

    # --- Callback depth ---

    def test_callback_depth_during_results(self, live_connection):
        """getCallbackDepth() > 0 inside a results callback."""
        depths = []
        binary = compile_grammar("<rule> exported = test depth check;")
        gram = natlink.GramObj()

        try:
            gram.setResultsCallBack(
                lambda w, r: depths.append(natlink.getCallbackDepth()))
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "depth", "check"])

            assert len(depths) >= 1 and depths[0] >= 1
        finally:
            gram.unload()

    # --- PhraseFinish pause_recog lifecycle ---

    def test_pause_recog_zero_after_results_callback(self, live_connection):
        """pause_recog returns to 0 after results callback completes.

        Full lifecycle through real COM:
          GrammarSink.PhraseFinish increments pause_recog, defers
          → _do_phrase_finish fires callback, calls reset_pause_recog
          → pause_recog back to 0

        If reset_pause_recog didn't run, subsequent Paused callbacks
        would be deferred forever and Dragon would freeze.
        """
        from natlink_compat._state import _state

        pause_during = []
        pause_after = []
        binary = compile_grammar("<rule> exported = test pause recog;")
        gram = natlink.GramObj()

        try:
            def on_results(words, res):
                conn = _state.backend._conn
                pause_during.append(conn._pause_recog)

            gram.setResultsCallBack(on_results)
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "pause", "recog"])

            conn = _state.backend._conn
            pause_after.append(conn._pause_recog)

            assert len(pause_during) >= 1, "Results callback never fired"
            assert pause_after[0] == 0, \
                f"pause_recog={pause_after[0]} after callback — should be 0 (leak)"
        finally:
            gram.unload()

    # --- Exception isolation ---

    def test_broken_begin_doesnt_kill_grammar(self, live_connection):
        """Exception in global begin callback must not prevent grammar callbacks.

        C++ makeCallback catches exceptions and prints them — the callback
        chain continues.  Verified live: broken global begin, grammar begin
        must still fire.
        """
        gram_received = []
        binary = compile_grammar("<rule> exported = test broken begin;")
        gram = natlink.GramObj()

        try:
            def broken_begin(info):
                raise RuntimeError("user callback exploded")

            natlink.setBeginCallback(broken_begin)
            gram.setBeginCallBack(lambda info: gram_received.append(info))
            gram.setResultsCallBack(lambda w, r: None)
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "broken", "begin"])

            assert len(gram_received) >= 1, \
                "Grammar begin callback must fire despite broken global begin"
        finally:
            natlink.setBeginCallback(None)
            gram.unload()

    def test_broken_results_doesnt_crash(self, live_connection):
        """Exception in results callback is caught — no crash, no freeze.

        The next recognition must still work after a broken results callback.
        """
        binary = compile_grammar("<rule> exported = test broken results;")
        binary2 = compile_grammar("<rule> exported = test recovery works;")
        gram = natlink.GramObj()
        gram2 = natlink.GramObj()

        try:
            gram.setResultsCallBack(
                lambda w, r: (_ for _ in ()).throw(RuntimeError("boom")))
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["test", "broken", "results"])  # must not crash

            # Verify Dragon isn't frozen — load a new grammar and mimic
            recovered = []
            gram2.setResultsCallBack(lambda w, r: recovered.append(True))
            gram2.load(binary2)
            gram2.activate("rule", 0)

            do_mimic(["test", "recovery", "works"])
            assert len(recovered) >= 1, \
                "Dragon frozen after broken results callback"
        finally:
            gram.unload()
            gram2.unload()

    # --- ResObj methods ---

    def test_resobj_getWordInfo(self, live_connection):
        """ResObj.getWordInfo returns 7-tuples with timing and pronunciation."""
        captured = []
        binary = compile_grammar("<rule> exported = hello world;")
        gram = natlink.GramObj()
        try:
            gram.setResultsCallBack(
                lambda w, r: captured.append(r.getWordInfo(0)))
            gram.load(binary)
            gram.activate("rule", 0)
            try:
                gram.setExclusive(1)
            except Exception:
                pass
            do_mimic(["hello", "world"])
            assert len(captured) >= 1, "Results callback never fired"
            info = captured[0]
            assert info is not None and len(info) >= 2
            for entry in info:
                assert len(entry) == 7
                word, cfg, score, start_t, end_t, flags, pron = entry
                assert isinstance(word, str) and word
                assert isinstance(cfg, int)
                assert isinstance(start_t, int) and isinstance(end_t, int)
                assert end_t >= start_t
                assert isinstance(pron, str)
        finally:
            gram.unload()


# =========================================================================
# Unit tests — callback stacking (no Dragon required)
# =========================================================================

class TestCallbackStacking:
    """Per-loader callback registration, dispatch, and removal."""

    @pytest.fixture(autouse=True)
    def _clean_state(self):
        """Clear callback lists before/after each test."""
        from natlink_compat._state import _state
        _state.begin_callbacks.clear()
        _state.change_callbacks.clear()
        _state.timer_callbacks.clear()
        yield
        _state.begin_callbacks.clear()
        _state.change_callbacks.clear()
        _state.timer_callbacks.clear()

    def test_single_callback(self):
        from natlink_compat._callbacks import setBeginCallback, dispatch_begin_callback
        hits = []
        setBeginCallback(lambda info: hits.append(info))
        dispatch_begin_callback("mod_info")
        assert hits == ["mod_info"]

    def test_multiple_loaders_both_fire(self):
        from natlink_compat._callbacks import setBeginCallback, dispatch_begin_callback

        class LoaderA:
            def on_begin(self, info): self.got = info
        class LoaderB:
            def on_begin(self, info): self.got = info

        a, b = LoaderA(), LoaderB()
        setBeginCallback(a.on_begin)
        setBeginCallback(b.on_begin)
        dispatch_begin_callback("info")
        assert a.got == "info"
        assert b.got == "info"

    def test_remove_one_loader_keeps_other(self):
        from natlink_compat._callbacks import (
            setBeginCallback, setChangeCallback,
            _remove_callbacks_for, dispatch_begin_callback)

        class LoaderA:
            __module__ = "pkg_a.loader"
            def on_begin(self, info): self.got = info
        class LoaderB:
            __module__ = "pkg_b.loader"
            def on_begin(self, info): self.got = info

        a, b = LoaderA(), LoaderB()
        setBeginCallback(a.on_begin)
        setBeginCallback(b.on_begin)
        _remove_callbacks_for(a)

        a.got = b.got = None
        dispatch_begin_callback("info")
        assert a.got is None
        assert b.got == "info"

    def test_remove_clears_all_callback_types(self):
        from natlink_compat._callbacks import (
            setBeginCallback, setChangeCallback, _remove_callbacks_for)
        from natlink_compat._state import _state

        class Loader:
            def on_begin(self, info): pass
            def on_change(self, t, v): pass

        loader = Loader()
        setBeginCallback(loader.on_begin)
        setChangeCallback(loader.on_change)
        assert len(_state.begin_callbacks) == 1
        assert len(_state.change_callbacks) == 1

        _remove_callbacks_for(loader)
        assert len(_state.begin_callbacks) == 0
        assert len(_state.change_callbacks) == 0

    def test_set_none_clears_all(self):
        from natlink_compat._callbacks import setBeginCallback
        from natlink_compat._state import _state

        class A:
            def cb(self, info): pass
        class B:
            def cb(self, info): pass

        setBeginCallback(A().cb)
        setBeginCallback(B().cb)
        assert len(_state.begin_callbacks) == 2
        setBeginCallback(None)
        assert len(_state.begin_callbacks) == 0

    def test_same_owner_replaces(self):
        from natlink_compat._callbacks import setBeginCallback
        from natlink_compat._state import _state

        class Loader:
            def cb_v1(self, info): pass
            def cb_v2(self, info): pass

        loader = Loader()
        setBeginCallback(loader.cb_v1)
        setBeginCallback(loader.cb_v2)
        assert len(_state.begin_callbacks) == 1
        assert _state.begin_callbacks[0].fn == loader.cb_v2

    def test_exception_in_one_does_not_block_others(self):
        from natlink_compat._callbacks import setBeginCallback, dispatch_begin_callback

        class Bad:
            def on_begin(self, info): raise RuntimeError("boom")
        class Good:
            def on_begin(self, info): self.got = info

        bad, good = Bad(), Good()
        setBeginCallback(bad.on_begin)
        setBeginCallback(good.on_begin)
        dispatch_begin_callback("info")
        assert good.got == "info"

    def test_change_callback_stacking(self):
        from natlink_compat._callbacks import setChangeCallback, dispatch_change_callback

        class LoaderA:
            def on_change(self, t, v): self.got = (t, v)
        class LoaderB:
            def on_change(self, t, v): self.got = (t, v)

        a, b = LoaderA(), LoaderB()
        setChangeCallback(a.on_change)
        setChangeCallback(b.on_change)
        dispatch_change_callback("mic", "on")
        assert a.got == ("mic", "on")
        assert b.got == ("mic", "on")

    def test_plain_function_callback(self):
        from natlink_compat._callbacks import setBeginCallback, dispatch_begin_callback
        hits = []

        def my_begin(info):
            hits.append(info)

        setBeginCallback(my_begin)
        dispatch_begin_callback("info")
        assert hits == ["info"]

    def test_remove_plain_function_by_module(self):
        """Plain function callbacks are removed when their module matches the loader."""
        from natlink_compat._callbacks import (
            setBeginCallback, _remove_callbacks_for, _get_owner)
        from natlink_compat._state import _state

        hits = []
        def my_begin(info):
            hits.append(info)

        setBeginCallback(my_begin)
        assert len(_state.begin_callbacks) == 1

        # _get_owner returns the module name for plain functions
        owner = _get_owner(my_begin)
        assert isinstance(owner, str)

        # Create a fake loader whose __module__ matches
        class FakeLoader:
            pass
        loader = FakeLoader()
        loader.__module__ = my_begin.__module__
        _remove_callbacks_for(loader)
        assert len(_state.begin_callbacks) == 0

    def test_remove_helper_object_callbacks(self):
        """Callbacks on helper objects within the loader's package are removed."""
        from natlink_compat._callbacks import (
            setBeginCallback, _remove_callbacks_for)
        from natlink_compat._state import _state

        class GrammarManager:
            __module__ = "myloader.grammar"
            def on_begin(self, info): pass

        class MyLoader:
            __module__ = "myloader.main"

        mgr = GrammarManager()
        loader = MyLoader()
        setBeginCallback(mgr.on_begin)
        assert len(_state.begin_callbacks) == 1
        _remove_callbacks_for(loader)
        assert len(_state.begin_callbacks) == 0

    def test_remove_module_object_callbacks(self):
        """Removing callbacks for a module object (slow-path reload) works."""
        from natlink_compat._callbacks import (
            setBeginCallback, _remove_callbacks_for)
        from natlink_compat._state import _state
        import types

        mod = types.ModuleType("myloader.core")

        class InstanceInMod:
            __module__ = "myloader.core"
            def on_begin(self, info): pass

        inst = InstanceInMod()
        setBeginCallback(inst.on_begin)
        assert len(_state.begin_callbacks) == 1
        _remove_callbacks_for(mod)
        assert len(_state.begin_callbacks) == 0

    def test_lambda_no_accumulation(self):
        """Repeated lambda registration replaces, not accumulates."""
        from natlink_compat._callbacks import setBeginCallback
        from natlink_compat._state import _state

        for _ in range(10):
            setBeginCallback(lambda info: None)
        assert len(_state.begin_callbacks) == 1

    def test_explicit_owner_tag_removes_uninferable_callback(self):
        """A callback registered under a loader context is removed by tag even
        when its owner can't be inferred (lambda)."""
        from natlink_compat._callbacks import (
            setBeginCallback, _remove_callbacks_for, loader_registration)
        from natlink_compat._state import _state

        class LoaderA:
            __module__ = "pkg_a.loader"
        loader = LoaderA()

        with loader_registration(loader):
            setBeginCallback(lambda info: None)  # no inferable owner
        assert len(_state.begin_callbacks) == 1
        assert _state.begin_callbacks[0].owner == "pkg_a"

        _remove_callbacks_for(loader)
        assert len(_state.begin_callbacks) == 0

    def test_explicit_tag_survives_other_loader_removal(self):
        """A tagged callback is not removed by a different loader's teardown."""
        from natlink_compat._callbacks import (
            setBeginCallback, _remove_callbacks_for, loader_registration)
        from natlink_compat._state import _state

        class LoaderA:
            __module__ = "pkg_a.loader"
        class LoaderB:
            __module__ = "pkg_b.loader"
        a, b = LoaderA(), LoaderB()

        with loader_registration(a):
            setBeginCallback(lambda info: None)  # tagged pkg_a
        _remove_callbacks_for(b)                  # different package
        assert len(_state.begin_callbacks) == 1
        _remove_callbacks_for(a)
        assert len(_state.begin_callbacks) == 0

    def test_timer_callback_disabled_when_loader_removed_empties_list(self):
        """Removing the last loader's timer callback disables Dragon's COM timer."""
        from unittest.mock import MagicMock
        from natlink_compat._callbacks import (
            setTimerCallback, _remove_callbacks_for, loader_registration)
        from natlink_compat._state import _state

        class Loader:
            __module__ = "pkg_t.loader"
        loader = Loader()
        _state.backend = MagicMock()  # connected
        try:
            with loader_registration(loader):
                setTimerCallback(lambda: None, 50)
            _remove_callbacks_for(loader)
            assert len(_state.timer_callbacks) == 0
            _state.backend.set_timer_callback.assert_called_with(False, 0)
        finally:
            _state.backend = None
