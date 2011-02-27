#!/usr/bin/env python
import os, sys
def startdefaultornotepad(path):
    """tries os.startfile on a path (....vcl for example)
    if exception occurs, start with notepad
    """
    try:
        os.startfile(path)
    except:
        os.startfile("notepad %s"% path)
        
if __name__ == "__main__":
    if sys.argv and len(sys.argv) >= 1:
        for path in sys.argv[1:]:
            startdefaultornotepad(path)
            
            
    