#!/bin/env python
# -*- coding: iso-8859-15 -*-
#----------------------------------------------------------------------------
# Name:         configurenatlinkvocola.py
# Author:       XXXX
# Created:      XX/XX/XX
# Copyright:    
#----------------------------------------------------------------------------

import wx, sys
from configurenatlink_wdr import *
import os, os.path
import RegistryDict, win32con

# nf: natlinkinstallfunctions, imported at end of init...
nf = None

# WDR: classes

class configurenatlink(wx.Panel):
    def __init__(self, parent, id, name="configurepanel",
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.TAB_TRAVERSAL ):
        global nf
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.frame = parent.frame
        # WDR: dialog function MainWindow for configurenatlink
        MainWindow( self, True )

        # WDR: handler declarations for configurenatlink
        wx.EVT_BUTTON(self, ID_BUTTONchangednsinifilepath, self.dochangensinifilepath)
        wx.EVT_BUTTON(self, ID_BUTTONchangednsinstallpath, self.dochangednsinstallpath)
        wx.EVT_BUTTON(self, ID_BUTTONClose, self.OnDoClose)

        try:
            nf = __import__('natlinkinstallfunctions')
        except:

            self.error('natlinkinstallfunctions import failed')
            return
        self.setInfo()

    def getNatlinkstatus(self):
        """get from the registry the path of NatlinkCore, and import natlinkstatus
        """
        self.error('not implemented')

    def error(self, text):
        """put error message on log panel and on status line"""
        print text
        print '-'*60
        self.frame.SetStatusText(text + ' (see log)')

    def message(self, text):
        """put message on log panel and on status line"""
        print text
        self.frame.SetStatusText(text)

    def setInfo(self):
        """extract data for the info controls
        """
        D = nf.getStatusDict()  # from natlinkinstallfunctions
        print 'StatusDict:'
        for k,v in D.items():
            print '%s: %s'% (k,v)
        print '-------'
        value = D['DNSdirectory']
        self.GetTextctrldnsinstallpath().SetLabel(value)
        value = str(D['DNSversion'])
        self.GetTextctrldnsversion().SetLabel(value)
        
    # WDR: methods for configurenatlink

    def GetTextctrldnsinstallpath(self):
        return self.FindWindowById( ID_TEXTCTRLDNSinstallpath )

    def GetTextctrlnatlinkinstallpath(self):
        return self.FindWindowById( ID_TEXTCTRLnatlinkinstallpath )

    def GetTextctrlregisternatlink(self):
        return self.FindWindowById( ID_TEXTCTRLregisternatlink )

    def GetTextctrlvocoladuserdir(self):
        return self.FindWindowById( ID_TEXTCTRLvocoladuserdir )


    def GetTextctrldnsversion(self):
        return self.FindWindowById( ID_TEXTCTRLdnsversion )

    def GetTextctrlnatlinkversion(self):
        return self.FindWindowById( ID_TEXTCTRLnatlinkversion )

    # WDR: handler implementations for configurenatlink

    def dochangensinifilepath(self, event):
        pass

    def dochangednsinstallpath(self, event):
        dlg = wx.DirDialog(self.frame, "Choose a directory:",
                  style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        dlg.SetPath(os.environ['PROGRAMFILES'])
        dlg.SetMessage('Please specify the path where the natspeak installation is located')
        if dlg.ShowModal() == wx.ID_OK:
            new_dns_path = dlg.GetPath()
            nf.setDNSdirectory(new_dns_path)
            self.message('Changed DNS path to: %s' % new_dns_path)
            self.setInfo()
        else:
            self.message('no change...')


    def OnDoClose(self, event):
        self.parent.frame.Destroy()

    def OnDoRepairNatlink(self, event):
        pass

    def OnDoResetVocolaUserdir(self, event):
        pass
        

    def OnDoResetNatlinkUserdir(self, event):
        pass

    def dummy(self):
        pass
        

    def OnDoVocolaUserDir(self, event):
        pass
        

    def OnDoGetNatlinkUserDir(self, event):
        pass
        

    def OnDonatlinkoutput(self, event):
        pass
        

    def OnDovocolacommand(self, event):
        pass
        

    def OnDoNatlinkenabled(self, event):
        pass
        

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.app = parent
        wx.EVT_MENU(self, ID_MENUhelp, self.OnMenuHelp)
        wx.EVT_MENU(self, ID_MENUClose, self.OnMenuClose)
                
        self.CreateStatusBar(1)
        self.SetStatusText("This is the Configure Natlink & vocola utility...")
        self.CreateMyMenuBar()
        # insert main window here
        self.nb = wx.Notebook(self, -1, name='panel',
                pos=wx.Point(0, 0), size=wx.Size(592, 498), style=0)

        self.log = wx.TextCtrl(self.nb, -1, name='log',
              style=wx.TE_READONLY | wx.TE_MULTILINE|wx.TE_NOHIDESEL, value='')
        sys.stdout = Stdout(self.log)
##        self.errors = wx.TextCtrl(self.nb, -1, name='errors', 
##              style=wx.TE_READONLY | wx.TE_MULTILINE|wx.TE_NOHIDESEL, value='')
##        sys.stderr = Stderr(self.errors)
        sys.stderr = sys.stdout
        
        self.nb.AddPage(imageId=-1, page=self.log, select=False,
              text='log')
##        self.nb.AddPage(imageId=-1, page=self.errors, select=False,
##              text='errors')
        self.nb.frame = self
        self.cpanel = configurenatlink(self.nb, -1, name='configurepanel')
        self.nb.AddPage(imageId=-1, page=self.cpanel, select=True,
              text='configure')
## self.nb = wx.Notebook(name='notebook', parent=self, style=0)

            
    # WDR: methods for MyFrame
    def CreateMyMenuBar(self):
        self.SetMenuBar(MyMenuBarFunc() )

    def OnMenuClose(self, event):
        self.Destroy()

    def OnMenuHelp(self, event):
        print 'help'

    
    # WDR: handler implementations for MyFrame

class Stdout:
    def __init__(self, object):
        self.writeto = object       
##      self.write('stdout started')
        
    def flush(self):
        pass
    def write(self, t):
        """write to output"""
        self.writeto.AppendText(t)

class Stderr:
    def __init__(self, txtctrl):
        self.window = txtctrl

    def flush(self):
        pass
    
    def write(self, t):
        """write to output"""
        self.window.AppendText(t)

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.frame = MyFrame( None, -1, "Configure Natlink & Vocola & Unimacro", [90,80], [670,670] )
        self.frame.Show(True)  
        return True

app = MyApp(True)
app.MainLoop()

