import sys

import natlink

class NewStdout(object):
    softspace=1
    def write(self,text):
        # if text.find('\x00') >= 0:
        #     text = text.replace('\x00', '')
        #     text = "===Warning, text contains null bytes==\n" + text
        # if type(text) == str:
        #     text = text.encode('cp1252')
        natlink.displayText(text, 0)
    def flush(self):
        pass

class NewStderr(object):
    softspace=1
    def write(self,text):
        # if text.find('\x00') >= 0:
        #     text = text.replace('\x00', '')
        #     text = "===Warning, text contains null bytes===\n" + text
        # if type(text) == str:
        #     text = text.encode('cp1252')
        natlink.displayText(text, 1)
    def flush(self):
        pass


sys.stdout = NewStdout()
sys.stderr = NewStderr()