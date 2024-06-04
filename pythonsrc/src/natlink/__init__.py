"""Natlink is an OpenSource extension module for the speech recognition program """
#set the version in pyroject.toml

# make import natlink possible, getting all the _natlink_corexx.pyd functions...
#we have to know which pyd is registered by the installer.
#pylint:disable=W0702

#site packages

import importlib
import importlib.machinery
import importlib.util
import traceback
import winreg
import ctypes
import contextlib
import win32api
import win32gui
from dtactions.vocola_sendkeys import ext_keys   ### , SendInput
W32OutputDebugString = ctypes.windll.kernel32.OutputDebugStringW

#copied from pydebugstring.  
def outputDebugString(to_show):
    """ 
    :param to_show: to_show
    :return: the value of W32OutputDebugString
    Sends a string representation of to_show to W32OutputDebugString 
    """
    return W32OutputDebugString(f"{to_show}")


clsid="{dd990001-bb89-11d2-b031-0060088dc929}"          #natlinks well known clsid

#these keys  hold the pyd name for natlink, set up through the installer run regsvr32
subkey1=fr"WOW6432Node\CLSID\{clsid}\InprocServer32"
subkey2=fr"CLSID\{clsid}\InprocServer32"  #only likely if not 64 bit windows
subkeys=[subkey1,subkey2]
default_pyd="_natlink_core.pyd"    #just a sensible default if one isn't registered.

path_to_pyd=""
#find the PYD actually registered, and load that one.
found_registered_pyd=False
for subkey in subkeys:
    try:
        reg = winreg.ConnectRegistry(None,winreg.HKEY_CLASSES_ROOT)
        sk = winreg.OpenKey(reg,subkey)
        path_to_pyd = winreg.QueryValue(sk,None)
        found_registered_pyd = True
        break
    except:
        pass

try:
    pyd_to_load=path_to_pyd if found_registered_pyd else default_pyd

    #if something goes wrong we will want these messages.
    outputDebugString(f"Loading {pyd_to_load} from {__file__}")


    loader=importlib.machinery.ExtensionFileLoader("_natlink_core",pyd_to_load)
    spec = importlib.util.spec_from_loader("_natlink_core", loader)
    _natlink_core=importlib.util.module_from_spec(spec)
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

    print('playEvents not implemented for Dragon 16 (yet)')
    # try to attach to (repository) \dtactions\vocola_sendkeys
    # SendInput.send_input(events)


    # this is the attempt of Dane, which fails.
    # # Post each 3-tuple event to the foreground window.
    # hwnd = win32gui.GetForegroundWindow()
    # for event in events:
    #     if not (isinstance(event, tuple) and len(event) == 3 and
    #             all((isinstance(i, int) for i in event))):
    #         raise TypeError("events must be a list containing 3-tuples of"
    #                         " integers")
    #     
    #     message, wParam, lParam = event
    #     win32api.PostMessage(hwnd, message, wParam, lParam)

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


def getDNSVersion():
    """find the correct DNS version number (as an integer)
    
    (copy from same function in natlinkstatus.py)

    """
    dragonIniDir = get_config_info_from_registry("dragonIniDir")
    if dragonIniDir:
        try:
            version = int(dragonIniDir[-2:])
        except ValueError:
            outputDebugString('getDNSVersion, invalid version found "{dragonIniDir[-2:]}", return 0')
            version = 0
    else:
        outputDebugString(f'Error, cannot get dragonIniDir from registry, unknown DNSVersion "{dragonIniDir}", return 0')
        version = 0
    return version

## duplicated from loader:
def get_config_info_from_registry(key_name: str) -> str:
    hive, key, flags = (winreg.HKEY_LOCAL_MACHINE, r'Software\Natlink', winreg.KEY_WOW64_32KEY)
    with winreg.OpenKeyEx(hive, key, access=winreg.KEY_READ | flags) as natlink_key:
        result, _ = winreg.QueryValueEx(natlink_key, key_name)
        return result



#wrap the C++ natConnect with a version that returns a context manager

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
        
    
