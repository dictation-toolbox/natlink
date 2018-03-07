#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# excel_sample7.py
#
# Example of using OLE Automation to control Excel from Python macros. Start
# Excel and put the names of colors (in lower case) in some of the cells.
# Then say "demo sample seven" and all the cells in your spreadsheet which
# contain a color which change to that color.
#
# The OLE automation code uses the Win32com package.  It allows you to
# access Excel just like you were using Visual Basic.  See the web site at
# http://starship.python.net/crew/pirx/spam7/ for more details os using OLE
# automation from Python.
#

import natlink
from natlinkutils import *

import string
import win32api
import win32com.client
consts = win32com.client.constants

colorMap = {
    'black':win32api.RGB(0,0,0),
    'dark red':win32api.RGB(128,0,0),
    'dark green':win32api.RGB(0,128,0),
    'dark yellow':win32api.RGB(128,128,0),
    'dark blue':win32api.RGB(0,0,128),
    'dark magenta':win32api.RGB(128,0,128),
    'dark cyan':win32api.RGB(0,128,128),
    'dark gray':win32api.RGB(128,128,128),
    'light gray':win32api.RGB(192,192,192),
    'light red':win32api.RGB(255,0,0),
    'light green':win32api.RGB(0,255,0),
    'light yellow':win32api.RGB(255,255,0),
    'light blue':win32api.RGB(0,0,255),
    'light magenta':win32api.RGB(255,0,255),
    'light cyan':win32api.RGB(0,255,255),
    'white':win32api.RGB(255,255,255),
    'gray':win32api.RGB(192,192,192),
    'red':win32api.RGB(255,0,0),
    'green':win32api.RGB(0,255,0),
    'yellow':win32api.RGB(255,255,0),
    'blue':win32api.RGB(0,0,255),
    'magenta':win32api.RGB(255,0,255),
    'cyan':win32api.RGB(0,255,255),
}

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = demo sample seven;
    """

    def initialize(self):
        self.load(self.gramSpec)

    def gotBegin(self,moduleInfo):
        winHandle=matchWindow(moduleInfo,'excel','Microsoft Excel')
        if winHandle:
            self.activateAll(window=winHandle)

    def gotResults_start(self,words,fullResults):
        application=win32com.client.Dispatch('Excel.Application')
        worksheet=application.Workbooks(1).Worksheets(1)
        for row in range(1,50):
            for col in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                cell=worksheet.Range(col+str(row))
                if cell.Value in colorMap:
                    cell.Font.Color=colorMap[cell.Value]
                    cell.Borders.Weight = consts.xlThick

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
