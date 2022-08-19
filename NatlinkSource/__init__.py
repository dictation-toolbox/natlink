# make import natlink possible, getting all the _natlink_core.pyd functions...
from ._natlink_core import *

print("Import natlink")
from ._natlink_core import execScript as _execScript
from ._natlink_core import playString as _playString
import locale

def lmap(fn,iter):
    return list(map(fn,iter))

def playString(a):
    print(f"wrapped playString {a}")
    _playString(a)
    print("returned from playString")
def execScript(script,*args):
    script_w=toWindowsEncoding(script)
    args_w=lmap(toWindowsEncoding,*args)
    print(f"Exec Scripts {script}  args {args} windows encodings script {script_w} {args_w}")
    _execScript(script,args)    
    print(f"returned from exec ")

def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
