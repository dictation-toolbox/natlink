"""test_regressions.py - Guards for specific defects, each tied to its cause.

These run without Dragon. Every test names the bug it prevents returning,
because each of these was silent in normal use and none was caught by the
existing suite.
"""

import gc
import itertools
import unittest
import unittest.mock
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Object handles must not be memory addresses
# ---------------------------------------------------------------------------

class TestObjectHandles(unittest.TestCase):
    """Handles keyed the sink registry AND travelled through the PostMessage
    deferral queue, resolving only when the pump drained. With ``id(self)``,
    a grammar freed during reload could have its queued results delivered to
    whatever new object landed on the same address.
    """

    def test_handles_are_unique_and_monotonic(self):
        from natlink_com._com_helpers import next_object_handle
        handles = [next_object_handle() for _ in range(100)]
        self.assertEqual(len(set(handles)), 100, "handles repeated")
        self.assertEqual(handles, sorted(handles), "handles not monotonic")

    def test_handle_not_reused_after_object_freed(self):
        """The actual aliasing scenario: free an object, allocate another.

        CPython will hand the same address back, so ``id()`` collides here.
        The allocator must not.
        """
        from natlink_com._com_helpers import next_object_handle

        class _Obj:
            def __init__(self):
                self.handle = next_object_handle()
                self.addr = id(self)

        first = _Obj()
        first_handle, first_addr = first.handle, first.addr
        del first
        gc.collect()

        # Allocate until CPython reuses the freed address, proving the
        # collision id(self) would have produced is real and reachable.
        reused_addr = False
        for _ in range(1000):
            other = _Obj()
            self.assertNotEqual(
                other.handle, first_handle,
                "handle reused after the owning object was freed")
            if other.addr == first_addr:
                reused_addr = True
                break
        # Not asserted as a requirement (allocator behaviour is not
        # contractual), but when it does happen it is exactly the aliasing
        # the old id(self) handle produced.
        if not reused_addr:
            self.skipTest("CPython did not reuse the address in this run")

    def test_grammar_and_dictation_handles_do_not_collide(self):
        from natlink_com._com_helpers import next_object_handle
        a = {next_object_handle() for _ in range(50)}
        b = {next_object_handle() for _ in range(50)}
        self.assertFalse(a & b, "handle namespaces overlap")

    # The tests above only exercise the allocator. These assert that the real
    # objects actually *use* it — without them the guard passes even with
    # ``self._handle = id(self)`` restored, which is exactly the bug.

    def _make_gram(self):
        from natlink_com._gram_obj import ComGramObj
        return ComGramObj(MagicMock(), MagicMock(), MagicMock(),
                          False, False, tlb=MagicMock())

    def _make_dict(self):
        from natlink_com._dict_obj import ComDictObj
        return ComDictObj(MagicMock(), MagicMock(), MagicMock(), MagicMock(),
                          tlb=MagicMock())

    def test_grammar_handle_is_not_its_address(self):
        gram = self._make_gram()
        self.assertNotEqual(gram.handle, id(gram),
                            "ComGramObj handle is its memory address")

    def test_dictation_handle_is_not_its_address(self):
        dobj = self._make_dict()
        self.assertNotEqual(dobj.handle, id(dobj),
                            "ComDictObj handle is its memory address")

    def test_freed_grammar_handle_is_never_handed_out_again(self):
        """The reload scenario, on the real class.

        Build a grammar, record its handle, free it, then build many more.
        With ``id(self)`` the address — and so the handle — comes back, and a
        queued WM_SENDRESULTS closure would resolve to the wrong grammar.
        """
        first = self._make_gram()
        first_handle = first.handle
        del first
        gc.collect()

        seen = set()
        for _ in range(500):
            g = self._make_gram()
            self.assertNotEqual(
                g.handle, first_handle,
                "a freed grammar's handle was reissued to a new grammar")
            self.assertNotIn(g.handle, seen, "two live grammars share a handle")
            seen.add(g.handle)


# ---------------------------------------------------------------------------
# ResObj must raise OutOfRange, not return None
# ---------------------------------------------------------------------------

class TestResObjRaisesOutOfRange(unittest.TestCase):
    """``while 1: ... except natlink.OutOfRange: break`` is how unimacro's
    _oops and the natlinkcore samples enumerate alternatives. Returning None
    turned the loop terminator into a TypeError further downstream.
    """

    def _exhausted_proxy(self):
        from natlink_com import NatlinkCOMError
        from natlink_com._errors import ERR_OUT_OF_RANGE
        proxy = MagicMock()
        err = NatlinkCOMError("get_results", error_type=ERR_OUT_OF_RANGE,
                              error_message="There is no result number 50")
        proxy.get_results.side_effect = err
        proxy.get_word_info.side_effect = err
        return proxy

    def test_getResults_raises(self):
        from natlink_compat._res_obj import ResObj
        from natlink_compat._exceptions import OutOfRange
        with self.assertRaises(OutOfRange):
            ResObj(self._exhausted_proxy()).getResults(50)

    def test_getWords_raises(self):
        from natlink_compat._res_obj import ResObj
        from natlink_compat._exceptions import OutOfRange
        with self.assertRaises(OutOfRange):
            ResObj(self._exhausted_proxy()).getWords(50)

    def test_getWordInfo_raises(self):
        from natlink_compat._res_obj import ResObj
        from natlink_compat._exceptions import OutOfRange
        with self.assertRaises(OutOfRange):
            ResObj(self._exhausted_proxy()).getWordInfo(50)

    def test_enumeration_idiom_terminates(self):
        """The consumer pattern, end to end."""
        from natlink_compat._res_obj import ResObj
        from natlink_compat._exceptions import OutOfRange
        from natlink_com import NatlinkCOMError
        from natlink_com._errors import ERR_OUT_OF_RANGE

        pages = [[{"word": "hello", "cfg_parse": 1}],
                 [{"word": "hallo", "cfg_parse": 1}]]

        def _get(choice):
            if choice < len(pages):
                return pages[choice]
            raise NatlinkCOMError("get_results", error_type=ERR_OUT_OF_RANGE,
                                  error_message="no such result")

        proxy = MagicMock()
        proxy.get_results.side_effect = _get
        res = ResObj(proxy)

        collected, i = [], 0
        while True:
            try:
                collected.append(res.getWords(i))
            except OutOfRange:
                break
            i += 1
            assert i < 10, "loop failed to terminate"
        self.assertEqual(collected, [["hello"], ["hallo"]])


# ---------------------------------------------------------------------------
# error_type ordinals must match the C++ enum
# ---------------------------------------------------------------------------

class TestErrorTypeMapping(unittest.TestCase):
    """22 of 35 raise sites carried a wrong ordinal, so consumers caught the
    wrong NatError subclass (natlinkutils catches BadGrammar on load; a bad
    grammar was raising OutOfRange).
    """

    def test_constants_match_cpp_enum_order(self):
        """Ordinals are fixed by Exceptions.h:14-33 — not free to renumber."""
        from natlink_com import _errors as E
        expected = {
            "ERR_NAT_ERROR": 0, "ERR_INVALID_WORD": 1, "ERR_UNKNOWN_NAME": 2,
            "ERR_BAD_GRAMMAR": 3, "ERR_USER_EXISTS": 4, "ERR_WRONG_STATE": 5,
            "ERR_OUT_OF_RANGE": 6, "ERR_MIMIC_FAILED": 7, "ERR_BAD_WINDOW": 8,
            "ERR_SYNTAX_ERROR": 9, "ERR_VALUE_ERROR": 10,
            "ERR_DATA_MISSING": 11, "ERR_WRONG_TYPE": 12,
        }
        for name, value in expected.items():
            self.assertEqual(getattr(E, name), value, f"{name} moved")

    def test_constants_resolve_to_right_exception_classes(self):
        from natlink_com import _errors as E
        from natlink_compat._exceptions import _ERROR_TYPE_MAP
        for const, cls_name in [
            (E.ERR_INVALID_WORD, "InvalidWord"),
            (E.ERR_UNKNOWN_NAME, "UnknownName"),
            (E.ERR_BAD_GRAMMAR, "BadGrammar"),
            (E.ERR_USER_EXISTS, "UserExists"),
            (E.ERR_WRONG_STATE, "WrongState"),
            (E.ERR_OUT_OF_RANGE, "OutOfRange"),
            (E.ERR_BAD_WINDOW, "BadWindow"),
            (E.ERR_WRONG_TYPE, "WrongType"),
        ]:
            self.assertEqual(_ERROR_TYPE_MAP[const].__name__, cls_name)

    def test_no_bare_numeric_error_types_in_source(self):
        """Magic numbers are what caused the original mis-transcriptions."""
        import pathlib
        import re
        src = pathlib.Path(__file__).parent.parent / "src" / "natlink_com"
        offenders = []
        for f in src.glob("*.py"):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"error_type\s*=\s*\d", line):
                    offenders.append(f"{f.name}:{n}")
        self.assertEqual(offenders, [], "use ERR_* constants, not literals")


# ---------------------------------------------------------------------------
# Legacy shims must be reachable through `import natlink`
# ---------------------------------------------------------------------------

class TestLegacyShimsReachable(unittest.TestCase):
    """_legacy.py exists so old code does not hit AttributeError, but its
    stubs were missing from __all__, so `import natlink` could not see them —
    the module failed at its only job.
    """

    def test_reachable_via_natlink_package(self):
        import natlink
        for name in ("setTrayIcon", "setMessageWindow", "displayText",
                     "dragon_status", "stop_provider"):
            self.assertTrue(hasattr(natlink, name),
                            f"natlink.{name} is not reachable")

    def test_setTrayIcon_accepts_the_unimacro_call(self):
        """unimacro _repeat calls this unconditionally; it must not raise."""
        import natlink
        natlink.setTrayIcon("_repeat.ico", "tooltip", lambda: None)
        natlink.setTrayIcon()          # remove-icon form
        natlink.setTrayIcon("right", "tip", None)


# ---------------------------------------------------------------------------
# Clearing a callback must not disable other loaders
# ---------------------------------------------------------------------------

class TestCallbackClearIsScoped(unittest.TestCase):
    """Legacy natlink had one callback slot, so set*Callback(None) was
    unambiguous. With several loaders, dragonfly's disconnect(), natlinkcore's
    finish() and NatlinkTimer all call it as ordinary teardown — a blanket
    clear let any one of them silently disable the others.
    """

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._saved = list(_state.begin_callbacks)
        _state.begin_callbacks.clear()

    def tearDown(self):
        self._state.begin_callbacks[:] = self._saved

    def _register_two(self):
        from natlink_compat import _callbacks as cb

        class _Loader:
            def on_begin(self, info): pass

        a, b = _Loader(), _Loader()
        cb._set_callback(self._state.begin_callbacks, a.on_begin,
                         owner_pkg="loader_alpha")
        cb._set_callback(self._state.begin_callbacks, b.on_begin,
                         owner_pkg="loader_beta")
        return a, b

    def test_one_loader_clearing_leaves_the_other(self):
        from natlink_compat import _callbacks as cb
        self._register_two()
        cb._set_callback(self._state.begin_callbacks, None,
                         owner_pkg="loader_alpha")
        owners = [e.owner for e in self._state.begin_callbacks]
        self.assertEqual(owners, ["loader_beta"],
                         "clearing one loader wiped another")

    def test_clearing_by_a_package_that_owns_nothing_is_a_no_op(self):
        from natlink_compat import _callbacks as cb
        self._register_two()
        cb._set_callback(self._state.begin_callbacks, None,
                         owner_pkg="some_other_package")
        owners = [e.owner for e in self._state.begin_callbacks]
        self.assertEqual(owners, ["loader_alpha", "loader_beta"])


# ---------------------------------------------------------------------------
# inputFromFile must wait on the channel Dragon actually signals
# ---------------------------------------------------------------------------

class TestInputFromFileWaitsOnRealSignal(unittest.TestCase):
    """It waited on conn.playback_done, a Win32 event nothing ever set, so it
    could only ever burn its full 5-minute timeout — measured at exactly
    300.0s against a live Dragon. Completion actually arrives as
    AttribChanged2(PLAYBACKDONE) -> signal(WM_ATTRIBCHANGED).
    """

    def test_dead_events_are_gone(self):
        """Nothing may reintroduce a handle with no SetEvent behind it."""
        import pathlib
        src = pathlib.Path(__file__).parent.parent / "src"
        hits = [f"{f.relative_to(src)}"
                for f in src.rglob("*.py")
                if not f.name.startswith("_gen_")
                and ("playback_done" in f.read_text(encoding="utf-8")
                     or "mimic_done" in f.read_text(encoding="utf-8"))]
        # The only permitted mention is the explanatory comment in _speech_ops.
        self.assertTrue(
            all(h.endswith("_speech_ops.py") for h in hits),
            f"dead completion events referenced in {hits}")

    def test_waits_on_attribchanged_playbackdone(self):
        import inspect
        from natlink_com import _speech_ops
        src = inspect.getsource(_speech_ops.input_from_file)
        self.assertIn("DGNSRAC_PLAYBACKDONE", src)
        self.assertIn("push_message_entry", src)
        self.assertIn("message_loop", src)


# ---------------------------------------------------------------------------
# natlink_com must not reach into natlink_compat objects
# ---------------------------------------------------------------------------

class TestLayerBoundary(unittest.TestCase):
    """The import graph was clean, but the COM layer unwrapped a compat
    wrapper by private attribute (gram_obj._com_gram), so renaming a compat
    private would have broken natlink_com silently at runtime.
    """

    def test_com_layer_touches_no_compat_privates(self):
        import pathlib
        import re
        src = pathlib.Path(__file__).parent.parent / "src" / "natlink_com"
        pattern = re.compile(r"\.\_com_gram\b|\.\_com_dict\b|\.\_proxy\b")
        offenders = []
        for f in src.glob("*.py"):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    offenders.append(f"{f.name}:{n}")
        self.assertEqual(offenders, [],
                         "natlink_com reached into a natlink_compat private")


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Loader lifecycle: registered is not the same as started
# ---------------------------------------------------------------------------

class TestLoaderLifecycle(unittest.TestCase):
    """``add_loader()`` before ``natConnect()`` could only register the loader —
    there was no engine to attach to yet — and nothing started it afterwards.
    Because ``running`` was derived from registry membership, such a loader was
    reported as running in the tray while its ``start()`` had never been called.
    """

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._saved = list(_state.loader_registry)
        _state.loader_registry.clear()
        _state.backend = None            # disconnected

    def tearDown(self):
        self._state.loader_registry[:] = self._saved
        from natlink_compat._actions import invalidate_loader_cache
        invalidate_loader_cache()

    def _loader(self, name="Pending"):
        l = MagicMock()
        type(l).__name__ = name
        return l

    def test_add_while_disconnected_registers_but_does_not_start(self):
        from natlink_compat._loaders import add_loader, get_loaders, get_running_loaders
        l = self._loader()
        add_loader(l, _module_name="pending_pkg")
        self.assertIn(l, get_loaders(), "loader was not registered")
        self.assertFalse(l.start.called, "start() ran with no connection")
        self.assertNotIn(l, get_running_loaders(),
                         "an unstarted loader is reported as running")

    def test_connect_starts_the_pending_loader(self):
        from natlink_compat._loaders import (add_loader, start_pending_loaders,
                                             get_running_loaders)
        l = self._loader()
        add_loader(l, _module_name="pending_pkg")
        started = start_pending_loaders()
        self.assertEqual(started, 1)
        l.start.assert_called_once()
        self.assertIn(l, get_running_loaders())

    def test_pending_start_is_not_repeated(self):
        from natlink_compat._loaders import add_loader, start_pending_loaders
        l = self._loader()
        add_loader(l, _module_name="pending_pkg")
        start_pending_loaders()
        self.assertEqual(start_pending_loaders(), 0, "loader started twice")
        l.start.assert_called_once()

    def test_active_loader_none_is_not_registered(self):
        """natlinkcore publishes shutdown with `natlink.active_loader = None`.

        Registering that put a NoneType entry in the registry, so get_loaders()
        handed callers a None to act on.
        """
        from natlink_compat._loaders import register_running_loader, get_loaders
        register_running_loader(None)
        self.assertEqual(get_loaders(), [], "None was registered as a loader")

    def test_register_running_loader_marks_it_started(self):
        from natlink_compat._loaders import (register_running_loader,
                                             get_running_loaders)
        l = self._loader("SelfRegistered")
        register_running_loader(l)
        self.assertIn(l, get_running_loaders(),
                      "a self-registering loader is already running")


class TestLoaderProtocolMatchesReality(unittest.TestCase):
    """The exported protocol rejected loaders natlink itself runs.

    ``runtime_checkable`` protocols require *every* declared member, so
    declaring both start() and stop() meant a perfectly valid loader without
    a stop() failed ``isinstance``. A third party validating against the
    documented protocol would have rejected working code.
    """

    def test_start_only_loader_satisfies_the_protocol(self):
        from natlink_compat import LoaderProtocol

        class StartOnly:
            def start(self): pass

        self.assertTrue(isinstance(StartOnly(), LoaderProtocol),
                        "a start()-only loader must satisfy LoaderProtocol")

    def test_is_loader_matches_what_add_loader_accepts(self):
        from natlink_compat import is_loader
        from natlink_compat._loaders import add_loader

        class StartOnly:
            def start(self): pass

        class RunOnly:
            def run(self): pass

        class NotALoader:
            pass

        self.assertTrue(is_loader(StartOnly()))
        self.assertTrue(is_loader(RunOnly()), "run() is the natlinkcore form")
        self.assertFalse(is_loader(NotALoader()))

        # add_loader must agree with is_loader on the rejection case.
        with self.assertRaises(TypeError):
            add_loader(NotALoader())

    def test_helpers_are_reachable_through_natlink(self):
        import natlink
        for name in ("is_loader", "get_running_loaders", "LoaderProtocol"):
            self.assertTrue(hasattr(natlink, name), f"natlink.{name} missing")


# ---------------------------------------------------------------------------
# Failure paths must not poison the process
# ---------------------------------------------------------------------------

class TestFailurePathsAreSafe(unittest.TestCase):
    """The connection mutex leak showed what this family costs: a cleanup path
    that leaks or throws leaves the process permanently unable to reconnect.
    """

    def test_disconnect_reaches_reset_even_when_a_step_raises(self):
        """_state.reset() clears the backend and closes the mutex.

        If a teardown step raises on the way there, connected stays True and
        the mutex stays held: the monitor re-signals dragon_exited forever and
        every later natConnect fails with ConnectionInUse.
        """
        from natlink_compat import _lifecycle
        from natlink_compat._state import _state

        backend = MagicMock()
        backend.conn = MagicMock()
        _state.backend = backend
        try:
            with unittest.mock.patch.object(
                    _lifecycle, "_disconnect_steps",
                    side_effect=RuntimeError("Dragon vanished mid-teardown")):
                with self.assertRaises(RuntimeError):
                    _lifecycle._disconnect()
            self.assertIsNone(_state.backend,
                              "reset() was skipped, so connected stays True")
            self.assertFalse(_state.connected)
        finally:
            _state.backend = None

    def test_create_returns_the_existing_hidden_window(self):
        """A second create() must not orphan the first window.

        Reachable whenever a connect fails after create() and is retried; the
        failure path does not destroy the window.
        """
        from natlink_com import _hidden_wnd

        first = _hidden_wnd.create()
        if not first:
            self.skipTest("could not create a hidden window in this session")
        try:
            second = _hidden_wnd.create()
            self.assertEqual(second, first,
                             "create() made a second window, orphaning the first")
        finally:
            _hidden_wnd.destroy()


class TestPerLoaderObjectAttribution(unittest.TestCase):
    """Callbacks and timers were owner-tagged, but grammars and dictation
    objects were not, so nothing could answer "which objects belong to this
    loader" -- even though Dragon permits releasing them individually.
    """

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._saved = dict(_state.grammar_registry), dict(_state.dict_registry)
        _state.grammar_registry.clear()
        _state.dict_registry.clear()

    def tearDown(self):
        self._state.grammar_registry.clear()
        self._state.dict_registry.clear()

    class _Fake:
        """Stands in for a compat GramObj/DictObj in the registry."""
        def __init__(self, owner):
            self._owner_pkg = owner
            self.unloaded = False
            self.destroyed = False

        def unload(self):
            self.unloaded = True

        def destroy(self):
            self.destroyed = True

    def _loader(self, pkg):
        # A real module loader, not a MagicMock: _loader_package prefers
        # __module__, which on a mock is "unittest.mock".
        import types
        return types.ModuleType(pkg)

    def test_objects_are_attributed_to_the_owning_loader(self):
        from natlink_compat._loaders import (get_grammars_for,
                                             get_dictation_objects_for)
        a, b = self._Fake("loader_alpha"), self._Fake("loader_beta")
        self._state.grammar_registry[1] = a
        self._state.grammar_registry[2] = b
        d = self._Fake("loader_alpha")
        self._state.dict_registry[3] = d

        alpha = self._loader("loader_alpha")
        self.assertEqual(get_grammars_for(alpha), [a])
        self.assertEqual(get_dictation_objects_for(alpha), [d])

    def test_unattributed_objects_belong_to_nobody(self):
        """A grammar made outside any loader must not be swept up."""
        from natlink_compat._loaders import get_grammars_for
        orphan = self._Fake(None)
        self._state.grammar_registry[1] = orphan
        self.assertEqual(get_grammars_for(self._loader("loader_alpha")), [])

    def test_release_touches_only_the_named_loader(self):
        from natlink_compat._loaders import release_objects_for
        mine, theirs = self._Fake("loader_alpha"), self._Fake("loader_beta")
        mine_dict = self._Fake("loader_alpha")
        self._state.grammar_registry[1] = mine
        self._state.grammar_registry[2] = theirs
        self._state.dict_registry[3] = mine_dict

        n_gram, n_dict = release_objects_for(self._loader("loader_alpha"))
        self.assertEqual((n_gram, n_dict), (1, 1))
        self.assertTrue(mine.unloaded)
        self.assertTrue(mine_dict.destroyed,
                        "dictation objects need destroy(); deactivate() "
                        "releases nothing")
        self.assertFalse(theirs.unloaded, "released another loader's grammar")

    def test_owner_context_attributes_creations(self):
        from natlink_compat._callbacks import owner_context, current_owner_package
        self.assertIsNone(current_owner_package())
        with owner_context("loader_alpha"):
            self.assertEqual(current_owner_package(), "loader_alpha")
        self.assertIsNone(current_owner_package())

    def test_remove_loader_releases_objects_the_framework_left(self):
        """Removing a loader must not leave its grammars loaded in Dragon.

        The "frameworks are authoritative for their own cleanup" contract is
        about not *guessing* -- _remove_callbacks_for infers ownership and
        could take another loader's callbacks. Objects record their owner, so
        there is nothing to guess, and leaving them loaded is user-visible:
        Dragon keeps recognising a disabled loader's commands.
        """
        import types
        from natlink_compat._loaders import _register, remove_loader

        loader = types.ModuleType("loader_alpha")
        loader.stop = lambda: None          # a framework that cleans up nothing
        _register(loader, "loader_alpha", started=True)

        mine = self._Fake("loader_alpha")
        theirs = self._Fake("loader_beta")
        self._state.grammar_registry[1] = mine
        self._state.grammar_registry[2] = theirs

        remove_loader(loader)

        self.assertTrue(mine.unloaded,
                        "removed loader's grammar was left loaded in Dragon")
        self.assertFalse(theirs.unloaded,
                         "removing one loader released another's grammar")

    def test_remove_loader_is_a_noop_when_the_framework_cleaned_up(self):
        """A well-behaved framework leaves nothing, so the backstop does nothing."""
        import types
        from natlink_compat._loaders import _register, remove_loader

        loader = types.ModuleType("loader_tidy")
        released = []

        def _stop():
            # Framework unloads its own grammar, as it should.
            obj = self._state.grammar_registry.pop(1, None)
            released.append(obj)

        loader.stop = _stop
        _register(loader, "loader_tidy", started=True)
        self._state.grammar_registry[1] = self._Fake("loader_tidy")

        remove_loader(loader)
        self.assertEqual(len(released), 1)
        self.assertEqual(list(self._state.grammar_registry), [])
