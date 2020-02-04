import os
import ctypes
import sys


def testdll(p, dllname=None):
    '''test validity of dll files (dll and pyd) in directory (recursive)'''
    for dirpath, subdirs, files in os.walk(p):
        if dllname:
            dllfiles = [f for f in files if f.lower() == dllname]
        else:
            dllfiles = [f for f in files if f.lower().endswith(".dll")]
            pydfiles = [f for f in files if f.lower().endswith(".pyd")]
            dllfiles = dllfiles + pydfiles


        for f in dllfiles:
            fPath = os.path.join(dirpath, f)
            try:
                dll = ctypes.windll[fPath]
            except:
                print('cannot be accessed: %s (%s)'% (f, dirpath))
                print(sys.exc_info())
                print('size: %s: %s'% (fPath, os.path.getsize(fPath)))
            else:
                pass
                print('OK: %s (%s)'% (f, dirpath))
                print('size: %s: %s'% (fPath, os.path.getsize(fPath)))

if __name__ == "__main__":
    #p = os.path.normpath(r'C:\Windows\syswow64')
    #p = os.path.normpath(r'C:\Windows\system32')
    p = os.path.normpath(r'C:\\')
    #p = os.path.normpath(r'C:\natlink\NatLink\Macrosystem\Core')
    dllname = 'msvcr100.dll'
    #dllname = 'msvcr100.dll'  # None for all testing dll pyd

    if os.path.isdir(p):
        print('scanning for pyd files', p)
        testdll(p, dllname=dllname)
    else:
        print('not a directory: ', p)