"""SendInput-based keystroke injection for DNS 13 on Windows 10/11.

Dragon 13 uses WH_JOURNALPLAYBACK hooks which Windows 10 1607+ blocks.
This module bypasses Dragon's playback and injects keystrokes directly
via Win32 SendInput, inspired by dtactions/vocola_sendkeys.

Only used as a fallback when Dragon's PlayString/PlayEvents fail.
DNS 16 handles this internally and does not need this module.
"""

import ctypes
import ctypes.wintypes
import logging
import re
import time

from . import _uipi

log = logging.getLogger("natlink.com.sendinput")

user32 = ctypes.windll.user32

# Private handle so GetLastError is readable: the shared ctypes.windll.user32
# is not created with use_last_error, and any intervening call can clobber the
# thread's error code before it is read back.
_user32_err = ctypes.WinDLL("user32", use_last_error=True)
_user32_err.SendInput.restype = ctypes.c_uint
_ERROR_ACCESS_DENIED = 5

user32.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]
user32.MapVirtualKeyW.restype = ctypes.c_uint
user32.VkKeyScanW.argtypes = [ctypes.c_wchar]
user32.VkKeyScanW.restype = ctypes.c_short

# --------------------------------------------------------------------------
# Win32 SendInput structures
# --------------------------------------------------------------------------

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]
    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]


def _last_error():
    """Thread's last Win32 error.

    Indirected so tests can simulate a failure without patching
    ``ctypes.get_last_error`` itself -- that is process-global and is the same
    call the connection mutex uses to detect ERROR_ALREADY_EXISTS, so faking
    it corrupts unrelated code running on other threads.
    """
    return ctypes.get_last_error()


def _send_inputs(inputs, operation="SendInput"):
    """Call Win32 SendInput with a list of INPUT structs.

    Two distinct failures hide here, and neither is visible from the return
    value alone:

    UIPI refusing the injection outright shows up as a short count with
    ERROR_ACCESS_DENIED, which the old code reported as a bare "sent 0/4"
    with no reason. GetLastError needs a private WinDLL -- the shared
    ``ctypes.windll.user32`` is not created with use_last_error, so the code
    read back from it is not trustworthy.

    An elevated foreground window is worse: SendInput accepts every event and
    sets no error while the keystrokes go nowhere useful. Only comparing
    integrity levels detects that, so it is checked before injecting.
    """
    n = len(inputs)
    if n == 0:
        return
    _uipi.warn_if_foreground_outranks_us(operation)

    arr = (INPUT * n)(*inputs)
    ctypes.set_last_error(0)
    sent = _user32_err.SendInput(n, ctypes.cast(arr, ctypes.c_void_p),
                                 ctypes.sizeof(INPUT))
    if sent == n:
        return

    err = _last_error()
    if err == _ERROR_ACCESS_DENIED:
        log.warning(
            "%s: Windows refused the injection (%d/%d events) -- the target "
            "runs at a higher integrity level than natlink. Run natlink "
            "elevated to send keys to elevated applications.",
            operation, sent, n)
    else:
        log.warning("%s: sent %d/%d events (error %d)", operation, sent, n, err)


def _vk_input(vk, down=True, extended=False):
    """Create a keyboard INPUT for a virtual key."""
    flags = 0
    if not down:
        flags |= KEYEVENTF_KEYUP
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY
    scan = user32.MapVirtualKeyW(vk, 0) & 0xFF
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = flags
    return inp


def _unicode_input(char, down=True):
    """Create a keyboard INPUT for a Unicode character."""
    flags = KEYEVENTF_UNICODE
    if not down:
        flags |= KEYEVENTF_KEYUP
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = 0
    inp.union.ki.wScan = ord(char)
    inp.union.ki.dwFlags = flags
    return inp


# --------------------------------------------------------------------------
# Virtual key codes
# --------------------------------------------------------------------------

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_NUMLOCK = 0x90

# Keys that need KEYEVENTF_EXTENDEDKEY
_EXTENDED_VKS = {
    0x21, 0x22, 0x23, 0x24,  # pgup, pgdn, end, home
    0x25, 0x26, 0x27, 0x28,  # left, up, right, down
    0x2D, 0x2E,              # insert, delete
    0x5B, 0x5C,              # lwin, rwin
    0x5D,                     # apps
    0xA0, 0xA1,              # lshift, rshift (when needed)
    0xA2, 0xA3,              # lcontrol, rcontrol
    0xA4, 0xA5,              # lmenu, rmenu
}

# Dragon key name -> (virtual key code, is_extended)
_KEY_NAMES = {
    # Modifiers
    "shift": (VK_SHIFT, False),
    "ctrl": (VK_CONTROL, False),
    "alt": (VK_MENU, False),
    "win": (VK_LWIN, True),
    # Navigation
    "up": (0x26, True), "down": (0x28, True),
    "left": (0x25, True), "right": (0x27, True),
    "home": (0x24, True), "end": (0x23, True),
    "pgup": (0x21, True), "pgdn": (0x22, True),
    # Editing
    "enter": (0x0D, False), "tab": (0x09, False),
    "space": (0x20, False), "backspace": (0x08, False),
    "delete": (0x2E, True), "del": (0x2E, True),
    "insert": (0x2D, True), "ins": (0x2D, True),
    "escape": (0x1B, False), "esc": (0x1B, False),
    # Function keys
    **{f"f{i}": (0x70 + i - 1, False) for i in range(1, 25)},
    # Numpad
    **{f"numkey{i}": (0x60 + i, False) for i in range(10)},
    "numkeyenter": (0x0D, False),  # same VK as Enter
    "numkeyplus": (0x6B, False), "numkeyminus": (0x6D, False),
    "numkeytimes": (0x6A, False), "numkeydivide": (0x6F, False),
    "numkeyperiod": (0x6E, False),
    # Lock keys
    "capslock": (0x14, False), "numlock": (0x90, False),
    "scrolllock": (0x91, False),
    # Special
    "printscreen": (0x2C, False), "prtsc": (0x2C, False),
    "pause": (0x13, False), "break": (0x13, False),
    "apps": (0x5D, True),
    # Extended left/right variants
    "lshift": (0xA0, False), "rshift": (0xA1, False),
    "lctrl": (0xA2, False), "rctrl": (0xA3, True),
    "lalt": (0xA4, False), "ralt": (0xA5, True),
}

# Add a-z, 0-9
for c in "abcdefghijklmnopqrstuvwxyz":
    _KEY_NAMES[c] = (ord(c.upper()), False)
for c in "0123456789":
    _KEY_NAMES[c] = (ord(c), False)


# --------------------------------------------------------------------------
# Dragon key string parser
# --------------------------------------------------------------------------

# Regex: {modifier+...+key_count} or plain text
_CHORD_RE = re.compile(
    r"\{([^}]+)\}"   # braced key spec
    r"|([^{]+)"      # plain text
)


def _parse_key_spec(spec):
    """Parse a braced key spec like 'ctrl+shift+a_5' into (modifiers, key, count)."""
    parts = spec.lower().split("+")
    count = 1
    # Check for _N suffix on last part
    last = parts[-1]
    m = re.match(r"^(.+?)_(\d+)$", last)
    if m:
        parts[-1] = m.group(1)
        count = int(m.group(2))

    modifiers = []
    key_name = None
    for p in parts:
        p = p.strip()
        if p in ("shift", "ctrl", "alt", "win", "lshift", "rshift",
                 "lctrl", "rctrl", "lalt", "ralt"):
            modifiers.append(p)
        else:
            key_name = p
    return modifiers, key_name, count


def _type_char(char):
    """Generate INPUT events to type a single character."""
    # Try VkKeyScan first for keyboard-layout-aware typing
    result = user32.VkKeyScanW(char)
    if result != -1:
        vk = result & 0xFF
        shift_state = (result >> 8) & 0xFF
        inputs = []
        if shift_state & 1:
            inputs.append(_vk_input(VK_SHIFT, down=True))
        if shift_state & 2:
            inputs.append(_vk_input(VK_CONTROL, down=True))
        if shift_state & 4:
            inputs.append(_vk_input(VK_MENU, down=True))
        inputs.append(_vk_input(vk, down=True))
        inputs.append(_vk_input(vk, down=False))
        if shift_state & 4:
            inputs.append(_vk_input(VK_MENU, down=False))
        if shift_state & 2:
            inputs.append(_vk_input(VK_CONTROL, down=False))
        if shift_state & 1:
            inputs.append(_vk_input(VK_SHIFT, down=False))
        return inputs
    # Fallback: Unicode SendInput
    return [_unicode_input(char, down=True), _unicode_input(char, down=False)]


def send_dragon_keys(specification):
    """Send keystrokes using Dragon key string syntax via SendInput.

    Parses Dragon-style key specifications:
      "hello"           -> types h, e, l, l, o
      "{Enter}"         -> presses Enter
      "{Ctrl+a}"        -> Ctrl+A
      "{Shift+Left_10}" -> Shift held, Left arrow 10 times
      "abc{Tab}def"     -> types abc, Tab, def
    """
    inputs = []
    for m in _CHORD_RE.finditer(specification):
        braced, plain = m.group(1), m.group(2)
        if plain is not None:
            for char in plain:
                inputs.extend(_type_char(char))
        elif braced is not None:
            modifiers, key_name, count = _parse_key_spec(braced)
            # Press modifiers
            mod_inputs = []
            for mod in modifiers:
                vk, ext = _KEY_NAMES[mod]
                mod_inputs.append(_vk_input(vk, down=True, extended=ext))
            inputs.extend(mod_inputs)
            # Press key N times
            if key_name:
                if key_name in _KEY_NAMES:
                    vk, ext = _KEY_NAMES[key_name]
                    for _ in range(count):
                        inputs.append(_vk_input(vk, down=True, extended=ext))
                        inputs.append(_vk_input(vk, down=False, extended=ext))
                elif len(key_name) == 1:
                    for _ in range(count):
                        inputs.extend(_type_char(key_name))
                else:
                    log.warning("Unknown key name: %s", key_name)
            # Release modifiers (reverse order)
            for mod in reversed(modifiers):
                vk, ext = _KEY_NAMES[mod]
                inputs.append(_vk_input(vk, down=False, extended=ext))

    if inputs:
        _send_inputs(inputs, "playString")
        log.debug("SendInput: %d events for %d chars", len(inputs), len(specification))


def send_events(event_buffer):
    """Send HOOK_EVENTMSG events via SendInput.

    event_buffer: bytes, packed as 3-DWORD structs (message, paramL, paramH).
    Converts WM_KEYDOWN/WM_KEYUP to SendInput keyboard events.
    """
    import struct
    WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
    WM_SYSKEYDOWN, WM_SYSKEYUP = 0x104, 0x105

    inputs = []
    event_size = 12  # 3 DWORDs
    for offset in range(0, len(event_buffer), event_size):
        msg, paramL, paramH = struct.unpack_from('<III', event_buffer, offset)
        vk = paramL & 0xFF
        extended = vk in _EXTENDED_VKS
        if msg in (WM_KEYDOWN, WM_SYSKEYDOWN):
            inputs.append(_vk_input(vk, down=True, extended=extended))
        elif msg in (WM_KEYUP, WM_SYSKEYUP):
            inputs.append(_vk_input(vk, down=False, extended=extended))

    if inputs:
        _send_inputs(inputs, "playEvents")
        log.debug("SendInput: %d events from %d-byte buffer",
                  len(inputs), len(event_buffer))
