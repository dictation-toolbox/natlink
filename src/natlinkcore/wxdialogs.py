"""some dialogs running with wx (wxpython)
"""
#pylint:disable=E1101
import os
import sys
import wx
from natlinkcore import config

def GetDirFromDialog(promptText, startdir=None):
    """call the directory dialog via wxPython

    startdir is directory to start with, can be "expanded" with "~" or
    environment variables, defaults to the current directory if not passed
        
    return a valid path (directory) or None if canceled
    """
    if startdir:
        startdir = config.expand_path(startdir)
        if not os.path.isdir(startdir):
            print(f'not a directory: "{startdir}", start with home directory')
            startdir = None
    if not startdir:
        startdir = config.expand_path("~")
    oldstdout, oldstderr = sys.stdout, sys.stderr
    wxApp = wx.App()
    try:
        dirpath = None
        dlg = wx.DirDialog(None, promptText, startdir, wx.FD_OPEN  | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            return dirpath

    finally:
        dlg.Destroy()
        del wxApp
        sys.stdout, sys.stderr = oldstdout, oldstderr
    return None


    
def GetFileFromDialog(promptText, wildcard=None, startdir=None):
    """call the file dialog via wxPython
        
    return a valid path (file) or None if dialog was canceled
    """
    # pylint: disable=E1101
    wildcard = wildcard or "*.*"
    if startdir:
        startdir = config.expand_path(startdir)
        if not os.path.isdir(startdir):
            print(f'not a directory: "{startdir}", start with home directory')
            startdir = None
    if not startdir:
        startdir = config.expand_path("~")

    oldstdout, oldstderr = sys.stdout, sys.stderr
    wxApp = wx.App()
    try:
        dlg = wx.FileDialog(None, promptText, startdir, wildcard,
                       style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            if paths:
                # if len(paths) > 1:
                #     print(r'{len(paths)} files chosen, take first "{paths[0]}"')
                # with these options, only one file can be selected...
                return paths[0]
            print("no file chosen")
            return ""
    finally:
        del wxApp
        sys.stdout, sys.stderr = oldstdout, oldstderr
    
    return None

if __name__ == "__main__":
    # result = GetDirFromDialog("Please specify a directory", startdir="%onedrive%/desktop")
    # print(f'GetDirFromDialog, result: {result}')
    result = GetFileFromDialog("Please specify a file", wildcard="*.xlsx", startdir="~/Documents")
    print(f'GetFileFromDialog, result: {result}')
    