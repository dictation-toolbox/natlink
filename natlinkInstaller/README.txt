We are slowly moving to a new stable release for Dragon 12 and NatLink too. (July 2014)

4.1kilo:
- adapt to Dragon13

4.1juliet:
- adapted playString function (Mark Lillibridge) via natlinkutils.playString (SendInput)
- natlinkmain.py has nearly all code caught in a try except statement

4.1india:
! MAJOR non-backward-compatible change to what names
  natlinkutils provides.
  - This was done because we are moving away from
    "from ... import *" statements in favour of "import ..."
    and qualify variables and functions.
  - In particular, recognitionMimic, getCursorPos, and Badwindow among
    others names now must be imported from natlink rather than from 
    natlinkutils.
  - See http://qh.antenna.nl/unimacro/installation/technicaldetails/natlinkutils.html for more details.
- Vocola suffered from this change, this is now fixed in Vocola 2.8.1I+

- more stable pyd files (hopefully)
- Title changed to "Messages from NatLink - built 01/01/2014"
- installer checks for 64 bit python (forbidden)
- many Unimacro improvements, action classes for specific programs (lines module hundred)
- autohotkey support
- New release of Vocola 2, 2.8.1:
    New in 2.8.1:
    
    ! Any series of one or more terms at least one of which is not optional
      or <_anything> can now be optional.
    
    * New built-ins, If and When.
    
    * Bug fix for list entries containing \'s with actions (produced invalid
      Python code).
    
    * Bug fix for adjacent <_anything>'s in command sequences

4.1hotel is removed.

From earlier "4.1" "beta" releases:
-This includes a new stable Vocola release which is complete implemented in python

-NatLink can be used with python 2.6 and python 2.7.

-Note that with Dragon 12, you should NOT use the speech model BestMatch V, which is used by default on most computers when create a new User Profile.

-Python 2.5 still can be used, but only for Dragon <= 11.

Consider to make a small donation to the 3 people who do most work for this development:
-Rudiger Wilke, working on the heart of the program, the NatLink core
-Mark Lillibridge, maintaining and improving Vocola 2
-Quintijn Hoogenboom, working at Unimacro and the installer stuff 
