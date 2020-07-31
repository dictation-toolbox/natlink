# new redirect trick, starting june 2020 (by Jan Scheffczyk)
# this module is imported by natlink.pyd.
# So apart from starting natlink via natlink.pyd (as called from Dragon),
# redirection of stdout and stderr is never done (unless you import this module)

import sys

import natlink


class NewStdout:
    softspace = 1

    def write(self, text):
        natlink.displayText(text, 0)

    def flush(self):
        pass


class NewStderr:
    softspace = 1

    def write(self, text):
        natlink.displayText(text, 1)

    def flush(self):
        pass


sys.stdout = NewStdout()
sys.stderr = NewStderr()
