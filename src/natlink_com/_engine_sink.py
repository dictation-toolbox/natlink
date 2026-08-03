"""Engine notification sink for Dragon callbacks.

Implements three COM interfaces on a single object:
  - IDgnSREngineNotifySinkW: Primary sink (AttribChanged2, Paused, MimicDone)
  - ISRNotifySink: Legacy notification interface (stubs)
  - IDgnGetSinkFlags: Tells Dragon which callbacks we want

Registered via ISRCentralW::Register(sink, IID_IDgnSREngineNotifySinkW).
Dragon QIs the sink for ISRNotifySink and IDgnGetSinkFlags.

Dispatch logic lives in the compat layer — this sink fires events via
callback slots on DragonConnection (on_paused_dispatch, on_attrib_changed).
"""

import logging
import time as _time

from ._com_helpers import get_dragon_error_message as _get_dragon_error_message
from ._dspeech_constants import (
    DGNSRAC_MICSTATE, DGNSRAC_REGISTRY,
    DGNSRAC_PLAYBACKDONE, DGNSRAC_TOPIC,
    DGNSRAC_LEXADD, DGNSRAC_LEXREMOVE,
    DGNSRSINKFLAG_SENDATTRIB,
    DGNSRSINKFLAG_SENDJITPAUSED,
    DGNSRSINKFLAG_SENDMIMICDONE,
)
from ._speech_constants import ISRNSAC_SPEAKER

# Logged at INFO (others at DEBUG) so operators can correlate Dragon's
# emission count against outgoing SetMicState / Select user calls.
_STATE_CHANGE_CODES = frozenset((DGNSRAC_MICSTATE, ISRNSAC_SPEAKER))

log = logging.getLogger("natlink.com.sink.engine")
_attrib_log = logging.getLogger("natlink.com.sink.engine.attrib_changed")

_ATTRIB_NAMES = {
    DGNSRAC_MICSTATE: "MICSTATE",            # 1001
    DGNSRAC_REGISTRY: "REGISTRY",            # 1002
    DGNSRAC_PLAYBACKDONE: "PLAYBACKDONE",    # 1003
    DGNSRAC_TOPIC: "TOPIC",                  # 1004
    DGNSRAC_LEXADD: "VOCAB_CHANGED",         # 1005
    DGNSRAC_LEXREMOVE: "VOCAB_DONE",         # 1006
}

# Sink flags — imported above from _dspeech_constants.
# From C++ CDgnSRNotifySink::SinkFlagsGet (DragonCode.cpp):
#   DGNSRSINKFLAG_SENDJITPAUSED — send just-in-time paused before grammars are loaded
#   DGNSRSINKFLAG_SENDATTRIB    — send AttribChanged messages
#   DGNSRSINKFLAG_SENDMIMICDONE — send MimicDone message

from ._com_helpers import lazy_com_factory


def _build_sink_class():
    """Build the EngineSink COMObject class."""
    from comtypes import COMObject
    tlb = __import__('natlink_com._tlb', fromlist=['get_tlb']).get_tlb()
    IDgnSREngineNotifySinkW = tlb.IDgnSREngineNotifySinkW
    ISRNotifySink = tlb.ISRNotifySink
    IDgnGetSinkFlags = tlb.IDgnGetSinkFlags
    from . import _hidden_wnd

    class EngineSink(COMObject):
        """Dragon engine notification sink.

        comtypes handles the dual-vtable requirement automatically:
        IDgnGetSinkFlags vtable slot [3] = SinkFlagsGet, which differs from
        IDgnSREngineNotifySinkW slot [3] = AttribChanged2. comtypes creates
        separate vtable pointers for each interface in _com_interfaces_.
        """
        _com_interfaces_ = [IDgnSREngineNotifySinkW, ISRNotifySink, IDgnGetSinkFlags]

        def __init__(self, connection):
            super().__init__()
            self._conn = connection

        # --- IDgnGetSinkFlags ---

        def IDgnGetSinkFlags_SinkFlagsGet(self, p0):
            # C++ CDgnSRNotifySink::SinkFlagsGet (DragonCode.cpp):
            #   *pdwFlags =
            #       DGNSRSINKFLAG_SENDJITPAUSED |  // send just-in-time paused before grammars are loaded
            #       DGNSRSINKFLAG_SENDATTRIB |     // send AttribChanged messages
            #       DGNSRSINKFLAG_SENDMIMICDONE;   // send MimicDone message
            log.info("SinkFlagsGet: ATTRIB|JITPAUSED|MIMICDONE")
            return (DGNSRSINKFLAG_SENDATTRIB |
                    DGNSRSINKFLAG_SENDJITPAUSED |
                    DGNSRSINKFLAG_SENDMIMICDONE)

        # --- IDgnSREngineNotifySinkW ---

        def IDgnSREngineNotifySinkW_AttribChanged2(self, dwCode):
            name = _ATTRIB_NAMES.get(dwCode, "?")
            if dwCode in _STATE_CHANGE_CODES:
                _attrib_log.info("← AttribChanged2(%d=%s)", dwCode, name)
            else:
                _attrib_log.debug("← AttribChanged2(%d=%s)", dwCode, name)
            # C++ postMessage(WM_ATTRIBCHANGED) served both the pump's
            # PLAYBACKDONE completion (signal) and the attrib-changed
            # callback (dispatch); those are split here.
            _hidden_wnd.signal(_hidden_wnd.WM_ATTRIBCHANGED, dwCode, 0)
            _hidden_wnd.dispatch(self._dispatch_attrib_changed, dwCode,
                                 channel=_hidden_wnd.WM_ATTRIBCHANGED_WORK)
            return 0  # S_OK

        def _dispatch_attrib_changed(self, dwCode):
            cb = self._conn.on_attrib_changed
            if cb:
                cb(dwCode)

        def IDgnSREngineNotifySinkW_Paused(self, qCookie):
            # C++ heap-allocated the cookie and posted WM_PAUSED; here
            # the cookie rides the closure queue instead.
            log.debug("Paused(cookie=%d, pause_recog=%d)",
                      qCookie, self._conn._pause_recog)
            _hidden_wnd.dispatch(self._do_paused, qCookie,
                                 channel=_hidden_wnd.WM_PAUSED)
            return 0  # S_OK

        def _do_paused(self, qCookie):
            """Process Paused on the main thread (deferred via queue).

            Maps to C++ CDragonCode::onPaused (DragonCode.cpp):
              if( m_nPauseRecog )
              {
                  // whoops, we want to pause recognition for a while (probably
                  // because we are processing the results of a previous recognition)
                  m_deferredCookie = *pCookie;
              }
              else
              {
                  doPausedProcessing( *pCookie );
              }
            """
            conn = self._conn
            if conn._pause_recog > 0:
                log.debug("Paused deferred (pause_recog=%d, cookie=%d)",
                          conn._pause_recog, qCookie)
                conn._deferred_cookies.append(qCookie)
                return
            self._do_paused_processing(qCookie)

        def _do_paused_processing(self, qCookie):
            """Fire begin callbacks then Resume.

            Maps to C++ CDragonCode::doPausedProcessing (DragonCode.cpp).
            From the C++ comment:
              // You must call Resume to get the engine started again.  Just
              // returning from this function is not enough.  For other
              // applications this gives us the flexibility to return from
              // this function and handle the processing later before the
              // recognition loop restarts.
            """
            t_enter = _time.perf_counter()
            self._conn._paused_cookie = qCookie
            resumed = False
            try:
                cb = self._conn.on_paused_dispatch
                if cb:
                    cb()
            except Exception:
                log.exception("Error in Paused handler")
            finally:
                ctl = self._conn.engine_ctl
                if ctl is not None:
                    try:
                        ctl.Resume(qCookie)
                        resumed = True
                        self._conn._resume_count += 1
                    except Exception:
                        log.exception("CRITICAL: Resume(%d) FAILED — "
                                      "Dragon may be frozen", qCookie)
                else:
                    log.error("CRITICAL: engine_ctl is None during Paused — "
                              "cannot Resume, Dragon is frozen")
                self._conn._paused_cookie = None
                freeze_ms = (_time.perf_counter() - t_enter) * 1000
                if not resumed:
                    log.error("Paused→STUCK: %.1fms, cookie=%d, "
                              "Resume not called", freeze_ms, qCookie)
                elif freeze_ms > 50:
                    log.warning("Paused→Resume took %.1fms (Dragon frozen)",
                                freeze_ms)
                else:
                    log.debug("Paused→Resume: %.1fms", freeze_ms)

        def IDgnSREngineNotifySinkW_MimicDone(self, dwClientCode, pUnknown):
            failed = 1 if pUnknown else 0
            log.debug("MimicDone(clientCode=%d, failed=%d)", dwClientCode, failed)
            # C++ CDgnSRNotifySink::MimicDone (DragonCode.cpp):
            #   if( pIUnknown != NULL )
            #   {
            #       pIUnknown->AddRef();
            #   }
            #   m_pParent->postMessage( WM_MIMICDONE, dwClientCode, (LPARAM)pIUnknown );
            # C++ AddRefs pIUnknown before posting (prevents release before
            # main thread processes it).  We pass a boolean instead — comtypes
            # prevents premature release via preventing release of COM pointers during
            # the callback, so the AddRef/Release pattern is not needed.
            # wParam = client code, lParam = 0 success / non-zero failure
            _hidden_wnd.signal(_hidden_wnd.WM_MIMICDONE, dwClientCode, failed)
            return 0  # S_OK

        def IDgnSREngineNotifySinkW_ErrorHappened(self, pUnknown):
            msg = _get_dragon_error_message(pUnknown)
            if msg:
                log.warning("ErrorHappened: %s", msg)
            else:
                log.warning("ErrorHappened callback from Dragon")
            return 0  # S_OK

        def IDgnSREngineNotifySinkW_Progress(self, iCode, pszMsg):
            log.debug("Progress(code=%d)", iCode)
            return 0  # S_OK

        # --- ISRNotifySink (stubs — Dragon may QI for this) ---

        def ISRNotifySink_AttribChanged(self, p0):
            return 0
        def ISRNotifySink_Interference(self, p0, p1, p2):
            return 0
        def ISRNotifySink_Sound(self, p0, p1):
            return 0
        def ISRNotifySink_UtteranceBegin(self, p0):
            return 0
        def ISRNotifySink_UtteranceEnd(self, p0, p1):
            return 0
        def ISRNotifySink_VUMeter(self, p0, p1):
            return 0

    return EngineSink


create_engine_sink = lazy_com_factory(_build_sink_class)


def completion_channels():
    """Signal channels this sink drives — wndproc handlers call trigger_message
    so ``message_loop`` sees completions even when COM's outgoing-call modal
    loop pre-consumes the message. WM_ATTRIBCHANGED is signal-only; its
    Python follow-up work rides WM_ATTRIBCHANGED_WORK (auto-routed dispatch).
    """
    from . import _hidden_wnd
    return (_hidden_wnd.WM_PLAYBACK, _hidden_wnd.WM_EXECUTION,
            _hidden_wnd.WM_MIMICDONE, _hidden_wnd.WM_ATTRIBCHANGED)
