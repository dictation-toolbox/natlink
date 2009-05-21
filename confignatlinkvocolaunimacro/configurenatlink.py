#!/bin/env python
#
# natlinkconfig.py
#   This module does the natlinkconfigfunctions through a
#   wxPython GUI
#
#  (C) Copyright Quintijn Hoogenboom, 2008-2009
#
#----------------------------------------------------------------------------

try:
    import wx
except ImportError:
    print 'Unable to run the GUI installer because module wx was not found.  This probably'
    print 'means that wxPython is not installed.'

    print
    print 'Either install wxPython (recommended) or use the CLI (Command Line Interface)'
    print 'NatLink configuration program.'
    print
    print 'A version of wxPython suitable for use with NatLink can be obtained from'
    print 'http://sourceforge.net/project/showfiles.php?group_id=70807&package_id=261793'
    print '(each package there contains a version of wxPython; get the one appropriate'
    print ' to the version of Python you have installed.)'
    print
    while True:
        pass
    raise

import sys
from configurenatlink_wdr import *
import os, os.path, string, copy, types

# nf: natlinkinstallfunctions, imported at end of init...
nf = None
nc = None  # natlinkcorefunctions
# WDR: classes

class DialogUnimacroVocolaCompatibiliy(wx.Dialog):
    def __init__(self, parent, title=None):
        parent = parent
        id = -1
        pos = wx.DefaultPosition
        title = title or "Unimacro/Vocola compatibility"
        wx.Dialog.__init__(self, parent, id, title, pos)
        # WDR: dialog function YesNoAbort for MyYesNoAbortDialog
        
        
        # WDR: dialog function DialogVocolaCombatibility for DialogUnimacroVocolaCompatibiliy
        DialogVocolaCombatibility( self, True )
        
        # WDR: handler declarations for DialogUnimacroVocolaCompatibiliy
        wx.EVT_BUTTON(self, ID_BUTTONCancel, self.OnCancel)
        wx.EVT_BUTTON(self, ID_BUTTONOK, self.OnOK)

    # WDR: methods for DialogUnimacroVocolaCompatibiliy

    def GetCheckboxremoveunimacroincludelines(self):
        return self.FindWindowById( ID_CHECKBOXRemoveUnimacroIncludeLines )

    def GetCheckboxmakeunimacroincludelines(self):
        return self.FindWindowById( ID_CHECKBOXMakeUnimacroIncludeLines )

    def GetCheckboxrefreshunimacrovch(self):
        return self.FindWindowById( ID_CHECKBOXRefreshUnimacroVch )

    # WDR: handler implementations for DialogUnimacroVocolaCompatibiliy

    def OnOK(self, event):
        code = 0
        if self.GetCheckboxremoveunimacroincludelines().GetValue():
            code += 2
        if self.GetCheckboxmakeunimacroincludelines().GetValue():
            code += 4
        if self.GetCheckboxrefreshunimacrovch().GetValue():
            code += 1


        self.SetReturnCode(code)
        self.Destroy()
            
    def OnCancel(self, event):
        self.SetReturnCode(0)
        self.Destroy()



class InfoPanel(wx.Panel):
    def __init__(self, parent, id, name="infopanel",
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.TAB_TRAVERSAL ):
        self.frame = parent.frame
        wx.Panel.__init__(self, parent, id, pos, size, style)
        # WDR: dialog function InfoWindow for infopanel
        InfoWindow( self, True )
        # WDR: handler declarations for infopanel
        wx.EVT_BUTTON(self, ID_BUTTONHelpInfo, self.OnButtonHelpInfo)
        wx.EVT_BUTTON(self, ID_BUTTONClearDNSInifilePath, self.OnButtonClearDNSInifilePath)
        wx.EVT_BUTTON(self, ID_BUTTONchangednsinifilepath, self.OnButtonChangeDNSInifilePath)
        wx.EVT_BUTTON(self, ID_BUTTONClearDNSInstallPath, self.OnButtonClearDNSInstallPath)
        wx.EVT_BUTTON(self, ID_BUTTONchangednsinstallpath, self.OnButtonChangeDNSInstallPath)
        wx.EVT_BUTTON(self, ID_BUTTONLogInfo, self.OnButtonLogInfo)

    # WDR: methods for infopanel
    def GetTextctrlpythonversion(self):
        return self.FindWindowById( ID_TEXTCTRLpythonversion )

    def GetTextctrlwindowsversion(self):
        return self.FindWindowById( ID_TEXTCTRLWindowsVersion )

    def GetTextctrlnatlinkcorepath(self):
        return self.FindWindowById( ID_TEXTCTRLnatlinkcorepath )

    def GetTextctrldnsinifilepath(self):
        return self.FindWindowById( ID_TEXTCTRLdnsinifilepath )

    def GetTextctrldnsinstallpath(self):
        return self.FindWindowById( ID_TEXTCTRLDNSinstallpath )

    def GetTextctrldnsversion(self):
        return self.FindWindowById( ID_TEXTCTRLDNSversion )

        return self.FindWindowById( ID_TEXTCTRLpythonversion )

    def GetTextctrlwindowsversion(self):
        return self.FindWindowById( ID_TEXTCTRLWindowsVersion )

    def GetTextctrlnatlinkcorepath(self):
        return self.FindWindowById( ID_TEXTCTRLnatlinkcorepath )


    # WDR: handler implementations for infopanel

    def OnButtonClearDNSInifilePath(self, event):
        D = self.cpanel.config.getNatlinkStatusDict()
        doLetter, undoLetter = 'C', 'c'
        old_path = D['DNSIniDir']
        if old_path and os.path.isdir(old_path):
            undoCmd = (undoLetter, old_path)
        else:
            self.setstatus("DNSIniDir was NOT set, so no action needed")
            return
    
        statustext = 'DNSIniDir is Cleared, search (again) for default.'
        result = self.do_command(doLetter, undo=undoCmd)
        if result:
            self.setstatus(result)
        else:
            self.setstatus(statustext)
        self.cpanel.setInfo(leaveStatus=1)

    def OnButtonChangeDNSInifilePath(self, event):
        # ask for the correct directory:
        D = self.cpanel.config.getNatlinkStatusDict()
        doLetter, undoLetter = 'c', 'C'
        undoCmd = (undoLetter,)
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE-wx.DD_NEW_DIR_BUTTON)
##                  style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        ## search for Unimacro directory as proposal:
        Path = D['DNSIniDir']
        if not (Path and os.path.isdir(Path)):
            Path = nc.getExtendedEnv("COMMON_APPDATA")
        
        dlg.SetPath(Path)
        dlg.SetMessage('Please specify the directory where the DNS INI files are located')
        statustext = 'DNS INI file location is changed'
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
        else:
            self.setstatus("nothing specified")
            return
        result = self.do_command(doLetter,new_path, undo=undoLetter)
        if result:
            self.setstatus(result)
        else:
            self.setstatus("DNSIniDir changed")
        self.cpanel.setInfo(leaveStatus=1)


    def OnButtonClearDNSInstallPath(self, event):

        D = self.cpanel.config.getNatlinkStatusDict()
        doLetter, undoLetter = 'D', 'd'
        old_path = D['DNSInstallDir']
        if old_path and os.path.isdir(old_path):
            undoCmd = (undoLetter, old_path)
        else:
            self.setstatus("DNSInstallDir was NOT set, so no action needed")
            return
    
        statustext = 'DNSInstallDir is Cleared, search (again) for default.'
        result = self.do_command(doLetter, undo=undoCmd)
        if result:
            self.setstatus(result)
        else:
            self.setstatus(statustext)
        self.cpanel.setInfo(leaveStatus=1)

    def OnButtonChangeDNSInstallPath(self, event):
        # ask for the correct directory:
        D = self.cpanel.config.getNatlinkStatusDict()
        doLetter, undoLetter = 'd', 'D'
        undoCmd = (undoLetter,)
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE-wx.DD_NEW_DIR_BUTTON)
##                  style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        ## search for Unimacro directory as proposal:
        Path = D['DNSInstallDir']
        if not (Path and os.path.isdir(Path)):
            Path = nc.getExtendedEnv("PROGRAMFILES")
        
        dlg.SetPath(Path)
        dlg.SetMessage('Please specify the directory where DNS is installed')
        statustext = 'DNS Install directory is changed'
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
        else:
            self.setstatus("nothing specified")
            return
        result = self.do_command(doLetter,new_path, undo=undoLetter)
        if result:
            self.setstatus(result)
        else:
            self.setstatus("DNSInstallDir changed")
        self.cpanel.setInfo(leaveStatus=1)

    def OnButtonLogInfo(self, event):
        self.cpanel.cli.do_i("dummy")
        self.cpanel.cli.do_I("dummy")
        self.cpanel.warning("See the info from natlinkstatus in the log panel")

    def OnButtonHelpInfo(self, event):
        print '---help on DNS Install Directory:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        cli = self.cpanel.cli
        cli.help_d()
        print '---help on DNS INI files Directory:'
        cli.help_c()
        text = \
"""This info panel has no undo function, like the config panel,
but clearing the settings falls back to NatSpeak defaults

The button Log info gives the complete natlinkstatus info in the log panel

See more help information in the log panel"""
        self.cpanel.warning(text)

    def setstatus(self, text):
        """put message on log panel and on status line"""
        print text
        self.frame.SetStatusText(text)

    def do_command(self, *args, **kw):
        """a single letter, optionally followed by a path
        for infopanel, no undo things, simply ignore

        when calling from undo button, provide 'noundo' = 1 as keyword argument.

    
        """
        if len(args) < 1:
            print 'empty command %s'% `args`
            return
        if len(args) > 2:
            print 'too many posional arguments: %s'% `args`
            return
        letter = args[0]
        if len(args) == 2:
            pathName = args[1]
        else:
            pathName = 'dummy'
        funcName = 'do_%s'% letter
        cli = self.cpanel.cli
        func = getattr(cli, funcName, None)
        if not func:
            mess = 'invalid command: %s'% letter
            print mess
            return mess
        result = func(pathName)
        self.cpanel.setInfo()
        return result


class ConfigureNatlinkPanel(wx.Panel):
    def __init__(self, parent, id, name="configurepanel",
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.TAB_TRAVERSAL ):
        global nf, nc   # natlinkconfigfunctions, self.cli, natlinkcorefunctions
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.frame = parent.frame
        # WDR: dialog function MainWindow for configurenatlink
        MainWindow( self, True )

        # WDR: handler declarations for configurenatlink
        wx.EVT_BUTTON(self, ID_BUTTONVocolaCompatibiliy, self.OnButtonVocolaCompatibility)
        wx.EVT_BUTTON(self, ID_BUTTONUnimacroEditor, self.OnButtonUnimacroEditor)
        wx.EVT_BUTTON(self, ID_BUTTONUnimacroInifilesDirectory, self.OnButtonUnimacroInifilesDirectory)
        wx.EVT_BUTTON(self, ID_BUTTONHelp5, self.OnButtonHelp5)
        wx.EVT_BUTTON(self, ID_BUTTONHelp1, self.OnButtonHelp1)
        wx.EVT_BUTTON(self, ID_BUTTONHelp4, self.OnButtonHelp4)
        wx.EVT_CHECKBOX(self, ID_CHECKBOXNatlinkDebug, self.OnCBNatlinkDebug)
        wx.EVT_BUTTON(self, ID_BUTTONClose, self.OnButtonClose)
        wx.EVT_BUTTON(self, ID_BUTTONUndo, self.OnButtonUndo)
        wx.EVT_BUTTON(self, ID_BUTTONNatlinkUserDirectory, self.OnButtonUnimacroEnableDisable)
        wx.EVT_BUTTON(self, ID_BUTTONVocolaEnable, self.OnButtonVocolaEnableDisable)
        wx.EVT_BUTTON(self, ID_BUTTONNatlinkEnable, self.OnButtonNatlinkEnable)
        wx.EVT_CHECKBOX(self, ID_CHECKBOXVocolaTakesLanguages, self.OnCBVocolaTakesLanguages)
        wx.EVT_CHECKBOX(self, ID_CHECKBOXDebugCallbackOutput, self.OnCBDebugCallback)
        wx.EVT_CHECKBOX(self, ID_CHECKBOXDebugLoad, self.OnDBDebugLoad)
        wx.EVT_BUTTON(self, ID_BUTTONHelp3, self.OnButtonHelp3)
        wx.EVT_BUTTON(self, ID_BUTTONHelp2, self.OnButtonHelp2)

        wx.EVT_BUTTON(self, ID_BUTTONunregister, self.OnButtonUnregister)
        wx.EVT_BUTTON(self, ID_BUTTONregister, self.OnButtonRegister)

        try:
            nf = __import__('natlinkconfigfunctions')
        except:

            self.error('natlinkinstallfunctions import failed')
            return

        class NatlinkConfigGUI(nf.NatlinkConfig):
            def __init__(self, parent=None):
                self.parent = parent
                super(NatlinkConfigGUI, self).__init__()
            def warning(self, text):
                """overload, to make it also in GUI visible"""
                super(NatlinkConfigGUI, self).warning(text)
                self.parent.warning(text)
        self.GUI = NatlinkConfigGUI(parent=self)
        try:
            self.cli = nf.CLI(self.GUI)
        except:
            self.error('could not start CLI instance')
            return
        try:
            nc = __import__('natlinkcorefunctions')
        except:
            self.error('could not import natlinkcorefunctions')
            return

        self.config = self.cli.config        
        title = self.frame.GetTitle()
        self.functions = self.getGetterFunctions()  # including self.checkboxes
        self.undoList = []
        # to see if things were changed:
        self.startInfo = copy.copy(self.config.getNatlinkStatusDict())
        version = self.startInfo['InstallVersion']
        if not title.endswith(version):
            title = '%s (%s)'% (title, version)
            self.frame.SetTitle(title)
        self.urgentMessage = None
        if self.cli.checkedConfig:
            # changed installation, message from natlinkconfigfunctions
            self.urgentMessage = "REREGISTER Natlink.dll and Close (restart) or Close right away to cancel"
            self.cli.checkedConfig = None
        self.setInfo()

    def warning(self, text, title='Message from Configure NatLink GUI'):
        if isinstance(text, basestring):
            Text = text
        else:
            Text = '\n'.join(text)
        dlg = wx.MessageDialog(self, Text, title,
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()               

    def getGetterFunctions(self):
        D = {}

##         '',
##        '', '', 'CoreDirectory',
##        '', '',
##        'VocolaUserDirectory'
        # checkboxes should have a getter, an event (OnCB...) and
        # be included in self.checkboxes list.
        
        D['DNSVersion'] = self.frame.infopanel.GetTextctrldnsversion
        D['DNSInstallDir'] = self.frame.infopanel.GetTextctrldnsinstallpath
        D['PythonVersion'] = self.frame.infopanel.GetTextctrlpythonversion
        D['CoreDirectory'] = self.frame.infopanel.GetTextctrlnatlinkcorepath
        D['UserDirectory'] = self.GetTextctrluserdirectory
        D['VocolaUserDirectory'] = self.GetTextctrlvocolauserdir
        D['WindowsVersion'] = self.frame.infopanel.GetTextctrlwindowsversion
        D['VocolaTakesLanguages'] = self.GetCheckboxvocolatakeslanguages
##        D['VocolaCommandFilesEditor'] = self.GetTextctrlvocolaeditor
        D['DebugCallback'] = self.GetCheckboxdebugcallbackoutput
        D['DebugLoad'] = self.GetCheckboxdebugload
        D['NatlinkDebug'] = self.GetCheckboxnatlinkdebug
        D['DNSIniDir'] = self.frame.infopanel.GetTextctrldnsinifilepath
        D['natlinkIsEnabled'] = self.GetButtonnatlinkenable
        D['vocolaIsEnabled'] = self.GetButtonvocolaenable
        
        D['unimacroIsEnabled'] = self.GetButtonnatlinkuserdirectory
        D['UnimacroUserDirectory'] = self.GetTextctrlunimacroinifilesdirectory
        D['UnimacroIniFilesEditor'] = self.GetTextctrlunimacroeditor
        self.checkboxes = ['VocolaTakesLanguages',
                           'DebugCallback', 'DebugLoad',
                           'NatlinkDebug']
        return D

    def error(self, text):
        """put error message on log panel and on status line"""
        print text
        print '-'*60
        self.frame.SetStatusText(text + ' (see log)')

    def setstatus(self, text):
        """put message on log panel and on status line"""
        print text
        self.frame.SetStatusText(text)

    def setInfo(self, leaveStatus=None):
        """extract data for the info controls
        """
        self.parent.Freeze()
        D = self.config.getNatlinkStatusDict()
##        print 'StatusDict:'
##        for k,v in D.items():
##            print '%s: %s'% (k,v)
##        print '-------'
        newStatus = {} # dict with keys NatLink, Vocola, Unimacro, values (value, changed) each of them
        
        
        try:
            changed = 0
    ##        print 'D.keys: %s'% D.keys()
            for key in D:
                if key in self.functions and self.functions[key]:
                    if key == 'VocolaCommandFilesEditor':
                        pass
                    func = self.functions[key]
##                    if func == None:
##                        print "no getter function for %s"% key
##                        continue
                    value = D[key]
                    thisOneChanged = 0
                    if value != self.startInfo[key]:
                        thisOneChanged = 1
                        changed = 1
                    if key in self.checkboxes:
                        if value:
                            func().SetValue(True)
                        else:
                            func().SetValue(False)
                            
                        if thisOneChanged:
                            func().SetForegroundColour(wx.RED)
                        else:
                            func().SetForegroundColour(wx.BLACK)
                    else:
                        # no checkbox:
                        label = str(value)
                        if key == 'DNSVersion':
                            # DNSFullVersion gives different information as 
                            # natspeak help window
                            label = '%s'% D[key]
                        elif key == 'PythonVersion':
                            # internal version (for dll, I believe) is  eg
                            # take first word of Fullversion as well.
                            fullPart = D['PythonFullVersion']
                            label = '%s (%s)'% (D[key], fullPart.split()[0])
                        elif value == None and key in ["DNSInstallDir", "DNSIniDir"]:
                            thisOneChanged = 1
                            label = "Please choose a valid path"
                            self.urgentMessage = "Invalid DNS path, see info panel"
                        if key.endswith('IsEnabled'):
                            if value:
                                label = 'Disable'
                            else:
                                label = 'Enable'
                            # compose newStatus for status text control:
                            part = key.split('Is')[0]
                            newStatus[part] = (value, thisOneChanged)
                        func().SetLabel(label)
                        if thisOneChanged:
                            func().SetForegroundColour(wx.RED)
                        else:
                            func().SetForegroundColour(wx.BLACK)

            # undo button:
            undoButton = self.GetButtonundo()
            if self.undoList:
                undoButton.Enable(True)
            else:
                undoButton.Enable(False)

            if D['natlinkIsEnabled']:
                value = True
            else:
                value = False
            for key in ['VocolaTakesLanguages',
                       'vocolaIsEnabled', 'unimacroIsEnabled',
                        'UserDirectory', 'VocolaUserDirectory']:
                if key in self.functions and self.functions[key]:
                    control = self.functions[key]()
                    control.Enable(value)
            
            self.composeStatusLine(newStatus)
            self.urgentStatusLine(self.urgentMessage)
            self.urgentMessage = None

        finally:
            self.parent.Thaw()

    def composeStatusLine(self, status):
        """takes a dict with NatLink, Vocola, Unimacro as keys,
        and a tuple (value, changed) as values. Value=0 means disable
        """
        L = []
        somethingChanged = 0
        for part in ('NatLink', 'Vocola', 'Unimacro'):
            value, changed = status[part.lower()]
            if value:
                enableddisabled = 'enabled'
            else:
                enableddisabled = 'disabled'
            if changed:
                somethingChanged = 1
                line = '%s will be %s'% (part, enableddisabled)
                line = line.upper()
                L.append(line)
            else:
                line = '%s is %s'% (part, enableddisabled)
                L.append(line)
                
            if part == 'NatLink' and enableddisabled == 'disabled':
                break # stop further status info
                    
        statusLine = '; '.join(L)
        control = self.GetTextctrlstatus()
        control.SetValue(statusLine)
        if somethingChanged:
            control.SetForegroundColour(wx.RED)
        else:
            control.SetForegroundColour(wx.BLACK)
        
    def urgentStatusLine(self, statusString=None):
        """writes a urgent message to the status text control
        """
        if not statusString: return
        control = self.GetTextctrlstatus()
        control.SetValue(statusString)
        control.SetForegroundColour(wx.RED)
        
        

    def do_command(self, *args, **kw):
        """a single letter, optionally followed by a path

        If you want undo information:
        Provide as 'undo' keyword argument

        for single arguments (checkboxes) provide the inverted character as undo
        (as is done in do_checkboxcommand)
        eg self.do_command('b', undo='B')

        for other commands (with paths) 'undo' must be provided as keyword argument,
        the parameters MUST be a tuple, length 1 for single letters, length 2 if a
        path is provided.
        eg self.do_command('V', undo=('v', 'path/to/previous'))

        when calling from undo button, provide 'noundo' = 1 as keyword argument.

    
        """
        if len(args) < 1:
            print 'empty command %s'% `args`
            return
        if len(args) > 2:
            print 'too many posional arguments: %s'% `args`
            return
        letter = args[0]
        if len(args) == 2:
            pathName = args[1]
        else:
            pathName = 'dummy'
        funcName = 'do_%s'% letter
        func = getattr(self.cli, funcName, None)
        if not func:
            mess = 'invalid command: %s'% letter
            print mess
            return mess
        result = func(pathName)
        # append to undoList
        if not 'undo' in kw:
            self.setInfo()
            return result
        undoInfo = kw['undo']
        if type(undoInfo) == types.TupleType and len(undoInfo) in [1,2]:
            undo = undoInfo
        elif isinstance(undoInfo, basestring):
            undo = (undoInfo,)
        else:
            print 'invalid undoInfo from button: %s'% `undoInfo`
            return result
        self.undoList.append(undo)
        self.setInfo(leaveStatus=result)
        return result

    def do_checkboxcommand(self, letter, control):
        """take value from control and do the command in upper or lowercase
        value = 1 (checked) lowercase command
        value = 0 (unchecked) uppercase command
        
        """
        value = control.GetValue()
        if value:
            doLetter = letter.lower()
            undoLetter = letter.upper()
        else:
            doLetter = letter.upper()
            undoLetter = letter.lower()                                       
        result = self.do_command(doLetter, undo=undoLetter)
        if not result:
            self.setstatus("checkbox option changed, restart NatSpeak to take effect")

       
    # WDR: methods for configurenatlink

    def GetTextctrlunimacroeditor(self):
        return self.FindWindowById( ID_TEXTCTRLunimacroeditor )

    def GetTextctrlunimacroinifilesdirectory(self):
        return self.FindWindowById( ID_TEXTCTRLunimacroinifilesDirectory )

    def GetTextctrlvocolaeditor(self):
        return self.FindWindowById( ID_TEXTCTRLVocolaEditor )

    def GetButtonvocolaeditor(self):
        return self.FindWindowById( ID_BUTTONVocolaEditor )

    def GetTextctrlstatus(self):
        return self.FindWindowById( ID_TEXTCTRLstatus )

    def GetButtonnatlinkuserdirectory(self):
        return self.FindWindowById( ID_BUTTONNatlinkUserDirectory )

    def GetButtonvocolaenable(self):
        return self.FindWindowById( ID_BUTTONVocolaEnable )

    def GetTextctrlvocolauserdir(self):
        return self.FindWindowById( ID_TEXTCTRLvocolauserdir )

    def GetTextctrluserdirectory(self):
        return self.FindWindowById( ID_TEXTCTRLuserDirectory )

    def GetCheckboxnatlinkdebug(self):
        return self.FindWindowById( ID_CHECKBOXNatlinkDebug )

    def GetButtonundo(self):
        return self.FindWindowById( ID_BUTTONUndo )

    def GetButtonnatlinkenable(self):
        return self.FindWindowById( ID_BUTTONNatlinkEnable )

    def GetCheckboxdebugcallbackoutput(self):
        return self.FindWindowById( ID_CHECKBOXDebugCallbackOutput )

    def GetCheckboxdebugload(self):
        return self.FindWindowById( ID_CHECKBOXDebugLoad )

    def GetCheckboxdebugoutput(self):
        return self.FindWindowById( ID_CHECKBOXDebugOutput )

    def GetCheckboxvocolatakeslanguages(self):
        return self.FindWindowById( ID_CHECKBOXVocolaTakesLanguages )

    def GetCheckboxdebugoutput(self):
        return self.FindWindowById( ID_CHECKBOXDebugOutput )

    def GetCheckboxenablenatlink(self):
        return self.FindWindowById( ID_CHECKBOXEnableNatlink )

    def GetTextctrldnsinifilepath(self):
        return self.FindWindowById( ID_TEXTCTRLdnsinifilepath )

    def GetTextctrldnsinstallpath(self):
        return self.FindWindowById( ID_TEXTCTRLDNSinstallpath )

    def GetTextctrlpythonversion(self):
        return self.FindWindowById( ID_TEXTCTRLpythonversion )

    def GetTextctrldnsversion(self):
        return self.FindWindowById( ID_TEXTCTRLDNSversion )


    def GetTextctrlregisternatlink(self):
        return self.FindWindowById( ID_TEXTCTRLregisternatlink )

    # WDR: handler implementations for configurenatlink

    def OnButtonVocolaCompatibility(self, event):
        title = "Unimacro features can be used by Vocola"
        dlg = DialogUnimacroVocolaCompatibiliy(self, title=title)
##        dlg.SetText(text)
        answer = dlg.ShowModal()
        if answer:
            print 'answer: %s'% answer
            if answer%2:
                print "(re)copy Unimacro.vch file to Vocola user commands directory"
                doLetter = 'l'
                statustext = 'Copied Unimacro.vch file to Vocola user commands directory'
                self.do_command(doLetter)
                self.setstatus(statustext)
                self.setInfo()
                answer -= 1
            if answer%4:
                print 'remove "include Unimacro.vch" lines from all Vocola command files in your Vocola user commands directory'
                doLetter = 'M'
                undoLetter = "m"
                statustext = 'Removed "include Unimacro.vch" lines from all Vocola command files in your Vocola user commands directory'
                self.do_command(doLetter, undo=undoLetter)
                self.setstatus(statustext)
                self.setInfo()
                answer -= 2
            if answer == 4:
                print 'add "include Unimacro.vch" lines to all Vocola command files in your Vocola user commands directory'
                doLetter = 'm'
                undoLetter = "M"
                statustext = 'added "include Unimacro.vch" lines to all Vocola command files in your Vocola user commands directory'
                self.do_command(doLetter, undo=undoLetter)
                self.setstatus(statustext)
                self.setInfo()
        else:
            print 'nothing chosen'
            

        

    def OnButtonUnimacroEditor(self, event):
        D = self.config.getNatlinkStatusDict()
        
        doLetter = 'p'
        undoLetter = 'P'
        statustext = 'Unimacro Editor is specified, this will take effect after you restart NatSpeak'

        # ask for the correct directory:
        dlg = wx.FileDialog(self.frame, "Choose the filename of your favorite Unimacro INI files editor please",
              style=wx.DD_DEFAULT_STYLE)
        ## search for Unimacro directory as proposal:
        old_path = D['UnimacroIniFilesEditor']
        Path = nc.getExtendedEnv("PROGRAMFILES")
        dlg.SetPath(Path)
        dlg.SetMessage('Please choose the filename of your favorite Unimacro INI files editor please\nPress cancel to return to default')
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            if new_path and os.path.isfile(new_path) and new_path.lower().endswith('.exe'):
                pass
            else:
                self.setstatus("no new valid (.exe) file specified")
                return
        else:
            if old_path:
                self.setstatus("Pressed Cancel, return to default")
                self.do_command( undoLetter, undo=(doLetter, old_path) )             
            return
        self.do_command(doLetter,new_path, undo=undoLetter)
        self.setstatus(statustext)
        self.setInfo()


#    def OnButtonVocolaEditor(self, event):
#        D = self.config.getNatlinkStatusDict()
#        
#        doLetter = 'w'
#        undoLetter = 'W'
#        statustext = 'Vocola Editor is specified, this will take effect after you restart NatSpeak'
#
#        # ask for the correct directory:
#        dlg = wx.FileDialog(self.frame, "Choose the filename of your favorite editor please",
#              style=wx.DD_DEFAULT_STYLE)
#        ## search for Unimacro directory as proposal:
#        old_path = D['VocolaCommandFilesEditor']
#        Path = nc.getExtendedEnv("PROGRAMFILES")
#        dlg.SetPath(Path)
#        dlg.SetMessage('Please choose the filename of your favorite editor please\nPress cancel to return to default')
#        if dlg.ShowModal() == wx.ID_OK:
#            new_path = dlg.GetPath()
#            if new_path and os.path.isfile(new_path) and new_path.lower().endswith('.exe'):
#                pass
#            else:
#                self.setstatus("no new valid (.exe) file specified")
#                return
#        else:
#            self.setstatus("Pressed Cancel, return to default")
#            self.do_command( undoLetter, undo=(doLetter, old_path) )             
#            return
#        self.do_command(doLetter,new_path, undo=undoLetter)
#        self.setstatus(statustext)
#        self.setInfo()
        

    def OnButtonLogInfo(self, event):
        self.cli.do_i("dummy")
        self.warning("See log panel")

    def OnButtonHelp5(self, event):
        print '---help on re(register) natlink.dll'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_r()
        text = \
"""
Help about re(register) natlink.dll you will find in the log panel

About this configure program window:

All actions are performed immediate, mostly doing something
in the registry section of NatLink. What is changed is shown in red.

The Undo button undoes these actions

If, for example, NatLink shows the button "Enable", it is currently disabled.

In order to let the changes take effect, you have to restart NatSpeak.
In some (rare) cases you have to restart the computer.

If you use Windows Vista, User Account Control must be turned off
before you can do the register/unregister actions!
"""
        self.warning(text)
        

    def OnButtonHelp1(self, event):
        text = \
"""The status line gives information about what you did or should do.

General status info is in the "info" panel, sometimes you should change things there as well.

Consult the "log" panel if you need more information.
"""
        self.warning(text)

    def OnButtonHelp4(self, event):
        print '---help on Enable/disable Unimacro/user grammars:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_n()
        self.cli.help_o()
        self.cli.help_p()
        self.cli.help_l()  # includes help for m and M
        text = \
"""
Unimacro is enabled by specifying a directory: the NatLink User Directory
(UserDirectory).

When you disable Unimacro, this UserDirectory setting is cleared from in the registry.

When Unimacro is enabled, you can also specify:
    - a directory where your own user (INI) files are located (e.g., a subdirectory
      in your "[My ]Documents" folder eg "[My ]Documents\Natlink\Unimacro")
      (default is the NatLink User Directory (UserDirectory), but preferably
      specify your own directory, in order to keep your ini file settings
      separate from the (python) grammar files)
    - a program for editing these user (INI) files, default is Notepad

For the above 2 settings: when you hit the button and subsequently Cancel, the
setting is cleared, and you fall back to the default value.

If you use your own NatLink grammar files, they can coexist with Unimacro in
the UserDirectory or you can specify your own UserDirectory.

Vocola can use Unimacro features, if both Vocola and Unimacro are enabled.
For easier access to the Unimacro Shorthand Commands from Vocola, an
include file (Unimacro.vch) can be copied into the Vocola User
Directory. More about this on http://qh.antenna.nl/unimacro/features/unimacroandvocola and
on http://vocola.net/v2

The necessary actions for this are performed through the "Vocola compatibility" button.

More information in the log panel """

        self.warning(text)


    def OnButtonClose(self, event):
        if self.undoList:
            self.warning('Please restart NatSpeak\n\n(in order to let the changes take effect)')
        self.parent.frame.Destroy()

    def OnButtonUndo(self, event):
        if self.undoList:
            cmd = self.undoList.pop()
            self.do_command(*cmd)
            self.setstatus("Did undo")
       

    def OnButtonUnimacroEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'n'
        if D['unimacroIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'Unimacro/user grammars is DISABLED, this will take effect after you restart NatSpeak'
            prevPath = D['UserDirectory']
            undoCmd = (undoLetter, prevPath)
            self.do_command(doLetter, undo=undoCmd)
            self.setstatus(statustext)
            self.setInfo()
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'Unimacro/user grammars is ENABLED, this will take effect after you restart NatSpeak'

        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE-wx.DD_NEW_DIR_BUTTON)
        ## search for Unimacro directory as proposal:
        Path = D['CoreDirectory']
        Path = os.path.normpath(os.path.join(Path, '..', '..', '..'))
        if os.path.isdir(Path):
            uPath = os.path.join(Path, 'Unimacro')
            if os.path.isdir(uPath):
                Path = uPath
                
        dlg.SetPath(Path)
        dlg.SetMessage('Please specify the directory where Unimacro/user grammar files are located')
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            if new_path and os.path.isdir(new_path):
                pass
            else:
                self.setstatus("no new valid directory specified")
                return
        else:
            self.setstatus("nothing specified")
            return
        self.do_command(doLetter,new_path, undo=undoLetter)
        self.setstatus(statustext)
        self.setInfo()

    def OnButtonUnimacroInifilesDirectory(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'o'
        if not self.config.UnimacroIsEnabled():
            self.warning("First enable Unimacro")
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'Unimacro INI Files Directory is set, this will take effect after you restart NatSpeak'

        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE)
        ## search for Unimacro directory as proposal:
        prevPath = D['UnimacroUserDirectory']
        if prevPath and os.path.isdir(prevPath):
            Path = prevPath
            undo = (doLetter, prevPath)
        else:
            prevPath = ""
            undo = (undoLetter, "")
            Path = nc.getExtendedEnv("PERSONAL")
            vPath = os.path.join(Path, "Unimacro")
            if os.path.isdir(vPath):
                Path = vPath

        dlg.SetPath(Path)
        dlg.SetMessage('Please specify the directory where Unimacro (user) INI files are/wil be located')
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            if new_path and os.path.isdir(new_path):
                pass
            else:
                self.setstatus("no directory specified: %s"% new_path)
                return
        else:
            self.setstatus("Pressed Cancel, return to default")
            if prevPath:
                self.do_command( undoLetter, undo=undo )
            else:
                self.do_command( undoLetter)
            return
        # correct OK:
        self.do_command(doLetter,new_path, undo=undo)
        self.urgentMessage = "changed UnimacroUserDirectory path, see info in log panel"
        self.setstatus(statustext)
        self.setInfo()
      

    def OnButtonVocolaEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'v'
        if D['vocolaIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'Vocola is DISABLED, this will take effect after you restart NatSpeak'
            prevPath = D['VocolaUserDirectory']
            undoCmd = (undoLetter, prevPath)
            self.do_command(doLetter, undo=undoCmd)
            self.setstatus(statustext)
            self.setInfo()
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'Vocola is ENABLED, this will take effect after you restart NatSpeak'

        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE)
        ## search for Unimacro directory as proposal:
        Path = nc.getExtendedEnv("PERSONAL")
        vPath = os.path.join(Path, "Vocola")
        if os.path.isdir(vPath):
            Path = vPath
                
        dlg.SetPath(Path)
        dlg.SetMessage('Please specify the directory where your Vocola Command Files are/will be located')
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            if new_path and os.path.isdir(new_path):
                pass
            else:
                self.setstatus("no new valid directory specified")
                return
        else:
            self.setstatus("nothing specified")
            return
        self.do_command(doLetter,new_path, undo=undoLetter)
        self.setstatus(statustext)
        self.setInfo()
        

    def OnButtonNatlinkEnable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'e'
        if D['natlinkIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'NatLink is DISABLED, this will take effect after you restart NatSpeak'
        else:
            doLetter = letter.lower()
            undoLetter = letter.upper()
            statustext = 'NatLink is ENABLED, this will take effect after you restart NatSpeak'
        self.do_command(doLetter, undo=undoLetter)
        self.setstatus(statustext)

        
    def OnCBNatlinkDebug(self, event):
        letter = 'g'
        control = self.GetCheckboxnatlinkdebug()
        self.do_checkboxcommand(letter, control)
        

    def OnCBVocolaTakesLanguages(self, event):
        letter = 'b'
        control = self.GetCheckboxvocolatakeslanguages()
        self.do_checkboxcommand(letter, control)

    def OnCBDebugCallback(self, event):
        letter = 'y'
        control = self.GetCheckboxdebugcallbackoutput()
        self.do_checkboxcommand(letter, control)
        

    def OnDBDebugLoad(self, event):
        letter = 'x'
        control = self.GetCheckboxdebugload()
        self.do_checkboxcommand(letter, control)



    def OnButtonHelp3(self, event):
        print '---help on Enable/disable Vocola:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_v()
        print '---help on additional Vocola options:'
        L = []
        L.append("Vocola is enabled by specifying a directory (VocolaUserDirectory)")
        L.append("where the Vocola command files are/will be located.")
        L.append("")
        L.append("When you disable Vocola, this setting is cleared in the registry.")
        L.append("")
        L.append("More information in the log panel")
        self.warning('\n'.join(L))

    def OnButtonHelp2(self, event):
        print '---help on Enable NatLink and corresponding functions:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_e()
        print '---help on NatLink debug options:'
        self.cli.help_x()
        text = """NatLink should be enabled before you can use Vocola and/or Unimacro.

When NatLink is disabled, Vocola and Unimacro will--consequently--be
disabled too.

Consult the "log" panel for more information."""
        self.warning(text)
        


    def OnButtonUnregister(self, event):
        self.do_command('R')
        self.warning("Close this program, Natspeak, all Python applications and\n\npossibly restart your computer\n\nbefore you run this program again!")
        self.urgentMessage = "Close this program, restart Natspeak, possibly computer"
        self.setInfo()

    def OnButtonRegister(self, event):
        self.do_command('r')
        self.warning("Close this program, Natspeak, all Python applications and\n\npossibly restart your computer\n\nbefore you run this program again!")
        self.urgentMessage = "Close this program, restart Natspeak, possibly computer"
        self.setInfo()
        

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_FRAME_STYLE ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.app = parent
        wx.EVT_MENU(self, ID_MENUhelp, self.OnMenuHelp)
        wx.EVT_MENU(self, ID_MENUClose, self.OnMenuClose)
                
        self.CreateStatusBar(1)
        self.SetStatusText("This is the Configure NatLink & Vocola & Unimacro GUI")
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
        self.infopanel =InfoPanel(self.nb, -1, name='infopanel')
        self.nb.AddPage(imageId=-1, page=self.infopanel, select=False,
              text='info')
        self.cpanel = ConfigureNatlinkPanel(self.nb, -1, name='configurepanel')
        self.nb.AddPage(imageId=-1, page=self.cpanel, select=True,
              text='configure')
        self.infopanel.cpanel = self.cpanel
## self.nb = wx.Notebook(name='notebook', parent=self, style=0)

            
    # WDR: methods for MyFrame
    def CreateMyMenuBar(self):
        self.SetMenuBar(MyMenuBarFunc() )

    def OnMenuClose(self, event):
        self.Destroy()

    def OnMenuHelp(self, event):
        text = ['This configure GUI makes it possible to configure NatLink, ',
                'including Vocola and Unimacro',"",
                'Detailed help is given through various help buttons and in the "log" panel',""
                'Written by Quintijn Hoogenboom, February, 2008/May, 2009,',
                'See also http://qh.antenna.nl/unimacro']
        self.warning('\n'.join(text))
                

    def warning(self, text, title='Message from Configure NatLink GUI'):                     
        dlg = wx.MessageDialog(self, text, title,
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()               

    
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
        self.frame = MyFrame( None, -1, "Configure NatLink & Vocola & Unimacro",
                              [110,80], [700,660] )
        self.frame.Show(True)  
        return True

app = MyApp(True)
app.MainLoop()

