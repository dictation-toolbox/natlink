#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _sleeping.py
#   Simply by having this file in the Python command and control subsystem
#   directory, we turn the microphone on and put the system in a sleeping
#   state when NatSpeak first loads
#
# April 25, 1999
#   - packaged for external release
#
# March 3, 1999
#   - initial version
#

import natlink

natlink.setMicState('sleeping')

def unload():
    # must be defined, we do not need to do anything here
    pass
