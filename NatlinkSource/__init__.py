# make import natlink possible, getting all the _natlink_core.pyd functions...
from ._natlink_core import *

print("Import natlink")
from ._natlink_core import execScript as _execScript
from ._natlink_core import playString as _playString
import locale

def lmap(fn,iter):
    return list(map(fn,iter))

def playString(a):
    return _playString(toWindowsEncoding(a))

def execScript(script,args=[]):
    #only encode the script.  can't find a single case of anyone using the args 
    script_w=toWindowsEncoding(script)
    return _execScript(script_w,args)    

def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
