### 
### Code for parsing extended SendDragonKeys syntax into a series of
### Input events suitable for calling SendInput with.
### 
### Uses ctypes (requires Python 2.5+).
### 
### Assumes input is 8-bit Windows-1252 encoding.
### 
### 
### Author:  Mark Lillibridge
### Version: 0.7
### 

import re
import win32con

from ctypes    import *
from SendInput import *


debug = False


# ignore_unknown_names True means type out bad chords rather than
# raising a KeyError; e.g., "{bad}" sends {, b, a, d, }.
#
def senddragonkeys_to_events(input, ignore_unknown_names=True):
    chords = parse_into_chords(input)

    events = []
    for c in chords:
        try:
            events += chord_to_events(c)
        except LookupError as e:
            if not ignore_unknown_names: 
                raise
            if not c[0] and not c[2] and len(c[1])==1:
                raise  # already a single key chord
            characters = c[3]
            if debug:
                print(("typing out bad chord: " + characters + ": " + repr(e)))
            for char in characters:
                events += chord_to_events([None, char, None, char])

    return events

    

### 
### Break SendDragonKeys input into the chords that make it up.  Each
### chord is represented in terms of its three parts: modifiers, base,
### and effect.
### 
### E.g., "a{shift+left_10} " -> [[None, "a", None], ["shift", "left",
###                               "10"], [None, "space", None]]
### 
### Update: The chord's text is also stored for unparsing without information loss.
###         E.g., "{{}" -> [None, "{", None, "{{}"]
### 

def parse_into_chords(specification):
    chords = []
    
    while len(specification) > 0:
        m = chord_pattern.match(specification)
        if m:
            modifiers = m.group(1)
            if modifiers: modifiers = modifiers[:-1]  # remove final "+"
            chords += [[modifiers, m.group(2), m.group(3), m.group(0)]]
            specification = specification[m.end():]
        else:
            char = specification[0]
            chords += [[None, char, None, char]]
            specification = specification[1:]
    
    return chords

# Because we can't be sure of the current code page, treat all non-ASCII
# characters as potential accented letters for now.  
chord_pattern = re.compile(r"""\{ ( (?: [a-zA-Z0-9\x80-\xff]+ \+ )* ) 
                                  ( . | [-a-zA-Z0-9/*+.\x80-\xff]+ )
                                  (?: [ _] (\d+|hold|release) )?
                               \}""", re.VERBOSE|re.IGNORECASE)


### 
### 
### 

def chord_to_events(chord):
    modifiers, base, effect, text = chord
    if base == " ":
        base = "space"
    if modifiers:
        modifiers = modifiers.split("+")
    else:
        modifiers = []
    hold_count = release_count = 1
    if effect:
        effect = effect.lower()
        if   effect == "hold":    release_count = 0
        elif effect == "release": hold_count    = 0
        else: 
            hold_count = int(effect)
            if hold_count == 0:
                # check for bad names even when no events:
                for modifier in modifiers:
                    single(modifier, False)
                single(base, False)   
                return []

    if len(base) == 1:
        try:
            m, f = how_type_character(base)
            if debug and (len(m)>0 or describe_key(f)!=base):
                mm = ""
                if m: mm = '+'.join(m) + "+"
                bb = "<" + base + ">"
                if ord(base[0])<32: bb = hex(ord(base[0]))
                print(("typing " + bb + " by {" + mm + describe_key(f) + "}"))
            modifiers += m
            base = "VK" + hex(f)
        except:
            if debug and ord(base[0])<128:
                bb = "<" + base + ">"
                if ord(base[0])<32: bb = hex(ord(base[0]))
                print(("can't type " + bb + " on current keyboard layout"))
            pass
    
    events         = []
    modifiers_down = []
    modifiers_up   = []
    for modifier in modifiers:
        modifiers_down +=                single(modifier, False)
        modifiers_up   =  modifiers_up + single(modifier, True)

    try:
        # down down up (hardware auto-repeat style) fails so use down,up pairs:
        if hold_count > 1:
            return modifiers_down \
                + (single(base,False)+single(base, True))*hold_count \
                + modifiers_up
        if hold_count > 0:
            events += modifiers_down + single(base,False)*hold_count
        if release_count > 0:
            events += single(base, True) + modifiers_up
        return events
    except:
        if len(base) != 1:
            raise

    if len(modifiers) != 0:
        print(("Warning: unable to use modifiers with character: " + base))
    
    # Unicode?
    
    if release_count==0:
        print(("Warning: unable to independently hold character: " + base))
    if hold_count==0:
        print(("Warning: unable to independently release character: " + base))
        return []

    if debug:
        print(("using numpad entry for: " + base))
    return windows1252_to_events(ord(base[0])) * hold_count



### 
### Pressing/releasing a single generalized virtual key or mouse button
### 

## 
## Keyboard key names:
## 

Key_name = {
    # 
    # SendDragonKeys virtual key names:
    # 
    
    "alt"         : VK_MENU,
    "backspace"   : VK_BACK,
    "break"       : VK_CANCEL,
    "capslock"    : VK_CAPITAL,
    "center"      : VK_CLEAR,
    "ctrl"        : VK_CONTROL,
    "del"         : VK_DELETE,
    "down"        : VK_DOWN,
    "end"         : VK_END,
    "enter"       : VK_RETURN,
    "esc"         : VK_ESCAPE,
    "home"        : VK_HOME,
    "ins"         : VK_INSERT,
    "left"        : VK_LEFT,
    "numlock"     : VK_NUMLOCK,
    "pgdn"        : VK_NEXT,
    "pgup"        : VK_PRIOR,
    "pause"       : VK_PAUSE,
    "prtsc"       : VK_SNAPSHOT,
    "right"       : VK_RIGHT,
    "scrolllock"  : VK_SCROLL,
    "shift"       : VK_SHIFT,
    "space"       : VK_SPACE,
    #"sysreq"     : VK_SYSREQ,# <<<>>>
    "tab"         : VK_TAB,
    "up"          : VK_UP,

    "f1"          : VK_F1,
    "f2"          : VK_F2,
    "f3"          : VK_F3,
    "f4"          : VK_F4,
    "f5"          : VK_F5,
    "f6"          : VK_F6,
    "f7"          : VK_F7,
    "f8"          : VK_F8,
    "f9"          : VK_F9,
    "f10"         : VK_F10,
    "f11"         : VK_F11,
    "f12"         : VK_F12,
    "f13"         : VK_F13,
    "f14"         : VK_F14,
    "f15"         : VK_F15,
    "f16"         : VK_F16,

    "numkey/"     : VK_DIVIDE,
    "numkey*"     : VK_MULTIPLY,
    "numkey-"     : VK_SUBTRACT,
    "numkey+"     : VK_ADD,
    "numkey0"     : VK_NUMPAD0,
    "numkey1"     : VK_NUMPAD1,
    "numkey2"     : VK_NUMPAD2,
    "numkey3"     : VK_NUMPAD3,
    "numkey4"     : VK_NUMPAD4,
    "numkey5"     : VK_NUMPAD5,
    "numkey6"     : VK_NUMPAD6,
    "numkey7"     : VK_NUMPAD7,
    "numkey8"     : VK_NUMPAD8,
    "numkey9"     : VK_NUMPAD9,
    "numkey."     : VK_DECIMAL,
    "numkeyenter" : GK_NUM_RETURN,

    "extdel"      : GK_NUM_DELETE,
    "extdown"     : GK_NUM_DOWN,
    "extend"      : GK_NUM_END,
    "exthome"     : GK_NUM_HOME,
    "extins"      : GK_NUM_INSERT,
    "extleft"     : GK_NUM_LEFT,
    "extpgdn"     : GK_NUM_NEXT,
    "extpgup"     : GK_NUM_PRIOR,
    "extright"    : GK_NUM_RIGHT,
    "extup"       : GK_NUM_UP,

    "leftalt"     : VK_LMENU,
    "rightalt"    : VK_RMENU,
    "leftctrl"    : VK_LCONTROL,
    "rightctrl"   : VK_RCONTROL,
    "leftshift"   : VK_LSHIFT,
    "rightshift"  : VK_RSHIFT,

    "0"           : VK_0,
    "1"           : VK_1,
    "2"           : VK_2,
    "3"           : VK_3,
    "4"           : VK_4,
    "5"           : VK_5,
    "6"           : VK_6,
    "7"           : VK_7,
    "8"           : VK_8,
    "9"           : VK_9,

    "a"           : VK_A,
    "b"           : VK_B,
    "c"           : VK_C,
    "d"           : VK_D,
    "e"           : VK_E,
    "f"           : VK_F,
    "g"           : VK_G,
    "h"           : VK_H,
    "i"           : VK_I,
    "j"           : VK_J,
    "k"           : VK_K,
    "l"           : VK_L,
    "m"           : VK_M,
    "n"           : VK_N,
    "o"           : VK_O,
    "p"           : VK_P,
    "q"           : VK_Q,
    "r"           : VK_R,
    "s"           : VK_S,
    "t"           : VK_T,
    "u"           : VK_U,
    "v"           : VK_V,
    "w"           : VK_W,
    "x"           : VK_X,
    "y"           : VK_Y,
    "z"           : VK_Z,


    # 
    # New names for virtual keys:
    # 

    "win"         : VK_LWIN,
    "leftwin"     : VK_LWIN,
    "rightwin"    : VK_RWIN,
    "apps"        : VK_APPS,  # name may change...

    "f17"         : VK_F17,
    "f18"         : VK_F18,
    "f19"         : VK_F19,
    "f20"         : VK_F20,
    "f21"         : VK_F21,
    "f22"         : VK_F22,
    "f23"         : VK_F23,
    "f24"         : VK_F24,

    "browserback"         : VK_BROWSER_BACK,
    "browserfavorites"    : VK_BROWSER_FAVORITES,
    "browserforward"      : VK_BROWSER_FORWARD,
    "browserhome"         : VK_BROWSER_HOME,
    "browserrefresh"      : VK_BROWSER_REFRESH,
    "browsersearch"       : VK_BROWSER_SEARCH,
    "browserstop"         : VK_BROWSER_STOP,

    # these names may change in the future...
    "launchapp1"          : VK_LAUNCH_APP1,
    "launchapp2"          : VK_LAUNCH_APP2,
    "launchmail"          : VK_LAUNCH_MAIL,
    "launchmediaselect"   : VK_LAUNCH_MEDIA_SELECT,

    "medianexttrack"      : VK_MEDIA_NEXT_TRACK,
    "mediaplaypause"      : VK_MEDIA_PLAY_PAUSE,
    "mediaprevioustrack"  : VK_MEDIA_PREV_TRACK,
    "mediastop"           : VK_MEDIA_STOP,

    "volumedown"          : VK_VOLUME_DOWN,
    "volumemute"          : VK_VOLUME_MUTE,
    "volumeup"            : VK_VOLUME_UP,

    # possibly more names to come...
    "oem1"      : VK_OEM_1,
    "oem2"      : VK_OEM_2,
    "oem3"      : VK_OEM_3,
    "oem4"      : VK_OEM_4,
    "oem5"      : VK_OEM_5,
    "oem6"      : VK_OEM_6,
    "oem7"      : VK_OEM_7,
    "oem8"      : VK_OEM_8,
    "oem102"    : VK_OEM_102,
    "oemcomma"  : VK_OEM_COMMA,
    "oemminus"  : VK_OEM_MINUS,
    "oemperiod" : VK_OEM_PERIOD,
    "oemplus"   : VK_OEM_PLUS,
}

Code_to_name = {}
for name in list(Key_name.keys()):
    Code_to_name[Key_name[name]] = name

def describe_key(code):
    try:
        return Code_to_name[code]
    except:
        return "VK" + hex(code)


## 
## Mouse button names:
## 

Button_name = {
    "leftbutton"   : "left",    # really primary button
    "middlebutton" : "middle",
    "rightbutton"  : "right",   # really secondary button
    "xbutton1"     : "X1",
    "xbutton2"     : "X2",
    }


GetSystemMetrics = windll.user32.GetSystemMetrics
GetSystemMetrics.argtypes = [c_int]
GetSystemMetrics.restype  = c_int

# Convert ExtendSendDragonKeys mouse button names to those required
# by SendInput.py, swapping left & right buttons if user has "Switch
# primary and secondary buttons" selected:
def get_mouse_button(button_name):
    try:
        button = Button_name[button_name.lower()]
        if button=="left" or button=="right":
            if GetSystemMetrics(win32con.SM_SWAPBUTTON):
                if button=="left":
                    button = "right"
                else:
                    button = "left"
        return button
    except:
        raise KeyError("unknown mouse button: " + key)


## 
## Create a single virtual event to press or release a keyboard key or
## mouse button:
## 

def single(key, releasing):
    # universal syntax is VK0xhh for virtual key with code 0xhh:
    if key[0:4] == "VK0x":
        return [virtual_key_event(int(key[4:],16), releasing)]
        
    lower_key = key.lower()
    try:
        return [virtual_key_event(Key_name[lower_key], releasing)]
    except:
        try:
            return [mouse_button_event(get_mouse_button(lower_key), releasing)]
        except:
            raise KeyError("unknown key/button: " + key)



### 
### 
### 

DWORD  = c_ulong        # 32 bits
SHORT  = c_short        # 16 bits
#TCHAR = c_char         # if not using Unicode
TCHAR  = c_wchar        # if using Unicode
HKL    = HANDLE = PVOID = c_void_p

GetKeyboardLayout = windll.user32.GetKeyboardLayout
GetKeyboardLayout.argtypes = [DWORD]
GetKeyboardLayout.restype  = HKL

VkKeyScan = windll.user32.VkKeyScanW
VkKeyScan.argtypes = [TCHAR]
VkKeyScan.restype  = SHORT

VkKeyScanEx = windll.user32.VkKeyScanExW
VkKeyScanEx.argtypes = [TCHAR, HKL]
VkKeyScanEx.restype  = SHORT


def how_type_character(char):
    how_type = VkKeyScan(char)
    
    virtual_key = how_type & 0xff
    if virtual_key == 0xff:
        raise ValueError("unable to type character with current keyboard layout: " 
                         + char)

    modifiers   = []
    if how_type&0x400: modifiers += ["alt"]
    if how_type&0x200: modifiers += ["ctrl"]
    if how_type&0x100: modifiers += ["shift"]

    if how_type&0xf800:
        raise ValueError("unknown modifiers required, tell MDL: " + hex(how_type)) 
    
    return modifiers, virtual_key


### 
### 
### 

def windows1252_to_events(code):
    events = []
    events += single("alt", False)
    events += numpad(0)
    events += numpad(code/100 %10)
    events += numpad(code/10  %10)
    events += numpad(code/1   %10)
    events += single("alt", True)
    return events

def numpad(i):
    return chord_to_events([None, "numkey"+str(i), None, "{numkey"+str(i)+"}"])



### 
### 
### 

Wheel_name = {
    "wheelup"    : [1, False],
    "wheeldown"  : [-1, False],
    "wheelright" : [1, True],
    "wheelleft"  : [-1, True]
    }
