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
def execScript(a,b):
    a1=toWindowsEncoding(a)
    b1=lmap(toWindowsEncoding,b)
    print(f"Exec Scripts {a} {b} windows encodings {a1} {b1}")
    _execScript(a,b)    
    print(f"returned from exec ")

def toWindowsEncoding(str_to_encode):
    return str_to_encode.encode('Windows-1252')
