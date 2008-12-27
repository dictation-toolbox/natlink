from simpscrp import *

Exec('notepad')
windows = EnumWindows()
flag = 0
for k in windows:
    if k[1] == 'Untitled - Notepad':
        SetForegroundWindow(k[0])
        flag = 1

if flag:
    SendKeys('Hello')