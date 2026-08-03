"""Recognition mimic tests."""

import pytest

import natlink_compat as natlink
from natlink_compat._exceptions import MimicFailed

from _helpers import compile_grammar, extract_words, do_mimic


@pytest.mark.online
class TestLiveRecognitionMimic:

    def test_mimic_recognized_words(self, live_connection):
        """Mimic words against a grammar and verify the exact words come back."""
        binary = compile_grammar("<rule> exported = hello world;")
        gram = natlink.GramObj()
        received = []

        try:
            gram.setResultsCallBack(
                lambda words, res: received.append((words, res)))
            gram.load(binary)
            gram.activate("rule", 0)
            try:
                gram.setExclusive(1)
            except Exception:
                pass

            do_mimic(["hello", "world"])

            assert len(received) >= 1, "Results callback was never called"
            words, res_obj = received[0]
            word_strs = extract_words(words)
            assert word_strs == ["hello", "world"]
            assert isinstance(res_obj, natlink.ResObj)
        finally:
            gram.unload()

    def test_mimic_no_matching_grammar_raises(self, live_connection):
        """Mimic words that no active grammar can match should raise MimicFailed."""
        binary = compile_grammar("<rule> exported = very specific command;")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.setExclusive(1)

            with pytest.raises(MimicFailed):
                natlink.recognitionMimic(["completely", "unrelated", "phrase"])
        finally:
            gram.setExclusive(0)
            gram.unload()
