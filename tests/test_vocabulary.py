"""Vocabulary management and user management tests."""

import pytest

import natlink_compat as natlink


@pytest.mark.online
class TestLiveVocabulary:

    _TEST_WORD = "natlinktestxyzzy"

    @pytest.fixture(autouse=True, scope="class")
    def _ensure_test_word_clean(self, live_connection):
        """One-time cleanup of leftover test word from a previous interrupted run."""
        try:
            if natlink.getWordInfo(self._TEST_WORD) is not None:
                natlink.deleteWord(self._TEST_WORD)
        except Exception:
            pass
        yield
        try:
            if natlink.getWordInfo(self._TEST_WORD) is not None:
                natlink.deleteWord(self._TEST_WORD)
        except Exception:
            pass

    def test_getWordInfo_known_word(self, live_connection):
        """A common word like 'hello' should have word info."""
        info = natlink.getWordInfo("hello")
        assert isinstance(info, int)

    def test_getWordInfo_unknown_word_returns_none(self, live_connection):
        result = natlink.getWordInfo("xyzzynonexistentword12345")
        assert result is None

    def test_addWord_and_deleteWord(self, live_connection):
        try:
            result = natlink.addWord(self._TEST_WORD)
            assert result == 1
            # Word should now exist
            info = natlink.getWordInfo(self._TEST_WORD)
            assert isinstance(info, int)
        finally:
            natlink.deleteWord(self._TEST_WORD)

    @pytest.mark.xfail(reason="ILexPronounceW cross-bitness broken on DNS 13")
    def test_addWord_with_pronunciation(self, live_connection):
        try:
            result = natlink.addWord(self._TEST_WORD, 0, "T EH S T")
            assert result == 1
        finally:
            try:
                natlink.deleteWord(self._TEST_WORD)
            except Exception:
                pass

    @pytest.mark.xfail(reason="ILexPronounceW cross-bitness broken on DNS 13")
    def test_addWord_with_multiple_pronunciations(self, live_connection):
        try:
            result = natlink.addWord(
                self._TEST_WORD, 0, ["T EH S T", "T AH S T"])
            assert result == 1
        finally:
            try:
                natlink.deleteWord(self._TEST_WORD)
            except Exception:
                pass

    def test_deleteWord(self, live_connection):
        natlink.addWord(self._TEST_WORD)
        natlink.deleteWord(self._TEST_WORD)
        assert natlink.getWordInfo(self._TEST_WORD) is None

    def test_getWordProns_known_word(self, live_connection):
        prons = natlink.getWordProns("hello")
        assert prons is None or isinstance(prons, list)
        if prons is not None:
            assert all(isinstance(p, str) for p in prons)

    def test_setWordInfo(self, live_connection):
        try:
            natlink.addWord(self._TEST_WORD)
            # Round-trip: setWordInfo is only meaningful if getWordInfo
            # reflects it. "does not raise" would pass on a silent no-op.
            natlink.setWordInfo(self._TEST_WORD, 0)
            assert natlink.getWordInfo(self._TEST_WORD) == 0
            natlink.setWordInfo(self._TEST_WORD, 1)
            assert natlink.getWordInfo(self._TEST_WORD) == 1, (
                "setWordInfo did not change the stored flags")
        finally:
            natlink.deleteWord(self._TEST_WORD)


@pytest.mark.online
class TestLiveUserManagement:

    def test_getAllUsers(self, live_connection):
        users = natlink.getAllUsers()
        assert isinstance(users, list)
        assert len(users) >= 1
        assert all(isinstance(u, str) for u in users)

    def test_getCurrentUser_in_user_list(self, live_connection):
        """Current user should appear in getAllUsers."""
        name, _ = natlink.getCurrentUser()
        users = natlink.getAllUsers()
        assert name in users

    def test_saveUser_callable(self, live_connection):
        assert callable(natlink.saveUser)

    def test_getUserTraining(self, live_connection):
        result = natlink.getUserTraining()
        assert result in (None, "calibrate", "trained")


@pytest.mark.online
class TestLiveVocabularyEnumeration:
    """Live tests for vocabulary enumeration helpers."""

    def test_enumerateWords_returns_list(self, live_connection):
        """enumerateWords returns a list of strings (may be empty on DNS 13)."""
        words = natlink.enumerateWords()
        assert isinstance(words, list)
        assert all(isinstance(w, str) for w in words)

    def test_enumeratePrefixWords_filters(self, live_connection):
        """enumeratePrefixWords should return only words starting with prefix."""
        words = natlink.enumeratePrefixWords("hel")
        assert isinstance(words, list)
        for w in words:
            assert w.lower().startswith("hel"), f"{w!r} doesn't start with 'hel'"

    @pytest.mark.xfail(reason="DNS 13 dispatches W calls to A stubs cross-bitness — returns E_INVALIDARG")
    def test_getWordFromPrefix_returns_string(self, live_connection):
        """getWordFromPrefix returns a matching word.

        DNS 13 limitation: dd10midl dispatches IDgnSRLexiconW::WordFromPrefix
        to IDgnSRLexiconA on the 32-bit side.  Dragon logs:
        "Unimplemented function call: IDgnSRLexiconA::WordFromPron"
        for WordFromPron, and returns E_INVALIDARG for WordFromPrefix
        (A-side receives wide chars where it expects ANSI).
        """
        result = natlink.getWordFromPrefix("hel")
        assert isinstance(result, str)
        assert result.lower().startswith("hel")

    @pytest.mark.xfail(reason="DNS 13 dispatches W calls to A stubs cross-bitness — returns E_INVALIDARG")
    def test_getWordFromPron_returns_string(self, live_connection):
        """getWordFromPron returns a matching word.

        Same DNS 13 limitation as WordFromPrefix — dd10midl dispatches
        IDgnSRLexiconW::WordFromPron to IDgnSRLexiconA on the 32-bit side.
        """
        result = natlink.getWordFromPron("HH EH L OW")
        assert isinstance(result, str)
        assert len(result) > 0
