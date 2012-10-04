import wx
import sys
import thread
import time
import traceback
import natlink

app = wx.App(False)

def close(frame = None, event = None):
    try:
        natlinkmain.natDisconnect()
        print 'natlink disconnected'
        time.sleep(10)
    except:
        pass
    sys.exit()
    app.ExitMainLoop()

class RedirectText:
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,text):
        self.out.WriteText(text)

class Application(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'NatLink (Dragon 12) Window', size=(550, 450))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        
        self.log = wx.TextCtrl(panel, -1, size=(500,400),
                               style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        sizer.Add(self.log, 0, wx.TOP|wx.LEFT|wx.EXPAND)        
        redir=RedirectText(self.log)
        sys.stdout=redir
        #print 'test'
        
        self.Bind(wx.EVT_CLOSE, close)        
        self.Centre()
        self.Show(True)

Application(None)
if not natlink.isNatSpeakRunning():
    print 'Start Dragon first, the rerun your starting up program (start_natlink.pyw)'
else:
    import natlinkmain # now the import does not start the macro system, if cmdLineStartup=1 (line 99 of natlinkmain.py)
    natlinkmain.start_natlink(doNatConnect=1)

try:
    app.MainLoop()    
except:
    pass
finally:
    close()


