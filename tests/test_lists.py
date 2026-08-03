"""GramObj list operations tests (appendList, emptyList, getList, removeList)."""

import time

import pytest

import natlink_compat as natlink
from natlink_compat._exceptions import MimicFailed, UnknownName

from _helpers import compile_grammar, extract_words, do_mimic


@pytest.mark.online
class TestLiveListOperations:

    def test_appendList_makes_word_recognizable(self, live_connection):
        """Appending a word to a grammar list makes it recognizable via mimic."""
        binary = compile_grammar("<rule> exported = open {files};")
        gram = natlink.GramObj()
        received = []

        try:
            gram.setResultsCallBack(
                lambda words, res: received.append(words))
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("files")
            gram.appendList("files", "document")
            try:
                gram.setExclusive(1)
            except Exception:
                pass
            time.sleep(0.3)

            do_mimic(["open", "document"])

            assert len(received) >= 1, "Results callback was never called"
            word_strs = extract_words(received[0])
            assert word_strs == ["open", "document"]
        finally:
            gram.unload()

    def test_emptyList_removes_words(self, live_connection):
        """After emptyList, previously appended words must not be recognizable."""
        binary = compile_grammar("<rule> exported = open {files};")
        gram = natlink.GramObj()

        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("files")
            gram.appendList("files", "document")
            gram.emptyList("files")
            time.sleep(0.3)

            gram.setExclusive(1)
            try:
                with pytest.raises(MimicFailed):
                    natlink.recognitionMimic(["open", "document"])
            finally:
                gram.setExclusive(0)
        finally:
            gram.unload()

    def test_getList_returns_appended_words(self, live_connection):
        """getList returns all words previously added via appendList."""
        binary = compile_grammar("<rule> exported = open {files};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("files")
            gram.appendList("files", "document")
            gram.appendList("files", "report")
            gram.appendList("files", "spreadsheet")
            words = gram.getList("files")
            assert sorted(words) == ["document", "report", "spreadsheet"]
        finally:
            gram.unload()

    def test_getList_after_empty_returns_nothing(self, live_connection):
        """After emptyList, getList should return an empty list."""
        binary = compile_grammar("<rule> exported = open {files};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("files")
            gram.appendList("files", "document")
            gram.emptyList("files")
            assert gram.getList("files") == []
        finally:
            gram.unload()

    def test_removeList_removes_specific_words(self, live_connection):
        """removeList removes specific words, leaving others intact."""
        binary = compile_grammar("<rule> exported = open {files};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            gram.emptyList("files")
            gram.appendList("files", "document")
            gram.appendList("files", "report")
            gram.appendList("files", "spreadsheet")
            gram.removeList("files", ["report"])
            assert sorted(gram.getList("files")) == ["document", "spreadsheet"]
        finally:
            gram.unload()


@pytest.mark.online
class TestLiveListErrors:

    def test_emptyList_unknown_name(self, live_connection):
        """emptyList with a list name not in the grammar raises UnknownName."""
        binary = compile_grammar("<rule> exported = open {mylist};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            with pytest.raises(UnknownName):
                gram.emptyList("nonexistent")
        finally:
            gram.unload()

    def test_appendList_unknown_name(self, live_connection):
        """appendList with a list name not in the grammar raises UnknownName."""
        binary = compile_grammar("<rule> exported = open {mylist};")
        gram = natlink.GramObj()
        try:
            gram.load(binary)
            gram.activate("rule", 0)
            with pytest.raises(UnknownName):
                gram.appendList("nonexistent", "word")
        finally:
            gram.unload()
