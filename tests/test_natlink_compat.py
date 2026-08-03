"""test_natlink_compat.py - Unit tests for the natlink compatibility adapter.

These tests do NOT require Dragon to be running.
They verify the adapter logic, exception hierarchy, data conversions,
and argument forwarding using mocks.
"""

import struct
import time
import unittest
from unittest.mock import MagicMock, patch


class TestResObjCompat(unittest.TestCase):
    """Test ResObj compatibility wrapper data conversions."""

    def _make_res_obj(self, word_dicts):
        """Create a ResObj wrapping a mock proxy ResObj."""
        from natlink_compat._res_obj import ResObj
        mock_proxy = MagicMock()
        mock_proxy.get_results.return_value = word_dicts
        return ResObj(mock_proxy)

    def test_get_results_tuple_format(self):
        res = self._make_res_obj([
            {"word": "hello", "cfg_parse": 1, "score": 100,
             "start": 0, "end": 100, "pronunciation": "HH EH L OW",
             "engine_flags": 0},
            {"word": "world", "cfg_parse": 2, "score": 95,
             "start": 100, "end": 200, "pronunciation": "W ER L D",
             "engine_flags": 0},
        ])
        result = res.getResults(0)
        self.assertEqual(result, [("hello", 1), ("world", 2)])

    def test_get_results_empty(self):
        res = self._make_res_obj([])
        result = res.getResults(0)
        self.assertEqual(result, [])

    def test_get_words_string_list(self):
        res = self._make_res_obj([
            {"word": "open", "cfg_parse": 1, "score": 0,
             "start": 0, "end": 0, "pronunciation": "", "engine_flags": 0},
            {"word": "file", "cfg_parse": 1, "score": 0,
             "start": 0, "end": 0, "pronunciation": "", "engine_flags": 0},
        ])
        result = res.getWords(0)
        self.assertEqual(result, ["open", "file"])

    def test_get_word_info_7_tuple(self):
        from natlink_compat._res_obj import ResObj
        mock_proxy = MagicMock()
        mock_proxy.get_word_info.return_value = [
            {"word": "test", "cfg_parse": 3, "word_score": 99,
             "start_time": 1000, "end_time": 2000,
             "engine_flags": 4, "pronunciation": "T EH S T"},
        ]
        res = ResObj(mock_proxy)
        result = res.getWordInfo(0)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(len(entry), 7)
        word, cfg, score, start, end, flags, pron = entry
        self.assertEqual(word, "test")
        self.assertEqual(cfg, 3)
        self.assertEqual(score, 99)
        self.assertEqual(start, 1000)
        self.assertEqual(end, 2000)
        self.assertEqual(flags, 4)
        self.assertEqual(pron, "T EH S T")

    def test_get_select_info_requires_gram_obj_instance(self):
        from natlink_compat._res_obj import ResObj

        res = ResObj(MagicMock())
        with self.assertRaises(TypeError):
            res.getSelectInfo(object())


class TestResObjPronunciationFallback(unittest.TestCase):
    """Test backend pronunciation fallback behavior for result metadata."""

    def test_engine_flags_fallback_when_pronunciation_lookup_fails(self):
        from natlink_com import _res_obj

        with patch("natlink_com._lexicon._lex_pron_get", return_value=(-1, None, 0, 0, b"", 0)):
            with patch("natlink_com._lexicon.get_word_info", return_value=7):
                pron, flags = _res_obj._get_pronunciation(object(), object(), "hello")

        self.assertEqual(pron, "")
        self.assertEqual(flags, 7)


class TestGramObjCompat(unittest.TestCase):
    """Test GramObj compatibility wrapper operations."""

    def test_empty_list_calls_list_set(self):
        from natlink_compat._gram_obj import GramObj

        gram = GramObj()
        mock_com_gram = MagicMock()
        gram._com_gram = mock_com_gram
        # _com_gram being set is sufficient — _loaded was removed

        gram.emptyList("myList")
        mock_com_gram.list_set.assert_called_once_with("myList", [])

    def test_append_list_delegates(self):
        from natlink_compat._gram_obj import GramObj

        gram = GramObj()
        mock_com_gram = MagicMock()
        gram._com_gram = mock_com_gram
        # _com_gram being set is sufficient — _loaded was removed

        gram.appendList("myList", "word1")
        mock_com_gram.list_append.assert_called_once_with("myList", "word1")

    def test_select_text_edit_helpers_delegate(self):
        from natlink_compat._gram_obj import GramObj

        gram = GramObj()
        mock_com_gram = MagicMock()
        gram._com_gram = mock_com_gram

        gram.changeSelectText(1, 4, "abc")
        gram.deleteSelectText(2, 5)
        gram.insertSelectText(3, "xyz")

        mock_com_gram.change_select_text.assert_called_once_with(1, 4, "abc")
        mock_com_gram.delete_select_text.assert_called_once_with(2, 5)
        mock_com_gram.insert_select_text.assert_called_once_with(3, "xyz")

    def test_callbacks_capital_b(self):
        """Verify the callback setter names use capital B."""
        from natlink_compat._gram_obj import GramObj
        gram = GramObj()
        self.assertTrue(hasattr(gram, "setBeginCallBack"))
        self.assertTrue(hasattr(gram, "setResultsCallBack"))
        self.assertTrue(hasattr(gram, "setHypothesisCallBack"))

    def test_set_callbacks(self):
        from natlink_compat._gram_obj import GramObj
        gram = GramObj()
        cb1 = lambda x: None
        cb2 = lambda x, y: None
        cb3 = lambda x: None

        gram.setBeginCallBack(cb1)
        gram.setResultsCallBack(cb2)
        gram.setHypothesisCallBack(cb3)

        self.assertIs(gram._begin_callback, cb1)
        self.assertIs(gram._results_callback, cb2)
        self.assertIs(gram._hypothesis_callback, cb3)

    def test_unloaded_raises(self):
        from natlink_compat._gram_obj import GramObj
        from natlink_compat._exceptions import WrongState

        gram = GramObj()
        with self.assertRaises(WrongState):
            gram.activate("rule", 0)
        with self.assertRaises(WrongState):
            gram.deactivate("rule")
        with self.assertRaises(WrongState):
            gram.emptyList("list")

    def test_non_callable_callbacks_raise_type_error(self):
        from natlink_compat._gram_obj import GramObj

        gram = GramObj()
        with self.assertRaises(TypeError):
            gram.setBeginCallback("bad")
        with self.assertRaises(TypeError):
            gram.setResultsCallback("bad")
        with self.assertRaises(TypeError):
            gram.setHypothesisCallback("bad")


class TestDictObjCompat(unittest.TestCase):
    """Test DictObj compatibility wrapper."""

    def test_callbacks_lowercase_b(self):
        """Verify DictObj uses lowercase b in Callback."""
        from natlink_compat._dict_obj import DictObj
        dobj = DictObj()
        self.assertTrue(hasattr(dobj, "setBeginCallback"))
        self.assertTrue(hasattr(dobj, "setChangeCallback"))

    def test_set_callbacks(self):
        from natlink_compat._dict_obj import DictObj
        dobj = DictObj()
        cb1 = lambda x: None
        cb2 = lambda *a: None
        dobj.setBeginCallback(cb1)
        dobj.setChangeCallback(cb2)
        self.assertIs(dobj._begin_callback, cb1)
        self.assertIs(dobj._change_callback, cb2)

    def test_non_callable_callbacks_raise_type_error(self):
        from natlink_compat._dict_obj import DictObj

        dobj = DictObj()
        with self.assertRaises(TypeError):
            dobj.setBeginCallback("bad")
        with self.assertRaises(TypeError):
            dobj.setChangeCallback("bad")

    def test_extra_dictation_helpers_delegate(self):
        from natlink_compat._dict_obj import DictObj

        dobj = DictObj()
        mock_com_dict = MagicMock()
        dobj._com_dict = mock_com_dict

        dobj.moveText(1, 3, 7, 9)
        dobj.removeText(2, 5, 4)
        dobj.hintText("hint")
        dobj.setWords("words")
        dobj.setAutoLock(1)
        dobj.getAutoLock()
        dobj.getThat()
        dobj.correctionDialog(1, 2)
        dobj.recentBufferCommit()

        mock_com_dict.move_text.assert_called_once_with(1, 3, 7, 9)
        mock_com_dict.remove_text.assert_called_once_with(2, 5, 4)
        mock_com_dict.hint_text.assert_called_once_with("hint")
        mock_com_dict.set_words.assert_called_once_with("words")
        mock_com_dict.set_auto_lock.assert_called_once_with(True)
        mock_com_dict.get_auto_lock.assert_called_once_with()
        mock_com_dict.get_that.assert_called_once_with()
        mock_com_dict.correction_dialog.assert_called_once_with(True, 2)
        mock_com_dict.recent_buffer_commit.assert_called_once_with()

    def test_bookmark_and_results_helpers_delegate(self):
        from natlink_compat._dict_obj import DictObj
        from natlink_compat._res_obj import ResObj

        dobj = DictObj()
        mock_com_dict = MagicMock()
        mock_proxy_res = MagicMock()
        mock_com_dict.get_results_object.return_value = (4, 2, mock_proxy_res)
        dobj._com_dict = mock_com_dict

        dobj.addBookmark(10, 22)
        dobj.removeBookmark(10)
        dobj.moveBookmark(10, 30)
        dobj.queryBookmark(10)
        dobj.enumBookmarks(3, 5)
        actual_start, actual_count, res_obj = dobj.getResultsObject(4, 2)

        mock_com_dict.add_bookmark.assert_called_once_with(10, 22)
        mock_com_dict.remove_bookmark.assert_called_once_with(10)
        mock_com_dict.move_bookmark.assert_called_once_with(10, 30)
        mock_com_dict.query_bookmark.assert_called_once_with(10)
        mock_com_dict.enum_bookmarks.assert_called_once_with(3, 5)
        mock_com_dict.get_results_object.assert_called_once_with(4, 2)
        self.assertEqual((actual_start, actual_count), (4, 2))
        self.assertIsInstance(res_obj, ResObj)
        self.assertIs(res_obj._proxy, mock_proxy_res)


class TestGetCallbackDepthBehavior(unittest.TestCase):
    """Test getCallbackDepth local/remote behavior."""

    def tearDown(self):
        from natlink_compat._state import _state
        _state.reset()

    def test_disconnected_uses_local_depth(self):
        from natlink_compat import getCallbackDepth
        from natlink_compat._state import _state

        _state.reset()
        _state.callback_depth = 2
        self.assertEqual(getCallbackDepth(), 2)

    def test_connected_reads_local_depth(self):
        from natlink_compat import getCallbackDepth
        from natlink_compat._state import _state

        _state.reset()
        _state.backend = MagicMock()
        _state.callback_depth = 3

        self.assertEqual(getCallbackDepth(), 3)


class TestExports(unittest.TestCase):
    """Verify the __init__.py exports all required names."""

    def test_all_functions_exported(self):
        import natlink_compat
        expected_funcs = [
            "natConnect", "natDisconnect", "isNatSpeakRunning",
            "waitForSpeech",
            "setBeginCallback", "setChangeCallback", "setTimerCallback",
            "setMessageWindow", "set_ui_provider", "clear_ui_provider", "get_ui_provider",
            "playString", "playEvents", "execScript",
            "recognitionMimic", "notify_text",
            "getClipboard", "getCursorPos", "getScreenSize",
            "getCurrentModule", "getCurrentUser",
            "getMicState", "setMicState",
            "inputFromFile", "getCallbackDepth",
            "getAllUsers", "createUser", "openUser", "saveUser",
            "getUserTraining", "getTrainingMode", "startTraining",
            "finishTraining",
            "getWordInfo", "addWord", "deleteWord", "setWordInfo",
            "getWordProns", "enumerateWords", "enumeratePrefixWords",
            "getWordFromPrefix", "getWordFromPron",
            "set_inactive",
        ]
        for name in expected_funcs:
            with self.subTest(name=name):
                self.assertTrue(hasattr(natlink_compat, name),
                                f"Missing function: {name}")
                self.assertTrue(callable(getattr(natlink_compat, name)),
                                f"Not callable: {name}")

    def test_all_classes_exported(self):
        import natlink_compat
        for name in ("GramObj", "ResObj", "DictObj"):
            with self.subTest(name=name):
                cls = getattr(natlink_compat, name)
                self.assertTrue(isinstance(cls, type),
                                f"Not a class: {name}")

    def test_all_exceptions_exported(self):
        import natlink_compat
        expected = [
            "NatError", "InvalidWord", "UnknownName", "OutOfRange",
            "MimicFailed", "BadGrammar", "WrongState", "BadWindow",
            "SyntaxError", "UserExists", "ValueError", "DataMissing",
            "WrongType",
        ]
        for name in expected:
            with self.subTest(name=name):
                cls = getattr(natlink_compat, name)
                self.assertTrue(issubclass(cls, Exception),
                                f"Not an exception: {name}")


class TestLauncherActiveGating(unittest.TestCase):
    """natConnect/natDisconnect re-entry guards when the launcher owns the
    connection (issue #228)."""

    def test_natDisconnect_noop_when_launcher_active(self):
        from natlink_compat import _lifecycle
        fake = MagicMock(launcher_active=True)
        with patch.object(_lifecycle, "_state", fake), \
             patch.object(_lifecycle, "_disconnect") as mock_disc:
            _lifecycle.natDisconnect()
        mock_disc.assert_not_called()

    def test_natDisconnect_tears_down_when_standalone(self):
        from natlink_compat import _lifecycle
        fake = MagicMock(launcher_active=False)
        with patch.object(_lifecycle, "_state", fake), \
             patch.object(_lifecycle, "_disconnect") as mock_disc:
            _lifecycle.natDisconnect()
        mock_disc.assert_called_once()

    def test_natConnect_returns_noop_handle_when_launcher_already_connected(self):
        from natlink_compat import _lifecycle
        fake = MagicMock(launcher_active=True, connected=True)
        with patch.object(_lifecycle, "_state", fake), \
             patch.object(_lifecycle, "_establish_com_connection") as mock_est, \
             patch.object(_lifecycle, "_disconnect") as mock_disc:
            cm = _lifecycle.natConnect(discovered_loaders=[])
            with cm:
                pass
        # Did not rebuild the shared connection, and exiting the handle did
        # not tear it down.
        mock_est.assert_not_called()
        mock_disc.assert_not_called()


class TestUIProviderContract(unittest.TestCase):
    """Unit tests for the third-party UI provider boundary."""

    def tearDown(self):
        from natlink_compat._state import _state
        _state.reset()

    def test_set_clear_ui_provider(self):
        import natlink_compat as natlink

        class Provider:
            def __init__(self):
                self.stopped = False

            def on_state_changed(self, state):
                pass

            def on_text(self, text, level=20):
                pass

            def stop(self):
                self.stopped = True

        first = Provider()
        natlink.set_ui_provider(first)
        self.assertIs(natlink.get_ui_provider(), first)

        natlink.clear_ui_provider()
        self.assertTrue(first.stopped)
        self.assertIsNone(natlink.get_ui_provider())

    def test_setting_new_provider_replaces_old_one(self):
        import natlink_compat as natlink

        class Provider:
            def __init__(self):
                self.stopped = False

            def on_state_changed(self, state):
                pass

            def on_text(self, text, level=20):
                pass

            def stop(self):
                self.stopped = True

        first = Provider()
        second = Provider()

        natlink.set_ui_provider(first)
        natlink.set_ui_provider(second)

        self.assertTrue(first.stopped)
        self.assertFalse(second.stopped)
        self.assertIs(natlink.get_ui_provider(), second)

    def test_text_and_state_dispatch_reach_active_provider(self):
        from natlink_compat._state import _state
        from natlink_compat._ui_protocol import notify_text, notify_ui

        class Provider:
            def __init__(self):
                self.states = []
                self.texts = []

            def on_state_changed(self, state):
                self.states.append(state)

            def on_text(self, text, level=20):
                self.texts.append((text, level))

        first = Provider()
        _state.ui_provider = first

        notify_ui()
        notify_text("hello", level=40)

        self.assertEqual(len(first.states), 1)
        self.assertEqual(first.texts, [("hello", 40)])

class _ConnectedTestBase(unittest.TestCase):
    """Base class that sets up a mocked connected state for testing
    functions that call _require_connected() and use the COM backend."""

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.backend = MagicMock()

    def tearDown(self):
        self._state.reset()



class TestGetUserTraining(_ConnectedTestBase):
    """Test getUserTraining delegates to proxy and maps results."""

    def test_not_calibrated_returns_none(self):
        from natlink_compat import getUserTraining
        self._state.backend.get_user_training.return_value = ""
        self.assertIsNone(getUserTraining())

    def test_calibrated_no_batch_returns_calibrate(self):
        from natlink_compat import getUserTraining
        self._state.backend.get_user_training.return_value = "calibrate"
        self.assertEqual(getUserTraining(), "calibrate")

    def test_calibrated_with_batch_returns_trained(self):
        from natlink_compat import getUserTraining
        self._state.backend.get_user_training.return_value = "trained"
        self.assertEqual(getUserTraining(), "trained")

    def test_failed_hresult_raises(self):
        from natlink_compat import getUserTraining
        from natlink_com._errors import NatlinkCOMError
        from natlink_compat._exceptions import NatError
        self._state.backend.get_user_training.side_effect = NatlinkCOMError(
            "GetUserTraining", hr=-1, error_message="failed")
        with self.assertRaises(NatError):
            getUserTraining()


class TestPlayEventsWireFormat(_ConnectedTestBase):
    """Test playEvents delegates to proxy with correct byte format."""

    def test_wire_format_bytes_blob(self):
        from natlink_compat import playEvents

        events = [(0x100, 0x41, 0), (0x101, 0x41, 0)]  # WM_KEYDOWN, WM_KEYUP
        playEvents(events)

        self._state.backend.play_events.assert_called_once()
        event_bytes = self._state.backend.play_events.call_args[0][0]
        self.assertEqual(len(event_bytes), 24)  # 2 events * 12 bytes each

        # Verify each event struct
        msg1, wp1, lp1 = struct.unpack_from("<III", event_bytes, 0)
        msg2, wp2, lp2 = struct.unpack_from("<III", event_bytes, 12)
        self.assertEqual((msg1, wp1, lp1), (0x100, 0x41, 0))
        self.assertEqual((msg2, wp2, lp2), (0x101, 0x41, 0))

    def test_events_size_multiple_of_12(self):
        from natlink_compat import playEvents

        playEvents([(1, 2, 3)])

        event_bytes = self._state.backend.play_events.call_args[0][0]
        self.assertEqual(len(event_bytes) % 12, 0)

    def test_non_list_raises_type_error(self):
        from natlink_compat import playEvents

        with self.assertRaises(TypeError):
            playEvents((1, 2, 3))

    def test_non_tuple_member_raises_type_error(self):
        from natlink_compat import playEvents

        with self.assertRaises(TypeError):
            playEvents([[1, 2, 3]])

    def test_non_int_tuple_member_raises_type_error(self):
        from natlink_compat import playEvents

        with self.assertRaises(TypeError):
            playEvents([("msg", object(), 0)])


class TestGetWordPronsResponseParsing(_ConnectedTestBase):
    """Test getWordProns delegates to proxy and maps results."""

    def test_parses_prons(self):
        from natlink_compat import getWordProns
        self._state.backend.get_word_prons.return_value = ["HH EH L OW", "HH AH L OW"]
        result = getWordProns("hello")
        self.assertIsNotNone(result)
        self.assertEqual(result, ["HH EH L OW", "HH AH L OW"])

    def test_single_pron(self):
        from natlink_compat import getWordProns
        self._state.backend.get_word_prons.return_value = ["T EH S T"]
        result = getWordProns("test")
        self.assertEqual(result, ["T EH S T"])

    def test_failed_raises(self):
        from natlink_compat import getWordProns
        from natlink_com._errors import NatlinkCOMError
        from natlink_compat._exceptions import NatError
        self._state.backend.get_word_prons.side_effect = NatlinkCOMError(
            "GetWordProns", hr=-1, error_message="failed")
        with self.assertRaises(NatError):
            getWordProns("bogus")

    def test_empty_returns_empty_list(self):
        from natlink_compat import getWordProns
        self._state.backend.get_word_prons.return_value = []
        self.assertEqual(getWordProns("empty"), [])


class TestExtendedVocabularyHelpers(_ConnectedTestBase):
    """Test extended lexicon helper delegation."""

    def test_enumerate_words(self):
        from natlink_compat import enumerateWords
        self._state.backend.enumerate_words.return_value = ["alpha", "beta"]
        self.assertEqual(enumerateWords(), ["alpha", "beta"])
        self._state.backend.enumerate_words.assert_called_once_with()

    def test_enumerate_prefix_words(self):
        from natlink_compat import enumeratePrefixWords
        self._state.backend.enumerate_prefix_words.return_value = ["alpha"]
        self.assertEqual(enumeratePrefixWords("al"), ["alpha"])
        self._state.backend.enumerate_prefix_words.assert_called_once_with("al")

    def test_get_word_from_prefix(self):
        from natlink_compat import getWordFromPrefix
        self._state.backend.get_word_from_prefix.return_value = "alpha"
        self.assertEqual(getWordFromPrefix("al", 7, 2), "alpha")
        self._state.backend.get_word_from_prefix.assert_called_once_with("al", 7, 2)

    def test_get_word_from_pron(self):
        from natlink_compat import getWordFromPron
        self._state.backend.get_word_from_pron.return_value = "alpha"
        self.assertEqual(getWordFromPron("AE L F AH", 3, 1), "alpha")
        self._state.backend.get_word_from_pron.assert_called_once_with(
            "AE L F AH", 3, 1)


class TestAddWordMultipleProns(_ConnectedTestBase):
    """Test addWord loops for multiple pronunciations."""

    def test_no_prons(self):
        from natlink_compat import addWord
        result = addWord("hello")
        self.assertEqual(result, 1)
        self._state.backend.add_word.assert_called_once_with("hello", "", 1)

    def test_single_string_pron(self):
        from natlink_compat import addWord
        result = addWord("hello", 0, "HH EH L OW")
        self.assertEqual(result, 1)
        self._state.backend.add_word.assert_called_once_with(
            "hello", "HH EH L OW", 0)

    def test_multiple_prons_sends_separate_requests(self):
        from natlink_compat import addWord
        prons = ["HH EH L OW", "HH AH L OW"]
        result = addWord("hello", 3, prons)
        self.assertEqual(result, 1)
        # Should be called twice, once per pronunciation
        self.assertEqual(self._state.backend.add_word.call_count, 2)
        calls = self._state.backend.add_word.call_args_list
        self.assertEqual(calls[0].args, ("hello", "HH EH L OW", 3))
        self.assertEqual(calls[1].args, ("hello", "HH AH L OW", 3))

    def test_empty_list_no_prons(self):
        from natlink_compat import addWord
        # pronList=None means no pronunciation
        result = addWord("hello", 0, None)
        self.assertEqual(result, 1)
        self._state.backend.add_word.assert_called_once_with("hello", "", 0)

    def test_default_word_info_is_one(self):
        from natlink_compat import addWord
        addWord("testword")
        self._state.backend.add_word.assert_called_once_with("testword", "", 1)


class TestLexiconBackendFallbacks(_ConnectedTestBase):
    """Test backend fallback behavior around pronunciation-sensitive paths."""

    def test_add_word_rejects_pronunciation_when_only_fallback_is_available(self):
        from natlink_com._errors import NatlinkCOMError
        from natlink_com._lexicon import add_word

        conn = MagicMock()
        conn.central = None
        conn.tlb = None
        conn.lex_word = MagicMock()

        with self.assertRaises(NatlinkCOMError) as ctx:
            add_word(conn, "hello", "HH EH L OW", 1)

        self.assertIn("explicit pronunciation", str(ctx.exception))
        conn.lex_word.assert_not_called()

    def test_word_info_forwarded(self):
        from natlink_compat import addWord
        addWord("test", 7, "T EH S T")
        self._state.backend.add_word.assert_called_once_with("test", "T EH S T", 7)


class TestRecognitionMimicForms(_ConnectedTestBase):
    """Test recognitionMimic accepts both list and varargs forms."""

    def test_varargs_form(self):
        from natlink_compat import recognitionMimic
        recognitionMimic("hello", "world")
        self._state.backend.recognition_mimic.assert_called_once_with(
            ["hello", "world"])

    def test_list_form(self):
        from natlink_compat import recognitionMimic
        recognitionMimic(["hello", "world"])
        self._state.backend.recognition_mimic.assert_called_once_with(
            ["hello", "world"])

    def test_tuple_form(self):
        from natlink_compat import recognitionMimic
        recognitionMimic(("hello", "world"))
        self._state.backend.recognition_mimic.assert_called_once_with(
            ["hello", "world"])

    def test_single_word_vararg(self):
        from natlink_compat import recognitionMimic
        recognitionMimic("hello")
        self._state.backend.recognition_mimic.assert_called_once_with(["hello"])

    def test_requires_at_least_one_argument(self):
        from natlink_compat import recognitionMimic

        with self.assertRaises(TypeError):
            recognitionMimic()

    def test_rejects_non_string_arguments(self):
        from natlink_compat import recognitionMimic

        with self.assertRaises(TypeError):
            recognitionMimic("hello", 1)

    def test_rejects_empty_list_form(self):
        from natlink_compat import recognitionMimic

        with self.assertRaises(TypeError):
            recognitionMimic([])


class TestExecScriptValidation(_ConnectedTestBase):
    """Test execScript input validation."""

    def test_args_must_be_list(self):
        from natlink_compat import execScript

        with self.assertRaises(TypeError):
            execScript("Cmd", ("a", "b"))

    def test_args_must_be_list_of_words(self):
        from natlink_compat import execScript

        with self.assertRaises(TypeError):
            execScript("Cmd", ["a", 1])


class TestGetWordInfoReturnsNone(_ConnectedTestBase):
    """Test getWordInfo returns None for unknown words (not InvalidWord)."""

    def test_returns_none_for_unknown(self):
        from natlink_compat import getWordInfo
        self._state.backend.get_word_info.return_value = None
        result = getWordInfo("nonexistentword")
        self.assertIsNone(result)

    def test_returns_flags_for_known(self):
        from natlink_compat import getWordInfo
        self._state.backend.get_word_info.return_value = 3
        result = getWordInfo("hello")
        self.assertEqual(result, 3)


class TestWaitForSpeech(_ConnectedTestBase):
    """waitForSpeech blocks until disconnect event or timeout."""

    def test_blocks_until_disconnect_event(self):
        import threading
        from natlink_compat import waitForSpeech

        from natlink_com._win32 import kernel32 as _k32

        # Signal disconnect after 200ms
        def signal():
            time.sleep(0.2)
            _k32.SetEvent(self._state._disconnect_event_handle)

        t = threading.Thread(target=signal)
        t.start()
        start = time.monotonic()
        waitForSpeech(timeout_ms=5000)
        elapsed = time.monotonic() - start
        t.join()
        self.assertLess(elapsed, 2.0)
        self.assertGreater(elapsed, 0.1)

    def test_returns_immediately_when_not_connected(self):
        from natlink_compat import waitForSpeech

        self._state.backend = None  # disconnected
        start = time.monotonic()
        waitForSpeech(timeout_ms=5000)
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 1.0)

    def test_respects_timeout(self):
        from natlink_compat import waitForSpeech

        start = time.monotonic()
        waitForSpeech(timeout_ms=200)
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, 0.15)
        self.assertLess(elapsed, 2.0)


class TestInputFromFile(_ConnectedTestBase):
    """Test inputFromFile flag computation and playlist."""

    def setUp(self):
        super().setUp()
        import tempfile, os
        # Create temp files with valid extensions for _testFileName validation
        self._tmpdir = tempfile.mkdtemp()
        self._wav = os.path.join(self._tmpdir, "test.wav")
        self._utt = os.path.join(self._tmpdir, "test.utt")
        for f in (self._wav, self._utt):
            open(f, 'w').close()

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        super().tearDown()

    def test_wav_auto_detect_utt(self):
        """WAV files with uttDetect=-1 get DGNUTTFLG_DETECTUTT."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._wav)

        call_args = _state.backend.input_from_file.call_args
        self.assertEqual(call_args[0][0], self._wav)
        flags = call_args[1]["flags"]
        self.assertTrue(flags & 0x0002)  # DGNUTTFLG_DETECTUTT
        self.assertFalse(flags & 0x0004)  # not DGNUTTFLG_REALTIME

    def test_non_wav_no_detect(self):
        """Non-WAV with uttDetect=-1 does NOT get DGNUTTFLG_DETECTUTT."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._utt)

        flags = _state.backend.input_from_file.call_args[1]["flags"]
        self.assertFalse(flags & 0x0002)

    def test_realtime_flag(self):
        """realtime=1 adds DGNUTTFLG_REALTIME."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._wav, realtime=1)

        flags = _state.backend.input_from_file.call_args[1]["flags"]
        self.assertTrue(flags & 0x0004)

    def test_utt_detect_explicit_off(self):
        """uttDetect=0 disables utterance detection even for WAV."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._wav, uttDetect=0)

        flags = _state.backend.input_from_file.call_args[1]["flags"]
        self.assertFalse(flags & 0x0002)

    def test_utt_detect_explicit_on_non_wav(self):
        """uttDetect=1 enables detection even for non-WAV."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._utt, uttDetect=1)

        flags = _state.backend.input_from_file.call_args[1]["flags"]
        self.assertTrue(flags & 0x0002)

    def test_playlist_bytes(self):
        """Playlist is converted to DWORD-pair bytes."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._wav, playlist=[(100, 200), (300, 400)])

        playlist_bytes = _state.backend.input_from_file.call_args[1]["playlist"]
        self.assertEqual(len(playlist_bytes), 16)  # 2 pairs * 8 bytes each
        val = struct.unpack("<IIII", playlist_bytes)
        self.assertEqual(val, (100, 200, 300, 400))

    def test_no_playlist(self):
        """No playlist sends empty bytes."""
        from natlink_compat import inputFromFile
        from natlink_compat._state import _state

        _state.backend.input_from_file = MagicMock()
        inputFromFile(self._wav)

        playlist_bytes = _state.backend.input_from_file.call_args[1]["playlist"]
        self.assertEqual(playlist_bytes, b"")

    def test_disconnected_raises(self):
        from natlink_compat import inputFromFile
        from natlink_compat._exceptions import WrongState
        self._state.reset()
        with self.assertRaises(WrongState):
            inputFromFile("test.wav")

    def test_playlist_must_be_list_or_tuple(self):
        from natlink_compat import inputFromFile

        with self.assertRaises(TypeError):
            inputFromFile(self._wav, playlist="bad")

    def test_playlist_ranges_must_contain_ints(self):
        from natlink_compat import inputFromFile

        with self.assertRaises(TypeError):
            inputFromFile(self._wav, playlist=[("a", "b")])

    def test_playlist_range_must_be_ascending(self):
        from natlink_compat import inputFromFile

        with self.assertRaises(TypeError):
            inputFromFile(self._wav, playlist=[(20, 10)])

    def test_playlist_scalars_must_be_ints(self):
        from natlink_compat import inputFromFile

        with self.assertRaises(TypeError):
            inputFromFile(self._wav, playlist=[object()])


class TestBuildPlaylist(unittest.TestCase):
    """Test the _build_playlist helper."""

    def test_tuple_pairs(self):
        from natlink_compat._system import _build_playlist
        result = _build_playlist([(10, 20), (30, 40)])
        self.assertEqual(len(result), 16)
        vals = struct.unpack("<IIII", result)
        self.assertEqual(vals, (10, 20, 30, 40))

    def test_single_values(self):
        from natlink_compat._system import _build_playlist
        result = _build_playlist([100, 200])
        vals = struct.unpack("<IIII", result)
        self.assertEqual(vals, (100, 100, 200, 200))

    def test_empty(self):
        from natlink_compat._system import _build_playlist
        result = _build_playlist([])
        self.assertEqual(result, b"")

    def test_mixed(self):
        from natlink_compat._system import _build_playlist
        result = _build_playlist([(10, 20), 50])
        vals = struct.unpack("<IIII", result)
        self.assertEqual(vals, (10, 20, 50, 50))

    def test_non_sequence_raises_type_error(self):
        from natlink_compat._system import _build_playlist

        with self.assertRaises(TypeError):
            _build_playlist("bad")

    def test_range_members_must_be_ints(self):
        from natlink_compat._system import _build_playlist

        with self.assertRaises(TypeError):
            _build_playlist([("a", "b")])

    def test_range_must_be_ascending(self):
        from natlink_compat._system import _build_playlist

        with self.assertRaises(TypeError):
            _build_playlist([(20, 10)])


class TestPendingChangeBothStoredIndependently(unittest.TestCase):
    """Verify that both speaker and mic changes can be pending simultaneously.

    C++ uses bitwise PENDING_SPEAKER | PENDING_MICSTATE — both can be stored
    independently.  Previously Python used a single _pending_change slot that
    dropped one when both arrived during the same callback.
    """

    def tearDown(self):
        from natlink_compat._state import _state
        _state.change_callbacks.clear()
        _state.callback_depth = 0
        _state._pending_speaker = None
        _state._pending_micstate = None

    def test_both_speaker_and_mic_replayed(self):
        """Both pending changes replay exactly once when outermost callback exits.

        Enters through _on_attrib_changed (the real COM callback handler),
        which calls backend.get_current_user() / get_mic_state() — the same
        path Dragon's AttribChanged2 notification takes.  Verifies the full
        chain: COM handler → backend call → dispatch → pending store → replay.
        """
        from natlink_compat._state import _state
        from natlink_compat._callbacks import (
            _on_attrib_changed, _callback_trace,
            ISRNSAC_SPEAKER, DGNSRAC_MICSTATE,
        )

        # Mock backend so _on_attrib_changed can call get_current_user / get_mic_state
        _state.backend = MagicMock()
        _state.backend.get_current_user.return_value = ("Alice", r"C:\Users\Alice")
        _state.backend.get_mic_state.return_value = "on"

        received = []
        _state.change_callbacks[:] = [lambda t, info: received.append((t, info))]

        # Enter a callback (depth 0 → 1)
        _state.callback_depth = 0
        with _callback_trace("outer"):
            # Inside the callback (depth=1): simulate Dragon firing both
            # AttribChanged2(SPEAKER) and AttribChanged2(MICSTATE)
            _on_attrib_changed(ISRNSAC_SPEAKER)
            _on_attrib_changed(DGNSRAC_MICSTATE)

            # Nothing fired yet — both are pending
            self.assertEqual(received, [])
            # Backend was called to fetch real values
            _state.backend.get_current_user.assert_called_once()
            _state.backend.get_mic_state.assert_called_once()
            self.assertIsNotNone(_state._pending_speaker)
            self.assertIsNotNone(_state._pending_micstate)
        # _callback_trace exit: depth 1→0, replays both pending

        # Both should have been replayed exactly once
        self.assertEqual(len(received), 2,
                         f"Expected exactly 2 callbacks, got: {received}")
        types = [r[0] for r in received]
        self.assertEqual(types.count("user"), 1, "user must fire exactly once")
        self.assertEqual(types.count("mic"), 1, "mic must fire exactly once")

        # Verify values came from the backend calls
        for change_type, info in received:
            if change_type == "user":
                self.assertEqual(info, ("Alice", r"C:\Users\Alice"))
            elif change_type == "mic":
                self.assertEqual(info, "on")

        # Pending slots must be cleared
        self.assertIsNone(_state._pending_speaker)
        self.assertIsNone(_state._pending_micstate)

    def test_only_last_of_same_type_kept(self):
        """If two mic changes arrive, only the last is replayed (same as C++)."""
        from natlink_compat._state import _state
        from natlink_compat._callbacks import dispatch_change_callback, _callback_trace

        received = []
        _state.change_callbacks[:] = [lambda t, info: received.append((t, info))]

        _state.callback_depth = 0
        with _callback_trace("outer"):
            dispatch_change_callback("mic", "off")
            dispatch_change_callback("mic", "on")  # overwrites

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], ("mic", "on"))


class TestDictTextChangedDeferred(unittest.TestCase):
    """Verify dictation TextChanged/TextSelChanged are deferred + pause_recog.

    C++ routes these through makeResultsCallback (deferred + pause_recog).
    The Python implementation must match: extract data on the RPC thread,
    defer dispatch to the main thread, and manage pause_recog.
    """

    def _make_mock_sink(self):
        """Build a minimal DictSink-like object for testing dispatch logic."""
        import threading

        # Mock connection with pause_recog tracking
        conn = MagicMock()
        conn._pause_recog = 0
        conn.on_dict_text_changed = MagicMock()
        conn._deferred_cookie = None
        conn._engine_sink = None

        def real_increment():
            
                conn._pause_recog += 1
        conn.increment_pause_recog = real_increment

        def real_reset():
            
                if conn._pause_recog > 0:
                    conn._pause_recog -= 1
        conn.reset_pause_recog = real_reset

        # Mock text interface — GetChanges returns (new_start=0, new_end=0,
        # old_start=0, old_end=2) so new_end <= new_start and TextGet is NOT called
        # (avoids sdata_to_bytes on a MagicMock).
        text_iface = MagicMock()
        text_iface.TextSelGet.return_value = (5, 3)
        text_iface.GetChanges.return_value = (0, 0, 0, 2)  # new_end == new_start → skip TextGet

        return conn, text_iface

    def test_text_changed_increments_pause_recog(self):
        """TextChanged must increment pause_recog before deferring."""
        from natlink_com._dict_sink import _build_sink_class

        conn, text_iface = self._make_mock_sink()

        SinkClass = _build_sink_class()
        sink = SinkClass.__new__(SinkClass)
        sink._dict_handle = 42
        sink._text_iface = text_iface
        sink._connection = conn

        sink._handle_text_changed()

        # pause_recog should have been incremented
        self.assertEqual(conn._pause_recog, 1,
                         "TextChanged must increment pause_recog")
        # Sink should route through conn.defer_dict_text_changed
        conn.defer_dict_text_changed.assert_called_once()
        args = conn.defer_dict_text_changed.call_args.args
        self.assertEqual(args[0], 42, "dict_handle passed first")

        # Simulate drain: conn router calls sink._do_dict_text_changed
        sink._do_dict_text_changed(*args)

        # After handler runs, pause_recog should be back to 0
        self.assertEqual(conn._pause_recog, 0,
                         "Handler must call reset_pause_recog")
        conn.on_dict_text_changed.assert_called_once()

    def test_text_sel_changed_increments_pause_recog(self):
        """TextSelChanged must also increment pause_recog before deferring."""
        from natlink_com._dict_sink import _build_sink_class

        conn, text_iface = self._make_mock_sink()

        SinkClass = _build_sink_class()
        sink = SinkClass.__new__(SinkClass)
        sink._dict_handle = 42
        sink._text_iface = text_iface
        sink._connection = conn

        sink._handle_text_sel_changed()

        self.assertEqual(conn._pause_recog, 1,
                         "TextSelChanged must increment pause_recog")
        conn.defer_dict_text_changed.assert_called_once()
        args = conn.defer_dict_text_changed.call_args.args
        self.assertEqual(args[0], 42)

        sink._do_dict_text_changed(*args)

        self.assertEqual(conn._pause_recog, 0)
        conn.on_dict_text_changed.assert_called_once()


class TestCallbackIntegration(unittest.TestCase):
    """Integration tests for callback dispatch paths.

    Tests 1-3 enter through the real COM event handlers (_on_paused,
    _on_attrib_changed) which call the backend and feed results into
    the dispatch chain.  Tests 4-7 enter at the compat dispatch layer
    (dispatch_phrase_finish, etc.) — one level above the sink — to verify
    flag interpretation, result classification, and registry lookup.
    The sink→deferred→dispatch boundary is tested separately in
    TestDictTextChangedDeferred and TestPhraseFinishPauseRecog.
    """

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.backend = MagicMock()
        self._state.backend.get_current_module.return_value = ("notepad.exe", "Untitled", 12345)
        self._state.backend.get_current_user.return_value = ("TestUser", r"C:\Users\Test")
        self._state.backend.get_mic_state.return_value = "on"

    def tearDown(self):
        self._state.reset()

    # --- 1. Begin callback (Paused → _on_paused → dispatch) ---
    # Happy-path begin callback tested live in test_05::test_begin_callback_fires_on_mimic

    def test_begin_callback_sets_during_paused(self):
        """_on_paused sets during_paused=True during execution, False after."""
        from natlink_compat._callbacks import _on_paused

        seen_during = []
        self._state.begin_callbacks[:] = [lambda info: seen_during.append(
            self._state.during_paused)]

        _on_paused()

        self.assertEqual(seen_during, [True])
        self.assertFalse(self._state.during_paused)

    def test_begin_callback_skipped_during_init(self):
        """_on_paused does nothing when during_init is True."""
        from natlink_compat._callbacks import _on_paused

        received = []
        self._state.begin_callbacks[:] = [lambda info: received.append(info)]
        self._state.during_init = True

        _on_paused()

        self.assertEqual(received, [])

    # --- 2. Per-grammar begin callback ---

    def test_grammar_begin_callback(self):
        """_on_paused fires per-grammar begin callbacks for registered grammars."""
        from natlink_compat._callbacks import _on_paused

        gram = MagicMock()
        gram_received = []
        gram._begin_callback = lambda info: gram_received.append(info)
        self._state.grammar_registry[42] = gram

        _on_paused()

        self.assertEqual(len(gram_received), 1)
        self.assertEqual(gram_received[0], ("notepad.exe", "Untitled", 12345))

    def test_grammar_begin_no_callback_no_error(self):
        """Grammars without begin callback don't crash _on_paused."""
        from natlink_compat._callbacks import _on_paused

        gram = MagicMock(spec=[])  # no _begin_callback attr
        self._state.grammar_registry[42] = gram

        _on_paused()  # should not raise

    # --- 3. Change callback (AttribChanged2 → _on_attrib_changed) ---
    # Mic change happy path tested live in test_05::test_change_callback_fires_on_mic_toggle

    def test_change_callback_user(self):
        """AttribChanged2(SPEAKER) fires change callback with user info.

        Can't be live — requires Dragon to switch users during test.
        """
        from natlink_compat._callbacks import _on_attrib_changed, ISRNSAC_SPEAKER

        received = []
        self._state.change_callbacks[:] = [lambda t, info: received.append((t, info))]

        _on_attrib_changed(ISRNSAC_SPEAKER)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], ("user", ("TestUser", r"C:\Users\Test")))

    def test_change_callback_skipped_during_init(self):
        """AttribChanged2 does nothing when during_init is True."""
        from natlink_compat._callbacks import _on_attrib_changed, ISRNSAC_SPEAKER

        received = []
        self._state.change_callbacks[:] = [lambda t, info: received.append((t, info))]
        self._state.during_init = True

        _on_attrib_changed(ISRNSAC_SPEAKER)

        self.assertEqual(received, [])

    # --- 4. Results callback (PhraseFinish → dispatch_phrase_finish) ---
    # Happy-path results tested live in test_05::test_results_callback_word_tuples_and_resobj
    # Reject/other tested live in test_05::test_allResults_reject_string, test_allResults_other_string

    def test_results_callback_skipped_without_all_results(self):
        """PhraseFinish for other grammar skipped when allResults=False."""
        from natlink_compat._callbacks import dispatch_phrase_finish

        gram = MagicMock()
        results = []
        gram._results_callback = lambda d, r: results.append(d)
        gram._all_results = False
        self._state.grammar_registry[99] = gram

        dispatch_phrase_finish(99, 0x01, MagicMock())  # RECOGNIZED, not THISGRAMMAR

        self.assertEqual(results, [])  # skipped

    # --- 5. Hypothesis callback ---
    # Happy-path hypothesis tested live in test_05::test_hypothesis_callback_fires

    def test_hypothesis_no_callback_no_error(self):
        """Grammars without hypothesis callback don't crash."""
        from natlink_compat._callbacks import dispatch_phrase_hypothesis

        gram = MagicMock()
        gram._hypothesis_callback = None
        self._state.grammar_registry[99] = gram

        dispatch_phrase_hypothesis(99, ["test"])  # should not raise

    # --- 6. Dictation text changed ---

    def test_dict_text_changed_callback(self):
        """dispatch_dict_text_changed fires with correct parameters."""
        from natlink_compat._callbacks import dispatch_dict_text_changed

        dobj = MagicMock()
        received = []
        dobj._change_callback = lambda *a: received.append(a)
        self._state.dict_registry[55] = dobj

        dispatch_dict_text_changed(55, 0, 5, "hello", 5, 5)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], (0, 5, "hello", 5, 5))

    def test_dict_text_changed_unregistered_handle(self):
        """Unregistered dict handle does nothing (no crash)."""
        from natlink_compat._callbacks import dispatch_dict_text_changed
        dispatch_dict_text_changed(999, 0, 0, "", 0, 0)  # should not raise

    # --- 7. Dictation begin callback ---

    def test_dict_begin_callback(self):
        """dispatch_dict_begin_callback fires with module info."""
        from natlink_compat._callbacks import dispatch_dict_begin_callback

        dobj = MagicMock()
        received = []
        dobj._begin_callback = lambda info: received.append(info)
        self._state.dict_registry[55] = dobj

        dispatch_dict_begin_callback(55, ("notepad.exe", "Untitled", 12345))

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], ("notepad.exe", "Untitled", 12345))

    # --- Cross-cutting: callback depth tracking ---

    def test_all_callbacks_increment_depth(self):
        """Every callback type increments/decrements callback depth."""
        from natlink_compat._callbacks import (
            dispatch_begin_callback, dispatch_change_callback,
            dispatch_phrase_finish, dispatch_phrase_hypothesis,
            dispatch_dict_text_changed, dispatch_dict_begin_callback,
            dispatch_timer_callback,
        )

        depths_seen = []

        def capture_depth(*args, **kwargs):
            depths_seen.append(int(self._state.callback_depth))

        # Begin
        self._state.begin_callbacks[:] = [capture_depth]
        dispatch_begin_callback(("", "", 0))

        # Change
        self._state.change_callbacks[:] = [capture_depth]
        dispatch_change_callback("mic", "on")

        # Timer
        self._state.timer_callbacks[:] = [capture_depth]
        dispatch_timer_callback()

        # PhraseFinish — needs a grammar with results callback
        gram = MagicMock()
        gram._results_callback = capture_depth
        gram._all_results = False
        self._state.grammar_registry[1] = gram
        mock_res = MagicMock()
        mock_res.get_results.return_value = [{"word": "x", "cfg_parse": 0}]
        dispatch_phrase_finish(1, 0x03, mock_res)

        # Hypothesis
        gram._hypothesis_callback = capture_depth
        dispatch_phrase_hypothesis(1, ["x"])

        # Dict text changed
        dobj = MagicMock()
        dobj._change_callback = capture_depth
        self._state.dict_registry[2] = dobj
        dispatch_dict_text_changed(2, 0, 0, "", 0, 0)

        # Dict begin
        dobj._begin_callback = capture_depth
        dispatch_dict_begin_callback(2, ("", "", 0))

        # Every callback should have seen depth >= 1
        self.assertEqual(len(depths_seen), 7,
                         f"Expected 7 callbacks, got {len(depths_seen)}")
        for i, d in enumerate(depths_seen):
            self.assertGreaterEqual(d, 1,
                                    f"Callback {i} ran at depth {d}, expected >= 1")

        # After all callbacks, depth should be back to 0
        self.assertEqual(int(self._state.callback_depth), 0)

    def test_change_deferred_during_begin(self):
        """Change callback during begin callback is deferred, not fired inline.

        Matches C++: "Change callbacks are not allowed when we are processing
        another callback."
        """
        from natlink_compat._callbacks import _on_paused, DGNSRAC_MICSTATE

        change_received = []
        begin_received = []

        def on_begin(info):
            begin_received.append(info)
            # Simulate Dragon firing AttribChanged2(MICSTATE) during begin
            from natlink_compat._callbacks import _on_attrib_changed
            _on_attrib_changed(DGNSRAC_MICSTATE)
            # Change should NOT have fired yet (we're at depth > 0)
            self.assertEqual(change_received, [],
                             "Change fired during begin — should be deferred")

        self._state.begin_callbacks[:] = [on_begin]
        self._state.change_callbacks[:] = [lambda t, info: change_received.append((t, info))]

        _on_paused()

        # After _on_paused returns, the deferred change should have replayed
        self.assertEqual(len(begin_received), 1)
        self.assertEqual(len(change_received), 1)
        self.assertEqual(change_received[0], ("mic", "on"))

    # --- Exception isolation ---
    # Broken begin + broken results tested live in test_05
    # (test_broken_begin_doesnt_kill_grammar, test_broken_results_doesnt_crash)

    def test_broken_dict_change_callback_doesnt_propagate(self):
        """Exception in dictation change callback is caught."""
        from natlink_compat._callbacks import dispatch_dict_text_changed

        dobj = MagicMock()
        dobj._change_callback = MagicMock(side_effect=RuntimeError("boom"))
        self._state.dict_registry[1] = dobj

        dispatch_dict_text_changed(1, 0, 0, "", 0, 0)  # must not raise


class TestPhraseFinishPauseRecog(unittest.TestCase):
    """Verify _do_phrase_finish (the deferred handler) calls reset_pause_recog.

    The full lifecycle is: GrammarSink.PhraseFinish increments pause_recog
    and posts _do_phrase_finish to the deferred queue.  _do_phrase_finish
    fires the callback then calls reset_pause_recog in finally.

    The increment half (inside the COM sink method) requires real COM args
    and is covered by the live test suite (test_05_callbacks).  Here we
    test the decrement half directly — _do_phrase_finish takes plain
    Python args (gram_handle, dwFlags, res_obj), no COM needed.
    """

    def test_do_phrase_finish_calls_reset_pause_recog(self):
        """_do_phrase_finish fires callback then decrements pause_recog."""
        import threading
        from natlink_com._grammar_sink import _build_sink_class

        conn = MagicMock()
        conn._pause_recog = 1  # simulate the increment that PhraseFinish did
        conn._deferred_cookie = None
        conn._engine_sink = None
        conn.on_phrase_finish = MagicMock()

        def real_reset():
            
                if conn._pause_recog > 0:
                    conn._pause_recog -= 1
        conn.reset_pause_recog = real_reset

        SinkClass = _build_sink_class()
        sink = SinkClass.__new__(SinkClass)
        sink._gram_handle = 1
        sink._connection = conn

        # Call _do_phrase_finish directly — plain Python args, no COM
        sink._do_phrase_finish(1, 0x03, MagicMock())

        conn.on_phrase_finish.assert_called_once()
        self.assertEqual(conn._pause_recog, 0,
                         "_do_phrase_finish must call reset_pause_recog")

    def test_do_phrase_finish_resets_even_on_callback_error(self):
        """reset_pause_recog runs even if the user callback throws."""
        import threading
        from natlink_com._grammar_sink import _build_sink_class

        conn = MagicMock()
        conn._pause_recog = 1
        conn._deferred_cookies = []
        conn._engine_sink = None
        conn.on_phrase_finish = MagicMock(side_effect=RuntimeError("boom"))

        def real_reset():
            if conn._pause_recog > 0:
                conn._pause_recog -= 1
        conn.reset_pause_recog = real_reset

        SinkClass = _build_sink_class()
        sink = SinkClass.__new__(SinkClass)
        sink._gram_handle = 1
        sink._connection = conn

        sink._do_phrase_finish(1, 0x03, MagicMock())  # must not raise

        self.assertEqual(conn._pause_recog, 0,
                         "reset_pause_recog must run even after callback error")


    # AtomicCounter tests removed — callback_depth is now a plain int (STA).


if __name__ == "__main__":
    unittest.main()
