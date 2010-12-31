import os
from win32api import ShellExecute

path = os.path.join(os.path.dirname(__file__), "start_configurenatlink.bat")
ShellExecute(0, "runas", path, None, "", 1)
