"""test_resource_release.py - What Dragon actually releases, measured.

Per-loader teardown depends on being able to release one loader's objects
without disturbing another's. Whether that is possible is a property of
Dragon, not of our code, so it was determined empirically and is pinned here.

The instrument is ``comtypes.COMObject._refcnt`` on each sink, which counts
Dragon's cross-process references. Our own Python attribute is not an AddRef
and does not contribute, so 0 means Dragon has let go entirely.

Measured on Dragon 13 (2026-08-02):

  grammar sink    5 refs after load/activate  -> 0 after unload()
  dictation sink  7 refs after activate       -> 7 after deactivate()
                                              -> 0 after destroy()

The dictation asymmetry is the trap: ``deactivate()`` releases nothing, so a
loader that deactivates without destroying leaks every reference.

Notably there is no explicit per-grammar UnRegister in the API — releasing
our interface pointers is what makes Dragon let go.
"""

import time

import pytest

from _helpers import compile_grammar


def _rc(sink):
    from natlink_com._connection import _sink_com_refcount
    return _sink_com_refcount(sink)


def _drain(seconds=1.0):
    """Pump so Dragon's cross-process Release calls can land."""
    from natlink_com._pump import pump
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        pump()
        time.sleep(0.02)


@pytest.mark.online
class TestGrammarSinkRelease:

    def test_dragon_takes_refs_and_releases_them_all_on_unload(self, live_connection):
        import natlink_compat as natlink
        gram = natlink.GramObj()
        gram.load(compile_grammar("<r> exported = release probe one;"))
        sink = gram._com_gram._sink
        gram.activate("r", 0)

        held = _rc(sink)
        assert held > 0, "Dragon took no reference on the grammar sink"

        gram.unload()
        _drain()
        assert _rc(sink) == 0, (
            f"Dragon retained {_rc(sink)} of {held} refs after unload — the "
            f"grammar sink cannot be reclaimed, so per-loader teardown leaks")

    def test_unloading_one_grammar_leaves_another_untouched(self, live_connection):
        """Isolation is what makes per-loader teardown possible at all."""
        import natlink_compat as natlink
        fired = {"a": 0, "b": 0}
        a, b = natlink.GramObj(), natlink.GramObj()
        try:
            a.setResultsCallback(lambda w, r: fired.__setitem__("a", fired["a"] + 1))
            a.load(compile_grammar("<ra> exported = isolation alpha probe;"))
            sink_a = a._com_gram._sink
            a.activate("ra", 0)

            b.setResultsCallback(lambda w, r: fired.__setitem__("b", fired["b"] + 1))
            b.load(compile_grammar("<rb> exported = isolation bravo probe;"))
            sink_b = b._com_gram._sink
            b.activate("rb", 0)
            b_before = _rc(sink_b)

            a.unload()
            _drain()

            assert _rc(sink_a) == 0
            assert _rc(sink_b) == b_before, "unloading A disturbed B's refs"

            natlink.recognitionMimic(["isolation", "bravo", "probe"])
            _drain(2.0)
            assert fired["b"] >= 1, "B stopped recognising after A was unloaded"
            assert fired["a"] == 0, "the unloaded grammar still received results"
        finally:
            for g in (a, b):
                try:
                    g.unload()
                except Exception:
                    pass


@pytest.mark.online
class TestReleaseDuringCallback:
    """Teardown does not get to choose its moment: a loader may be removed
    while Dragon is mid-dispatch into one of its grammars.
    """

    def test_unload_from_inside_its_own_results_callback(self, live_connection):
        import natlink_compat as natlink
        gram = natlink.GramObj()
        seen = {"fired": 0, "error": None}
        captured = {}

        def _on_results(words, res):
            seen["fired"] += 1
            try:
                gram.unload()          # release while Dragon is calling us
            except Exception as exc:
                seen["error"] = f"{type(exc).__name__}: {exc}"

        gram.setResultsCallback(_on_results)
        gram.load(compile_grammar("<r> exported = reentrant unload probe;"))
        captured["sink"] = gram._com_gram._sink
        gram.activate("r", 0)

        natlink.recognitionMimic(["reentrant", "unload", "probe"])
        _drain(2.0)

        assert seen["fired"] == 1
        assert seen["error"] is None, f"unload inside callback failed: {seen['error']}"
        assert _rc(captured["sink"]) == 0
        # The engine must survive releasing a sink it was dispatching into.
        assert natlink.getMicState() in ("on", "off", "sleeping")

    def test_unload_from_begin_callback_mid_utterance(self, live_connection):
        """Removing a loader between gotBegin and results — the reload window."""
        import natlink_compat as natlink
        gram = natlink.GramObj()
        seen = {"begin": 0, "results": 0, "error": None}
        captured = {}

        def _on_begin(info):
            seen["begin"] += 1
            try:
                gram.unload()
            except Exception as exc:
                seen["error"] = f"{type(exc).__name__}: {exc}"

        gram.setBeginCallback(_on_begin)
        gram.setResultsCallback(lambda w, r: seen.__setitem__("results", seen["results"] + 1))
        gram.load(compile_grammar("<r> exported = begin unload probe;"))
        captured["sink"] = gram._com_gram._sink
        gram.activate("r", 0)

        try:
            natlink.recognitionMimic(["begin", "unload", "probe"])
        except Exception:
            pass  # no active grammar remains to match — acceptable
        _drain(2.0)

        assert seen["begin"] == 1
        assert seen["error"] is None, f"unload in begin callback failed: {seen['error']}"
        assert _rc(captured["sink"]) == 0
        assert natlink.getMicState() in ("on", "off", "sleeping")


@pytest.mark.online
class TestDictationSinkRelease:

    def test_deactivate_does_not_release_but_destroy_does(self, live_connection):
        """The asymmetry that makes dictation objects easy to leak.

        A loader that deactivates its dictation objects without destroying
        them leaves every Dragon reference in place.
        """
        import natlink_compat as natlink
        dobj = natlink.DictObj()
        dobj.activate(0)               # DictObj is lazily constructed
        sink = dobj._com_dict._sink

        held = _rc(sink)
        assert held > 0, "Dragon took no reference on the dictation sink"

        dobj.deactivate()
        _drain(0.5)
        assert _rc(sink) == held, (
            "deactivate() released references — if Dragon's behaviour changed, "
            "the teardown guidance in this module needs revisiting")

        dobj.destroy()
        _drain()
        assert _rc(sink) == 0, (
            f"Dragon retained {_rc(sink)} refs after destroy() — dictation "
            f"objects cannot be reclaimed per-loader")


@pytest.mark.online
class TestConnectRollback:
    """Acquisition is not atomic: by Register() the connection holds the site
    object, ~9 AddRef'd interface pointers and the hidden window. Without an
    unwind, a failure part-way leaves all of it alive while _state.backend is
    never assigned, so natDisconnect never runs and Dragon keeps the session.
    """

    def test_failure_midway_releases_what_was_acquired(self, live_connection):
        import natlink_compat as natlink
        from natlink_compat._state import _state
        from natlink_com._connection import DragonConnection

        # Real acquisition against a live Dragon, made to fail at the last
        # step -- after the interfaces and hidden window have been taken.
        conn = DragonConnection()
        import unittest.mock as mock
        with mock.patch.object(
                DragonConnection, "_try_qi",
                side_effect=RuntimeError("injected failure mid-acquisition")):
            with pytest.raises(Exception):
                conn.connect(register_marshal=False)

        # Whatever it managed to take must have been released.
        assert not conn._raw_ptrs, (
            f"{len(conn._raw_ptrs)} AddRef'd interface pointers survived a "
            f"failed connect")
        assert conn.central is None, "central interface retained after failure"

        # The live session must be unaffected.
        assert _state.connected
        assert natlink.getMicState() in ("on", "off", "sleeping")


@pytest.mark.online
class TestPerLoaderRelease:
    """Attribution plus the measured release behaviour: a loader's objects can
    be enumerated and released without touching another loader's.
    """

    def test_release_objects_for_drops_only_that_loaders_refs(self, live_connection):
        import types
        import natlink_compat as natlink
        from natlink_compat._callbacks import owner_context
        from natlink_compat._loaders import (get_grammars_for,
                                             release_objects_for)

        alpha = types.ModuleType("loader_alpha")
        beta = types.ModuleType("loader_beta")

        # Grammars created inside a loader's context are attributed to it,
        # exactly as they are during start()/reload or a begin callback.
        with owner_context("loader_alpha"):
            a = natlink.GramObj()
            a.load(compile_grammar("<ra> exported = attribution alpha probe;"))
            a.activate("ra", 0)
        with owner_context("loader_beta"):
            b = natlink.GramObj()
            b.load(compile_grammar("<rb> exported = attribution bravo probe;"))
            b.activate("rb", 0)

        sink_a, sink_b = a._com_gram._sink, b._com_gram._sink
        try:
            assert get_grammars_for(alpha) == [a]
            assert get_grammars_for(beta) == [b]
            b_before = _rc(sink_b)

            n_gram, n_dict = release_objects_for(alpha)
            _drain()

            assert n_gram == 1
            assert _rc(sink_a) == 0, "alpha's grammar was not released"
            assert _rc(sink_b) == b_before, "beta's grammar was disturbed"
            assert get_grammars_for(alpha) == [], "registry still lists alpha's"
        finally:
            for g in (a, b):
                try:
                    g.unload()
                except Exception:
                    pass


@pytest.mark.online
@pytest.mark.teardown
class TestAllEngineSinksDrain:
    """Everything natlink registers with the engine must let go at teardown.

    ``ISRCentralW`` is the only interface exposing ``UnRegister``. The action
    sink (registered on OutputEvent and Interpreter) and the dictation sink
    expose ``Register`` only, so for those, releasing our interface pointers
    is the entire release mechanism -- there is nothing else to call.

    Measured on Dragon 13: engine sink 7 refs -> 0, action sink 3 refs -> 0.

    Opt-in (``pytest -m teardown``): the only way to observe the drain is to
    disconnect, and the reconnect that follows costs the suite ~70s.
    """

    def test_engine_and_action_sinks_release_on_disconnect(self, live_connection):
        import natlink_compat as natlink
        from natlink_compat._state import _state

        conn = _state.backend.conn
        engine_sink, action_sink = conn._engine_sink, conn._action_sink
        assert _rc(engine_sink) > 0, "engine sink was never registered"
        assert _rc(action_sink) > 0, "action sink was never registered"

        natlink.natDisconnect()
        _drain()
        try:
            assert _rc(engine_sink) == 0, (
                f"engine sink retained {_rc(engine_sink)} refs after disconnect")
            assert _rc(action_sink) == 0, (
                f"action sink retained {_rc(action_sink)} refs — it has no "
                f"UnRegister, so releasing the interfaces is the only way it "
                f"can be let go")
        finally:
            # _ensure_connected reconnects for the next test, but be explicit.
            if not _state.connected:
                natlink.natConnect(discovered_loaders=[])


@pytest.mark.online
class TestResultObjectLifetime:
    """Each live result object holds Dragon references plus an
    ``ISRResMemory::LockSet(True)`` on the utterance's wave data, so they must
    not accumulate. They are tracked by weakref rather than owned: the wrapper
    is an ephemeral callback argument, but consumers may retain it (dragonfly
    keeps results for corrections).

    There is no ``LockSet(False)`` — as in the C++ original, the lock lives on
    the result object and goes when the object is released.
    """

    def _mimic(self, natlink, n):
        from natlink_com._pump import pump
        for _ in range(n):
            natlink.recognitionMimic(["lifetime", "probe", "utterance"])
            for _ in range(6):
                pump()
                time.sleep(0.01)

    def test_results_do_not_accumulate_and_clear_when_dropped(self, live_connection):
        import gc
        import natlink_compat as natlink
        from natlink_com import _res_obj

        retained = []
        keep = {"on": False}
        gram = natlink.GramObj()
        gram.setResultsCallback(
            lambda w, r: retained.append(r) if keep["on"] else None)
        gram.load(compile_grammar("<r> exported = lifetime probe utterance;"))
        gram.activate("r", 0)
        try:
            # Not retained: nothing should be left alive.
            self._mimic(natlink, 5)
            gc.collect()
            _drain(0.3)
            assert len(_res_obj._live_res_objs) == 0, (
                "result objects accumulated even though nothing retained them")

            # Retained: tracked for exactly as long as the consumer holds them.
            keep["on"] = True
            self._mimic(natlink, 5)
            gc.collect()
            assert len(retained) == 5
            assert len(_res_obj._live_res_objs) == 5, (
                "retained result objects are not tracked, so natDisconnect "
                "would not release them")

            # Dropped: the weakref callback must clear the registry.
            retained.clear()
            gc.collect()
            _drain(0.3)
            assert len(_res_obj._live_res_objs) == 0, (
                "registry kept entries for collected result objects")
        finally:
            keep["on"] = False
            try:
                gram.unload()
            except Exception:
                pass

    def test_released_result_fails_cleanly_rather_than_crashing(self, live_connection):
        """natDisconnect releases results out from under any consumer still
        holding one; using it afterwards must raise, not access freed COM."""
        import natlink_compat as natlink
        from natlink_com._pump import pump

        got = []
        gram = natlink.GramObj()
        gram.setResultsCallback(lambda w, r: got.append(r))
        gram.load(compile_grammar("<r> exported = released result probe;"))
        gram.activate("r", 0)
        try:
            natlink.recognitionMimic(["released", "result", "probe"])
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not got:
                pump()
                time.sleep(0.01)
            assert got, "no result delivered"

            got[0]._proxy.release()
            with pytest.raises(Exception):
                got[0].getWords(0)
        finally:
            try:
                gram.unload()
            except Exception:
                pass
