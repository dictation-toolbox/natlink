"""Grammar notification sink for Dragon recognition callbacks.

Implements two COM interfaces on a single object:
  - ISRGramNotifySinkW: Grammar callbacks (PhraseFinish, PhraseHypothesis, etc.)
  - IDgnGetSinkFlags: Tells Dragon which grammar callbacks we want

Created per-grammar and passed to ISRCentralW::GrammarLoad.
"""

import ctypes
import logging

log = logging.getLogger("natlink.com.sink.grammar")
# Partial-result hypothesis fires several times per utterance; route it
# through a child logger so it can be silenced independently.
_hypo_log = log.getChild("hypothesis")

# Grammar sink flags — imported from _dspeech_constants.
# SENDPHRASEFINISH    — "send PhraseFinish for our grammar"
# SENDFOREIGNFINISH   — "send PhraseFinish for all grammars" (allResults mode)
# SENDPHRASEHYPO      — "send PhraseHypothesis"
# — Joel Gould, GrammarObject.cpp (CSRGramNotifySink::SinkFlagsGet)
from ._dspeech_constants import (
    DGNSRGRAMSINKFLAG_SENDPHRASESTART,
    DGNSRGRAMSINKFLAG_SENDPHRASEHYPO,
    DGNSRGRAMSINKFLAG_SENDPHRASEFINISH,
    DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH,
)
from ._speech_constants import ISRNOTEFIN_RECOGNIZED as _ISRNOTEFIN_RECOGNIZED

from ._com_helpers import lazy_com_factory


def _build_sink_class():
    """Build the GrammarSink COMObject class."""
    from comtypes import COMObject
    from ._tlb import get_tlb; tlb = get_tlb()
    ISRGramNotifySinkW = tlb.ISRGramNotifySinkW
    IDgnGetSinkFlags = tlb.IDgnGetSinkFlags
    from . import _hidden_wnd

    class GrammarSink(COMObject):
        """Per-grammar notification sink."""
        _com_interfaces_ = [ISRGramNotifySinkW, IDgnGetSinkFlags]

        def __init__(self, gram_handle, all_results, hypothesis, connection=None):
            super().__init__()
            self._gram_handle = gram_handle
            self._all_results = all_results
            self._hypothesis = hypothesis
            self._connection = connection

        # --- IDgnGetSinkFlags ---
        # "Dragon NaturallySpeaking allows sink object to have a separate
        # interface called IDgnGetSinkFlags.  That interface implements a
        # single function which is call by Drgaon [sic] NaturallySpeaking
        # when the sink is first registered.
        #
        # if IDgnGetSinkFlags exists, SinkFlagsGet returns a list of the
        # notifications we want.  This interface is optional.  Without it
        # we return the normal set (PhraseState, PhraseFinish, etc.) but
        # with this interface we can reduce the notification traffic."
        # — Joel Gould, GrammarObject.cpp (CSRGramNotifySink::SinkFlagsGet)

        def IDgnGetSinkFlags_SinkFlagsGet(self, p0):
            flags = DGNSRGRAMSINKFLAG_SENDPHRASEFINISH
            if self._all_results:
                flags |= DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH
            if self._hypothesis:
                flags |= DGNSRGRAMSINKFLAG_SENDPHRASEHYPO
            return flags

        # --- ISRGramNotifySinkW ---

        def ISRGramNotifySinkW_BookMark(self, p0):
            return 0

        def ISRGramNotifySinkW_Paused(self):
            return 0

        def ISRGramNotifySinkW_PhraseFinish(self, dwFlags, qBegin, qEnd, pSRPhrase, pUnknown):
            log.debug("PhraseFinish(flags=0x%X, handle=%d)", dwFlags, self._gram_handle)
            # C++: "do nothing if there is no results object"
            # — Joel Gould, GrammarObject.cpp (CGrammarObject::PhraseFinish)
            if pUnknown is None:
                return 0
            try:
                from ._res_obj import ComResObj, parse_srphrasew
                conn = self._connection
                tlb = conn.tlb if conn else None
                if tlb is None:
                    from ._tlb import get_tlb
                    tlb = get_tlb()
                words = parse_srphrasew(pSRPhrase)
                log.debug("PhraseFinish words: %s", words)
                # Wrap the raw pointer in an independent comtypes wrapper that
                # ComResObj solely owns and releases — the comtypes pUnknown
                # passed into this callback is released by the RPC dispatcher
                # when we return, so its reference cannot survive the call.
                import comtypes
                from ._com_helpers import wrap_comtypes
                raw = ctypes.cast(pUnknown, ctypes.c_void_p).value
                owned = wrap_comtypes(raw, comtypes.IUnknown)
                try:
                    res_obj = ComResObj(owned, words=words, tlb=tlb,
                                        connection=conn)
                except Exception:
                    from ._com_helpers import force_release
                    force_release(owned)
                    raise
                # "setting this will delay recognition at the start of the
                # next utterance until results are processed"
                # — Joel Gould, DragonCode.cpp (makeResultsCallback)
                if conn is not None:
                    conn.increment_pause_recog()

                # Defer to main thread.  "we do not callback into Python
                # code from a PhraseFinish callback.  Instead we post
                # ourselves a message to do the callback after returning
                # from the PhraseFinish call. Then we set a flag to tell
                # us that we should not respond to the next Paused callback
                # from NatSpeak until all our clients have finished
                # processing their Results (PhraseFinish) callbacks."
                # — Joel Gould, DragonCode.cpp (lines 79-84)
                #
                # Without this, recognitionMimic from inside gotResults
                # would deadlock: mimic needs the recognition loop to
                # proceed, but Dragon won't restart recognition until
                # PhraseFinish returns.
                # Route through the connection so the drain-time grammar
                # lookup remains authoritative (handles mid-connection
                # unload race).  defer_send_results returns False if
                # shutdown is in progress or the post failed — in either
                # case it has already unwound pause_recog itself.
                if conn is not None:
                    conn.defer_send_results(self._gram_handle, dwFlags, res_obj)
            except Exception:
                log.exception("Error in PhraseFinish handler")
            return 0

        def _do_phrase_finish(self, gram_handle, dwFlags, res_obj):
            """Fire resultsCallback on the main thread (deferred from RPC).

            After the callback, decrement pause_recog — if it hits 0 and a
            Paused callback was deferred, process it now (Begin + Resume).
            Matches C++ WM_SENDRESULTS handler → resetPauseRecog().
            """
            try:
                conn = self._connection
                cb = conn.on_phrase_finish if conn else None
                if cb:
                    cb(gram_handle, dwFlags, res_obj)
            except Exception:
                log.exception("Error in deferred PhraseFinish")
            finally:
                conn = self._connection
                if conn is not None:
                    conn.reset_pause_recog()

        def ISRGramNotifySinkW_PhraseHypothesis(self, dwFlags, qBegin, qEnd, pSRPhrase, pUnknown):
            # "Note that a results object is not available." for hypothesis
            # callbacks — only words are passed, no IUnknown.
            # — Joel Gould, GrammarObject.cpp (CSRGramNotifySink::PhraseHypothesis)
            _hypo_log.debug("PhraseHypothesis(flags=0x%x, handle=%d)", dwFlags, self._gram_handle)

            # "do nothing if the recognition is being rejected"
            # — Joel Gould, GrammarObject.cpp (CGrammarObject::PhraseHypothesis)
            if not (dwFlags & _ISRNOTEFIN_RECOGNIZED):
                return 0

            try:
                from ._res_obj import parse_srphrasew
                raw_words = parse_srphrasew(pSRPhrase)
                words = [w for w, _ in raw_words]
                conn = self._connection
                if conn is not None:
                    conn.defer_phrase_hypo(self._gram_handle, words)
            except Exception:
                log.exception("Error in PhraseHypothesis handler")
            return 0

        def _do_phrase_hypothesis(self, gram_handle, words):
            """Fire hypothesisCallback on the main thread."""
            try:
                conn = self._connection
                cb = conn.on_phrase_hypothesis if conn else None
                if cb:
                    cb(gram_handle, words)
            except Exception:
                log.exception("Error in deferred PhraseHypothesis")

        def ISRGramNotifySinkW_PhraseStart(self, p0):
            return 0

        def ISRGramNotifySinkW_ReEvaluate(self, p0):
            return 0

        def ISRGramNotifySinkW_Training(self, p0):
            return 0

        def ISRGramNotifySinkW_UnArchive(self, p0):
            return 0

    return GrammarSink


create_grammar_sink = lazy_com_factory(_build_sink_class)
