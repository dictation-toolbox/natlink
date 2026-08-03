"""_res_obj.py - ResObj compatibility wrapper.

Wraps natlink_com.ResObj to provide the exact original natlink API:
  getResults(choice) -> List[Tuple[str, int]]  (word, ruleNumber)
  getWords(choice)   -> List[str]
  getWordInfo(choice) -> List[Tuple[str,int,int,int,int,int,str]]
  getWave()          -> str  (bytes as str for compat)
  correction(words)  -> None
  getSelectInfo(gramObj, choice) -> Tuple[int,int]
"""

import logging
from typing import List, Optional, Tuple

from natlink_com import ComResObj as _ProxyResObj
from natlink_com import NatlinkCOMError
from ._exceptions import com_call as _com_call

log = logging.getLogger("natlink.compat")


class ResObj:
    """Compatibility wrapper around natlink_com.ResObj."""

    def __init__(self, proxy_res: _ProxyResObj):
        self._proxy = proxy_res

    def getResults(self, choice: int = 0) -> Optional[List[Tuple[str, int]]]:
        """Get recognition results as (word, ruleNumber) tuples.

        Raises ``natlink.OutOfRange`` when *choice* is past the last
        available result, matching the C++ original (ResultObject.cpp:169).
        Callers enumerate alternatives with the idiom::

            i = 0
            while 1:
                try: words = res.getResults(i)
                except natlink.OutOfRange: break
                i += 1

        which unimacro's ``_oops`` and the natlinkcore samples rely on — so
        swallowing the error and returning None turns the loop terminator
        into a TypeError further downstream.
        """
        dicts = _com_call("ResObj.getResults", self._proxy.get_results, choice)
        if dicts is None:
            return None
        return [(d["word"], d["cfg_parse"]) for d in dicts]

    def getWords(self, choice: int = 0):
        """Get recognized words as a flat string list.

        Raises ``natlink.OutOfRange`` past the last result — see getResults.
        """
        result = _com_call("ResObj.getWords", self._proxy.get_results, choice)
        if result is None:
            return None
        return [d["word"] for d in result]

    def getWordInfo(self, choice: int = 0) -> Optional[
            List[Tuple[str, int, int, int, int, int, str]]]:
        """Get detailed word info as 7-tuples.

        Each tuple: (word, cfgParse, wordScore, startTime, endTime, engineFlags, pronunciation)
        Times are in 100ns units relative to utterance start.

        Raises ``natlink.OutOfRange`` past the last result — see getResults.
        """
        dicts = _com_call("ResObj.getWordInfo", self._proxy.get_word_info,
                          choice)
        if not dicts:
            return None
        result = []
        for d in dicts:
            result.append((
                d["word"],
                d["cfg_parse"],
                d["word_score"],
                d["start_time"],
                d["end_time"],
                d["engine_flags"],
                d["pronunciation"],
            ))
        return result

    def getWave(self) -> bytes:
        """Get the audio waveform data as raw bytes."""
        data = _com_call("ResObj.getWave", self._proxy.get_wave)
        # Original natlink returned raw bytes; in Python 3 this is bytes.
        # Some callers may expect str, but bytes is the practical type.
        return data

    def correction(self, *args) -> int:
        """Submit a correction for this recognition result.

        Accepts either a list: correction(["a", "b"])
        or varargs: correction("a", "b")

        Returns 1 if training succeeded, 0 otherwise.
        "returns S_OK if training succeeds and S_FALSE otherwise."
        — Joel Gould, ResultObject.cpp
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            words = list(args[0])
        else:
            words = list(args)
        return int(_com_call("ResObj.correction", self._proxy.correction, words))

    def getSelectInfo(self, gramObj, choice: int = 0) -> Tuple[int, int]:
        """Get selection info relative to a grammar.

        Returns (startWord, endWord).
        """
        # The COM layer needs the grammar's handle to look up select info.
        if gramObj.__class__.__name__ != "GramObj":
            raise TypeError("first parameter must be a GramObj instance")
        com_gram = getattr(gramObj, '_com_gram', None)
        if com_gram is None:
            from ._exceptions import WrongState
            raise WrongState("Grammar not loaded")
        gram_handle = com_gram.handle
        start, end = _com_call(
            "ResObj.getSelectInfo", self._proxy.get_select_info, gram_handle, choice)
        return (start, end)
