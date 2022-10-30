"""Natlink is an OpenSource extension module for the speech recognition program """
#set the version in pyroject.toml

# make import natlink possible, getting all the _natlink_corexx.pyd functions...
#we have to know which pyd is registered by the installer.
#pylint:disable=W0702
import importlib
import importlib.machinery
import importlib.util
import traceback
import winreg
import ctypes
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
default_pyd="_natlink_core15.pyd"    #just a sensible default if one isn't registered.

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
    from _natlink_core import recognitionMimic as _recognitionMimic
except Exception as exc:
    tb_lines=''.join(traceback.format_exception(exc))

    outputDebugString(f"Python traceback \n{tb_lines}\n in {__file__}")

def lmap(fn,Iter):
    return list(map(fn, Iter))

def playString(a, hook=0):
    return _playString(toWindowsEncoding(a), hook)

def execScript(script,args=None):
    #only encode the script.  can't find a single case of anyone using the args
    if args is None:
        args = []
    else:
        ## added QH:
        print(f'execScript, args found: {args}!!!!')
    script_w=toWindowsEncoding(script)
    return _execScript(script_w,args)    


def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
