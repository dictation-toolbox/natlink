import os, ctypes, sys


def testdll(p):
    '''test validity of dll files (dll and pyd) in directory (recursive)'''
    for dirpath, subdirs, files in os.walk(p):
        dllfiles = [f for f in files if f.lower().endswith(".dll")]
        pydfiles = [f for f in files if f.lower().endswith(".pyd")]
        for f in dllfiles + pydfiles:
            fPath = os.path.join(dirpath, f)
            try:
                dll = ctypes.windll[fPath]
            except:
                print 'cannot be accessed: %s (%s)'% (f, dirpath)
                # print sys.exc_info()
            else:
                print 'OK: %s (%s)'% (f, dirpath)

if __name__ == "__main__":
    p = os.path.normpath(r'C:/natlink/natlink')
    testdll(p)