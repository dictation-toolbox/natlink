"""User management and training operations."""

import ctypes
import logging
from typing import List, Optional, Tuple

from ._com_helpers import cotaskmem_free
from ._errors import (NatlinkCOMError,
                      ERR_INVALID_WORD,
                      ERR_OUT_OF_RANGE,
                      ERR_UNKNOWN_NAME,
                      ERR_USER_EXISTS)

log = logging.getLogger("natlink.com")

from ._dspeech_constants import (
    DGNTRNMODE_NORMAL, DGNTRNMODE_CALIBRATE, DGNTRNMODE_CROSSWORD,
    DGNTRNMODE_BATCHWORD, DGNTRNMODE_SINGLESET, DGNTRNMODE_SHORTBATCH,
    DGNERR_INVALIDMODE as _DGNERR_INVALIDMODE,
    DGNERR_ALREADYACTIVE as _DGNERR_ALREADYACTIVE,
    DGNERR_MODENOTACTIVE as _DGNERR_MODENOTACTIVE,
)

_TRAINING_MODE_TO_STR = {
    DGNTRNMODE_NORMAL: "",
    DGNTRNMODE_CALIBRATE: "calibrate",
    DGNTRNMODE_CROSSWORD: "longtrain",
    DGNTRNMODE_BATCHWORD: "batchadapt",
    DGNTRNMODE_SINGLESET: "",  # C++: same as NORMAL — returns Py_None
    DGNTRNMODE_SHORTBATCH: "shorttrain",
}
_TRAINING_STR_TO_MODE = {
    "calibrate": DGNTRNMODE_CALIBRATE,
    "shorttrain": DGNTRNMODE_SHORTBATCH,
    "longtrain": DGNTRNMODE_CROSSWORD,
    "batchadapt": DGNTRNMODE_BATCHWORD,
}


def get_current_user(conn) -> Tuple[str, str]:
    """Get current Dragon user as (name, directory).

    Raises NatlinkCOMError if speaker interface is unavailable
    (matching C++ RETURNIFERROR behavior).  Returns ("","") only
    for SRERR_NOUSERSELECTED (no user loaded).
    """
    if conn.speaker is None:
        raise NatlinkCOMError("get_current_user",
                              error_message="No speaker interface")
    return conn.get_current_user()


def get_all_users(conn) -> List[str]:
    """Get list of all Dragon user profiles.

    ISRSpeakerW::Enum([out, size_is(,*p1/2)] wchar_t** p0, [in,out] DWORD* p1)

    Uses the comtypes __com_ raw method.  The [out, size_is(,*p1/2)]
    double-pointer pattern requires exact ctypes types that match the
    generated wrapper: LP_LP_c_ushort for the server-allocated buffer.
    """
    sp = conn.speaker
    if sp is None:
        raise NatlinkCOMError("get_all_users", error_message="No speaker interface")
    LP_c_ushort = ctypes.POINTER(ctypes.c_ushort)
    names_ptr = LP_c_ushort()
    count = ctypes.c_ulong(0)
    hr = getattr(sp, "_ISRSpeakerW__com_Enum")(
        ctypes.pointer(names_ptr), ctypes.byref(count))
    if hr < 0:
        raise NatlinkCOMError("ISRSpeakerW::Enum", hr=hr)
    raw_addr = ctypes.cast(names_ptr, ctypes.c_void_p).value
    if not raw_addr or count.value == 0:
        return []
    try:
        # count is byte count; each WCHAR is 2 bytes
        raw = ctypes.wstring_at(raw_addr, count.value // 2)
        names = raw.rstrip("\x00").split("\x00")
        return [n for n in names if n]
    finally:
        cotaskmem_free(ctypes.c_void_p(raw_addr))


from ._speech_constants import (
    SRERR_SPEAKEREXISTS as _SRERR_SPEAKEREXISTS,
    SRERR_INVALIDPARAM as _E_INVALIDARG,
    SRERR_VALUEOUTOFRANGE as _E_UNEXPECTED,
    LEXERR_INVALIDTEXTCHAR as _LEXERR_INVALIDTEXTCHAR,
)


def select_user(conn, user: str) -> None:
    """Select a Dragon user profile.

    Matches C++ CDragonCode::openUser:
      1. Validate user exists via Enum
      2. ISRSpeakerW::Select(user, FALSE)

    "make sure the user exists"
    — Joel Gould, DragonCode.cpp (openUser)
    """
    sp = conn.speaker
    if sp is None:
        raise NatlinkCOMError("select_user", error_message="No speaker interface")
    # "make sure the user exists"
    all_users = get_all_users(conn)
    if user not in all_users:
        # C++: errUnknownName, "The user named '%s' does not exist"
        raise NatlinkCOMError("select_user", error_type=ERR_UNKNOWN_NAME,
                              error_message=f"The user named '{user}' does not exist")
    try:
        sp.Select(user, 0)  # bLock=FALSE
    except Exception as exc:
        hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
        if hr == _E_INVALIDARG:
            # C++: "The user name '%s' is invalid"
            raise NatlinkCOMError("select_user", error_type=ERR_INVALID_WORD,
                error_message=f"The user name '{user}' is invalid") from exc
        raise
    log.info("→ Select user: %s", user)


def create_user(conn, name: str, model: str = "", topic: str = "") -> None:
    """Create a new Dragon user profile.

    "The normal SAPI way of creating a user is to call ISRSpeaker::New.
    This method does not allow for a model or topic name, however.  If
    the Python client has not specified a model name then we use the
    standard SAPI function call.  This causes NatSpeak to create a
    speaker with the default model and topic."
    — Joel Gould, DragonCode.cpp (createUser)

    If model is specified, uses IDgnSRSpeakerW::New(name, model).
    If topic is specified, also calls IDgnSRTopic2W::New(name, topic, topic).

    "This call lets you specify the base topic to use and the topic
    name to use.  We make the topic name the same as the base topic.
    This matches the behavior of the NatSpeak new user wizard."
    — Joel Gould, DragonCode.cpp (createUser)
    """
    central = conn.central
    if central is None:
        raise NatlinkCOMError("create_user", error_message="Not connected")
    tlb = conn.tlb

    try:
        if not model:
            # Standard SAPI path — default model and topic
            sp = conn.speaker
            if sp is None:
                raise NatlinkCOMError("create_user", error_message="No speaker interface")
            sp.New(name)
        else:
            # Dragon-specific path — custom base model
            dgn_speaker = central.QueryInterface(tlb.IDgnSRSpeakerW)
            dgn_speaker.New(name, model)
    except NatlinkCOMError:
        raise
    except Exception as exc:
        hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
        if hr == _E_INVALIDARG:
            # C++: "The user name '%s' is invalid"
            raise NatlinkCOMError("create_user", error_type=ERR_INVALID_WORD,
                error_message=f"The user name '{name}' is invalid") from exc
        if hr == _SRERR_SPEAKEREXISTS:
            # C++: "A user names '%s' already exists" (sic — typo in original)
            raise NatlinkCOMError("create_user", error_type=ERR_USER_EXISTS,
                error_message=f"A user named '{name}' already exists") from exc
        if hr == _E_UNEXPECTED:
            # C++: "The base model '%s' does not exist"
            raise NatlinkCOMError("create_user", error_type=ERR_OUT_OF_RANGE,
                error_message=f"The base model '{model}' does not exist") from exc
        raise

    if topic:
        # C++: "Now if a topic has been specified, we create that topic.
        # Otherwise we do not explicitly create a topic and count on the
        # fact that NatSpeak will create a default topic when the user
        # is opened."
        try:
            dgn_topic = central.QueryInterface(tlb.IDgnSRTopic2W)
            # "We make the topic name the same as the base topic.
            # This matches the behavior of the NatSpeak new user wizard"
            dgn_topic.New(name, topic, topic)
        except NatlinkCOMError:
            raise
        except Exception as exc:
            hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
            if hr == _E_UNEXPECTED:
                # C++: "The base topic '%s' does not exist"
                raise NatlinkCOMError("create_user", error_type=ERR_OUT_OF_RANGE,
                    error_message=f"The base topic '{topic}' does not exist") from exc
            raise

    log.debug("Created user: %s (model=%r, topic=%r)", name, model, topic)


def save_speaker(conn) -> None:
    """Save the current Dragon user profile.

    IDgnSREngineControlW::SaveSpeaker(BOOL bBackup)
    """
    ctl = conn.engine_ctl
    if ctl is None:
        raise NatlinkCOMError("save_speaker", error_message="No engine control")
    ctl.SaveSpeaker(False)
    log.debug("SaveSpeaker OK")


def get_changed_info(conn) -> Tuple[bool, int]:
    """Get Dragon's dirty state and changed-info flags."""
    ctl = conn.engine_ctl
    if ctl is None:
        raise NatlinkCOMError("get_changed_info",
                              error_message="No engine control")
    changed, flags = ctl.GetChangedInfo()
    return bool(changed), int(flags)


def preinitialize(conn) -> None:
    """Call Dragon's engine preinitialization hook."""
    ctl = conn.engine_ctl
    if ctl is None:
        raise NatlinkCOMError("preinitialize", error_message="No engine control")
    ctl.Preinitialize()
    log.debug("Preinitialize OK")


def rename_speaker(conn, old_name: str, new_name: str) -> None:
    """Rename a Dragon speaker profile."""
    ctl = conn.engine_ctl
    if ctl is None:
        raise NatlinkCOMError("rename_speaker",
                              error_message="No engine control")
    ctl.SpeakerRename(old_name, new_name)
    log.debug("SpeakerRename(%r -> %r) OK", old_name, new_name)


def get_base_models(conn) -> List[str]:
    """Enumerate Dragon base speaker models."""
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        raise NatlinkCOMError("get_base_models", error_message="Not connected")
    try:
        dgn_speaker = central.QueryInterface(tlb.IDgnSRSpeakerW)
    except Exception as exc:
        raise NatlinkCOMError("get_base_models",
                              error_message="No IDgnSRSpeakerW interface") from exc

    LP_c_ushort = ctypes.POINTER(ctypes.c_ushort)
    names_ptr = LP_c_ushort()
    count = ctypes.c_ulong(0)
    hr = getattr(dgn_speaker, "_IDgnSRSpeakerW__com_EnumBaseModels")(
        ctypes.pointer(names_ptr), ctypes.byref(count))
    if hr < 0:
        raise NatlinkCOMError("IDgnSRSpeakerW::EnumBaseModels", hr=hr)
    raw_addr = ctypes.cast(names_ptr, ctypes.c_void_p).value
    if not raw_addr or count.value == 0:
        return []
    try:
        raw = ctypes.wstring_at(raw_addr, count.value // 2)
        names = raw.rstrip("\x00").split("\x00")
        return [n for n in names if n]
    finally:
        cotaskmem_free(ctypes.c_void_p(raw_addr))


def speaker_copy(conn, src_speaker: str, dst_speaker: str) -> None:
    """Copy topic data from one speaker to another."""
    central = conn.central
    tlb = conn.tlb
    if central is None or tlb is None:
        raise NatlinkCOMError("speaker_copy", error_message="Not connected")
    try:
        dgn_topic = central.QueryInterface(tlb.IDgnSRTopic2W)
    except Exception as exc:
        raise NatlinkCOMError("speaker_copy",
                              error_message="No IDgnSRTopic2W interface") from exc
    dgn_topic.SpeakerCopy(src_speaker, dst_speaker)
    log.debug("SpeakerCopy(%r -> %r) OK", src_speaker, dst_speaker)


def get_user_training(conn) -> Optional[str]:
    """Get user training status.

    Returns None (no training), "calibrate", or "trained".
    """
    trn = conn.training
    if trn is None:
        raise NatlinkCOMError("get_user_training",
                              error_message="No training interface")
    calibrate, batch_count, speech_length = trn.TotalCountGet()
    if not calibrate:
        return None
    elif batch_count == 0:
        return "calibrate"
    else:
        return "trained"


def get_training_mode(conn) -> Tuple[str, int]:
    """Get current training mode.

    Returns (modeString, speechLength). modeString is "" if no training active.
    """
    trn = conn.training
    if trn is None:
        raise NatlinkCOMError("get_training_mode",
                              error_message="No training interface")
    mode, speech_length, _num_calls = trn.TrainingModeGet()
    # C++ default case: assert(FALSE) + return ("error", speechLength)
    mode_str = _TRAINING_MODE_TO_STR.get(mode, "error")
    return (mode_str, speech_length)


# Training error HRESULTs — imported above from _dspeech_constants.


def start_training_mode(conn, mode: str) -> None:
    """Start a training session.

    Matches C++ CDragonCode::startTraining:
      1. Decode mode string (case-insensitive)
      2. TrainingModeSet(mode)
      3. Check DGNERR_INVALIDMODE, DGNERR_ALREADYACTIVE
    """
    trn = conn.training
    if trn is None:
        raise NatlinkCOMError("start_training_mode",
                              error_message="No training interface")
    mode_code = _TRAINING_STR_TO_MODE.get(mode.lower())
    if mode_code is None:
        # C++: "Invalid parameter (calling startTraining)"
        raise NatlinkCOMError("start_training_mode",
                              error_message="Invalid parameter "
                              "(calling startTraining)")
    try:
        trn.TrainingModeSet(mode_code)
    except Exception as exc:
        hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
        if hr == _DGNERR_INVALIDMODE:
            # C++: "Training mode %s is not valid at this time for the current user"
            raise NatlinkCOMError("start_training_mode",
                error_message=f"Training mode {mode} is not valid at this "
                              f"time for the current user") from exc
        if hr == _DGNERR_ALREADYACTIVE:
            # C++: "A special training mode is already active"
            raise NatlinkCOMError("start_training_mode",
                error_message="A special training mode is already active") from exc
        raise
    conn._training_active = True


def finish_training(conn, process: bool = True) -> None:
    """Finish training. If process=True, perform training; else cancel.

    Matches C++ CDragonCode::finishTraining:
      bNoCancel=TRUE  → TrainingPerform()
      bNoCancel=FALSE → TrainingCancel()
      DGNERR_MODENOTACTIVE → "A special training mode is not active"
    """
    trn = conn.training
    if trn is None:
        raise NatlinkCOMError("finish_training",
                              error_message="No training interface")
    conn._training_active = False
    try:
        if process:
            trn.TrainingPerform()
        else:
            trn.TrainingCancel()
    except Exception as exc:
        hr = getattr(exc, 'hresult', 0) & 0xFFFFFFFF
        if hr == _DGNERR_MODENOTACTIVE:
            # C++: "A special training mode is not active (calling finishTraining)"
            raise NatlinkCOMError("finish_training",
                error_message="A special training mode is not active "
                              "(calling finishTraining)") from exc
        raise
