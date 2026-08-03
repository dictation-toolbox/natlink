"""_legacy.py - No-op stubs for removed natlink APIs.

These functions exist solely so existing code (natlinkcore, third-party
grammars) that calls them doesn't raise AttributeError.  Each stub
silently accepts its original arguments and does nothing.

The import in __init__.py re-exports them under their original names.
"""

import logging
from typing import Callable, Optional


def setMessageWindow(callback: Optional[Callable] = None, flags: int = 0) -> None:
    """Enable, disable, or update natlink's message window.

    In the original C extension, this controlled a Win32 message window
    with File>Reload and File>Exit menu items. In the current out-of-process
    architecture, the output window is managed by the UI provider and this
    function is accepted for backwards compatibility only.

    Args:
        callback: A function accepting one parameter (the event type:
            ``idd_reload`` or ``idd_exit``), or ``None`` to disable.
        flags: Optional combination of:

            - ``0x01`` — enable the File>Exit menu item
            - ``0x02`` — disable the File>Reload menu item
            - ``0x04`` — disable the menu entirely
    """


def setTrayIcon(iconName: str = "", toolTip: str = "",
                callback: Optional[Callable] = None) -> None:
    """Draw an icon in the taskbar tray (accepted, not currently drawn).

    In the original C extension (DragonCode.cpp:3575) this added an icon to
    the notification area. natlink's tray is now owned by the UI provider,
    which exposes no per-grammar icon slot, so this is accepted and ignored
    rather than raising AttributeError — unimacro's ``_repeat`` repeating
    mode, its tray-icon grammars and the natlinkcore ``_mouse`` sample all
    call it unconditionally and would otherwise crash.

    Args:
        iconName: Absolute path to a ``.ico`` file, or one of the predefined
            names (``right``, ``left``, ``up``, ``down``, ``nodir``), or
            ``""`` to remove the icon.
        toolTip: Tooltip text shown when hovering the icon.
        callback: Called when the user clicks the icon.
    """


def displayText(text: str, isError: bool = False, logText: bool = True) -> None:
    """Append a message to the natlink output window.

    In the original C extension, this displayed text in a dedicated Win32
    window (red for errors, black for normal text).  Routes through
    notify_text so all registered UI providers receive the text.

    Args:
        text: The text to display.
        isError: If True, treat as error output.
        logText: If True, also copy the text to the Dragon log file
            (not implemented in this shim).
    """
    try:
        from ._ui_protocol import notify_text
        notify_text(text, level=logging.ERROR if isError else logging.INFO)
    except Exception:
        import sys
        stream = sys.__stderr__ if isError else sys.__stdout__
        if stream is not None:
            stream.write(text)
