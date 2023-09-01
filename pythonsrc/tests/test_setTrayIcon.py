def testIcons(self):
    r"""in the subdirectory icons of Unimacro there are 4 icons
    
    These should show up when natlink.setTrayIcon('_repeat.ico', 'tooltip', func) is called,
    but this is not working any more.
    There are also predefined icons, which are now stored in defaulticons directory of unimacro (fork)
    
    I don't know how to call these again...
    
It was tested in C:\DT\NatlinkDoug\pythonsrc\tests\unittestNatlink.py, this test could be taken out and put into
a pytest module!
    
**From natlink.txt**:
    
setTrayIcon( iconName, toolTip, callback )
This function, provided by Jonathan Epstein, will draw an icon in the
tray section of the tackbar.  

Pass in the absolute path to a Windows icon file (.ico) or pass in one
of the following predefined names: 
    'right', 'right2', 'down', 'down2',
    'left', 'left2', 'up', 'up2', 'nodir' 
You can also pass in an empty string (or nothing) to remove the tray
icon.

The toolTip parameter is optional.  It is the text which is displayed
as a tooltip when the mouse is over the tray icon.  If missing, a generic
tooltip is used.

The callback parameter is optional.  When used, it should be a Python
function which will be called when a mouse event occurs for the tray
icon.  The function should take one parameters which is the type of
mouse event:
    wm_lbuttondown, wm_lbuttonup, wm_lbuttondblclk, wm_rbuttondown, 
    wm_rbuttonup, wm_rbuttondblclk, wm_mbuttondown, wm_mbuttonup, 
    or wm_mbuttondblclk (all defined in natlinkutils)

Raises ValueError if the iconName is invalid.

The following functions are used in the natlinkmain base module.  You
should only used these if you are control NatSpeak using the NatLink module
instead of using Python as a command and control subsystem for NatSpeak. In
the later case, users programs should probably not use either of these two
functions because they replace the callback used by the natlinkmain module
which could prevent proper module (re)loading and user changes.
    
    """
    natlink.setTrayIcon('_repeat.ico')
    natlink.setTrayIcon('_down')   # ????
        
