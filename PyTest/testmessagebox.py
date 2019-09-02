import ctypes
MessageBox = ctypes.windll.user32.MessageBoxA

MessageBox(None, "message", "title", 0)