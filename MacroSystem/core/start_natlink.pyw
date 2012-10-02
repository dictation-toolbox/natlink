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

    def write(self,string):
        self.out.WriteText(string)


last_module = []
def heartbeat():
    global last_module
    pass
    #print 'heartbeat!'
    #try:
    #    current_module = natlink.getCurrentModule()
    #    if current_module != last_module:
    #        last_module = current_module
    #        print "virtually toggling microphone..."
    #        natlinkmain.changeCallback("mic", "on")
    #        call_got_begin(current_module)
    #except:
    #    traceback.print_exc()

def call_got_begin(module_info):
    for module in sys.modules.keys():
        try:
            sys.modules[module].thisGrammar.beginCallback(module_info)
            print " called gotBegin for " + module
        except:
            pass

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
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.Bind(wx.EVT_CLOSE, close)        
        self.Centre()
        self.Show(True)
        #self.timer.Start(250)        

    def update(self, event):
        pass
        #heartbeat()

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


