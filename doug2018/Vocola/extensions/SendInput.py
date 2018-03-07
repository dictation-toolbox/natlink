### 
### Interface to Microsoft Windows SendInput function using ctypes
### (requires Python 2.5+)
### 
###     This code allows sending an arbitrary sequence of raw input
### events via the SendInput call.  Determining the correct sequence
### of raw input events to produce a desired result based on the
### current keyboard layout and key state is the responsibility of the
### caller.
### 
### 
### Author:  Mark Lillibridge
### Version: 0.6
### 

from ctypes import *
import win32con


## 
## SendInput function:
## 
##   Synthesizes keystrokes, mouse motions, and button clicks.
## 
##       Events is a list of objects that support a to_input() method
##   that returns an Input.  Events can be created directly from the
##   raw data structures ({Mouse,Keyboard,Hardware}Input) or using
##   event-creation convenience functions.
## 
##       Can be blocked by other threads (e.g., BlockInput) or UIPI
##   (applications are not permitted to inject input into applications
##   at a higher integrity level).  The latter causes silent failure.
## 
##       These events are not interspersed with other keyboard or mouse
##   input events inserted either by the user (with the keyboard or
##   mouse) or by calls to keybd_event, mouse_event, or other calls to
##   SendInput.
##
##       This function does not reset the keyboard's current state. Any
##   keys that are already pressed when the function is called might
##   interfere with the events that this function generates. To avoid
##   this problem, check the keyboard's state with the GetAsyncKeyState
##   function and correct as necessary.
## 

def send_input(events):
    inputs = [e.to_input() for e in events]
    input = (Input * len(events))(*inputs)
    inserted = windll.user32.SendInput(len(input), byref(input), sizeof(Input))
    if inserted != len(events):
        raise ValueError("windll.user32.SendInput: " + FormatMessage())


## 
## The raw INPUT data structure used to pass events to SendInput.
## 

DWORD     = c_ulong          # 32 bits
LONG      = c_long           # 32 bits
ULONG     = c_ulong          # 32 bits 
ULONG_PTR = POINTER(ULONG)
WORD      = c_ushort         # 16 bits

class MouseInput(Structure):
    _fields_ = [('dx',          LONG),
                ('dy',          LONG),
                ('mouseData',   DWORD),
                ('dwFlags',     DWORD),
                ('time',        DWORD),
                ('dwExtraInfo', ULONG_PTR)]
    def to_input(self):
        return Input(win32con.INPUT_MOUSE, _EventUnion(mi=self))

class KeyboardInput(Structure):
    _fields_ = [('wVk',         WORD),
                ('wScan',       WORD),
                ('dwFlags',     DWORD),
                ('time',        DWORD),
                ('dwExtraInfo', ULONG_PTR)]
    def to_input(self):
        return Input(win32con.INPUT_KEYBOARD, _EventUnion(ki=self))

class HardwareInput(Structure):
    _fields_ = [('uMsg',    DWORD),
                ('wParamL', WORD),
                ('wParamH', WORD)]
    def to_input(self):
        return Input(win32con.INPUT_HARDWARE, _EventUnion(hi=self))

class _EventUnion(Union):
    _fields_ = [('mi', MouseInput),
                ('ki', KeyboardInput),
                ('hi', HardwareInput)]

class Input(Structure):
    _fields_ = [('type', DWORD),
                ('Union', _EventUnion)]
    def to_input(self):
        return self



### 
### Keyboard events:
### 

## 
## All defined virtual-key codes; from:
## 
##   http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
## 

# Modifiers:

VK_SHIFT               = 0x10  # SHIFT key
VK_CONTROL             = 0x11  # CTRL key
VK_MENU                = 0x12  # ALT key

VK_LSHIFT              = 0xA0  # Left  SHIFT key
VK_RSHIFT              = 0xA1  # Right SHIFT key
VK_LCONTROL            = 0xA2  # Left  CONTROL key
VK_RCONTROL            = 0xA3  # Right CONTROL key
VK_LMENU               = 0xA4  # Left  MENU key
VK_RMENU               = 0xA5  # Right MENU key

VK_LWIN                = 0x5B  # Left  Windows key (Natural keyboard)
VK_RWIN                = 0x5C  # Right Windows key (Natural keyboard)
VK_APPS                = 0x5D  # Applications key (Natural keyboard)

# Toggle keyboard-state keys:

VK_CAPITAL             = 0x14  # CAPS LOCK key
VK_NUMLOCK             = 0x90  # NUM LOCK key
VK_SCROLL              = 0x91  # SCROLL LOCK key

# Mouse buttons (only used to check button state using
# Get[Async]KeyState as far as I know):

VK_LBUTTON             = 0x01  # Left mouse button
VK_RBUTTON             = 0x02  # Right mouse button
VK_MBUTTON             = 0x04  # Middle mouse button (three-button mouse)
VK_XBUTTON1            = 0x05  # X1 mouse button
VK_XBUTTON2            = 0x06  # X2 mouse button

# Alphanumeric keys:

VK_0                   = 0x30  # 0 key
VK_1                   = 0x31  # 1 key
VK_2                   = 0x32  # 2 key
VK_3                   = 0x33  # 3 key
VK_4                   = 0x34  # 4 key
VK_5                   = 0x35  # 5 key
VK_6                   = 0x36  # 6 key
VK_7                   = 0x37  # 7 key
VK_8                   = 0x38  # 8 key
VK_9                   = 0x39  # 9 key

VK_A                   = 0x41  # A key
VK_B                   = 0x42  # B key
VK_C                   = 0x43  # C key
VK_D                   = 0x44  # D key
VK_E                   = 0x45  # E key
VK_F                   = 0x46  # F key
VK_G                   = 0x47  # G key
VK_H                   = 0x48  # H key
VK_I                   = 0x49  # I key
VK_J                   = 0x4A  # J key
VK_K                   = 0x4B  # K key
VK_L                   = 0x4C  # L key
VK_M                   = 0x4D  # M key
VK_N                   = 0x4E  # N key
VK_O                   = 0x4F  # O key
VK_P                   = 0x50  # P key
VK_Q                   = 0x51  # Q key
VK_R                   = 0x52  # R key
VK_S                   = 0x53  # S key
VK_T                   = 0x54  # T key
VK_U                   = 0x55  # U key
VK_V                   = 0x56  # V key
VK_W                   = 0x57  # W key
VK_X                   = 0x58  # X key
VK_Y                   = 0x59  # Y key
VK_Z                   = 0x5A  # Z key

# Function keys:

VK_F1                  = 0x70  # F1 key
VK_F2                  = 0x71  # F2 key
VK_F3                  = 0x72  # F3 key
VK_F4                  = 0x73  # F4 key
VK_F5                  = 0x74  # F5 key
VK_F6                  = 0x75  # F6 key
VK_F7                  = 0x76  # F7 key
VK_F8                  = 0x77  # F8 key
VK_F9                  = 0x78  # F9 key
VK_F10                 = 0x79  # F10 key
VK_F11                 = 0x7A  # F11 key
VK_F12                 = 0x7B  # F12 key
VK_F13                 = 0x7C  # F13 key
VK_F14                 = 0x7D  # F14 key
VK_F15                 = 0x7E  # F15 key
VK_F16                 = 0x7F  # F16 key
VK_F17                 = 0x80  # F17 key
VK_F18                 = 0x81  # F18 key
VK_F19                 = 0x82  # F19 key
VK_F20                 = 0x83  # F20 key
VK_F21                 = 0x84  # F21 key
VK_F22                 = 0x85  # F22 key
VK_F23                 = 0x86  # F23 key
VK_F24                 = 0x87  # F24 key

# Remaining codes sorted by name:

VK_ACCEPT              = 0x1E  # IME accept
VK_ADD                 = 0x6B  # Add key
VK_ATTN                = 0xF6  # Attn key
VK_BACK                = 0x08  # BACKSPACE key
VK_BROWSER_BACK        = 0xA6  # Browser Back key
VK_BROWSER_FAVORITES   = 0xAB  # Browser Favorites key
VK_BROWSER_FORWARD     = 0xA7  # Browser Forward key
VK_BROWSER_HOME        = 0xAC  # Browser Start and Home key
VK_BROWSER_REFRESH     = 0xA8  # Browser Refresh key
VK_BROWSER_SEARCH      = 0xAA  # Browser Search key
VK_BROWSER_STOP        = 0xA9  # Browser Stop key
VK_CANCEL              = 0x03  # Control-break processing
VK_CLEAR               = 0x0C  # CLEAR key (non-numlock version of numpad 5, a " ")
VK_CONVERT             = 0x1C  # IME convert
VK_CRSEL               = 0xF7  # CrSel key
VK_DECIMAL             = 0x6E  # Decimal key
VK_DELETE              = 0x2E  # DEL key
VK_DIVIDE              = 0x6F  # Divide key
VK_DOWN                = 0x28  # DOWN ARROW key
VK_END                 = 0x23  # END key
VK_EREOF               = 0xF9  # Erase EOF key
VK_ESCAPE              = 0x1B  # ESC key
VK_EXECUTE             = 0x2B  # EXECUTE key
VK_EXSEL               = 0xF8  # ExSel key
VK_FINAL               = 0x18  # IME final mode
VK_HANGUEL             = 0x15  # IME Hanguel mode (maintained for compatibility; use VK_HANGUL)
VK_HANGUL              = 0x15  # IME Hangul mode
VK_HANJA               = 0x19  # IME Hanja mode
VK_HELP                = 0x2F  # HELP key
VK_HOME                = 0x24  # HOME key
VK_INSERT              = 0x2D  # INS key
VK_JUNJA               = 0x17  # IME Junja mode
VK_KANA                = 0x15  # IME Kana mode
VK_KANJI               = 0x19  # IME Kanji mode
VK_LAUNCH_APP1         = 0xB6  # Start Application 1 key
VK_LAUNCH_APP2         = 0xB7  # Start Application 2 key
VK_LAUNCH_MAIL         = 0xB4  # Start Mail key
VK_LAUNCH_MEDIA_SELECT = 0xB5  # Select Media key
VK_LEFT                = 0x25  # LEFT ARROW key
VK_MEDIA_NEXT_TRACK    = 0xB0  # Next Track key
VK_MEDIA_PLAY_PAUSE    = 0xB3  # Play/Pause Media key
VK_MEDIA_PREV_TRACK    = 0xB1  # Previous Track key
VK_MEDIA_STOP          = 0xB2  # Stop Media key
VK_MODECHANGE          = 0x1F  # IME mode change request
VK_MULTIPLY            = 0x6A  # Multiply key
VK_NEXT                = 0x22  # PAGE DOWN key
VK_NONAME              = 0xFC  # Reserved
VK_NONCONVERT          = 0x1D  # IME nonconvert
VK_NUMPAD0             = 0x60  # Numeric keypad 0 key
VK_NUMPAD1             = 0x61  # Numeric keypad 1 key
VK_NUMPAD2             = 0x62  # Numeric keypad 2 key
VK_NUMPAD3             = 0x63  # Numeric keypad 3 key
VK_NUMPAD4             = 0x64  # Numeric keypad 4 key
VK_NUMPAD5             = 0x65  # Numeric keypad 5 key
VK_NUMPAD6             = 0x66  # Numeric keypad 6 key
VK_NUMPAD7             = 0x67  # Numeric keypad 7 key
VK_NUMPAD8             = 0x68  # Numeric keypad 8 key
VK_NUMPAD9             = 0x69  # Numeric keypad 9 key
VK_OEM_102             = 0xE2  # Either the angle bracket key or the backslash key on the RT 102-key keyboard
VK_OEM_1               = 0xBA  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the ';:' key
VK_OEM_2               = 0xBF  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '/?' key
VK_OEM_3               = 0xC0  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '`~' key
VK_OEM_4               = 0xDB  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '[{' key
VK_OEM_5               = 0xDC  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the '\|' key
VK_OEM_6               = 0xDD  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the ']}' key
VK_OEM_7               = 0xDE  # Used for miscellaneous characters; it can vary by keyboard.  For the US standard keyboard, the 'single-quote/double-quote' key
VK_OEM_8               = 0xDF  # Used for miscellaneous characters; it can vary by keyboard.
VK_OEM_CLEAR           = 0xFE  # Clear key
VK_OEM_COMMA           = 0xBC  # For any country/region, the ',' key
VK_OEM_MINUS           = 0xBD  # For any country/region, the '-' key
VK_OEM_PERIOD          = 0xBE  # For any country/region, the '.' key
VK_OEM_PLUS            = 0xBB  # For any country/region, the '+' key
VK_PA1                 = 0xFD  # PA1 key
VK_PACKET              = 0xE7  # Used to pass Unicode characters as if they were keystrokes.  The VK_PACKET key is the low word of a 32-bit Virtual Key value used for non-keyboard input methods.  For more information, see Remark in KEYBDINPUT, SendInput, WM_KEYDOWN, and WM_KEYUP.
VK_PAUSE               = 0x13  # PAUSE key
VK_PLAY                = 0xFA  # Play key
VK_PRINT               = 0x2A  # PRINT key
VK_PRIOR               = 0x21  # PAGE UP key
VK_PROCESSKEY          = 0xE5  # IME PROCESS key
VK_RETURN              = 0x0D  # ENTER key
VK_RIGHT               = 0x27  # RIGHT ARROW key
VK_SELECT              = 0x29  # SELECT key
VK_SEPARATOR           = 0x6C  # Separator key
VK_SLEEP               = 0x5F  # Computer Sleep key
VK_SNAPSHOT            = 0x2C  # PRINT SCREEN key
VK_SPACE               = 0x20  # SPACEBAR
VK_SUBTRACT            = 0x6D  # Subtract key
VK_TAB                 = 0x09  # TAB key
VK_UP                  = 0x26  # UP ARROW key
VK_VOLUME_DOWN         = 0xAE  # Volume Down key
VK_VOLUME_MUTE         = 0xAD  # Volume Mute key
VK_VOLUME_UP           = 0xAF  # Volume Up key
VK_ZOOM                = 0xFB  # Zoom key


## 
## Generalized (virtual) key codes:
## 
##     These are a new generalization of virtual key codes that allow
## distinguishing between the keys that have both a numpad and
## non-numpad version using a single code.  The relevant keys and
## their generalized key codes are:
## 
##                    non-numpad:      numpad:
##   home      key     VK_HOME      GK_NUM_HOME
##   end       key     VK_END       GK_NUM_END
##   left      key     VK_LEFT      GK_NUM_LEFT
##   right     key     VK_RIGHT     GK_NUM_RIGHT
##   up        key     VK_UP        GK_NUM_UP
##   down      key     VK_DOWN      GK_NUM_DOWN
##   page up   key     VK_PRIOR     GK_NUM_PRIOR
##   page down key     VK_NEXT      GK_NUM_NEXT
##   insert    key     VK_INSERT    GK_NUM_INSERT
##   delete    key     VK_DELETE    GK_NUM_DELETE
##   return    key     VK_RETURN    GK_NUM_RETURN
## 
## All other keys' generalized key codes are the same as their virtual
## key codes.
## 
##     Note that some software does not handle the numpad versions
## correctly in some cases due to bugs (e.g., shift left typed via the
## numpad fails to select) so it is best to stick with the non-numpad
## versions unless the application intentionally assigns them
## different meanings.
## 

USE_NUMPAD = 0x1000

GK_NUM_HOME   = VK_HOME   + USE_NUMPAD
GK_NUM_END    = VK_END    + USE_NUMPAD
GK_NUM_LEFT   = VK_LEFT   + USE_NUMPAD
GK_NUM_RIGHT  = VK_RIGHT  + USE_NUMPAD
GK_NUM_UP     = VK_UP     + USE_NUMPAD
GK_NUM_DOWN   = VK_DOWN   + USE_NUMPAD
GK_NUM_PRIOR  = VK_PRIOR  + USE_NUMPAD
GK_NUM_NEXT   = VK_NEXT   + USE_NUMPAD
GK_NUM_INSERT = VK_INSERT + USE_NUMPAD
GK_NUM_DELETE = VK_DELETE + USE_NUMPAD
GK_NUM_RETURN = VK_RETURN + USE_NUMPAD


# 
# Which virtual key codes require the extended key bit on is basically
# historical: if it wasn't on the original IBM keyboard then I think
# it needs the extended keyboard bit on.
# 
Extended_bit = {}  # Default: extended bit is not allowed
for key in [VK_HOME, VK_END, VK_NEXT, VK_PRIOR, VK_INSERT, VK_DELETE, 
            VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN]:
    # Case 1: extended bit is optional (two versions exist) but on for
    # the non-numpad version.
    Extended_bit[key] = 1

# Case 2: extended bit is optional (two versions exist) but off for
# the non-numpad version.
Extended_bit[VK_RETURN] = 2

for key in [VK_RCONTROL, VK_RMENU, VK_LWIN, VK_RWIN, VK_APPS, VK_SNAPSHOT, 
            VK_CANCEL, VK_NUMLOCK, VK_DIVIDE,  
            VK_VOLUME_DOWN, VK_VOLUME_MUTE, VK_VOLUME_UP, 
            VK_MEDIA_NEXT_TRACK, VK_MEDIA_PLAY_PAUSE, VK_MEDIA_PREV_TRACK, 
            VK_MEDIA_STOP, 
            VK_BROWSER_BACK, VK_BROWSER_FAVORITES, VK_BROWSER_FORWARD, 
            VK_BROWSER_HOME, VK_BROWSER_REFRESH, VK_BROWSER_SEARCH, 
            VK_BROWSER_STOP, 
            VK_LAUNCH_APP1, VK_LAUNCH_APP2, VK_LAUNCH_MAIL, 
            VK_LAUNCH_MEDIA_SELECT]:
    Extended_bit[key] = 3   # Case 3: extended bit is required


def unpack_generalized_key_code(generalized_key_code):
    virtual_key_code = generalized_key_code
    numpad_requested = False
    if generalized_key_code >= USE_NUMPAD:
        virtual_key_code -= USE_NUMPAD
        numpad_requested = True
    
    try:
        case = Extended_bit[virtual_key_code]
        if   case == 1: extended_bit = not numpad_requested
        elif case == 2: extended_bit =     numpad_requested
        else:           extended_bit = True   # case 3
    except KeyError:
        extended_bit = False
    
    return virtual_key_code, extended_bit
    

## 
## Obtaining scan codes from virtual key codes:
## 

HKL  = HANDLE = PVOID = c_void_p
UINT = c_uint

GetKeyboardLayout = windll.user32.GetKeyboardLayout
GetKeyboardLayout.argtypes = [DWORD]
GetKeyboardLayout.restype  = HKL

MapVirtualKey = windll.user32.MapVirtualKeyW
MapVirtualKey.argtypes = [UINT, UINT]
MapVirtualKey.restype  = UINT

MapVirtualKeyEx = windll.user32.MapVirtualKeyExW
MapVirtualKeyEx.argtypes = [UINT, UINT, HKL]
MapVirtualKeyEx.restype  = UINT


def scan_code(virtual_key_code):
    # As far as I can tell, no need to use MapVirtualKeyEx here:
    
    #layout = GetKeyboardLayout(0)
    #return MapVirtualKeyEx(virtual_key_code, 0, layout)  # MAPVK_VK_TO_VSC = 0
    
    return MapVirtualKey(virtual_key_code, 0)  # MAPVK_VK_TO_VSC = 0
    

## 
## Atomic keyboard events:
## 

def virtual_key_event(generalized_key_code, releasing=False):
    virtual_key_code, extended_bit = unpack_generalized_key_code(generalized_key_code)
    flags = 0
    if releasing:     flags |= win32con.KEYEVENTF_KEYUP
    if extended_bit:  flags |= win32con.KEYEVENTF_EXTENDEDKEY
    # For many applications, a scan code of 0 seems to work fine and
    # might be faster:
    code = scan_code(virtual_key_code)
    return KeyboardInput(virtual_key_code, code, flags)


#
# A non-keyboard input method for sending a single Unicode character.
#
#     Ignores all modifier keys, is converted to nearest ASCII
# equivalent if destination window is an ASCII window.  These input
# events are relatively recent and some applications don't handle
# these events properly or at all (e.g., the Cygwin X server).
#
# char_code is a 16-bit Unicode code point (e.g., a single UCS-2 character)
#
def Unicode_event(char_code, releasing=False):
    flags = 0x0004  # KEYEVENTF_UNICODE
    if releasing: flags |= win32con.KEYEVENTF_KEYUP
    return KeyboardInput(0, char_code, flags)
    


### 
### Mouse events:
### 

# Warning: left here means the physical left mouse button, not the
# primary mouse button.  (These differ if the user has "Switch primary
# and secondary buttons" selected.)  Ditto for right.

Mouse_buttons = { 
    "left"  : [win32con.MOUSEEVENTF_LEFTDOWN,   win32con.MOUSEEVENTF_LEFTUP,   0],
    "right" : [win32con.MOUSEEVENTF_RIGHTDOWN,  win32con.MOUSEEVENTF_RIGHTUP,  0],
    "middle": [win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP, 0],
    # XBUTTON1 = 1
    "X1"    : [win32con.MOUSEEVENTF_XDOWN,      win32con.MOUSEEVENTF_XUP,      1],
    # XBUTTON2 = 2
    "X2"    : [win32con.MOUSEEVENTF_XDOWN,      win32con.MOUSEEVENTF_XUP,      2],
    }

def mouse_button_event(button, releasing=False):
    try:
        down_flag, up_flag, mouse_data = Mouse_buttons[button]
        flags = down_flag
        if releasing: flags = up_flag
        
        return MouseInput(0, 0, mouse_data, flags, 0)
    except KeyError:
        raise ValueError("unknown mouse button: " + button)


# clicks>0 => wheel rotated forward (if horizontal false) or else rotated right
def mouse_wheel_event(horizontal, clicks):
    flags = win32con.MOUSEEVENTF_WHEEL
    if horizontal: flags = win32con.MOUSEEVENTF_HWHEEL
    amount = int(clicks * win32con.WHEEL_DELTA)
    return MouseInput(0, 0, amount, flags, 0)

# dx>0: moves right, dy>0: moves down
# absolute: 0..65535 each dim for primary monitor (virtual => entire desktop)
def mouse_move_event(x, y, absolute, virtual=False, coalesce=False):
    flags = win32con.MOUSEEVENTF_MOVE
    if not coalesce:
        flags |= win32con.MOUSEEVENTF_NOCOALESCE
    if absolute: 
        flags |= win32con.MOUSEEVENTF_ABSOLUTE
        if virtual:
            flags |= win32con.MOUSEEVENTF_VIRTUALDESK
    return MouseInput(x, y, 0, flags, 0)
