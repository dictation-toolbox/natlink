#!/bin/env python
#
# confignatlinkvocolaunimacro.py
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

import sys, traceback, win32ui
from configurenatlink_wdr import *
import os, os.path, string, copy, types
from natlinkconfigfunctions import ElevationError
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
        wx.EVT_CHECKBOX(self, ID_IncludeUnimacroInPythonPath, self.OnIncludeUnimacroInPythonPath)
        wx.EVT_BUTTON(self, ID_BUTTONCancel, self.OnCancel)
        wx.EVT_BUTTON(self, ID_BUTTONOK, self.OnOK)
        

    # WDR: methods for DialogUnimacroVocolaCompatibiliy

    def GetIncludeunimacroinpythonpath(self):
        return self.FindWindowById( ID_IncludeUnimacroInPythonPath )

    def GetCheckboxremoveunimacroincludelines(self):
        return self.FindWindowById( ID_CHECKBOXRemoveUnimacroIncludeLines )

    def GetCheckboxmakeunimacroincludelines(self):
        return self.FindWindowById( ID_CHECKBOXMakeUnimacroIncludeLines )

    def GetCheckboxrefreshunimacrovch(self):
        return self.FindWindowById( ID_CHECKBOXRefreshUnimacroVch )

    # WDR: handler implementations for DialogUnimacroVocolaCompatibiliy

    def OnIncludeUnimacroInPythonPath(self, event):
        pass

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
        return self.FindWindowById( ID_TEXTCTRLDNSVersion )

    def GetTextctrlpythonversion(self):
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
        #print text
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
        try:
            result = func(pathName)
        except ElevationError as e:
            mess = 'This program should run in elevated mode (%s).'% e.message
            self.error(mess)
            mess2  = mess = '\n\nPlease Close and run via start_configurenatlink.py\n\nPlease close Dragon too.'
            windowsMessageBox(mess)
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
        wx.EVT_CHECKBOX(self, ID_CHECKBOXVocolaTakesUnimacroActions, self.OnCheckVocolaTakesUnimacroActions)
        wx.EVT_CHECKBOX(self, ID_IncludeUnimacroInPythonPath, self.OnButtonIncludeUnimacroInPythonPath)
        wx.EVT_BUTTON(self, ID_BUTTONVocolaCompatibiliy, self.OnButtonVocolaCompatibility)
        wx.EVT_BUTTON(self, ID_BUTTONUnimacroEditor, self.OnButtonUnimacroEditor)
        wx.EVT_BUTTON(self, ID_BUTTONUnimacroEnable, self.OnButtonUnimacroEnableDisable)
        wx.EVT_BUTTON(self, ID_BUTTONHelp5, self.OnButtonHelp5)
        wx.EVT_BUTTON(self, ID_BUTTONHelp1, self.OnButtonHelp1)
        wx.EVT_BUTTON(self, ID_BUTTONHelp4, self.OnButtonHelp4)
        #wx.EVT_CHECKBOX(self, ID_CHECKBOXNatlinkDebug, self.OnCBNatlinkDebug)
        wx.EVT_BUTTON(self, ID_BUTTONClose, self.OnButtonClose)
        wx.EVT_BUTTON(self, ID_BUTTONUndo, self.OnButtonUndo)
        wx.EVT_BUTTON(self, ID_BUTTONUserEnable, self.OnButtonUserEnableDisable)
        wx.EVT_BUTTON(self, ID_BUTTONVocolaEnable, self.OnButtonVocolaEnableDisable)
        wx.EVT_BUTTON(self, ID_BUTTONNatlinkEnable, self.OnButtonNatlinkEnableDisable)
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

            self.error('natlinkconfigfunctions import failed')
            return

        class NatlinkConfigGUI(nf.NatlinkConfig):
            def __init__(self, parent=None):
                self.parent = parent
                super(NatlinkConfigGUI, self).__init__()
            def warning(self, text):
                """overload, to make it also in GUI visible"""
                super(NatlinkConfigGUI, self).warning(text)
                #self.parent.warning(text)
    
        self.GUI = NatlinkConfigGUI(parent=self)
        error = 0
        try:
            self.cli = nf.CLI(self.GUI)
        except ElevationError as e:
            mess = 'This program should run in elevated mode (%s).'% e.message
            self.error(mess)
            mess += '\n\nPlease Close and run via start_configurenatlink.pyw'
            windowsMessageBox(mess)
            error = 1
        except:
            self.error('could not start CLI instance')
            error = 1
        try:
            nc = __import__('natlinkcorefunctions')
        except:
            self.error('could not import natlinkcorefunctions')
            error = 1
        if not error:
            self.config = self.cli.config        
        title = self.frame.GetTitle()
        self.functions = self.getGetterFunctions()  # including self.checkboxes
        self.undoList = []
        # to see if things were changed:
        self.urgentMessage = None
        if not error:
            self.startInfo = copy.copy(self.config.getNatlinkStatusDict())
            version = self.startInfo['InstallVersion']
            if not title.endswith(version):
                title = '%s (%s)'% (title, version)
                self.frame.SetTitle(title)
            if self.cli.checkedConfig:
                # changed installation, message from natlinkconfigfunctions
                self.urgentMessage = "REREGISTER natlink.pyd and Close (restart) or Close right away to cancel (see log panel)"
                self.cli.checkedConfig = None
            if self.config.changesInInitPhase:
                if self.cli.getFatalErrors():
                    self.urgentMessage = "See the log panel for urgent startup information!!"
                else:
                    self.urgentMessage = "See the log panel for startup information, the init phase was succesful"
                
            self.setInfo()
        # now self.DNSName is known (NatSpeak or Dragon)
            self.DNSName = self.config.getDNSName()

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
        ##QH: should include DNSName maybe (2014)
        
        D['DNSVersion'] = self.frame.infopanel.GetTextctrldnsversion
        D['DNSInstallDir'] = self.frame.infopanel.GetTextctrldnsinstallpath
        D['PythonVersion'] = self.frame.infopanel.GetTextctrlpythonversion
        D['CoreDirectory'] = self.frame.infopanel.GetTextctrlnatlinkcorepath
        D['UserDirectory'] = self.GetTextctrlnatlinkuserdirectory
        D['VocolaUserDirectory'] = self.GetTextctrlvocolauserdirectory
        D['UnimacroUserDirectory'] = self.GetTextctrlunimacrouserdirectory
        D['WindowsVersion'] = self.frame.infopanel.GetTextctrlwindowsversion
        D['VocolaTakesLanguages'] = self.GetCheckboxvocolatakeslanguages
        D['VocolaTakesUnimacroActions'] = self.GetCheckboxvocolatakesunimacroactions
##        D['VocolaCommandFilesEditor'] = self.GetTextctrlvocolaeditor
        D['DebugCallback'] = self.GetCheckboxdebugcallbackoutput
        D['DebugLoad'] = self.GetCheckboxdebugload
        #D['NatlinkDebug'] = self.GetCheckboxnatlinkdebug
        D['DNSIniDir'] = self.frame.infopanel.GetTextctrldnsinifilepath
        D['natlinkIsEnabled'] = self.GetButtonnatlinkenable
        D['vocolaIsEnabled'] = self.GetButtonvocolaenable
        
        D['unimacroIsEnabled'] = self.GetButtonunimacroenable
        D['userIsEnabled'] = self.GetButtonuserenable
        # D['UnimacroEnable'] = self.GetTextctrlunimacroinifilesdirectory
        D['UnimacroIniFilesEditor'] = self.GetTextctrlunimacroeditor
        D['IncludeUnimacroInPythonPath'] = self.GetIncludeunimacroinpythonpath
        self.checkboxes = ['VocolaTakesLanguages',
                           'VocolaTakesUnimacroActions',
                           'DebugCallback', 'DebugLoad',
                           #'NatlinkDebug',
                           'IncludeUnimacroInPythonPath'
                           ]
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
##            if v:
##                print '%s: %s'% (k,v)
##        print '-------'
        newStatus = {} # dict with keys NatLink, Vocola, Unimacro, values (value, changed) each of them
        
        
        try:
            changed = 0
            for key in D:
                if key in self.functions and self.functions[key]:
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
                            # internal version (for pyd, I believe) is  eg
                            # take first word of Fullversion as well.
                            #fullPart = D['PythonFullVersion']
                            #label = '%s (%s)'% (D[key], fullPart.split()[0])
                            label = '%s'% D[key]
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
                       'vocolaIsEnabled', 'unimacroIsEnabled', 'userIsEnabled',
                        ]:
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
        for part in ('NatLink', 'Vocola', 'Unimacro', 'User'):
            value, changed = status[part.lower()]
            if value:
                enableddisabled = 'enabled'
            else:
                enableddisabled = 'disabled'
            if part == 'User':
                part = 'UserDirectory'
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
    
        try:
            result = func(pathName)
        except ElevationError as e:
            mess = 'This command needs elevated mode: %s'% e.message
            mess2 = mess + '\n\nClose this program and run "start_configurenatlink.py"'
            self.error(mess)
            self.warning(mess2)
            return mess
        
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
            self.setstatus("checkbox option changed, restart %s to take effect"% self.DNSName)

       
    # WDR: methods for configurenatlink
    def GetCheckboxvocolatakesunimacroactions(self):
        return self.FindWindowById( ID_CHECKBOXVocolaTakesUnimacroActions )

    def GetIncludeunimacroinpythonpath(self):
        return self.FindWindowById( ID_IncludeUnimacroInPythonPath )

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

    def GetButtonvocolaenable(self):
        return self.FindWindowById( ID_BUTTONVocolaEnable )
    

    def GetTextctrlvocolauserdirectory(self):
        return self.FindWindowById( ID_TEXTCTRLvocolauserdirectory )

    def GetTextctrlunimacrouserdirectory(self):
        return self.FindWindowById( ID_TEXTCTRLunimacrouserdirectory )


    def GetTextctrlnatlinkuserdirectory(self):
        return self.FindWindowById( ID_TEXTCTRLnatlinkuserdirectory )

    #def GetCheckboxnatlinkdebug(self):
    #    return self.FindWindowById( ID_CHECKBOXNatlinkDebug )

    def GetButtonundo(self):
        return self.FindWindowById( ID_BUTTONUndo )

    def GetButtonnatlinkenable(self):
        return self.FindWindowById( ID_BUTTONNatlinkEnable )

    def GetButtonnatlinkenable(self):
        return self.FindWindowById( ID_BUTTONNatlinkEnable )

    def GetButtonunimacroenable(self):
        return self.FindWindowById( ID_BUTTONUnimacroEnable )

    def GetButtonuserenable(self):
        return self.FindWindowById( ID_BUTTONUserEnable )

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

    def OnCheckVocolaTakesUnimacroActions(self, event):
        letter = 'a'
        control = self.GetCheckboxvocolatakesunimacroactions()
        self.do_checkboxcommand(letter, control)
        

    def OnButtonIncludeUnimacroInPythonPath(self, event):
        letter = 'f'
        control = self.GetIncludeunimacroinpythonpath()
        self.do_checkboxcommand(letter, control)

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
        statustext = 'Unimacro Editor is specified, this will take effect after you restart %s'% self.DNSName

        # ask for the correct directory:
        dlg = wx.FileDialog(self.frame, "Choose the filename of your favorite Unimacro INI files editor",
              style=wx.DD_DEFAULT_STYLE)
        ## search for Unimacro directory as proposal:
        old_path = self.config.isValidPath(D['UnimacroIniFilesEditor'], wantFile=1)
        if not old_path:
            old_path = self.config.isValidPath(self.config.userregnl.get('OldUnimacroIniFilesEditor'),
                                               wantFile=1)
        if old_path:
            dlg.SetPath(old_path)
        else:
            old_path = self.config.isValidPath("%PROGRAMFILES%", wantDirectory=1)
            if old_path:
                dlg.SetDirectory(old_path)
        dlg.SetMessage('Choose the filename of your favorite Unimacro INI files editor; Cancel for return to default')
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
#        statustext = 'Vocola Editor is specified, this will take effect after you restart %s'% self.DNSName
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
        print '---help on re(register) natlink.pyd'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_r()
        text = \
"""
Help about re(register) natlink.pyd you will find in the log panel

About this configure program:

All actions are performed immediate, mostly doing something
in the natlinkstatus.ini file of NatLink (in the MacroSystem/Core directory).

What is changed is shown in red. The Undo button undoes these actions.

If, for example, Vocola shows the button "Enable", it is currently disabled.

In order to let the changes take effect, you have to restart NatSpeak.

For the actions Enable/Disable NatLink and unregister/(re)register natlink.pyd
you should first close Dragon and you need elevated mode", so run start_configurenatlink.py
.
"""
        self.warning(text)
        

    def OnButtonHelp4(self, event):
        text = \
"""User Grammar files can be activated/deactivated by specifying the UserDirectory.

This directory should NOT be Unimacro or MacroSystem, as these are for Vocola and Unimacro.

Dragonfly users can use this option.
"""
        self.warning(text)

    def OnButtonHelp3(self, event):
        print '---help on Enable/disable Unimacro:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_n()
        self.cli.help_o()
        self.cli.help_p()
        self.cli.help_l()  # includes help for m and M
        text = \
"""
Unimacro is enabled by specifying the UnimacroUserDirectory.

When you disable Unimacro, this UnimacroUserDirectory setting is cleared from the natlinkstatus.ini file.

When Unimacro is enabled, you can also specify:
    - a program for editing these user (INI) files, default is Notepad

Vocola can use Unimacro features.
If Unimacro is NOT enabled, still this feature can be switched on if
also the checkbox 'Include Unimacro directory in PythonPath' is checked.

The necessary include file (Unimacro.vch) is copied into the Vocola User
Directory at startup of NatLink/Vocola/Unimacro when Dragon starts.

More control on the Unimacro features in the "Vocola compatibility" dialog.
"""

        self.warning(text)


    def OnButtonClose(self, event):
        if self.undoList:
            self.warning('Please restart %s\n\n(in order to let the changes take effect)'% self.DNSName)
        self.parent.frame.Destroy()

    def OnButtonUndo(self, event):
        if self.undoList:
            cmd = self.undoList.pop()
            self.do_command(*cmd)
            self.setstatus("Did undo")
       

    def OnButtonUnimacroEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'o'
        if D['unimacroIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'Unimacro is DISABLED, this will take effect after you restart %s'% self.DNSName
            prevPath = D['UnimacroUserDirectory']
            undoCmd = (undoLetter, prevPath)
            self.do_command(doLetter, undo=undoCmd)
            self.setstatus(statustext)
            self.setInfo()
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'Unimacro/user grammars is ENABLED, this will take effect after you restart %s'% self.DNSName

        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE-wx.DD_NEW_DIR_BUTTON)
        ## search for Unimacro User directory as proposal:
        oldPath = self.config.userregnl.get('OldUnimacroUserDirectory')
        if oldPath:
            oldPath = self.config.isValidPath(oldPath)
        if not oldPath:
            tryHome = self.config.isValidPath("~")
            if not tryHome:
                tryHome = self.config.isValidPath("%PERSONAL%")
            if tryHome:
                oldPath = tryHome
        if oldPath:                
            dlg.SetPath(oldPath)
        dlg.SetMessage('Specify the UnimacroUserDirectory, where your ini files are/will be located; this also enables Unimacro.')
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

    def OnButtonUserEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'n'
        if D['userIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'User Grammars are DISABLED, this will take effect after you restart %s'% self.DNSName
            prevPath = D['UserDirectory']
            undoCmd = (undoLetter, prevPath)
            self.do_command(doLetter, undo=undoCmd)
            self.setstatus(statustext)
            self.setInfo()
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'User Grammars are ENABLED, this will take effect after you restart %s'% self.DNSName

        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Please choose the UserDirectory, where your NatLink grammar files are located.",
              style=wx.DD_DEFAULT_STYLE-wx.DD_NEW_DIR_BUTTON)
        ## search for previous directory or other default:
        oldPath = self.config.userregnl.get('OldUserDirectory')
        if oldPath:
            oldPath = self.config.isValidPath(oldPath)
        if not oldPath:
            tryNatlink = os.path.join(D['CoreDirectory'], '..', '..', '..')
            oldPath = self.config.isValidPath(tryNatlink)
        if oldPath:                
            dlg.SetPath(oldPath)
        dlg.SetMessage('Please specify the UserDirectory, where user grammar files are located')
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            new_path = self.config.isValidPath(new_path, wantDirectory=1)
            if not new_path:
                self.setstatus("no new valid directory specified")
            elif new_path == D['UnimacroDirectory']:
                self.setstatus("Please do not specify Unimacro as UserDirectory")
                return
            elif new_path == D['BaseDirectory']:
                self.setstatus("Please do not specify BaseDirectory, used by Vocola, as UserDirectory")
                return
        else:
            self.setstatus("nothing specified")
            return
        self.do_command(doLetter,new_path, undo=undoLetter)
        self.setstatus(statustext)
        self.setInfo()

    def OnButtonVocolaEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        isValidPath = self.config.isValidPath
        letter = 'v'
        if D['vocolaIsEnabled']:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            statustext = 'Vocola is DISABLED, this will take effect after you restart %s'% self.DNSName
            prevPath = D['VocolaUserDirectory']
            undoCmd = (undoLetter, prevPath)
            self.do_command(doLetter, undo=undoCmd)
            self.setstatus(statustext)
            self.setInfo()
            return
        # now go for enable:
        doLetter = letter.lower()
        undoLetter = letter.upper()
        statustext = 'Vocola is ENABLED, this will take effect after you restart %s'% self.DNSName
    
    
    
        # ask for the correct directory:
        dlg = wx.DirDialog(self.frame, "Choose a directory please",
              style=wx.DD_DEFAULT_STYLE)
        ## search for Vocola directory as proposal:
        oldPath = self.config.userregnl.get('OldVocolaUserDirectory')
        if oldPath:
            oldPath = self.config.isValidPath(oldPath)
        if not oldPath:
            tryHome = self.config.isValidPath("~")
            if not tryHome:
                tryHome = self.config.isValidPath("%PERSONAL%")
            if tryHome:
                oldPath = tryHome
        if oldPath:                
            dlg.SetPath(oldPath)
        dlg.SetMessage('Specify the VocolaUserDirectory, where your Vocola Command Files are located; this also enables Vocola')
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
        

    def OnButtonNatlinkEnableDisable(self, event):
        D = self.config.getNatlinkStatusDict()
        letter = 'e'
        if D['natlinkIsEnabled']:
            # disable:
            doLetter = letter.upper()
            undoLetter = letter.lower()
            self.do_command(doLetter, undo=undoLetter)
            if self.config.NatlinkIsEnabled():
                statustext = 'NatLink is NOT DISABLED, please run this program in "elevated mode"'
            else:
                statustext = 'NatLink is DISABLED, this will take effect after you restart %s'% self.DNSName
                
        else:
            # enable:
            doLetter = letter.lower()
            undoLetter = letter.upper()
            self.do_command(doLetter, undo=undoLetter)
            if self.config.NatlinkIsEnabled():
                statustext = 'NatLink is ENABLED, this will take effect after you restart %s'% self.DNSName
            else:
                statustext = 'NatLink is NOT ENABLED, please run this program in "elevated mode"'
        self.setstatus(statustext)
        
    #def OnCBNatlinkDebug(self, event):   ## obsolete, QH 26-08-2013
    #    letter = 'g'
    #    control = self.GetCheckboxnatlinkdebug()
    #    self.do_checkboxcommand(letter, control)
        

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



    def OnButtonHelp2(self, event):
        print '---help on Enable/disable Vocola:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_b()
        self.cli.help_a()
        print '---help on additional Vocola options:'
        L = []
        L.append("Vocola is enabled by specifying a directory (VocolaUserDirectory)")
        L.append("where the Vocola Command files are/will be located.")
        L.append("")
        L.append("When you disable Vocola, this setting is cleared in the natlinkstatus.ini file.")
        L.append("")
        L.append('When you use more languages, eg speech profiles for English and Dutch, please read the log panel for the "Vocola multi languages" option.')
        L.append("")
        L.append('When you want to use Unimacro actions in your Vocola comman files, you can check the "Vocola takes Unimacro Actions" option.')
        L.append("More information about this on the NatLink/Vocola/Unimacro website")
        L.append("")
        self.warning('\n'.join(L))

    def OnButtonHelp1(self, event):
        print '---help on Enable NatLink and corresponding functions:'
        print 'note the letters correspond to the commands in the self.cli (command line interface)'
        self.cli.help_e()
        print '---help on NatLink debug options:'
        self.cli.help_x()
        text = """

This Enables or Disables NatLink. The state of NatLink is shown in the Status bar above, and is the opposite of the button text.

NatLink should be enabled before you can use Vocola and/or Unimacro or other python grammars, like Dragonfly.

When NatLink is disabled, Vocola and Unimacro will -- consequently -- be disabled too.

Note that you need elevated mode and possibly Dragon be switched off before you can Enable or Disable NatLink.

At first run after you installed NatLink, natlink.pyd is registered silently, but NatLink is still Disabled.

So in that case click on Enable for getting started.
"""
        self.warning(text)
        


    def OnButtonUnregister(self, event):
        self.do_command('R')
        self.warning("Close this program, and also close %s\n\nthen you run this program again in elevated mode via start_configurenatlink.py"% self.DNSName)
        # self.urgentMessage = "Close this program, restart %s, possibly computer"% self.DNSName
        self.setInfo()

    def OnButtonRegister(self, event):
        self.do_command('r')
        self.warning("Close this program, %s, all Python applications and\n\npossibly restart your computer\n\nbefore you run this program again!"% self.DNSName)
        self.urgentMessage = "Close this program, restart %s, possibly computer"% self.DNSName
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

def windowsMessageBox(message, title="NatLink configure program"):
    """do messagebox from windows, no wx needed
    """
    win32ui.MessageBox(message, title)
    


class MyApp(wx.App):
    def OnInit(self):
        # wx.InitAllImageHandlers()
        self.frame = MyFrame( None, -1, "Configure NatLink & Vocola & Unimacro",
                              [110,80], [750,735] )
        self.frame.Show(True)
        return True
try:
    app = MyApp(True)
except:
    import sys, traceback
    # traceback.print_exception(type, value, traceback[, limit[, file]])
    traceback.print_exc(file=open("configurenatlink_error.txt", "w")) 
    mess  = traceback.format_exc(limit=1)
    mess += '\n\nMore info in configurenatlink_error.txt'
    windowsMessageBox(mess, "Error at startup of configurenatlink")
    sys.exit(1)
else:
    app.MainLoop()

