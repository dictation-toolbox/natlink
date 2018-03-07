#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _mouse.py
#   Sample macro file which implements mouse and keyboard movement modes
#   similar to DragonDictate for Windows
#
# April 1, 2000
#   Updates from Jonathan Epstein
#   - cancel arrow movement when the active window changes
#   - add support for tray icon during arrow movement
#

# In the grammar we map some keywords into pixel counts according to the
# following dictionary.  These numbers can be safely changed within reason.

amountDict = { 
    'little':3,     # as in 'move a little left'
    'lot':10 }      # as in 'move left a lot'

# For caret movement, this represents the default speed in milliseconds
# between arrow keys

defaultMoveSpeed = 250

# For caret movement, this is the rate change applied when you make it
# faster.  For example, 1.5 is a 50% speed increase.

moveRateChange = 2.0

# For mouse movement, this represents the default speed in milliseconds
# between pixel movements and the default number of pixels per move.  We
# do not want the update rate to be less than 50 milliseconds so if it 
# gets faster than that, we adjust the mouse pixels instead.

defaultMouseSpeed = 100
defaultMousePixels = 1

# For mouse movement, this is the rate change applied when you make it
# faster.  For example, 1.5 is a 50% speed increase.

mouseRateChange = 3.0

############################################################################
#
# Here are some of our instance variables
#
#   self.haveCallback   set when the timer callback in installed
#   self.curMode        1 for caret movement, 2 for mouse movement, or None
#   self.curSpeed       current movement speed (milliseconds for timer)
#   self.curPixels      for mouse movement, pixels per move
#   self.lastClock      time of last timer callback or 0
#   self.curDirection   direction of movement as string
#

import string       # for atoi
import time         # for clock
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    # when we unload the grammar, we must make sure we clear the timer
    # callback so we keep a variable which is set when we currently own
    # the timer callback

    def __init__(self):
        self.haveCallback = 0
        self.curMode = None
        self.iconState = 0
        GrammarBase.__init__(self)

    def unload(self):
        if self.haveCallback: 
            natlink.setTimerCallback(None,0)
            self.haveCallback = 0
        GrammarBase.unload(self)

    # This is our grammar.  The rule 'start' is what is normally active.  The
    # rules 'nowMoving' and 'nowMousing' are used when we are in caret or
    # mouse movement mode.

    gramDefn = """
        # this is the rule which is normally active
        <start> exported = <startMoving> | <startMousing> | 
            <nudgeMouse> | <mouseButton>;

        # this rule is active when we are moving the caret
        <nowMoving> exported =
            [ move ] ( {direction} | [much] faster | [much] slower ) |
            stop [ moving ];

        # this rule is active when we are moving the mouse
        <nowMousing> exported =
            [ move ] ( {direction} | faster | slower ) |
            stop [ moving ] | <mouseButton> | <mouseButton>;

        # here are the subrules which deal with caret movement
        <startMoving> = move {direction} | start moving {direction};

        # here are the subrules which deal with mouse movement
        <startMousing> = [ start moving ] mouse {direction};
        <nudgeMouse> = 
            nudge mouse {direction} |
            [ move ] mouse {direction} ( a little | a lot | {count} pixels ) |
            [ move ] mouse ( a little | a lot | {count} pixels ) {direction};
        <mouseButton> = 
            [ mouse ] [ left | middle | right ] [ single | double ] click;
    """

    # These are the lists which we use in our grammar.  The directions and 
    # counts are implemented as lists to make parsing easier (words from
    # lists are referenced as part of the rule which includes the list).

    listDefn = {
        'direction' : ['up','down','left','right'],
        'count' : ['1','2','3','4','5','6','7','8','9','10','11','12','13',
            '14','15','16','17','18','19','20','25','30','35','40','45','50'] }

    # Load the grammar, build the direction and count lists and activate the
    # main rule ('start')
    
    def initialize(self):
        self.load(self.gramDefn)
        for listName in list(self.listDefn.keys()):
            self.setList(listName,self.listDefn[listName])
        self.activateSet(['start'],exclusive=0)

    # This subroutine moves the mouse cursor in an indicated direction
    # by an indicated number of pixels

    def moveMouse(self,direction,count):
        xPos,yPos = natlink.getCursorPos()
        if direction == 'up': yPos = yPos - count
        elif direction == 'down': yPos = yPos + count
        elif direction == 'left': xPos = xPos - count
        elif direction == 'right': xPos = xPos + count
        xSize,ySize = natlink.getScreenSize()
        if xPos < 0: xPos = 0
        if xPos >= xSize: xPos = xSize - 1
        if yPos < 0: yPos = 0
        if yPos >= ySize: yPos = ySize - 1
        natlink.playEvents([(wm_mousemove,xPos,yPos)])

    # This subroutine cancels any active movement mode
    
    def cancelMode(self):
        self.curMode = None
        if self.haveCallback: 
            natlink.setTimerCallback(None,0)
            self.haveCallback = 0
        self.activateSet(['start'],exclusive=0)
        natlink.setTrayIcon()

    # This function is called on a timer event.  If we are in a movement
    # mode then we move the mouse or caret by the indicated amount.
    #
    # The apparent speed for mouse movement is the speed divided by the
    # number of pixels per move.  We calculate the number of pixels per
    # move to ensure that the speed is never faster than 50 milliseconds.

    def onTimer(self):
        if self.lastClock:
            diff = int( (time.clock() - self.lastClock) * 1000 )
            self.lastClock = time.clock()
        if self.curMode == 1:
            moduleInfo = natlink.getCurrentModule()
            if natlink.getMicState() == 'on' and moduleInfo == self.moduleInfo:
                self.setTrayIcon(1)
                # Note: it is often during a playString operation that the
                # "stop moving" command occurs
                natlink.playString('{'+self.curDirection+'}')
            else:
                self.cancelMode()
        elif self.curMode == 2:
            self.moveMouse(self.curDirection,self.curPixels)

    # This handles the nudgeMouse rule. We want to extract the direction
    # and the count or amount.

    def gotResults_nudgeMouse(self,words,fullResults):
        self.cancelMode()
        direction = findKeyWord(words,self.listDefn['direction'])
        count = findKeyWord(words,self.listDefn['count'])
        amount = findKeyWord(words,list(amountDict.keys()))
        if count: 
            count = string.atoi(count)
        elif amount: 
            count = amountDict[amount]
        self.moveMouse(direction,count)

    # This handles the mouseButton rule.  We want to extract the button
    # name (if specified) and whether this is a single or double click.

    def gotResults_mouseButton(self,words,fullResults):
        self.cancelMode()
        which = findKeyWord(words,['left','right','middle'])
        if not which: which = 'left'
        if 'double' in words: count = 2
        else: count = 1
        buttonClick(which,count)

    # This handles the startMoving rule.  We only need to extract the
    # direction.  To turn on cursor movement mode we need to install a 
    # timer callback (warning: this is global) and set the recognition
    # state to be exclusively from the rule <nowMoving>.  The cursor only
    # moves in the timer callback itself.

    def gotResults_startMoving(self,words,fullResults):
        self.cancelMode()
        direction = findKeyWord(words,self.listDefn['direction'])
        self.curMode = 1
        self.curDirection = direction
        self.setTrayIcon(0)
        self.moduleInfo = natlink.getCurrentModule()
        self.curSpeed = defaultMoveSpeed
        self.lastClock = time.clock()
        natlink.setTimerCallback(self.onTimer,defaultMoveSpeed)
        self.haveCallback = 1
        self.activateSet(['nowMoving'],exclusive=1)

    # This handles the nowMoving rule.  We want to extract the keyword which
    # tells us what to do.

    def gotResults_nowMoving(self,words,fullResults):
        direction = findKeyWord(words,self.listDefn['direction'])
        if direction:
            self.curDirection = direction
            self.setTrayIcon(0)
        elif 'stop' in words:
            self.cancelMode()
        elif 'faster' in words:
            speed = int(self.curSpeed / moveRateChange)
            if 'much' in words:
                speed = int(speed / (moveRateChange*moveRateChange))
            if speed < 50: speed = 50
            self.curSpeed = speed
            natlink.setTimerCallback(self.onTimer,speed)
        elif 'slower' in words:
            speed = int(self.curSpeed * moveRateChange)
            if 'much' in words:
                speed = int(speed * (moveRateChange*moveRateChange))
            if speed > 4000: speed = 4000
            self.curSpeed = speed
            natlink.setTimerCallback(self.onTimer,speed)

    # This handles the startMousing rule.  We only need to extract the
    # direction.  To turn on cursor movement mode we need to install a 
    # timer callback (warning: this is global) and set the recognition
    # state to be exclusively from the rule <nowMoving>.  The cursor only
    # moves in the timer callback itself.

    def gotResults_startMousing(self,words,fullResults):
        self.cancelMode()
        direction = findKeyWord(words,self.listDefn['direction'])
        self.curMode = 2
        self.curDirection = direction
        self.curSpeed = defaultMouseSpeed
        self.curPixels = defaultMousePixels
        self.lastClock = time.clock()
        natlink.setTimerCallback(self.onTimer,defaultMouseSpeed)
        self.haveCallback = 1
        self.activateSet(['nowMousing'],exclusive=1)

    # This handles the nowMousing rule.  We want to extract the keyword which
    # tells us what to do.

    def gotResults_nowMousing(self,words,fullResults):
        direction = findKeyWord(words,self.listDefn['direction'])
        if direction:
            self.curDirection = direction
        elif 'stop' in words:
            self.cancelMode()
        elif 'faster' in words:
            speed = int(self.curSpeed / moveRateChange)
            pixels = self.curPixels
            while speed < 50: 
                speed = speed * 2
                pixels = pixels * 2
            if pixels > 10: pixels = 10
            self.curSpeed = speed
            self.curPixels = pixels
            natlink.setTimerCallback(self.onTimer,speed)
        elif 'slower' in words:
            speed = int(self.curSpeed * moveRateChange)
            pixels = self.curPixels
            while pixels > defaultMousePixels and speed >= 2*50:
                speed = speed / 2
                pixels = pixels / 2
            if speed > 2000: speed = 2000
            self.curSpeed = speed
            self.curPixels = pixels
            natlink.setTimerCallback(self.onTimer,speed)

    # This turns on the tray icon depending on the movement direction.
    # self.iconState is used to toggle the image to animate the icon.            
    def setTrayIcon(self,toggleIcon):
        iconName = self.curDirection
        toolTip = 'moving '+self.curDirection
        if not toggleIcon or self.iconState:
            self.iconState = 0
        else:
            self.iconState = 1
            iconName = iconName + '2'
        natlink.setTrayIcon(iconName,toolTip,self.onTrayIcon)

    # This is called if the user clicks on the tray icon.  We simply cancel
    # movement in all cases.
    def onTrayIcon(self,message):
        self.cancelMode()

# This is a simple utility subroutine.  It takes two lists of words and 
# returns the first word it finds which is in both lists.  We use this to
# extract special words (like the direction) from recognition results.

def findKeyWord(list1,list2):
    for word in list1:
        if word in list2: 
            return word
    return None

#
# Here is the initialization and termination code.  See wordpad.py for more
# comments.
#

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None

