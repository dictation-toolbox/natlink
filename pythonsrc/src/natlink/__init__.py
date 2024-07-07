"""Natlink is an OpenSource extension module for the speech recognition program """
#set the version in pyroject.toml

# make import natlink possible, getting all the _natlink_corexx.pyd functions...
#we have to know which pyd is registered by the installer.
#pylint:disable=W0702

#site packages
import json
import os
import importlib
import importlib.machinery
import importlib.util
import traceback
import winreg
import ctypes
import contextlib
import win32api
import win32gui
from dtactions.vocola_sendkeys import ext_keys
W32OutputDebugString = ctypes.windll.kernel32.OutputDebugStringW

#copied from pydebugstring.  
def outputDebugString(to_show):
    """ 
    :param to_show: to_show
    :return: the value of W32OutputDebugString
    Sends a string representation of to_show to W32OutputDebugString 
    """
    return W32OutputDebugString(f"{to_show}")

def get_config():
    """get the configuration information from environment.json
    Returns:
        (dict): the configuration data
    """
    try:
        # get the path to the environment.json file user directory .natlink
        path = os.path.join(os.path.expanduser("~"), ".natlink", "environment.json")
        with open(path) as file:
            data = json.load(file)
        return data
    except Exception as e:
        outputDebugString(f"get_config: {e}")

try:
    data = get_config()
    path_to_pyd = data.get("natlink_pyd")
    #if something goes wrong we will want these messages.
    outputDebugString(f"Loading {path_to_pyd} from {__file__}")

    loader = importlib.machinery.ExtensionFileLoader("_natlink_core", path_to_pyd)
    spec = importlib.util.spec_from_loader("_natlink_core", loader)
    _natlink_core = importlib.util.module_from_spec(spec)
    from _natlink_core import *

    import locale
    from _natlink_core import execScript as _execScript
    from _natlink_core import playString as _playString
    from _natlink_core import playEvents as _playEvents
    from _natlink_core import recognitionMimic as _recognitionMimic
except Exception:
    tb_lines = traceback.format_exc()

    outputDebugString(f"Python traceback \n{tb_lines}\n in {__file__}")

def lmap(fn,Iter):
    return list(map(fn, Iter))

def playString(a, hook=0):
    """send to dtactions.sendkeys, causes an ESP error in Dragon 16
    """
    # return _playString(toWindowsEncoding(a), hook)
    if hook:
        return execScript(f'SendSystemKeys("{a}")')
    # normal case:
    return ext_keys.send_input(a)

def playEvents16(events):
    """a short version, written by Dany Finlay
    """
    print(f'try a playEvents on Dragon16: {events}')
    # Check that *events* is a list.
    if not isinstance(events, list):
        raise TypeError("events must be a list of 3-tuples")

    # Post each 3-tuple event to the foreground window.
    hwnd = win32gui.GetForegroundWindow()
    for event in events:
        if not (isinstance(event, tuple) and len(event) == 3 and
                all((isinstance(i, int) for i in event))):
            raise TypeError("events must be a list containing 3-tuples of"
                            " integers")
        message, wParam, lParam = event
        win32api.PostMessage(hwnd, message, wParam, lParam)

def getDNSVersion():
    """find the correct DNS version number (as an integer)
    
    (copy from same function in natlinkstatus.py)

    """
    try:
        data = get_config()
        version = data.get("dragon_version")

        if version:
            return int(version)
    except Exception as e:
        outputDebugString(f"getDNSVersion: {e}")
    return 0

def playEvents(a):
    """causes a halt (ESP error) in Dragon 16.
    """
    if getDNSVersion() >= 16:
        playEvents16(a)
        return None
    return _playEvents(a)

def execScript(script,args=None):
    #only encode the script.  can't find a single case of anyone using the args
    if args is None:
        args = []
    else:
        ## added QH:
        outputDebugString(f'execScript, args found: {args}!!!!')
    script_w=toWindowsEncoding(script)
    return _execScript(script_w,args)    


def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
   
# wrap the C++ natConnect with a version that returns a context manager

_original_natconnect=natConnect
def wrappedNatConnect(*args,**keywords):
    _original_natconnect(*args,**keywords)
    return NatlinkConnector()
natConnect=wrappedNatConnect

@contextlib.contextmanager
def NatlinkConnector():
    """context manager for natlink connections.
    """
    # use the method from https://towardsdatascience.com/how-to-build-custom-context-managers-in-python-31727ffe96e1
    yield
    outputDebugString("natlink disconnecting")
    natDisconnect()


def _test_playEvents():
    """perform a few mouse moves
    """
    import time
    wm_mousemove = 0x0200
    positionsx = [10, 500, 500, 10, 10]
    positionsy = [10, 10, 500, 500, 10]
    for x, y in zip(positionsx, positionsy):
        playEvents( [(wm_mousemove, x, y)] )
        time.sleep(1)
            
            

if __name__ == "__main__":
    outputDebugString(f'getDNSVersion: {getDNSVersion()} (type: {type(getDNSVersion())}))')
    # playString('abcde')
    # playEvents( [(0,0,0)] )
    _test_playEvents()
        
    
