### 
### Module Window part I: switching between windows
### 
### Version: 0.1
### 

import win32gui
import win32api
import win32process
import win32con
import ctypes
import ctypes.wintypes
import re
import os.path
import traceback     #<<<>>>


## 
## Retrieving attributes of the current top-level window:
## 

# Vocola function: Window.ID
def window_ID():
    return format_ID(win32gui.GetForegroundWindow())

def format_ID(window_handle):
    return "0x%08x" % (window_handle)
    #return str(window_handle)

    
# Vocola function: Window.Title
def window_title():
    handle = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(handle)


# Vocola function: Window.Class
def window_class():
    handle = win32gui.GetForegroundWindow()
    return win32gui.GetClassName(handle)


# Vocola function: Window.App
def window_app():
    handle = win32gui.GetForegroundWindow()
    return executable_for_window(handle)



##
## Getting the executable name (e.g., emacs.exe) for a given window:
##

def executable_for_window(window_handle):
    result = executable_for_unelevated_window(window_handle)
    if result == "":
        result = executable_for_elevated_window(window_handle)
    return result

# fast but does not work with elevated windows:
def executable_for_unelevated_window(window_handle):
    # Get window's process ID:
    tid, pid = win32process.GetWindowThreadProcessId(window_handle)

    # Get the process handle of this window's process ID.
    #   (auto closed on garbage collection)
    try:
        process_handle = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION | 
            win32con.PROCESS_VM_READ, 
            False, pid)
    except:
        return ""
    if not process_handle:
        return ""

    try:
        # This doesn't work for 64 bit applications:
        executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
    except:
        Psapi = ctypes.WinDLL('Psapi.dll')
        GetProcessImageFileName         = Psapi.GetProcessImageFileNameA
        GetProcessImageFileName.restype = ctypes.wintypes.DWORD
        
        MAX_PATH = 260  # Windows pathname limit for non-Unicode calls
        ImageFileName = (ctypes.c_char*MAX_PATH)()
        size = GetProcessImageFileName(process_handle.handle, ImageFileName, 
                                       MAX_PATH)
        if size == 0:
            raise ctypes.WinError()
            return ""
        executable_path = ImageFileName.value[0: size]

    filename = os.path.basename(executable_path)
    # at this point we have Unicode so...
    return filename.encode("windows-1252", 'xmlcharrefreplace')


TH32CS_SNAPPROCESS = 0x00000002
class PROCESSENTRY32(ctypes.Structure):
     _fields_ = [("dwSize",              ctypes.c_ulong),
                 ("cntUsage",            ctypes.c_ulong),
                 ("th32ProcessID",       ctypes.c_ulong),
                 ("th32DefaultHeapID",   ctypes.c_ulong),
                 ("th32ModuleID",        ctypes.c_ulong),
                 ("cntThreads",          ctypes.c_ulong),
                 ("th32ParentProcessID", ctypes.c_ulong),
                 ("pcPriClassBase",      ctypes.c_ulong),
                 ("dwFlags",             ctypes.c_ulong),
                 ("szExeFile",           ctypes.c_char * 260)]

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Process32First           = ctypes.windll.kernel32.Process32First
Process32Next            = ctypes.windll.kernel32.Process32Next
CloseHandle              = ctypes.windll.kernel32.CloseHandle


# slower but works even with elevated windows:
def executable_for_elevated_window(window_handle):
    # Get window's process ID:
    tid, pid = win32process.GetWindowThreadProcessId(window_handle)

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe32         = PROCESSENTRY32()
    pe32.dwSize  = ctypes.sizeof(PROCESSENTRY32)
    if Process32First(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
        return ""
    result = ""
    while result == "":
        if pe32.th32ProcessID == pid:
            result = pe32.szExeFile
        if Process32Next(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
            break
    CloseHandle(hProcessSnap)
    return result



## 
## Matching Windows:
## 

def make_matcher(specification):
    need_ID    = re.search("ID>",    specification) != None
    need_title = re.search("title>", specification) != None
    need_class = re.search("class>", specification) != None
    need_app   = re.search("app>",   specification) != None
    pattern    = re.compile(specification, re.IGNORECASE)

    def matcher(window_handle):
        target = ""
        if need_ID:    target += "ID>"    + format_ID(window_handle)              + "\n"
        if need_title: target += "title>" + win32gui.GetWindowText(window_handle) + "\n"
        if need_class: target += "class>" + win32gui.GetClassName(window_handle)  + "\n"
        if need_app:   target += "app>"   + executable_for_window(window_handle)  + "\n"
        if not (need_ID or need_title or need_class or need_app):
            target = win32gui.GetWindowText(window_handle)

        match = pattern.search(target)
        return match and not is_results_window(window_handle)

    return matcher

def is_results_window(window_handle):
    # This only works for DNS 11 and later:
    return win32gui.GetClassName(window_handle) == "DgnResultsBoxWindow"


# Vocola function: Window.Match
def window_match(specification):
    if make_matcher(specification)(win32gui.GetForegroundWindow()):
        return "true"
    return "false"



## 
## Finding Windows:
## 

# return list of non-hidden windows satisfying matcher in topmost to
# bottommost Z order:
def find_windows(matcher, max_count=1):
    results = []

    def callback(window_handle, extra):
        if not win32gui.IsWindowVisible(window_handle):
            return True
        if matcher(window_handle):
            results.append(window_handle)
        return len(results) < max_count

    try:
        win32gui.EnumWindows(callback, None)
    except Exception, e:
        # EnumWindows raises an exception when the enumeration is
        # terminated early :-(
        #print "EnumWindows exception: " + repr(e)
        #traceback.print_exc()
        pass
    return results



## 
## Switching to window by its ID:
## 

def switch_to(window_ID):
    #return switch_to1(window_ID)
    return switch_to2(window_ID)


#
# Neither of these can restore an elevated application
#


#from vocola_ext_subprocess import subprocess_sync
#from vocola_ext_variables  import variable_get

#def switch_to1(window_ID):
#    executable    = os.getenv("ProgramFiles") + r'\AutoHotkey\AutoHotkey.exe-'
#    script        = os.getenv("HOME") + r'\AutoHotkey\switch.ahk'
#    specification = '"ahk_id ' + str(window_ID) + '"'
#
#    subprocess_sync(executable, "AutoHotkey.exe", script, specification)
#    return variable_get("exit_code") == "0"


def switch_to2(window_ID):
    print "moving"
    if win32gui.IsIconic(window_ID):
        print "undoing"
        print win32gui.ShowWindow(window_ID, win32con.SW_RESTORE)
    print win32gui.SetForegroundWindow(window_ID)
    return True



## 
## Non-throwing versions of switching procedures.
## 
##   Each sets Window.Success() with their success status.
## 
## 

success = True                  # success status of last switching procedure

# Vocola function: Window.Success
def window_success():
    global success
    if success:
        return "true"
    else:
        return "false"

# Vocola procedure: Window.Go_
def window_go_(specification):
    global success
    success = False
    windows = find_windows(make_matcher(specification))
    if len(windows)==0:
        print "NOT FOUND: " + specification   # <<<>>>
        return
    window = windows[-1]
    print "-> "+ format_ID(window)            # <<<>>>
    success = switch_to(window)



## 
## Versions of the switching procedures that throw runtime errors if they fail:
## 

class WindowError(Exception):
    pass

# Vocola procedure: Window.Go
def window_go(specification):
    global success
    window_go_(specification)
    if not success:
        m = ("Unable to switch to a window with specification '" + 
             specification + "'")
        raise WindowError, m



##
## Test code:
##

# Describes each visible window to the Messages from NatLink window as
# "*>ID: TITLE|CLASS|EXECUTABLE" where * is present only if
# the window matches the passed specification, if any, and the first >
# is shown only for the foreground window.
#
# Vocola procedure: Window.ListWindows,0-1
def list_windows(specification="never match anything 24328#45348932453"):
    print
    foreground_window = win32gui.GetForegroundWindow()
    try:
        results = find_windows(make_matcher(".*"), 1000000)
    except Exception, e:
        print "find_windows failed: " + repr(e)
        traceback.print_exc()
        return

    for w in results:
        if matches(w, specification):
            out = "*"
        else:
            out = " "
        if w==foreground_window:
            out += ">"
        else:
            out += " "
        out += format_ID(w) + ": " + \
              win32gui.GetWindowText(w) + "|" + \
              win32gui.GetClassName(w)
        try:
            out += "|" + executable_for_window(w)
        except:
            out += "|FAILED"
        print out
    print

def matches(window_handle, specification):
    return make_matcher(specification)(window_handle)
