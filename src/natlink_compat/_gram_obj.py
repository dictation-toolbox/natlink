"""_gram_obj.py - GramObj: Dragon grammar loading and recognition.

Capital-B aliases (setBeginCallBack etc.) provided for ecosystem compatibility.
"""

import logging
from typing import Callable, List, Optional, Union

from natlink_com import ComGramObj as _ComGramObj

from ._state import _state
from ._exceptions import com_call as _com_call

log = logging.getLogger("natlink.compat")


class GramObj:
    """Grammar object — wraps Dragon's grammar loading and recognition COM interface."""

    def __init__(self):
        self._com_gram: Optional[_ComGramObj] = None
        self._begin_callback: Optional[Callable] = None
        self._results_callback: Optional[Callable] = None
        self._hypothesis_callback: Optional[Callable] = None
        self._all_results: bool = False

    def _require_loaded(self):
        """Raise WrongState if grammar is not loaded."""
        if self._com_gram is None:
            from ._exceptions import WrongState
            raise WrongState("Grammar not loaded")

    def load(self, binary: Union[str, bytes],
             allResults: int = 0, hypothesis: int = 0) -> None:
        """Load a binary grammar.

        The grammar binary is the SAPI 4 CFG format (SRHEADER + SRCHUNKs).
        """
        if self._com_gram is not None:
            self.unload()

        if isinstance(binary, str):
            binary = binary.encode("latin-1")

        backend = _state.backend
        if backend is None:
            from ._exceptions import WrongState
            raise WrongState("natlink is not connected")

        self._com_gram = _com_call(
            "GramObj.load",
            backend.grammar_load,
            binary,
            all_results=bool(allResults),
            hypothesis=bool(hypothesis),
        )
        self._all_results = bool(allResults)

        # Attribute to the loader whose start/reload/callback we are inside,
        # so a loader's objects can be enumerated (see loaders.get_grammars_for).
        # None when created outside any loader — e.g. a user script at the REPL.
        from ._callbacks import current_owner_package
        self._owner_pkg = current_owner_package()

        # Register in global grammar registry so callbacks can find us
        with _state.lock:
            _state.grammar_registry[self._com_gram.handle] = self

    def unload(self) -> None:
        """Unload/destroy the grammar.

        Order matches C++ ``CGrammarObject::unload``: Release the COM
        pointer first, null it out, then remove from the registry.
        Raises on COM failure so explicit callers (Dragonfly, user code)
        see real errors; ``__del__`` catches separately so finalization
        never propagates out.
        """
        if self._com_gram is not None:
            handle = self._com_gram.handle
            log.debug("Unloading grammar (handle=%d)", handle)
            conn = _state.backend.conn if _state.backend else None
            _com_call("GramObj.unload", self._com_gram.unload, conn)
            self._com_gram = None
            with _state.lock:
                _state.grammar_registry.pop(handle, None)
        self._begin_callback = None
        self._results_callback = None
        self._hypothesis_callback = None

    def activate(self, ruleName: Optional[str], window: int) -> None:
        """Activate a rule in this grammar for a specific window.

        Pass ruleName="" or None for the top-level rule.
        Pass window=0 for global activation.
        """
        self._require_loaded()
        rule = ruleName if ruleName else ""
        _com_call(
            "GramObj.activate",
            self._com_gram.activate,
            rule_name=rule,
            window_handle=window,
        )

    def deactivate(self, ruleName: str) -> None:
        """Deactivate a rule."""
        self._require_loaded()
        _com_call("GramObj.deactivate", self._com_gram.deactivate, ruleName)

    def setExclusive(self, state: bool) -> None:
        """Set grammar as exclusive or not."""
        self._require_loaded()
        _com_call("GramObj.setExclusive", self._com_gram.set_exclusive, state)

    def setBeginCallback(self, callback: Optional[Callable]) -> None:
        """Set the begin callback."""
        if callback is not None and not callable(callback):
            raise TypeError("parameter must be callable")
        self._begin_callback = callback

    # Alias for backward compat (some docs use capital B)
    setBeginCallBack = setBeginCallback

    def setResultsCallback(self, callback: Optional[Callable]) -> None:
        """Set the results callback."""
        if callback is not None and not callable(callback):
            raise TypeError("parameter must be callable")
        self._results_callback = callback

    setResultsCallBack = setResultsCallback

    def setHypothesisCallback(self, callback: Optional[Callable]) -> None:
        """Set the hypothesis callback."""
        if callback is not None and not callable(callback):
            raise TypeError("parameter must be callable")
        self._hypothesis_callback = callback

    setHypothesisCallBack = setHypothesisCallback

    def emptyList(self, listName: str) -> None:
        """Clear a grammar list."""
        self._require_loaded()
        _com_call("GramObj.emptyList", self._com_gram.list_set, listName, [])

    def appendList(self, listName: str, word: str) -> None:
        """Append a word to a grammar list."""
        self._require_loaded()
        _com_call("GramObj.appendList", self._com_gram.list_append, listName, word)

    def getList(self, listName: str) -> List[str]:
        """Get the words currently in a grammar list."""
        self._require_loaded()
        data = _com_call("GramObj.getList", self._com_gram.list_get, listName)
        if not data:
            return []
        from natlink_com._res_obj import _parse_srwordw_array
        return [text for text, _word_num in _parse_srwordw_array(data)]

    def queryList(self, listName: str) -> bool:
        """Check if a grammar list exists and is populated."""
        self._require_loaded()
        return _com_call("GramObj.queryList", self._com_gram.list_query, listName)

    def removeList(self, listName: str, words: List[str]) -> None:
        """Remove specific words from a grammar list."""
        self._require_loaded()
        _com_call("GramObj.removeList", self._com_gram.list_remove, listName, words)

    def linkQuery(self, linkName: str) -> bool:
        """Check if a grammar link name exists."""
        self._require_loaded()
        return _com_call("GramObj.linkQuery", self._com_gram.link_query, linkName)

    def setContext(self, beforeText: str = "", afterText: str = "") -> None:
        """Set dictation context (before/after text)."""
        self._require_loaded()
        _com_call(
            "GramObj.setContext",
            self._com_gram.set_context,
            beforeText,
            afterText,
        )

    def setSelectText(self, text: str) -> None:
        """Set select-and-say text buffer."""
        self._require_loaded()
        _com_call("GramObj.setSelectText", self._com_gram.set_select_text, text)

    def getSelectText(self) -> str:
        """Get select-and-say text buffer."""
        self._require_loaded()
        return _com_call("GramObj.getSelectText", self._com_gram.get_select_text) or ""

    def changeSelectText(self, start: int, end: int, text: str) -> None:
        """Replace a range in the select-and-say buffer."""
        self._require_loaded()
        _com_call("GramObj.changeSelectText",
                  self._com_gram.change_select_text, start, end, text)

    def deleteSelectText(self, start: int, end: int) -> None:
        """Delete a range from the select-and-say buffer."""
        self._require_loaded()
        _com_call("GramObj.deleteSelectText",
                  self._com_gram.delete_select_text, start, end)

    def insertSelectText(self, start: int, text: str) -> None:
        """Insert text into the select-and-say buffer."""
        self._require_loaded()
        _com_call("GramObj.insertSelectText",
                  self._com_gram.insert_select_text, start, text)

    def __del__(self):
        if self._com_gram is not None:
            try:
                self.unload()
            except Exception:
                log.debug("Grammar cleanup in __del__ failed", exc_info=True)
