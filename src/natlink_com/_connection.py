"""Dragon COM connection lifecycle."""

import ctypes
import logging
import os
import sys
import threading
from ctypes import POINTER, byref, c_void_p, c_ulong, c_long
from typing import Tuple

from ._com_helpers import qi_raw, release_raw, call_query_service, wrap_comtypes, addref_raw
from ._guids import (
    GUID, IID, CLSID_DgnSite, GUID_DgnDictate, GUID_SpchServices, GUID_DgnVDct,
    GUID_DgnExtModSupport, IID_IUnknown, IID_IServiceProvider, IID_ISRCentralW,
)
from ._errors import NatlinkCOMError
from ._speech_constants import (
    E_BUFFERTOOSMALL as _E_BUFFERTOOSMALL,
    SRERR_NOUSERSELECTED as _SRERR_NOUSERSELECTED,
)

log = logging.getLogger("natlink.com.conn")

ole32 = ctypes.windll.ole32
ole32.CoCreateInstance.argtypes = [POINTER(GUID), c_void_p, c_ulong, POINTER(GUID), POINTER(c_void_p)]
ole32.CoCreateInstance.restype = c_long

CLSCTX_LOCAL_SERVER = 0x4

# Dragon is a 32-bit LocalServer32.  A 64-bit client must request the 32-bit
# registration explicitly: where a 64-bit-view CLSID entry for DgnSite exists
# (natlink's historical dgnSiteSurrogate registration leaves an AppID with an
# empty DllSurrogate), plain CLSCTX_LOCAL_SERVER resolves to that entry and
# activation fails with CO_E_SERVER_EXEC_FAILURE instead of binding to the
# running Dragon.
CLSCTX_ACTIVATE_32_BIT_SERVER = 0x40000

# COM HRESULT codes for CoCreateInstance error handling (winerror.h).
_CO_E_SERVER_EXEC_FAILURE = 0x80080005
_CO_E_OBJSRV_RPC_FAILURE = 0x80080006
_REGDB_E_CLASSNOTREG = 0x80040154

# Marshal registration persists for the process lifetime — never revoked.
_marshal_registered = False
_marshal_lock = threading.Lock()



def _sink_com_refcount(sink) -> int:
    """Return a comtypes server's external COM refcount, robustly.

    comtypes.COMObject stores its refcount in ``_refcnt``, a
    ``ctypes.c_long`` initialized to 0 and driven by IUnknown_AddRef /
    IUnknown_Release (Dragon's cross-process refs).  Our Python attribute
    (``self._engine_sink``) is NOT an AddRef and does not count.  When
    Dragon has released every ref the value reaches 0.

    A None sink, or one whose refcount cannot be read, is treated as
    already-drained (returns 0) — never block teardown on a value we
    cannot trust.
    """
    if sink is None:
        return 0
    refcnt = getattr(sink, "_refcnt", None)
    if refcnt is None:
        return 0
    value = getattr(refcnt, "value", refcnt)  # c_long → int, or plain int
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _detect_dragon_major() -> int:
    """Detect Dragon major version — delegates to _config.detect_dragon_major."""
    from ._config import detect_dragon_major
    return detect_dragon_major()


from ._tlb import load_tlb as _load_tlb


class DragonConnection:
    """Manages COM connection to Dragon NaturallySpeaking."""

    def __init__(self):
        self._central = None          # ISRCentralW comtypes wrapper
        self._engine_ctl = None       # IDgnSREngineControlW comtypes wrapper
        self._speaker = None          # ISRSpeakerW comtypes wrapper
        self._output_event = None     # IDgnSSvcOutputEventW comtypes wrapper
        self._interpreter = None      # IDgnSSvcInterpreterW comtypes wrapper
        self._engine_sink = None      # EngineSink COMObject
        self._action_sink = None      # ActionSink COMObject
        self._detected_major: int = 0
        self._dragon_version: Tuple[int, int, int] = (0, 0, 0)  # (major, minor, build)
        self._marshal_hmod: int = 0
        self._marshal_cookie: int = 0
        self._sink_keys: dict = {}    # name -> DWORD registration key
        self._grammar_sinks: dict = {}  # gram_handle -> GrammarSink
        self._dict_sinks: dict = {}     # dict_handle -> DictSink
        self._tlb = None              # comtypes TLB module
        # Phase 5 interfaces
        self._lexicon = None          # IDgnSRLexiconW comtypes wrapper
        # ILexPronounceW is not part of the reliable baseline. The current
        # cross-process Get() path still fails in practice, so lexicon code
        # keeps IDgnLexWordW as the dependable fallback.
        self._lex_word = None         # IDgnLexWordW comtypes wrapper
        self._training = None         # IDgnSRTrainingA comtypes wrapper
        self._training_active = False # set by start_training, cleared by finish/cancel
        self._audio_file_source = None  # IDgnSRAudioFileSourceW comtypes wrapper
        # Win32 manual-reset events for COM callback signaling.
        # Initialized to 0 before CreateEventW so __del__ is safe
        # even if __init__ fails partway through.
        self._mimic_failed = False
        _k32 = ctypes.windll.kernel32
        self._paused_cookie = None      # set during Paused, cleared after Resume
        self._deferred_cookies = []     # Paused cookies queued when results pending
        self._pause_recog = 0           # >0 means defer Paused until results done
        self._resume_count = 0          # incremented each Resume call
        # Raw COM pointers — independently AddRef'd for deterministic release.
        # comtypes may internally release proxies before our disconnect(),
        # leaving force_release operating on dead proxies.  These raw pointers
        # guarantee Dragon sees the Release in the right order regardless of
        # what comtypes does.  Same pattern as _psp_raw (IServiceProvider).
        self._raw_ptrs: list = []         # [(name, raw_ptr), ...] release order
        # Flipped via begin_shutdown() so defer_* routers reject new work.
        self._shutting_down: bool = False
        # Dictation (Phase 6) — raw IServiceProvider kept for lazy QueryService
        self._psp_raw: int = 0            # raw IServiceProvider pointer (AddRef'd)
        self._ext_mod_strings = None  # IDgnExtModSupStringsW comtypes wrapper
        # Callback slots — set by the compat layer during natConnect.
        # Keeps natlink_com free of any natlink_compat imports.
        self._clear_callback_slots()

    # Slot names must match register_all/unregister_all in natlink_compat._callbacks
    CALLBACK_SLOTS = (
        "on_paused_dispatch", "on_attrib_changed", "on_timer_dispatch",
        "on_phrase_finish", "on_phrase_hypothesis",
        "on_dict_text_changed", "on_dict_begin", "lookup_com_grammar",
    )

    def _clear_callback_slots(self):
        for name in self.CALLBACK_SLOTS:
            setattr(self, name, None)

    def __del__(self):
        _k32 = ctypes.windll.kernel32

    def connect(self, register_marshal: bool = True) -> None:
        """Establish COM connection to Dragon.

        Connection order matches the C++ CDragonCode::natConnect:
        1. CoCreateInstance(DgnSite, CLSCTX_LOCAL_SERVER) -> IServiceProvider
        2. QueryService(DgnDictate, ISRCentralW) -> engine object
        3. QI for IDgnSREngineControl, speaker, output event, interpreter
        4. QueryService(DgnExtModSupport) -> GetWindowModuleFileName helper
        5. Register engine sink and action sink

        "We connect to NatSpeak through a site object which is a better
        way than using the SAPI enumerator objects because it also gives
        us access to the other DgnSAPI interfaces at the same time."
        — Joel Gould, DragonCode.cpp (initGetSiteObject)

        "The CoCreateInstance call is known to occassionally fail with
        a CO_E_OBJSRV_RPC_FAILURE error but retrying this will get
        around this unexplained failure."
        — Joel Gould, DragonCode.cpp (initGetSiteObject, line 1518)

        Args:
            register_marshal: If True, register custom marshal DLLs.
        """
        # Acquisition is not atomic: by the time Register() runs we hold the
        # site object, ~9 AddRef'd interface pointers and the hidden window.
        # Without an unwind, a failure part-way leaves all of it alive with
        # _state.backend never assigned, so natDisconnect is never reached and
        # Dragon keeps the session open -- exactly what the unreleased-COM
        # warning at shutdown reports.
        try:
            self._connect_impl(register_marshal)
        except BaseException:
            try:
                self.disconnect()
            except Exception:
                log.debug("rollback after failed connect did not complete",
                          exc_info=True)
            raise

    def _connect_impl(self, register_marshal: bool = True) -> None:
        _k32 = ctypes.windll.kernel32

        # STA (2) — COM callbacks serialized on main thread via message queue,
        # matching the original C++ architecture.
        flags = getattr(sys, 'coinit_flags', None)
        if flags is None:
            log.warning("sys.coinit_flags not set — set to 2 (STA) "
                        "before importing comtypes")

        detected = _detect_dragon_major()
        self._detected_major = detected
        log.debug("Dragon %d from detection", detected)

        self._tlb = _load_tlb()

        # Register custom marshaling DLLs (once per process — never revoked)
        global _marshal_registered
        with _marshal_lock:
            if register_marshal and not _marshal_registered:
                from ._marshaling import register_marshaling
                self._marshal_hmod, self._marshal_cookie = register_marshaling(
                    dragon_major=detected)
                _marshal_registered = True

        # CoCreateInstance(DgnSite) -> IUnknown
        #
        # "The CoCreateInstance call is known to occassionally fail with
        # a CO_E_OBJSRV_RPC_FAILURE error but retrying this will get
        # around this unexplained failure."
        # — Joel Gould, DragonCode.cpp (initGetSiteObject, line 1518)
        ppv = c_void_p()
        last_hr = 0
        for attempt in range(3):
            hr = ole32.CoCreateInstance(
                byref(CLSID_DgnSite), None,
                CLSCTX_LOCAL_SERVER | CLSCTX_ACTIVATE_32_BIT_SERVER,
                byref(IID_IUnknown), byref(ppv)
            )
            last_hr = hr & 0xFFFFFFFF
            if hr >= 0:
                break
            if last_hr == _CO_E_OBJSRV_RPC_FAILURE:
                log.warning("CoCreateInstance attempt %d: CO_E_OBJSRV_RPC_FAILURE "
                            "(transient), retrying...", attempt + 1)
                import time
                time.sleep(0.5)
                continue
            break  # non-transient error, don't retry

        if hr < 0:
            hints = {
                _REGDB_E_CLASSNOTREG:
                    "Dragon is not installed or its COM server is not registered.",
                _CO_E_SERVER_EXEC_FAILURE:
                    "Dragon's COM server failed to start — it may be crash-looping.",
                _CO_E_OBJSRV_RPC_FAILURE:
                    "Dragon's COM server is not responding after 3 attempts.",
            }
            hint = hints.get(last_hr,
                             "Is Dragon running? If so, a stale natlink process "
                             "may be blocking the connection.")
            raise NatlinkCOMError(
                "CoCreateInstance(DgnSite)", hr=hr,
                error_message=f"HRESULT 0x{last_hr:08X} — {hint}")
        punk = ppv.value
        log.debug("CoCreateInstance(DgnSite) -> 0x%X", punk)

        # QI -> IServiceProvider
        hr, psp = qi_raw(punk, IID_IServiceProvider)
        release_raw(punk)
        if hr < 0:
            raise NatlinkCOMError("QI(IServiceProvider)", hr=hr)

        # QueryService(DgnDictate, ISRCentralW) -> raw pointer
        hr, pcentral = call_query_service(psp, GUID_DgnDictate, IID_ISRCentralW)
        if hr < 0:
            release_raw(psp)
            raise NatlinkCOMError("QueryService(DgnDictate, ISRCentralW)", hr=hr)
        log.debug("ISRCentralW raw ptr = 0x%X", pcentral)

        # QueryService(SpchServices, IUnknown) -> speech services object
        hr, pspch = call_query_service(psp, GUID_SpchServices, IID_IUnknown)
        # Keep IServiceProvider for lazy QueryService(DgnVDct) in create_dictation
        self._psp_raw = psp
        if hr < 0:
            log.warning("QueryService(SpchServices) failed: 0x%08X", hr & 0xFFFFFFFF)
            pspch = None
        else:
            log.debug("SpchServices raw ptr = 0x%X", pspch)

        # QueryService(DgnExtModSupport, IDgnExtModSupStringsW) -> module filename helper
        hr, pextmod = call_query_service(psp, GUID_DgnExtModSupport,
            IID(0xDD109601, 0x6205, 0x11CF, [0xAE, 0x61, 0x00, 0x00, 0xE8, 0xA2, 0x86, 0x47]))
        if hr < 0:
            log.debug("QueryService(DgnExtModSupport) not available: 0x%08X", hr & 0xFFFFFFFF)
            self._ext_mod_strings = None
        else:
            log.debug("DgnExtModSupStringsW raw ptr = 0x%X", pextmod)
            self._ext_mod_strings = wrap_comtypes(pextmod, self._tlb.IDgnExtModSupStringsW)
            release_raw(pextmod)

        self._central = wrap_comtypes(pcentral, self._tlb.ISRCentralW)
        # Keep raw pointer for deterministic release (pcentral still has 1 ref)
        self._raw_ptrs.append(("ISRCentralW", pcentral))
        # Don't release_raw(pcentral) — we keep it for disconnect

        # --- Phase 2: QI for interfaces needed before sink registration ---
        # "This interface contains the microphone logic"
        # — Joel Gould, DragonCode.cpp (natConnect)
        self._qi_core_interfaces(pspch)

        # --- Phase 3: Create hidden window ---
        # C++ calls initSecondWindow after sinks, but our sinks post to
        # the hidden window immediately — so we create it first.
        from . import _hidden_wnd
        if not _hidden_wnd.create():
            raise NatlinkCOMError("connect",
                                  error_message="Failed to create hidden COM window")

        # --- Phase 4: Register sinks ---
        # "create an engine sink and register it"
        # "create a playback sink and register it"
        # — Joel Gould, DragonCode.cpp (natConnect)
        self._register_sinks()

        # --- Phase 5: QI for remaining interfaces (after sink registration) ---
        # C++ QIs IDgnSRTraining after registering sinks.
        self._qi_late_interfaces()

        # --- Phase 6: Get Dragon version ---
        if self._engine_ctl is not None:
            try:
                major, minor, build = self._engine_ctl.GetVersion()
                self._dragon_version = (major, minor, build)
                log.info("Dragon version: %d.%d.%d", major, minor, build)
            except Exception as e:
                log.warning("Could not get Dragon version: %s", e)

        log.debug("Connected to Dragon via COM")

    def _try_qi(self, source, iface_name):
        """Try QI, log warning on failure, return result or None.

        Also saves an AddRef'd raw pointer for deterministic release
        during disconnect.  comtypes may internally release proxy
        refcounts before our disconnect runs — the raw pointers
        guarantee Dragon sees every Release.
        """
        try:
            iface = source.QueryInterface(getattr(self._tlb, iface_name))
            log.debug("Got %s", iface_name)
            raw = addref_raw(iface)
            if raw:
                self._raw_ptrs.append((iface_name, raw))
            return iface
        except Exception as e:
            log.warning("Could not get %s: %s", iface_name, e)
            return None

    def _qi_core_interfaces(self, pspch):
        """QI for interfaces needed before sink registration.

        Matches C++ natConnect order:
          ISRCentral → IDgnSREngineControl  (line 1727)
          SpchServices → IDgnSSvcOutputEvent (line 1739)
                       → IDgnSSvcInterpreter (line 1748)
          DgnExtModSupport → IDgnExtModSupStrings (already done in connect)
        """
        # "This interface contains the microphone logic"
        self._engine_ctl = self._try_qi(self._central, "IDgnSREngineControlW")

        # Speech services interfaces — needed to register action sink
        if pspch is not None:
            import comtypes
            spch_unk = wrap_comtypes(pspch, comtypes.IUnknown)
            release_raw(pspch)
            self._output_event = self._try_qi(spch_unk, "IDgnSSvcOutputEventW")
            self._interpreter = self._try_qi(spch_unk, "IDgnSSvcInterpreterW")

        # Additional interfaces needed before sinks
        self._speaker = self._try_qi(self._central, "ISRSpeakerW")
        self._lexicon = self._try_qi(self._central, "IDgnSRLexiconW")
        self._lex_word = self._try_qi(self._central, "IDgnLexWordW")
        self._audio_file_source = self._try_qi(self._central, "IDgnSRAudioFileSourceW")

    def _qi_late_interfaces(self):
        """QI for interfaces after sink registration.

        Matches C++ natConnect: IDgnSRTraining is QI'd after sinks
        are registered (line 1828).
        """
        # "Used for training"
        # — Joel Gould, DragonCode.cpp (natConnect, line 1826)
        self._training = self._try_qi(self._central, "IDgnSRTrainingA")

    def _register_sinks(self):
        """Register sinks and wire signal-channel handlers into wndproc.

        Each sink declares its own ``completion_channels``; this method
        is agnostic to which channels exist. Adding a new signal channel
        is owned by the sink module, not the registration site.
        """
        from . import _hidden_wnd
        from ._engine_sink import create_engine_sink, completion_channels
        self._engine_sink = create_engine_sink(self)

        from ._pump import trigger_message
        for wm in completion_channels():
            _hidden_wnd.register_message_handler(
                wm, lambda wp, lp, m=wm: trigger_message(m, wp, lp))

        iid = self._tlb.IDgnSREngineNotifySinkW._iid_
        key = self._central.Register(self._engine_sink, iid)
        self._sink_keys["engine"] = key
        log.debug("Registered engine sink (key=%d)", key)

        from ._action_sink import create_action_sink
        self._action_sink = create_action_sink()
        self._action_sink._conn = self
        for name, source in [("OutputEvent", self._output_event),
                              ("Interpreter", self._interpreter)]:
            if source is not None:
                try:
                    source.Register(self._action_sink)
                    log.debug("Registered action sink with %s", name)
                except Exception as e:
                    log.warning("Could not register action sink with %s: %s", name, e)

    def unregister_sinks(self) -> None:
        """Unregister all sinks from Dragon.

        Called BEFORE unloading grammars/results/dicts — sinks must be
        removed first to stop Dragon from sending callbacks during teardown.

        The C++ natDisconnect sequence:
          1. Unregister engine sink ("The Unregister call will caused
             NatSpeak to release its references on the notification
             sink" [sic] — line 1875)
          2. Free grammar, result, and dictation objects (releaseObjects)
          3. Release interfaces in order: EngineControl, OutputEvent,
             OutputEventA, ExtModSupStrings, ServiceProvider,
             Interpreter, InterpreterA, Training, Central (last)
             (lines 1888-1896; we omit the "A" ANSI variants)
        — Joel Gould, DragonCode.cpp (natDisconnect)
        """
        # Drain any in-flight sync ops (mimic, playString, execScript)
        # before tearing down sinks.  If Dragon is still processing a
        # mimic when we UnRegister, it will try to deliver MimicDone to
        # a dead sink → CNotify RPC error.
        from ._pump import pump, _message_stack
        if _message_stack:
            log.debug("Draining %d pending sync op(s) before unregister",
                      len(_message_stack))
            pump(timeout_ms=2000)

        # Resume if paused — failure leaves Dragon frozen until restart
        if self._paused_cookie is not None and self._engine_ctl is not None:
            try:
                self._engine_ctl.Resume(self._paused_cookie)
            except Exception:
                log.warning("Resume() failed during disconnect — Dragon may be frozen",
                            exc_info=True)
            self._paused_cookie = None

        # Unregister all sinks via ISRCentralW::UnRegister
        for name, key in list(self._sink_keys.items()):
            try:
                if self._central is not None:
                    self._central.UnRegister(key)
                    log.debug("Unregistered sink %s (key=%d)", name, key)
            except Exception:
                log.warning("Failed to unregister sink %s", name, exc_info=True)
        self._sink_keys.clear()

        # Pump messages to dispatch any in-flight callbacks
        from ._pump import pump
        pump()

        # Destroy hidden window after all sinks are unregistered.
        # unregister_all_message_handlers clears the signal/OS handler
        # registry (WM_PLAYBACK, WM_TIMER, etc.); dispatch channels
        # (closures) are cleared by destroy() itself.
        from . import _hidden_wnd
        _hidden_wnd.unregister_all_message_handlers()
        _hidden_wnd.destroy()

    def begin_shutdown(self) -> None:
        """Mark the connection as shutting down so defer_* routers drop new work."""
        self._shutting_down = True

    def disconnect(self) -> None:
        """Release COM references (step 2 of disconnect).

        Sinks must already be unregistered and grammars/results/dicts
        already destroyed before calling this (see unregister_sinks).

        Release order matches C++ natDisconnect (lines 1888-1896):
        EngineControl, OutputEvent, OutputEventA, ExtModSupStrings,
        ServiceProvider, Interpreter, InterpreterA, Training, Central.
        (We omit the "A" ANSI variants.)
        — Joel Gould, DragonCode.cpp (natDisconnect)

        """
        # "check for special training mode which we should cancel"
        # — Joel Gould, DragonCode.cpp (natDisconnect, line 1865)
        if self._training_active and self._training is not None:
            try:
                self._training.TrainingCancel()
            except Exception:
                log.debug("TrainingCancel failed during disconnect", exc_info=True)
            self._training_active = False

        # Result-object drain is done in natlink_compat._lifecycle._teardown_objects
        # (matches C++ CDragonCode::releaseObjects grouping).  By the time we
        # get here, natlink_com._res_obj._live_res_objs should already be empty.

        # Release comtypes wrappers and flush their Release calls via GC
        # BEFORE releasing raw pointers.  comtypes holds ~13 internal QI refs
        # per interface; setting wrappers to None + gc.collect sends those
        # Releases to Dragon.  Our raw pointers release one additional ref
        # each.  Dragon needs ALL refs to reach 0 before it tears down the
        # session and cleans CNotify.
        self._engine_ctl = None
        self._ext_mod_strings = None
        self._output_event = None
        self._audio_file_source = None
        self._speaker = None
        self._lex_word = None
        self._lexicon = None
        self._interpreter = None
        self._training = None
        self._central = None

        import gc
        gc.collect()
        gc.collect()  # second pass for weak ref / QI cache cycles

        # Release IServiceProvider (already a raw pointer)
        if self._psp_raw:
            try:
                release_raw(self._psp_raw)
            except Exception:
                log.debug("Failed to release IServiceProvider", exc_info=True)
            self._psp_raw = 0

        # Release independently AddRef'd raw pointers in reverse order
        # (Central last — its Release triggers Dragon session teardown).
        for name, raw in reversed(self._raw_ptrs):
            try:
                release_raw(raw)
                log.debug("Released raw %s", name)
            except Exception:
                log.debug("Failed to release raw %s", name, exc_info=True)
        self._raw_ptrs.clear()

        # Pump messages so Dragon's LRPC channel delivers the Releases it
        # owes on our sink COMObjects.  Bounded drain on the real signal —
        # both sinks' external COM refcount reaching 0 — instead of a fixed
        # nap.  Dragon's Releases arrive as incoming RPC calls dispatched
        # through this STA thread's message queue, so we wait briefly for
        # input between dispatch passes and re-check the refcounts.
        from ._pump import pump
        from ._win32 import user32 as _u32
        import time

        _QS_ALLINPUT = 0x04FF
        _WAIT_TIMEOUT = 0x102
        _SLICE_MS = 20
        _BUDGET_S = 0.5

        pump()
        deadline = time.monotonic() + _BUDGET_S
        while True:
            eng = _sink_com_refcount(self._engine_sink)
            act = _sink_com_refcount(self._action_sink)
            if not (eng or act):
                break
            if time.monotonic() >= deadline:
                log.debug("disconnect: sink Release drain timed out "
                          "(engine=%d, action=%d refs remaining)", eng, act)
                break
            # Block up to a slice for the next incoming Release RPC (or wake
            # early when one arrives), then dispatch it.
            _u32.MsgWaitForMultipleObjects(0, None, False, _SLICE_MS, _QS_ALLINPUT)
            pump()
        pump()

        # NOW safe to release sinks — Dragon has released its references to
        # our sink objects (external COM refcount 0), so dropping the Python
        # reference cannot strand a live cross-process pointer.
        self._engine_sink = None
        self._action_sink = None

        # Close Win32 event handles — fresh ones are created on next connect.
        _k32 = ctypes.windll.kernel32
        self._mimic_failed = False
        if self._pause_recog > 0:
            log.warning("disconnect: pause_recog was %d (should be 0)",
                        self._pause_recog)
        if self._deferred_cookies:
            log.warning("disconnect: %d deferred Paused cookie(s) pending (lost)",
                        len(self._deferred_cookies))
        self._pause_recog = 0
        self._deferred_cookies.clear()
        self._clear_callback_slots()

        log.info("Disconnected from Dragon")

    def register_sink(self, sink, iid_comtype) -> int:
        """Register a sink with ISRCentralW::Register.

        Args:
            sink: comtypes COMObject implementing the sink interface
            iid_comtype: comtypes IID (e.g., ISRNotifySink._iid_)

        Returns:
            DWORD registration key for UnRegister
        """
        key = self._central.Register(sink, iid_comtype)
        return key

    def register_grammar_sink(self, gram_handle, sink):
        self._grammar_sinks[gram_handle] = sink

    def unregister_grammar_sink(self, gram_handle):
        self._grammar_sinks.pop(gram_handle, None)

    def register_dict_sink(self, dict_handle, sink):
        self._dict_sinks[dict_handle] = sink

    def unregister_dict_sink(self, dict_handle):
        self._dict_sinks.pop(dict_handle, None)

    # --- Dispatch routers for handle-keyed channels ---------------------
    #
    # Grammar and dict sinks can be unloaded mid-connection.  If a sink
    # closure captured ``self`` on the sink directly, it would keep the
    # sink alive past unload — and the closure might then call into a
    # released COM object.
    #
    # Routing through the connection keeps the closure capturing the
    # long-lived connection instead.  The ``_do_*`` method looks up the
    # sink in its authoritative registry at drain time.  If the sink is
    # gone (grammar/dict unloaded between post and drain), the router
    # unwinds ``pause_recog`` so Dragon does not stay blocked.
    #
    # Post-time ``_shutting_down`` check is additive: rejects new work
    # once natDisconnect starts, so closures don't race with teardown.

    def defer_send_results(self, gram_handle, dwFlags, res_obj) -> bool:
        if self._shutting_down:
            self.reset_pause_recog()
            return False
        from . import _hidden_wnd
        if _hidden_wnd.dispatch(
                self._do_send_results, gram_handle, dwFlags, res_obj,
                channel=_hidden_wnd.WM_SENDRESULTS):
            return True
        # Dispatch refused / post failed — unwind pause_recog so Dragon
        # doesn't stay blocked waiting for a callback that never arrives.
        self.reset_pause_recog()
        return False

    def _do_send_results(self, gram_handle, dwFlags, res_obj):
        if self._shutting_down:
            self.reset_pause_recog()
            return
        gram = self._grammar_sinks.get(gram_handle)
        if gram is None:
            log.debug("WM_SENDRESULTS: grammar %d gone, resetting pause_recog",
                      gram_handle)
            self.reset_pause_recog()
            return
        gram._do_phrase_finish(gram_handle, dwFlags, res_obj)

    def defer_phrase_hypo(self, gram_handle, words) -> bool:
        # WM_PHRASE_HYPO doesn't participate in pause_recog.
        if self._shutting_down:
            return False
        from . import _hidden_wnd
        return _hidden_wnd.dispatch(
            self._do_phrase_hypo, gram_handle, words,
            channel=_hidden_wnd.WM_PHRASE_HYPO)

    def _do_phrase_hypo(self, gram_handle, words):
        if self._shutting_down:
            return
        gram = self._grammar_sinks.get(gram_handle)
        if gram is None:
            return
        gram._do_phrase_hypothesis(gram_handle, words)

    def defer_dict_text_changed(self, dict_handle, *payload) -> bool:
        if self._shutting_down:
            self.reset_pause_recog()
            return False
        from . import _hidden_wnd
        if _hidden_wnd.dispatch(
                self._do_dict_text_changed, dict_handle, *payload,
                channel=_hidden_wnd.WM_DICT_TEXTCHANGED):
            return True
        self.reset_pause_recog()
        return False

    def _do_dict_text_changed(self, dict_handle, *payload):
        if self._shutting_down:
            self.reset_pause_recog()
            return
        sink = self._dict_sinks.get(dict_handle)
        if sink is None:
            log.debug("WM_DICT_TEXTCHANGED: dict %d gone, resetting pause_recog",
                      dict_handle)
            self.reset_pause_recog()
            return
        sink._do_dict_text_changed(dict_handle, *payload)

    def increment_pause_recog(self):
        """Increment pause_recog counter (called when posting WM_SENDRESULTS).

        C++ CDragonCode::makeResultsCallback (line 1293):
        "setting this will delay recognition at the start of the next
        utterance until results are processed"
        — Joel Gould, DragonCode.cpp (makeResultsCallback, line 1295)
        """
        self._pause_recog += 1
        log.debug("pause_recog++ → %d", self._pause_recog)

    def reset_pause_recog(self):
        """Decrement pause_recog counter; process deferred Paused if it hits 0.

        Called after results processing completes and from recognitionMimic/
        execScript.  Matches C++ CDragonCode::resetPauseRecog (line 1304):
        "If the client code executes recognitionMimic or execScript then
        we reset this synchronization flag and let the next recognition
        proceed normally."
        — Joel Gould, DragonCode.cpp (header comment, lines 85-87)

        Always runs on the main thread: called from deferred PhraseFinish,
        deferred ExecutionStatus, and user code (recognitionMimic).
        """
        if self._pause_recog > 0:
            self._pause_recog -= 1
            log.debug("pause_recog-- → %d", self._pause_recog)
        if self._pause_recog == 0 and self._deferred_cookies:
            cookies = list(self._deferred_cookies)
            self._deferred_cookies.clear()
            for cookie in cookies:
                log.debug("reset_pause_recog: processing deferred cookie=%d", cookie)
                if self._engine_sink is not None:
                    self._engine_sink._do_paused_processing(cookie)

    def unregister_sink(self, key: int) -> None:
        """Unregister a sink by its key."""
        if self._central is not None:
            self._central.UnRegister(key)

    @property
    def central(self):
        return self._central

    @property
    def engine_ctl(self):
        return self._engine_ctl

    @property
    def speaker(self):
        return self._speaker

    @property
    def output_event(self):
        return self._output_event

    @property
    def interpreter(self):
        return self._interpreter

    @property
    def dragon_version(self) -> Tuple[int, int, int]:
        return self._dragon_version

    @property
    def tlb(self):
        return self._tlb

    @property
    def lexicon(self):
        return self._lexicon

    @property
    def lex_word(self):
        return self._lex_word

    @property
    def training(self):
        return self._training

    @property
    def audio_file_source(self):
        return self._audio_file_source

    @property
    def action_sink(self):
        return self._action_sink

    @property
    def mimic_failed(self):
        return self._mimic_failed

    @mimic_failed.setter
    def mimic_failed(self, value):
        self._mimic_failed = value

    @property
    def supports_dw_notify(self) -> bool:
        """True when playback APIs expect the DNS 16+ dwNotify parameter.

        DNS 16+ includes dwNotify on PlayString/PlayEvents.
        DNS 15 does not — the IDL and TLB include it but Dragon 15 ignores it.
        We detect the actual Dragon version to decide whether to pass it.
        """
        major = self._dragon_version[0] if self._dragon_version[0] > 0 else self._detected_major
        return major >= 16

    def get_current_user(self) -> Tuple[str, str]:
        """Get current Dragon user as (name, directory).

        Matches C++ CDragonCode::getCurrentUser:
          1. ISRSpeakerW::Query for speaker name
             - E_BUFFERTOOSMALL → retry with larger buffer
             - SRERR_NOUSERSELECTED → return ("", "")
          2. IDgnSRSpeakerW::GetSpeakerDirectory for user directory
             - E_BUFFERTOOSMALL → retry with larger buffer
          3. Append "\\current" to the directory path

        "first we get the name of the speaker.  If there is no speaker
        loaded we return empty strings"
        — Joel Gould, DragonCode.cpp (getCurrentUser)
        """
        # C++ does QI(ISRSpeaker) here; we use the cached interface
        sp = self._speaker
        if sp is None:
            return ("", "")

        # ISRSpeakerW::Query(wchar_t* buf, DWORD bufSizeBytes, DWORD* needed)
        buf_size = 261  # _MAX_PATH + 1
        buf = ctypes.create_unicode_buffer(buf_size)
        buf_ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ushort))
        needed = c_ulong(0)
        hr = getattr(sp, "_ISRSpeakerW__com_Query")(
            buf_ptr, buf_size * 2, byref(needed))
        if (hr & 0xFFFFFFFF) == _E_BUFFERTOOSMALL:
            buf_size = needed.value + 1
            buf = ctypes.create_unicode_buffer(buf_size)
            buf_ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ushort))
            hr = getattr(sp, "_ISRSpeakerW__com_Query")(
                buf_ptr, buf_size * 2, byref(needed))
        if (hr & 0xFFFFFFFF) == _SRERR_NOUSERSELECTED:
            return ("", "")
        if hr < 0:
            raise NatlinkCOMError("ISRSpeakerW::Query", hr=hr)
        user_name = buf.value
        if not user_name:
            return ("", "")

        # "now we get the speaker directory"
        directory = self._get_speaker_directory(user_name)
        return (user_name, directory)

    def _get_speaker_directory(self, user_name: str) -> str:
        """Get speaker directory, append \\current.

        Matches C++ getCurrentUser steps 4-6:
          QI(IDgnSRSpeaker) from ISRCentral
          GetSpeakerDirectory(user, buf, size, &needed)
          Retry on E_BUFFERTOOSMALL (dwLength = dwNeeded + 11)
          Append "\\current"

        "NatSpeak returns the base user directory, we append 'current'
        to get us to where the files are."
        — Joel Gould, DragonCode.cpp (getCurrentUser)
        """
        if self._central is None or self._tlb is None:
            return ""
        # C++ does QI(IDgnSRSpeaker) each call and releases within scope.
        # Don't use _try_qi here — it AddRef's into _raw_ptrs, which would
        # leak a raw pointer on every get_current_user() call.
        try:
            dgn_speaker = self._central.QueryInterface(self._tlb.IDgnSRSpeakerW)
        except Exception:
            log.debug("QI(IDgnSRSpeakerW) failed — directory not available")
            return ""

        try:
            # GetSpeakerDirectory(wchar_t* name, wchar_t* buf, DWORD bufSize, DWORD* needed)
            path_size = 271  # _MAX_PATH + 11
            path_buf = ctypes.create_unicode_buffer(path_size)
            path_ptr = ctypes.cast(path_buf, ctypes.POINTER(ctypes.c_ushort))
            needed = c_ulong(0)
            hr = getattr(dgn_speaker, "_IDgnSRSpeakerW__com_GetSpeakerDirectory")(
                user_name, path_ptr, path_size, byref(needed))
            if (hr & 0xFFFFFFFF) == _E_BUFFERTOOSMALL:
                path_size = needed.value + 11
                path_buf = ctypes.create_unicode_buffer(path_size)
                path_ptr = ctypes.cast(path_buf, ctypes.POINTER(ctypes.c_ushort))
                hr = getattr(dgn_speaker, "_IDgnSRSpeakerW__com_GetSpeakerDirectory")(
                    user_name, path_ptr, path_size, byref(needed))
            if hr < 0:
                log.debug("GetSpeakerDirectory failed: 0x%08X", hr & 0xFFFFFFFF)
                return ""
            return path_buf.value + "\\current"
        except Exception:
            log.debug("GetSpeakerDirectory call failed", exc_info=True)
            return ""

    def create_voice_dict(self):
        """Get IVoiceDictation0W via QueryService(DgnVDct).

        Returns a comtypes IVoiceDictation0W wrapper. Each call returns
        the same underlying Dragon dictation object (there's only one per service).
        """
        if not self._psp_raw:
            raise NatlinkCOMError("create_voice_dict",
                                  error_message="Not connected (no IServiceProvider)")
        iid_vdict = self._tlb.IVoiceDictation0W._iid_
        # Build a ctypes GUID from comtypes IID
        iid_raw = GUID(iid_vdict.Data1, iid_vdict.Data2, iid_vdict.Data3,
                        list(iid_vdict.Data4))
        hr, pvdict = call_query_service(self._psp_raw, GUID_DgnVDct, iid_raw)
        if hr < 0:
            raise NatlinkCOMError("QueryService(DgnVDct, IVoiceDictation0W)", hr=hr)
        vdict = wrap_comtypes(pvdict, self._tlb.IVoiceDictation0W)
        release_raw(pvdict)
        log.debug("Got IVoiceDictation0W via DgnVDct service")
        return vdict
