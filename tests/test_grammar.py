"""GramObj lifecycle tests (offline + live)."""

import gc
from unittest.mock import MagicMock

import pytest

import natlink_compat as natlink
from natlink_compat._state import _state
from natlink_compat._exceptions import WrongState, WrongType

from _helpers import compile_grammar


class TestGramObjOffline:

    def setup_method(self):
        _state.reset()

    METHODS_REQUIRING_LOAD = [
        ("activate",      lambda g: g.activate("rule", 0)),
        ("deactivate",    lambda g: g.deactivate("rule")),
        ("emptyList",     lambda g: g.emptyList("mylist")),
        ("appendList",    lambda g: g.appendList("mylist", "word")),
        ("removeList",    lambda g: g.removeList("mylist", ["word"])),
        ("linkQuery",     lambda g: g.linkQuery("mylink")),
        ("setContext",    lambda g: g.setContext("before", "after")),
        ("setExclusive",  lambda g: g.setExclusive(True)),
        ("setSelectText", lambda g: g.setSelectText("text")),
        ("getSelectText", lambda g: g.getSelectText()),
        ("getList",       lambda g: g.getList("mylist")),
        ("queryList",     lambda g: g.queryList("mylist")),
    ]

    def test_load_raises_without_connection(self):
        gram = natlink.GramObj()
        binary = compile_grammar("<rule> exported = hello;")
        with pytest.raises(WrongState):
            gram.load(binary)

    @pytest.mark.parametrize(
        "name,func", METHODS_REQUIRING_LOAD,
        ids=[x[0] for x in METHODS_REQUIRING_LOAD],
    )
    def test_raises_without_load(self, name, func):
        gram = natlink.GramObj()
        with pytest.raises(WrongState):
            func(gram)

    def test_unload_without_load_is_noop(self):
        gram = natlink.GramObj()
        gram.unload()  # should not raise

    def test_drop_last_ref_unloads_and_unregisters(self):
        _state.backend = type("_Backend", (), {"conn": None})()

        gram = natlink.GramObj()
        mock_com_gram = MagicMock()
        mock_com_gram.handle = 42
        gram._com_gram = mock_com_gram
        _state.grammar_registry[42] = gram

        del gram
        gc.collect()

        assert 42 not in _state.grammar_registry
        mock_com_gram.unload.assert_called_once_with(None)

    def test_callback_setters_work_without_load(self):
        gram = natlink.GramObj()
        gram.setBeginCallBack(lambda x: None)
        gram.setResultsCallBack(lambda x, y: None)
        gram.setHypothesisCallBack(lambda x: None)
        assert gram._begin_callback is not None
        assert gram._results_callback is not None
        assert gram._hypothesis_callback is not None
        gram.setBeginCallBack(None)
        gram.setResultsCallBack(None)
        gram.setHypothesisCallBack(None)
        assert gram._begin_callback is None

    def test_capital_B_aliases_exist(self):
        """GramObj class defines CallBack aliases (capital B) for Callback."""
        assert natlink.GramObj.setBeginCallBack is natlink.GramObj.setBeginCallback
        assert natlink.GramObj.setResultsCallBack is natlink.GramObj.setResultsCallback
        assert natlink.GramObj.setHypothesisCallBack is natlink.GramObj.setHypothesisCallback


@pytest.mark.online
class TestLiveGrammar:

    def test_full_lifecycle(self, live_connection):
        """Compile, load, activate, deactivate, unload — full grammar lifecycle."""
        binary = compile_grammar("<rule> exported = hello world;")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            assert gram._com_gram is not None
            gram.activate("rule", 0)  # global activation
            gram.deactivate("rule")
        finally:
            gram.unload()
        assert gram._com_gram is None

    def test_load_registers_in_grammar_registry(self, live_connection):
        binary = compile_grammar("<rule> exported = test;")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            handle = gram._com_gram.handle
            assert handle in _state.grammar_registry
            assert _state.grammar_registry[handle] is gram
        finally:
            gram.unload()
        assert gram._com_gram is None

    def test_unload_removes_from_registry(self, live_connection):
        binary = compile_grammar("<rule> exported = test;")
        gram = natlink.GramObj()
        gram.load(binary)
        handle = gram._com_gram.handle
        gram.unload()
        assert handle not in _state.grammar_registry

    def test_grammar_released_when_user_drops_refs(self, live_connection):
        """Dropping the last GramObj ref unregisters it from the registry.

        Matches the C++ contract: `gramobj_dealloc` → `destroy()` →
        `unload()` → `removeGramObj(this)`.  Registry membership is the
        observable cleanup signal.  We don't assert on Dragon-side
        recognition because Dragon's own grammars (e.g. dictation for a
        focused edit control) can recognize arbitrary English words
        after ours unloads, so mimic outcome is not a reliable probe.
        """
        binary = compile_grammar("<rule> exported = test drop refs;")

        gram = natlink.GramObj()
        gram.load(binary)
        gram.activate("rule", 0)
        handle = gram._com_gram.handle

        assert handle in _state.grammar_registry

        del gram
        gc.collect()

        assert handle not in _state.grammar_registry

    def test_load_with_allResults(self, live_connection):
        binary = compile_grammar("<rule> exported = test;")
        gram = natlink.GramObj()
        try:
            gram.load(binary, allResults=1)
            assert gram._all_results is True
        finally:
            gram.unload()

    def test_load_with_hypothesis(self, live_connection):
        binary = compile_grammar("<rule> exported = test;")
        gram = natlink.GramObj()
        try:
            gram.load(binary, hypothesis=1)
        finally:
            gram.unload()

    def test_reload_grammar(self, live_connection):
        """Loading a second grammar on the same GramObj should unload the first."""
        binary1 = compile_grammar("<rule> exported = hello;")
        binary2 = compile_grammar("<rule> exported = goodbye;")
        gram = natlink.GramObj()
        try:
            gram.load(binary1)
            first_com = gram._com_gram
            gram.load(binary2)
            second_com = gram._com_gram
            # A new ComGramObj is created for each load.  Handle values
            # (raw pointer addresses) may recycle, so compare wrappers.
            assert second_com is not first_com
            assert _state.grammar_registry[second_com.handle] is gram
        finally:
            gram.unload()

    def test_emptyList_and_appendList(self, live_connection):
        """List management: emptyList clears, appendList adds."""
        binary = compile_grammar("<rule> exported = open {filelist};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("filelist")
            assert gram.getList("filelist") == []

            gram.appendList("filelist", "report")
            gram.appendList("filelist", "spreadsheet")
            assert sorted(gram.getList("filelist")) == ["report", "spreadsheet"]

            gram.emptyList("filelist")
            assert gram.getList("filelist") == [], "emptyList did not clear"

            gram.appendList("filelist", "document")
            assert gram.getList("filelist") == ["document"]
        finally:
            gram.unload()

    def test_setContext_rejects_cfg_grammar(self, live_connection):
        """setContext requires a dictation grammar — CFG grammars correctly raise WrongType."""
        binary = compile_grammar("""
            <dgndictation> imported;
            <rule> exported = <dgndictation>;
        """)
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            with pytest.raises(WrongType):
                gram.setContext("the quick ", "")
        finally:
            gram.unload()

    def test_setExclusive(self, live_connection):
        binary = compile_grammar("<rule> exported = exclusive test;")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.setExclusive(True)
            gram.setExclusive(False)
        finally:
            gram.unload()

    def test_multiple_grammars(self, live_connection):
        """Multiple grammars can be loaded simultaneously."""
        binary1 = compile_grammar("<rule> exported = alpha;")
        binary2 = compile_grammar("<rule> exported = bravo;")
        gram1 = natlink.GramObj()
        gram2 = natlink.GramObj()
        try:
            gram1.load(binary1)
            gram2.load(binary2)
            gram1.activate("rule", 0)
            gram2.activate("rule", 0)
            assert len(_state.grammar_registry) >= 2
        finally:
            gram1.unload()
            gram2.unload()

    def test_callbacks_set_before_load(self, live_connection):
        """Callbacks set before load should persist through load."""
        binary = compile_grammar("<rule> exported = test;")
        gram = natlink.GramObj()
        begin_cb = lambda info: None
        results_cb = lambda words, res: None
        gram.setBeginCallBack(begin_cb)
        gram.setResultsCallBack(results_cb)
        try:
            gram.load(binary)
            # Callbacks should still be set
            assert gram._begin_callback is begin_cb
            assert gram._results_callback is results_cb
        finally:
            gram.unload()
        # Unload clears callbacks
        assert gram._begin_callback is None
        assert gram._results_callback is None

    def test_setSelectText_wrong_grammar_type(self, live_connection):
        """setSelectText on a CFG grammar raises WrongType."""
        binary = compile_grammar("<rule> exported = hello;")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            with pytest.raises(WrongType):
                gram.setSelectText("some text")
        finally:
            gram.unload()
