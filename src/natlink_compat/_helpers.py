"""_helpers.py - Shared precondition checks used across natlink_compat modules."""

from ._state import _state
from ._exceptions import NatError, WrongState, com_call


def _require_connected():
    """Raise WrongState if not connected."""
    if _state.backend is None:
        raise WrongState("natlink is not connected — call natConnect() first")


def _require_not_during_init(func_name):
    """Raise NatError if called during initialization.

    Matches C++ NOTDURING_INIT macro:
    "Calling %s is not allowed during initialization"
    — Joel Gould, DragonCode.cpp
    """
    if _state.during_init:
        raise NatError(
            f"Calling {func_name} is not allowed during initialization")


def _require_not_paused(func_name):
    """Raise NatError if called from inside a Paused (begin) callback.

    Matches C++ NOTDURING_PAUSED macro:
    "Calling %s is not allowed from gotBegin callback"
    — Joel Gould, DragonCode.cpp

    These functions cannot be called from beginCallback because Dragon's
    recognition loop is paused and COM calls would deadlock.

    resultsCallback is safe because it runs deferred on the main thread
    (after the Dragon RPC has returned).
    """
    if _state.during_paused:
        raise NatError(
            f"Calling {func_name} is not allowed from gotBegin callback")
