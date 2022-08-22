# make import natlink possible, getting all the _natlink_core.pyd functions...
from ._natlink_core import *

print("Import natlink")
import locale
from ._natlink_core import execScript as _execScript
from ._natlink_core import playString as _playString

def lmap(fn,iter):
    return list(map(fn,iter))

def playString(a, hook=0):
    return _playString(toWindowsEncoding(a), hook)

def execScript(script,args=None):
    #only encode the script.  can't find a single case of anyone using the args
    if args is None:
        args = []
    script_w=toWindowsEncoding(script)
    return _execScript(script_w,args)    

def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
