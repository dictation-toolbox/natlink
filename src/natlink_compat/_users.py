"""_users.py - Dragon user profile management functions."""

from typing import List, Optional

from ._helpers import _require_connected, com_call
from ._state import _state


def getAllUsers() -> List[str]:
    """Return a list of the names of all existing Dragon user profiles."""
    _require_connected()
    return com_call("getAllUsers", _state.backend.get_all_users)


def createUser(userName: str, baseModel: str = "",
               baseTopic: str = "") -> None:
    """Create a new Dragon user (speaker profile).

    Creating a user does not open it — call openUser separately.

    Args:
        userName: Name for the new user.
        baseModel: Optional base model name (e.g. ``"BestMatch Model"``).
            If empty, the default base model is used.
        baseTopic: Optional base topic name (e.g.
            ``"General English - BestMatch"``). If empty, the default is used.

    Raises:
        InvalidWord: If the user name is invalid.
        UserExists: If the user already exists.
        OutOfRange: If the baseModel or baseTopic does not exist.
    """
    _require_connected()
    com_call("createUser", _state.backend.create_user,
                userName, baseModel, baseTopic)


def openUser(userName: str) -> None:
    """Open a specified Dragon user for recognition.

    Raises:
        UnknownName: If the user does not exist.
    """
    _require_connected()
    com_call("openUser", _state.backend.select_user, userName)


def saveUser() -> None:
    """Save any modifications made to the currently open Dragon user to disk."""
    _require_connected()
    com_call("saveUser", _state.backend.save_speaker)


def getUserTraining() -> Optional[str]:
    """Return the training status for the current user.

    Returns:
        - ``None`` — no training has been done
        - ``"calibrate"`` — only calibration was done
        - ``"trained"`` — the user has been fully trained
    """
    _require_connected()
    result = com_call("getUserTraining", _state.backend.get_user_training)
    return result if result else None


# --- Training mode ---

def getTrainingMode():
    """Return the current special training mode.

    Returns ``None`` if no special training mode is active, otherwise a
    tuple of (mode, milliseconds) where mode is one of ``'calibrate'``,
    ``'shorttrain'``, ``'longtrain'``, or ``'batchadapt'``, and milliseconds
    is the total speech accepted for training so far.
    """
    _require_connected()
    mode, speech_length = com_call("getTrainingMode", _state.backend.get_training_mode)
    if not mode:
        return None
    return (mode, speech_length)


def startTraining(mode: str) -> None:
    """Initiate a special training mode.

    Training workflow: call startTraining, then call ResObj.correction for
    a series of results, then call finishTraining.

    Args:
        mode: One of:

            - ``'calibrate'`` — initial calibration (5-10 utterances, new users only)
            - ``'shorttrain'`` — short training (3+ min speech, BestMatch III)
            - ``'longtrain'`` — long training (18+ min speech, normal models)
            - ``'batchadapt'`` — batch adaptation (can be repeated any time)

    Raises:
        WrongState: If the mode is not valid for the current training state
            (e.g. calibrate on an already-calibrated user).
        ValueError: If mode is not one of the accepted strings.
    """
    _require_connected()
    com_call("startTraining", _state.backend.start_training_mode, mode)


def finishTraining(bProcess: int = 1) -> None:
    """Terminate a special training mode.

    Args:
        bProcess: If 1 (default), perform the actual training operation
            (may take a while). If 0, cancel training without processing.

    Raises:
        WrongState: If no special training mode is active.
    """
    _require_connected()
    com_call("finishTraining", _state.backend.finish_training, bool(bProcess))
