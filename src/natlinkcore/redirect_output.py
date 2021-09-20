#pylint:disable=C0115, C0114, C0116, R0201
# new redirect trick, starting june 2020 (by Jan Scheffczyk)
# this module is imported by natlink.pyd.
# So apart from starting natlink via natlink.pyd (as called from Dragon),
# redirection of stdout and stderr is never done (unless you import this module)
# in 2021, added outputDebugString to stderr.

import sys
from pydebugstring.output import outputDebugString
import natlink

class NewStdout:
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

class NewStderr:
    softspace=1
    def write(self,text):
        # if text.find('\x00') >= 0:
        #     text = text.replace('\x00', '')
        #     text = "===Warning, text contains null bytes===\n" + text
        # if type(text) == str:
        #     text = text.encode('cp1252')

        natlink.displayText(text, 1)
        outputDebugString(text)
    def flush(self):
        pass


sys.stdout = NewStdout()
sys.stderr = NewStderr()
