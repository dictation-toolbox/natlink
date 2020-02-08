#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# natlinkutils.py
#   This file contains utility classes and functions for grammar files.
#
# November 2018 (QH)
#   Accept unicode input, convert to python 2.6 string
#
# September 2016 (QH)
# - rulenumbers are one lower than before in Dragon 15, fix in resultsCallback.
#
# Februari 2016 (QH):
# - added modifier keys for buttonClick (shift, ctrl, alt)
# - add a {shift} in front of every "normal" playString call, thus preventing the double/dropping character bug.
#   (the {shift} key is language specific, natlinkmain hold the correct string)
# September 2013 (QH):
# use import natlink instead of from natlink import *, forcing qualifying all calls to natlink functions from this module.
# March 2010 (QH):
#   - added deactivateSet() function in GrammarBase
#   - added exceptlist optional variable to activateAll method of GrammarBase
#   - added callRuleResultsFunctions in resultsCallback, so the calling of
#         the rule result functions can be overloaded (for DocstringGrammar)
# Dec 2009:
#   - added the variable self.doOnlyGotResultsObject, which can be set inside a user gotResultsObject
#     routine, in order to NOT further process the recognition
#     (for kaiser_dictation.py, dictation to target application, QH)
# August 17, 2009
#   - added throughWords in SelectGramBase, in order to make more
#     throughWords possible, like "through" and "until".
# April 1, 2000
#   - reformated this file to move documentation to the beginning of
#     the classes
#   - added DictGramBase and SelectGramBase and split common functions
#     into shared internal GramClassBase
#
# Documentation
#
# This file contains three base classes and some useful constants and
# utility functions.
#
#   GrammarBase - base class for all command and control grammars.
#       See documentation below just before the class definition.
#
#   DictGramBase - base class for all pure dictation grammars.
#       See documentation below just before the class definition.
#
#   SelectGramBase - base class for all selection grammars.
#       See documentation below just before the class definition.
#
#   buttonClick( btnName='left',count=1 )
#       This function simulates a button click or button double click.  Pass
#       in the button name ('left','right' or 'middle') and the count (1 or
#       2)
#
#   matchWindow( moduleInfo, modName, wndText )
#       A utility function which determines whether moduleInfo matches a
#       specified module name and window title.  Returns window handle on
#       match and None on mismatch. Note that moduleInfo may be ("","",0)
#       which we should handle cleanly.
#
#   See also the constants at the top of this file.

############################################################################
# experiment Mark (Vocola Extension)
# making this experiment final:
useMarkSendInput = 1
if useMarkSendInput:
    import ExtendedSendDragonKeys
    import SendInput

    from ExtendedSendDragonKeys import senddragonkeys_to_events
    from SendInput import send_input
    # print "======\nSendInput, a Vocola extension written by Mark Lillibridge,  is "
    # print "used for all normal playString calls!  If you do not want this,"
    # print "change the variable useMarkSendInput to 0 in line 65 of"
    # print "natlinkutils.py.  This file is located in the directory "
    # print "NatLink\MacroSystem\Core.  Then restart Dragon...\n======"
# 
import os
import os.path
import copy
import types
import struct
import time
#from natlink import *
import natlink
#from gramparser import *
import gramparser
import natlinkmain
import utilsqh
import sys
import traceback
DNSVersion = natlinkmain.DNSVersion
# print 'DNSVersion (natlinkutils) %s'% DNSVersion
debugLoad = natlinkmain.debugLoad

# The following constants define the common windows message codes which
# are passed to playEvents.

wm_keydown = 0x0100
wm_keyup = 0x0101
wm_syskeydown = 0x0104
wm_syskeyup = 0x0105
wm_mousemove = 0x0200
wm_lbuttondown = 0x0201
wm_lbuttonup = 0x0202
wm_lbuttondblclk = 0x0203
wm_rbuttondown = 0x0204
wm_rbuttonup = 0x0205
wm_rbuttondblclk = 0x0206
wm_mbuttondown = 0x0207
wm_mbuttonup = 0x0208
wm_mbuttondblclk = 0x0209

# common keystroke constants used during mouse movement

vk_shift = 0x10
vk_control = 0x11
vk_menu = 0x12      # alt-key

# The following constants are the flag values for playString.  The names
# come from the NatSpeak header files.  Refer to natlink.txt for descriptions.

hook_f_shift = 0x01
hook_f_alt = 0x02
hook_f_ctrl = 0x04
hook_f_rightshift = 0x08
hook_f_rightalt = 0x10
hook_f_rightctrl = 0x20
hook_f_extended = 0x40
hook_f_defertermination = 0x100
hook_f_systemkeys = 0x200
hook_f_syskeys_checkshifts = 0x400
genkeys_f_scan_code = 0x10000
genkeys_f_uppercase = 0x20000
genkeys_f_lowercase = 0x40000
genkeys_f_capitalize = 0x80000
genkeys_f_virtkey = 0x200000
genkeys_f_usekeypad = 0x400000

# These are the flags which are returned from getWordInfo

dgnwordflag_useradded		= 0x00000001
dgnwordflag_nodelete		= 0x00000008
dgnwordflag_passive_cap_next= 0x00000010
dgnwordflag_active_cap_next	= 0x00000020
dgnwordflag_uppercase_next	= 0x00000040
dgnwordflag_lowercase_next	= 0x00000080
dgnwordflag_no_space_next	= 0x00000100
dgnwordflag_two_spaces_next	= 0x00000200
dgnwordflag_cond_no_space	= 0x00000400
dgnwordflag_cap_all			= 0x00000800
dgnwordflag_uppercase_all	= 0x00001000
dgnwordflag_lowercase_all	= 0x00002000
dgnwordflag_no_space_all	= 0x00004000
dgnwordflag_reset_no_space	= 0x00008000
dgnwordflag_is_period		= 0x00020000
dgnwordflag_no_formatting	= 0x00040000
dgnwordflag_no_space_change	= 0x00080000
dgnwordflag_no_cap_change	= 0x00100000
dgnwordflag_no_space_before	= 0x00200000
dgnwordflag_reset_uc_lc_caps= 0x00400000
dgnwordflag_new_line		= 0x00800000
dgnwordflag_new_paragraph	= 0x01000000
dgnwordflag_title_mode		= 0x02000000
dgnwordflag_space_bar		= 0x08000000
dgnwordflag_topicadded		= 0x40000000
dgnwordflag_DNS8newwrdProp  = 0x20000000
 

#---------------------------------------------------------------------------
# matchWindow
#
# A utility function which determines whether moduleInfo matches a specified
# module name and window title.  Returns window handle on match and None on
# mismatch.
#
# Note that moduleInfo may be ("","",0) which we should handle cleanly.

def matchWindow(moduleInfo, modName, wndText):
    if len(moduleInfo)<3 or not moduleInfo[0]: return None
    curName = getBaseName(moduleInfo[0]).lower()
    if curName != modName: return None
    if moduleInfo[1].find(wndText) == -1: return None
    return moduleInfo[2]

#---------------------------------------------------------------------------
# buttonClick
#    
# This function simulates a button click or button double click.  Pass in the
# button name ('left','right' or 'middle') and the count (1 or 2)
#


def buttonClick(btnName='left', count=1, modifiers=None):
    """performs a button (double) click of the mouse
    
    without parameters: a single left click
    accepted values:
     - btnName: 'left', 'right' or 'middle', or 1, 2, 3
     - count: 1 or 2 or 3 (3 not fully tested)
     -  modifiers: 'shift', 'ctrl', 'alt', 'menu' ('alt' and 'menu' are identical)
            (see function getModifierKeyCodes below)
            (if you want more modifiers, separate by "+" or " ", eg. "shift+ctrl")
    """
    x, y = natlink.getCursorPos()
    
    unimacroButtons = {1:'left', 2:'right', 3:'middle'}
    if btnName in [1,2,3]:
        btnName = unimacroButtons[btnName]
        
    singleLookup = { 
        'left':  [(wm_lbuttondown,x,y),(wm_lbuttonup,x,y)],
        'right': [(wm_rbuttondown,x,y),(wm_rbuttonup,x,y)],
        'middle':[(wm_mbuttondown,x,y),(wm_mbuttonup,x,y)] }
    doubleLookup = {
        'left':  [(wm_lbuttondblclk,x,y),(wm_lbuttonup,x,y)],
        'right': [(wm_rbuttondblclk,x,y),(wm_rbuttonup,x,y)],
        'middle':[(wm_mbuttondblclk,x,y),(wm_mbuttonup,x,y)] }

    try:
        single = singleLookup[btnName]  # KeyError means invalid button name
        double = doubleLookup[btnName]
    except KeyError:
        raise ValueError('buttonClick, invalid "btnName": %s'% btnName)
        
    events = [] # collect all events in a list
    if modifiers:
        try:
            keycodes = getModifierKeyCodes(modifiers)
        except KeyError:
            raise ValueError('buttonClick, invalid "modifiers": %s'% repr(modifiers))
        for k in keycodes:
            events.append( (wm_keydown, k) )
        # print "modifiers keycodes: %s"% keycodes
        
    if count == 1:
        events.extend( single )
    elif count == 2:
        events.extend( single )
        events.extend( double )
    elif count == 3:
        events.extend( single )
        events.extend( single )
        events.extend( single )
    else:
        raise ValueError( 'buttonClick, invalid "count": %s'% count )

    if modifiers:
        for k in keycodes:
            events.append( (wm_keyup, k) )
    if events:
        # print 'buttonClick events: %s'% events
        natlink.playEvents(events)

 
def getModifierKeyCodes(modifiers):
    """return a list with keycodes for modifiers
    
    input can be a list of valid modifiers (ctrl, shift or menu == alt ),
    either in a sequence or as single string. If string contains the + symbol or a space,
    the string is split before searching the keycodes
    
    Invalid input raises a KeyError.
    Testing in unittestNatLink, see testNatlinkUtilsFunctions
    
    """
    modifier_dict = dict(ctrl=vk_control,
                         shift=vk_shift,
                         menu=vk_menu,
                         alt=vk_menu)   # added alt  == menu
    if not modifiers: return

    if type(modifiers) == str:
        modifiers = modifiers.replace("+", " ").split()
    return [modifier_dict[m] for m in modifiers]

# temporary hopefully, QH, 4-9-2013  now 22-10-2013:
# reverting to Marks solution, insert {shift}
# use the language specific shift code, as given in natlinkstatus, and set in natlinkmain  (december 2015)
def playString(keys, hooks=None):
    """do smarter and faster playString than natlink.playString
    
    If useMarkSendInput is set to 1 (True) (top of this file):
    the SendInput module of Mark Lillibridge is used.
    
    Disadvantage: does not work in elevated windows.
    
    This behaviour can be circumvented by adding a hook in the call,
    or by using SendDragonKeys, SendSystemKeys or SSK (Unimacro).
    
    If useMarkSendInput is set to 0 (False), or a hook is added
    (0x100 for normal behaviour, 0x200 for systemkeys behaviour)
    then natlink.playString is used, but a {shift} in front of the keystrokes is inserted,
    in order to prevent doubling or losing keystrokes.
    
    (if default behaviour is wanted, you can call natlink.playString directly)
    """
    if not keys:
        return
    # if type(keys) == str:
    #     keys = utilsqh.convertToBinary(keys)
    if hooks is None and useMarkSendInput:
        SendInput.send_input(
            ExtendedSendDragonKeys.senddragonkeys_to_events(keys))
    else:    
        if hooks not in (None, 0x100):
            natlink.playString(keys, hooks)
        else:
            shiftkey = natlinkmain.shiftkey
            natlink.playString(shiftkey + keys)

#---------------------------------------------------------------------------
# (internal use) shared base class for all Grammar base classes.  Do not use
# this class directly.  See GrammarBase, DictGramBase or SelectGramBase.

class GramClassBase:

    def __init__(self):
        self.gramObj = natlink.GramObj()

    def __del__(self):
        self.gramObj.unload()

    def load(self,grammar,allResults=0,hypothesis=0):
        pass
        try:
            self.gramObj.setBeginCallback(self.beginCallback)
            self.gramObj.setResultsCallback(self.resultsCallback)
            self.gramObj.setHypothesisCallback(self.hypothesisCallback)
        except:
            print("GramClassBase.load(), Error at setting Callback functions ", sys.exc_info())
            traceback.print_exc()
            raise
        try:
            self.gramObj.load(grammar,allResults,hypothesis)
        except:
            print("GramClassBase.load(), Error at loading the grammar ", sys.exc_info())
            traceback.print_exc()
            raise

    def unload(self):        
        self.gramObj.unload()
        self.gramObj.setBeginCallback(None)
        self.gramObj.setResultsCallback(None)
        self.gramObj.setHypothesisCallback(None)

    def activate(self,window=0,exclusive=None):
        self.gramObj.activate('',window)
        if exclusive != None:
            self.setExclusive(exclusive)

    def deactivate(self):
        self.gramObj.deactivate('')

    def setExclusive(self, exclusive):
        self.gramObj.setExclusive(exclusive)
        
    def beginCallback(self, moduleInfo):
        self.callIfExists( "gotBegin", (moduleInfo,) )

    def hypothesisCallback(self, words):
        self.callIfExists( "gotHypothesis", (words,) )

    # This is a utility function.  It calls a member function if and only
    # if that member function is defined.

    def callIfExists(self, funcName, argList):
        try: func = getattr(self, funcName)
        except AttributeError: pass
        else:
            return func(*argList)

#---------------------------------------------------------------------------
# GrammarBase
#
# This is the basic grammar class.  All user grammar classes should use this
# as the base class.
#
# Here are the functions which derived classes can call:
#
#   load( gramSpec, allResults=0, hypothesis=0 )
#       This function will takes a textual representation of a grammar,
#       either as a single string or as a list of strings and load that
#       grammar into Dragon NaturallySpeaking.
#
#       allResults=1 will make it so this grammar see every recognition
#           result even if it is for another grammar,
#       hypothesis=1 means that the gotHypothesis callback will be made.
#           Otherwise, that callback is not made to avoid too much overhead.
#
#   unload()
#       Unload reset the state of the grammar.  Any SAPI objects will be
#       freed and all callbacks will be terminated.
#
# You need to activate rules before they will be recognized.  You activate
# rules by name.  Any rule which is "exported" in the grammar can be
# activated.  This base class offers a number of was to activate rules
# depending on what is convient.
#
#   activate( ruleName, window=0, exclusive=None, noError=0 )
#       Activate a single rule by name.
#
#       noError=1 will suppress the error message when you try to activate
#           a rule which is already active
#       window=N will activate this rule conditionally when the window
#           whose window handle is X is the foreground window.  This is
#           the normal case.  Use window=0 to activate a global rule.
#       exclusive=1 will make this grammar exclusive which means that no
#           other grammars will be included in recognition when this
#           grammar is active unless they are also exclusive
#
#   activateSet( ruleNames, window=0, exclusive=None )
#       This is the most efficient way to activate rules, it takes a list of
#       rules and makes sure that all those rules and only those rules are
#       active.  Do not use this function to change the window handle if you
#       have already activates some rules with a different window handle.
#
#   activateAll( window=0, exclusive=None, exceptlist=None )
#       This will activate every exported rule.
#       can optionally add a list of rules NOT to activate (QH, 2010)
#
#   deactivate( ruleName, noError=0 )
#       Deactivates a single rule by name.
#         noError=1 will suppress the error message when you try to deactivate
#             a rule which is not active
#
#   deactivateAll():
#       This will deactivate every currently active rule.
#
#   setExclusive( exclusive ):
#       Set or reset the exclusive flag for this grammar (see comments under
#       activate method).
#
# Lists are part of SAPI.  They are list subrules except that they can be
# changed while the grammar is loaded.  Also, the list a word comes from is
# not available in recognition results, you only see the innermost rule name
# in recognition results.
#
#   emptyList( listName )
#       This will remove all words currently in a names list.
#
#   appendList( listName, words )
#       This will add one word (phrase) or a list of words (phrases) to a
#       named list.
#
#   setList( listName, words )
#       This function is an efficient way to set the contents of a list in    
#       one operation to a list of words or phrases.
#
# Derived classes should defined callback functions if they want recognition
# results.  The following callback functions can be defined:
#
#   gotBegin( moduleInfo )
#       called when speech is detected before recognition begins.  The
#       parameter is the same value returned by getCurrentModule.
#
#   gotResultsObject( recogType, resObj )
#       called when results are available (before any of the other results
#       callbacks).  The first parameter is one of 'self','other' or 'reject'
#       where the second two types are only possible if the allResults flag
#       was set on the load call.  The second parameter is the results object.
#
#   gotResultsInit( words, fullResults )
#       called when results are available for this grammar before any calls
#       to gotResults_XXX.  Parameters are a list of the recognized words
#       and a list of word,ruleName pairs.
#
#   gotResults_XXX( words, fullResults )
#       called when results are available.  The XXX refers to the rule name
#       in the grammar.  This function is called once for each sequential
#       series of words in the results which come from the same rule in the
#       grammar.  The first parameter is the sequential series of words and
#       the second parameter is a list of word,ruleName pairs.
#
#   gotResults( words, fullResults )
#       called when results are available for this grammar before any calls
#       to gotResults_XXX.  Parameters are a list of the recognized words
#       and the same value a list of word,ruleName pairs.
#
#   gotHypothesis( words)
#       only called when the hypothesis flag is set on load, this callback
#       contains the partial recognition hypothesis during recognition.
#       
# Here is an example of how the callbacks work.  Assume the following grammar:
#
#   <start> exported = this <ruleOne> is {list}
#   <ruleOne> = big <ruleTwo> object
#   <ruleTwo> = red | blue
#   
# And assume that {list} contains the words "good" and "bad".
#
# Now if "this big red object is good" is recognized, the following callbacks
# will be made (in the order indicated).  
#
# (Note: The second parameter to gotResults_XXX and gotResults is the same as
# the second parameter to gotResultsInit.  The example has been abbreviated
# to save space.)
#
#   gotBegin( ??? )
#   gotResultsObject( 'self', resObj )
#   gotResultsInit( 
#       ['this','big','red','object','is','good'],
#       [('this','start'),('big','ruleOne'),('red','RuleTwo'),
#           ('object','ruleOne'),('is','start'),('good','start')] )
#   gotResults_start( ['this'], ... )
#   gotResults_ruleOne( ['big'], ... )
#   gotResults_ruleTwo( ['red'], ... )
#   gotResults_ruleOne( ['object'], ... )
#   gotResults_start( ['is','good'], ... )
#   gotResults( ['this','big','red','object','is','good'], ... )
#

class GrammarBase(GramClassBase):

    def __init__(self):
        GramClassBase.__init__(self)
        self.exclusiveState = 0
        self.activeRules = {}
        self.validRules = []
        self.validLists = []
        self.doOnlyGotResultsObject = None # can rarely be set (QH, dec 2009)

    def load(self,gramSpec,allResults=0,hypothesis=0, grammarName=None):
        try:
            # print 'loading grammar %s, gramspec type: %s'% (grammarName, type(gramSpec))
            # code upper ascii characters with latin1 if they were in the process entered as unicode
            if not type(gramSpec) in (str, list):
                raise TypeError( "grammar definition of %s must be a string or a list of strings, not %s"% (grammarName, type(gramSpec)))
            # print 'loading %s, type: %s'% (grammarName, type(gramSpec) )
            if type(gramSpec) == list:
                pass
                # for i, grampart in enumerate(gramSpec):
                #     line = grampart
                    # if type(line) == bytes:
                    #     line = utilsqh.convertToUnicode(line)
                    # if type(line) == str:
                    #     line = utilsqh.convertToBinary(line)
                    # if line != grampart:
                    #     gramSpec[i] = line
            # if type(gramSpec) == bytes:
            #     gramSpec = utilsqh.convertToUnicode(gramSpec)
            if type(gramSpec) == str:
                # gramSpec = utilsqh.convertToBinary(gramSpec)
                gramSpec = gramSpec.split('\n')
                gramSpec = [g.rstrip() for g in gramSpec]

            gramparser.splitApartLines(gramSpec)
            parser = gramparser.GramParser(gramSpec, grammarName=grammarName)
            parser.doParse()
            parser.checkForErrors()
            gramBin = gramparser.packGrammar(parser)
            self.scanObj = parser.scanObj  # for later error messages.
            try:
                GramClassBase.load(self,gramBin,allResults,hypothesis)
            except natlink.BadGrammar:
                print('GrammarBase, cannot load grammar, BadGrammar:\n%s\n'% gramSpec)
                raise
            # we want to keep a list of the rules which can be activated and the
            # known lists so we can catch errors earlier
            self.validRules = list(parser.exportRules.keys())
            self.validLists = list(parser.knownLists.keys())

            # we reverse the rule dictionary so we can convert rule numbers back
            # to rule names during recognition
            self.ruleMap = {}
            for x in list(parser.knownRules.keys()):
                self.ruleMap[ parser.knownRules[x] ] = x
            return 1

        except:
            print("Unexpected error load GramClassBase:", sys.exc_info())
            print(traceback.print_exc())

    # these are wrappers for the GramObj base methods.  We also keep track of
    # legal rules, lists and active rules so we can do some first level error
    # checking

    def unload(self):
        GramClassBase.unload(self)
        self.activeRules.clear()
        while self.validRules:
            self.validRules.pop()
        while self.validLists:
            self.validLists.pop()
        self.exclusiveState = 0

    def activate(self, ruleName, window=0, exclusive=None, noError=0):
        # print('ruleName: %s, validRules: %s'% (ruleName, self.validRules))
        # if type(ruleName) == str:
        #     ruleName = utilsqh.convertToBinary(ruleName)
        if ruleName not in self.validRules:
            raise gramparser.GrammarError( "rule %s was not exported in the grammar" % ruleName , self.scanObj)
        # if type(ruleName) != bytes:
        #     raise gramparser.GrammarError( 'GrammarBase, wrong type in activate, %s (%s)'% (ruleName, type(ruleName)), self.scanObj)
        if ruleName in self.activeRules:
            if window == self.activeRules[ruleName]:
                print('rule %s already active for window %s'% (ruleName, window))
                return
            else:
                print('change rule %s from window %s to window %s'% (ruleName, self.activeRules[ruleName], window))
                self.gramObj.deactivate(ruleName)
        if debugLoad: print('activate rule %s (window: %s)'% (ruleName, window))
        self.gramObj.activate(ruleName,window)
        self.activeRules[ruleName] = window
        if not exclusive is None:
            if debugLoad: print('set exclusive mode to %s for rule %s'% (exclusive, ruleName))
            self.setExclusive(exclusive)
        pass            

    def deactivate(self, ruleName, noError=0):
        # if type(ruleName) == str:
        #     ruleName = utilsqh.convertToBinary(ruleName)
        if ruleName not in self.validRules:
            if noError: return
        if type(ruleName) != bytes:
            print('GrammarBase, deactivate, %s (%s)'% (ruleName, type(ruleName)))
            raise gramparser.GrammarError( "rule %s (%s) was not exported in the grammar" %
                                          ruleName, type(ruleName), self.scanObj)
        if ruleName not in self.activeRules:
            if noError: return
            raise gramparser.GrammarError( "rule %s is not active", self.scanObj)
        if debugLoad: print('deactivate rule %s'% ruleName)
        self.gramObj.deactivate(ruleName)
        del self.activeRules[ruleName]

    def activateSet(self, ruleNames, window=0, exclusive=None):
        """activate a set of rules.

        Try new strategy, based on the trick of Vocola. Natlink does not work completely correct here.        
        """
        if type(ruleNames) == list:
            rulenames = copy.copy(ruleNames) # so we can pop items
        elif type(ruleNames) == tuple:
            rulenames = list(ruleNames) # so we can pop items
        else:
            raise TypeError("activateSet, ruleNames (%s) must be a list or a tuple, not: %s"%
                            (repr(ruleNames), type(ruleNames)))
        activeKeys = list(self.activeRules.keys())
        for x in activeKeys:
            if type(x) != bytes:
                raise TypeError('activateSet, rulename "%s" should be of binary_type, not: %s'% (x, type(x)))

            curWindow = self.activeRules[x]
            if x in rulenames:
                if curWindow == window:
                    rulenames.remove(x)
                    if debugLoad: print('activateSet, rule %s already active for %s'% (x, window))
                else:
                    if debugLoad: print('activateSet, rule %s, change from window %s to window %s'% (x, curWindow, window))
                    self.deactivate(x)
                    # self.activate(x, window)
                    # rulenames.remove(x)
            else:
                # if same window, deactivate, otherwise just leave...
                # deactivate direct to gramObj here:
                if window == curWindow:
                    if debugLoad: print('activateSet, do not want %s, so deactivate, same window: %s'% (x, curWindow))
                    self.deactivate(x)
                elif window == 0:
                    if debugLoad: print('activateSet, deactivate rule %s (global), previous window: %s'% (x, curWindow))
                    self.deactivate(x)
                elif curWindow == 0:
                    if debugLoad: print('activateSet, deactivate global rule %s, new window window: %s'% (x, window))
                    self.deactivate(x)
                else:
                    if debugLoad: print('activateSet, deactivate not needed, different window: rule %s, previous window: %s new window: %s'% (x, curWindow, window))             
        for x in rulenames:
            self.activate(x, window)
        if not exclusive is None:
            self.setExclusive(exclusive)

    def deactivateSet(self, ruleNames, noError=0):
        if not type(ruleNames ) in (list, tuple):
            raise TypeError("deactivateSet, ruleNames (%s) must be a list or a tuple, not: %s"%
                            (repr(ruleNames), type(ruleNames)))
        for x in ruleNames:
            if type(x) != bytes:
                print('GrammarBase, deactivateSet, wrong type in rule to deactivate, %s (%s)'% (x, type(x)))
            self.deactivate(x, noError=noError)

    def activateAll(self, window=0, exclusive=None, exceptlist=None):
        """activate all rules
        
        as experiment first deactivate all rules before doing so
        """
        allRules = copy.copy(self.validRules)
        if exceptlist:
            for x in exceptlist:
                allRules.remove(x)
            if debugLoad: print('activateAll except %s'% exceptlist)
            
        self.activateSet(allRules, window=window, exclusive=exclusive)
        if not exclusive is None:
            self.setExclusive(exclusive)

    def _deactivateAll(self):
        """deactivate all rules, no change of exclusive state
        """
        activeRules = list(self.activeRules.keys())
        
        for x in activeRules:
            self.deactivate(x)

    def deactivateAll(self):
        """deactivate all rules and reset explicit the exclusive state of the grammar
        """
        self._deactivateAll()
        self.setExclusive(0)

    def setExclusive(self, exclusive):
        """call into gramObj directly
        maintain self.exclusiveState
        """
        if exclusive is None: return
        if exclusive:
            value = 1
        else:
            value = 0
            
        self.gramObj.setExclusive(value)
        self.exclusiveState = value

    def isExclusive(self):
        """return True if exclusive, False if non-exclusive (most of the time)
        """
        if self.exclusiveState:
            return True
        return False

    def isActive(self):
        """return True is active (rules activated), False if loaded, but no rules active
        return None if grammar is not loaded (yet)
        """
        if self.activeRules:
            return True
        return False
    
    def isLoaded(self):
        """return True if grammar is loaded
        """
        if self.validRules:
            return True
        return False
    
    def emptyList(self, listName):
        # if type(listName) == str:
        #     listName = utilsqh.convertToBinary(listName)
        if listName not in self.validLists:
            raise gramparser.GrammarError( "list %s was not defined in the grammar" % listName , self.scanObj)
        self.gramObj.emptyList(listName)

    def appendList(self, listName, words):
        # listName = utilsqh.convertToBinary(listName)
        if listName not in self.validLists:
            raise gramparser.GrammarError( "list %s was not defined in the grammar" % listName , self.scanObj)
        if type(words) == str:
            # words = utilsqh.convertToBinary(words)
            self.gramObj.appendList(listName,words)
        else:
            for x in words:
                # if type(x) == str:
                #     x = utilsqh.convertToBinary(x)
                self.gramObj.appendList(listName,x)
    
    def setList(self, listName, words):
        # if type(listName) == str:
        #     listName = utilsqh.convertToBinary(listName)
        print('listName: %s, validLists: %s'% (listName, self.validLists))
        self.emptyList(listName)
        self.appendList(listName, words) # other way around?

    # when a recognition for this grammar occurs, this function gets called
    # by GramObj (it is set as the callback in GrammarBase.load.
    def resultsCallback(self, wordsAndNums, resObj):
        # if the allResults flag is set it is possible that the first
        # parameter will be a string instead of a data structure. We 
        # compute the recognition type from this parameter
        if type(wordsAndNums) == str:
            recogType = wordsAndNums
        else:
            recogType = 'self'

        # make an optional callback which allows the clients to have access 
        # to the recognition object
        self.callIfExists( 'gotResultsObject', (recogType,resObj) )

        # do nothing more if the recog results were not for this grammar
        if type(wordsAndNums) != type([]):
            return None

        # we first convert the passed array of word/ruleNumbers into an
        # array of word/ruleNames and an array of only words
        words = []
        fullResults = []
        wordsByRule = {}
        if self.doOnlyGotResultsObject:
            # can switch on in gotResultsObject, so rest of processing is not done.
            # grammar kaiser_dictation, (voicedictation with exclusive mode catching)
            # QH (dec, 2009)
            #print 'skip rest of resultsCallback'
            return
        for x in wordsAndNums:
            word, ruleNumber = x
            words.append( word )
            # the numbering of some rules appears to be different in NatSpeak10, catch with try:
            # if DNSVersion >= 15:
            #     ruleNumber += 1
            try:
                ruleName = self.ruleMap[ruleNumber]
            except KeyError:
                if ruleNumber in (1000000, 1000001) and 'dgndictation' in list(self.ruleMap.values()):
                    ruleName = 'dgndictation'
                elif ruleNumber in (1000001, 1000002) and 'dgnletters' in list(self.ruleMap.values()):
                    ruleName = 'dgnletters'
                elif ruleNumber == 0 and word == '\\noise\\?':
                    continue
                else:
                    print('='*50)
                    print('word: %s, ruleNumber: %s'% (word, ruleNumber))
                    print('wordsAndNums: %s'% wordsAndNums)
                    print('ruleMap: %s'% repr(self.ruleMap))
                    mess =  'Invalid key %s for ruleMap'% ruleNumber
                    print(mess)
                    print('===============================')
                    continue

            fullResults.append( ( word, ruleName ) )
            wordsByRule.setdefault(ruleName, []).append(word)
                
        # we also compute a list similar to fullResults except that we group
        # all words which are sequential and in the same rule together in a
        # sublist. For example:
        #   [ ('red','color'), ('blue','color'), ('and','conj'), ('green','color') ]
        # Becomes:
        #   [ (['red','blue'],'color'), (['and'],'conj'), (['green'],'color') ]
        seqsAndRules = []
        for x in fullResults:
            if len(seqsAndRules) > 0 and seqsAndRules[-1:][0][1] == x[1]:
                # duplicate rule, append previous entry
                seqsAndRules[-1:][0][0].append(x[0])
            else:
                seqsAndRules.append( ([x[0]], x[1]) )
        # provide fullResults and seqsAndRules also as instance variables:
        self.fullResults = fullResults
        self.seqsAndRules = seqsAndRules
        self.wordsByRule = wordsByRule
        # if wordsAndNums[0][0] == 'testtestrun':
        # if wordsAndNums[0][0] == 'testtestrun' or True:
        #     print 'wordsAndNums: %s'% wordsAndNums
        # ## print for debugging puposes, eg in the testIniGrammar.py module of Unimacro:
        #     print 'words = %s'% words
        #     print 'seqsAndRules = %s'% seqsAndRules
        #     print 'fullResults = %s'% fullResults
        
        ## printing for debug purposes...
        # now we make the callbacks (in each case we only call the fucntion 
        # if it exists in the derived class)
        # - we first call gotResultsInit
        # - then we make one callback for each different rule found as we
        #   sequentially scan the results (see seqsAndRules example)
        # - finally we call gotResults
        self.callIfExists( 'gotResultsInit', (words, fullResults) )
        self.callRuleResultsFunctions(seqsAndRules, fullResults)
        self.callIfExists( 'gotResults', (words, fullResults) )

    def callRuleResultsFunctions(self, seqsAndRules, fullResults):
        """call the rule functions, can be overloaded (eg in DocstringGrammar)
        
        Also give self.nextRule (the name) self.nextWords, self.prevRule, self.prevWords
        so the result of the adjacent rules are known
        """
        ruleName, ruleWords = None, None
        lenSeqsAndRules = len(seqsAndRules)
        for i, x in enumerate(seqsAndRules):
            if i == 0:
                self.prevRule, self.prevWords = None, []
            else:
                Prev = copy.copy(seqsAndRules[i-1])
                self.prevRule, self.prevWords = Prev[1], Prev[0]
            
            if i == lenSeqsAndRules - 1:
                self.nextRule, self.nextWords = None, []
            else:                
                Next = copy.copy(seqsAndRules[i+1])
                self.nextRule, self.nextWords = Next[1], Next[0]
            
            ruleName, ruleWords = x[1], copy.copy(x[0])    
            self.callIfExists( 'gotResults_'+ruleName, (ruleWords, fullResults) )


#---------------------------------------------------------------------------
# DictGramBase
#        
# This base class is similar to GrammarBase except that it is used for real
# dictation grammars.  A real dictation grammar allows a client application
# to get raw dictation results from the recognizer.  It is very similat to
# creating a command and control grammar with the <dgndictation> rule except
# that you have the added ability to set the dictation context (words to
# consider as having been spoken juct before the current recognition).
#
# Here are the functions which derived classes can call:
#
#   load( allResults=0, hypothesis=0 )
#       Creates the dictation grammar.  See GrammarBase class for definition
#       of flags.
#
#   unload()
#       Unload reset the state of the grammar.  Any SAPI objects will be
#       freed and all callbacks will be terminated.
#
# You need to activate the grammar before it can be recognized.  Activation
# of a dictation grammar is simplier than a command grammar because there
# are no named rules.
#
#   activate( window=0, exclusive=None )
#       noError=1 will suppress the error message when you try to activate
#           a rule which is already active
#       window=N will activate this rule conditionally when the window
#           whose window handle is X is the foreground window.  This is
#           the normal case.  Use window=0 to activate a global rule.
#
#   deactivate()
#       Deactivates the grammar.
#
#   setExclusive( exclusive ):
#       Set or reset the exclusive flag for this grammar (see comments under
#       activate method of GrammarBase).
#
# Dictation gramars have a special method which allows you to indicate what
# text should be considered to been recognized just before this dictation
# result, and after this dictation result.
#
#   setContext( beforeText='', afterText='' )
#       Note current version of Dragon NaturallySpeaking ignore the
#       afterText but the before text is critical to increasing recognition
#       accuracy.
#
# Derived classes should defined callback functions if they want recognition
# results.  The following callback functions can be defined:
#
#   gotBegin( moduleInfo )
#       called when speech is detected before recognition begins.  The
#       parameter is the same value returned by getCurrentModule.
#
#   gotResultsObject( recogType, resObj )
#       called when results are available (before any of the other results
#       callbacks).  The first parameter is one of 'self','other' or 'reject'
#       where the second two types are only possible if the allResults flag
#       was set on the load call.  The second parameter is the results object.
#
#   gotResults( words )
#       called when results are available for this grammar.
#
#       words = list of recognized words
#
#   gotHypothesis( words )
#       only called when the hypothesis flag is set on load, this callback
#       contains the partial recognition hypothesis during recognition.
#

class DictGramBase(GramClassBase):

    def load(self,allResults=0,hypothesis=0):
        gramBin=self.makeGrammar()
        GramClassBase.load(self,gramBin,allResults,hypothesis)

    def setContext(self, beforeText='', afterText=''):
        self.gramObj.setContext(beforeText,afterText)

    # This code is very similar to the corresponding code in GrammarBase
    def resultsCallback(self, wordsAndNums, resObj):
        if type(wordsAndNums) == type(''): 
            recogType = wordsAndNums
        else:
            recogType = 'self'
        self.callIfExists( 'gotResultsObject', (recogType,resObj) )
        if type(wordsAndNums) != type([]):
            return None

        # convert the wordsAndNums array into simply words (ignore nums)
        words = []
        for word,num in wordsAndNums:
            words.append( word )

        # Now make the callback                
        self.callIfExists( 'gotResults', (words,) )

    # This makes a raw dictation grammar.  The grammar is in SAPI binary
    # format as defined by Microsoft.
    def makeGrammar(self):
        return struct.pack("LL", 2, 0)

#---------------------------------------------------------------------------
# SelectGramBase
#
# This base class is similar to GrammarBase except that it is used for
# select XYZ grammars.  A select XYZ grammar is a special grammar which
# recognizes an utterance of the form "<verb> <text> [ through <text> ]"
# where <verb> is specified and <text> is an arbitrary sequence of words in
# a specified text buffer.
#
# Here are the functions which derived classes can call:
#
# make default select and through words "select" and "though" (lower case)
# Quintijn december 2010
# adapt to throughWords as well, for future enhancement VoiceCode
# Quintijn August, 2009
#   load( selectWords=['Select'], throughWord='Through', throughWords=None, allResults=0, hypothesis=0 )
#       selectWords is a list of words or phrases which can introduce a
#           comand of this type.  For example, you can pass in a list like
#           ['Select','Correct','Insert Before','Insert After'] to simulate
#           some of NatSpeak's behavior.
#       throughWord is a single word which is used between the two parts of
#           the command as in "Select <text> Through <text>".  Pass in None
#           or an empty string to disable two part commands.
#       allResults=1 will make it so this grammar see every recognition
#           result even if it is for another grammar,
#       hypothesis=1 means that the gotHypothesis callback will be made.
#           Otherwise, that callback is not made to avoid too much overhead.
#
#   unload()
#       Unload reset the state of the grammar.  Any SAPI objects will be
#       freed and all callbacks will be terminated.
#
# You need to activate the grammar before it can be recognized.  Activation
# of a dictation grammar is simplier than a command grammar because there
# are no named rules.
#
#   activate( window=0, exclusive=None )
#       noError=1 will suppress the error message when you try to activate
#           a rule which is already active
#       window=N will activate this rule conditionally when the window
#           whose window handle is X is the foreground window.  This is
#           the normal case.  Use window=0 to activate a global rule.
#
#   deactivate()
#       Deactivates the grammar.
#
#   setExclusive( exclusive ):
#       Set or reset the exclusive flag for this grammar (see comments under
#       activate method of GrammarBase).
#
# Selection gramars work on a text buffer which you pass to the grammar.
# The speech recognition engine maintains a copy of this text and performs
# all selection on its copy.  Then when the grammar is recognized, you can
# find out the range of text which is effected.
#
#   setSelectText(text)
#       Pass in a block of text (string).
#
#   getSelectText()
#       Returns the text buffer contents currently stored in the speech
#       recognition engine.
#
# Derived classes should defined callback functions if they want recognition
# results.  The following callback functions can be defined:
#
#   gotBegin( moduleInfo )
#       called when speech is detected before recognition begins.  The
#       parameter is the same value returned by getCurrentModule.
#
#   gotResultsObject( recogType, resObj )
#       called when results are available (before any of the other results
#       callbacks).  The first parameter is one of 'self','other' or 'reject'
#       where the second two types are only possible if the allResults flag
#       was set on the load call.  The second parameter is the results object.
#
#   gotResults( words, start, end )
#       called when results are available for this grammar.
#
#       words = list of recognized words; the first word will be one of
#           the words or phrases in selectWords (passed in when the grammar
#           was created).
#       start = index into getSelectText of the start of the selection
#       end = index into getSelectText of the end of the selection
#
#   gotHypothesis( words )
#       only called when the hypothesis flag is set on load, this callback
#       contains the partial recognition hypothesis during recognition.
#

class SelectGramBase(GramClassBase):

    def load( self, selectWords=None, throughWord='through',
              throughWords=None,allResults=0, hypothesis=0 ):
        if selectWords is None:
            selectWords = ['select']
        if throughWords is None:
            throughWords = [throughWord]
        # QH, throughWords also maybe a list of words, the default being
        # ['Through'] (being the throughWord...
        gramBin=self.makeGrammar(selectWords,throughWords)
        GramClassBase.load(self,gramBin,allResults,hypothesis)

    def setSelectText(self,text):
        self.gramObj.setSelectText(text)
        
    def getSelectText(self):
        return self.gramObj.getSelectText()
        
    # This code is very similar to the corresponding code in GrammarBase
    def resultsCallback(self, wordsAndNums, resObj):
        if type(wordsAndNums) == type(''): 
            recogType = wordsAndNums
        else:
            recogType = 'self'
        self.callIfExists( 'gotResultsObject', (recogType,resObj) )
        if type(wordsAndNums) != type([]):
            return None

        # convert the wordsAndNums array into simply words (ignore nums)
        words = []
        for word,num in wordsAndNums:
            words.append( word )

        # query the text range which corresponds to this result
        startPos,endPos = resObj.getSelectInfo(self.gramObj,0)

        # Now make the callback
        self.callIfExists( 'gotResults', (words, startPos, endPos) )

    #;ydebug(lLoO9)::::  (NL Verenigde Staten)
    # A selection grammar is similar to a Microsoft SAPI grammar.
    #   SRHEADER
    #       dwType = DGNSRHDRTYPE_SELECT(10)
    #       dwFlags = 0
    #   SRCHUNK
    #       dwChunkID = DGNSRCKSELECT_INTROPHRASES(0x1017)
    #       dwChunkSize = size of SRWORDs
    #       data = series of SRWORDs for selectWords
    #   SRCHUNK (optional)
    #       dwChunkID = DGNSRCKSELECT_THRUWORD(0x1018)
    #       dwChunkSize = size of SRWORD
    #       data = single SRWORD for throughWord
    # Use the routines in gramparser.py to build the grammar just like with
    # command grammars.
    # throughWords is a list of words:
    def makeGrammar(self,selectWords,throughWords):
        output = struct.pack("LL", 10, 0)
        if selectWords:
            wordDict = {}
            for word in selectWords:
                wordDict[word] = 0
            output = output + gramparser.packGrammarChunk(0x1017,wordDict)
        # throughWords maybe more words now:
        if throughWords:
            wordDict = {}
            for word in throughWords:
                wordDict[word] = 0
            output = output + gramparser.packGrammarChunk(0x1018,wordDict)
        return output            
        
#---------------------------------------------------------------------------        

# Utility subroutine.  This returns the base module name from a complete path

def getBaseName(name):
    return os.path.splitext(os.path.split(name)[1])[0]

# This utility routine converts a fullResults parameter into a dictionary
#   [ ('red','color'), ('flower','object'), ('and','conj'), ('green','color') ]
# Becomes:
#   { 'color':['red','green'], 'object':['flower'], 'conj':['and'] }

def convertResults(fullResults):
    dict = {}
    for x in fullResults:
        if x[1] in dict: dict[x[1]].append(x[0])
        else: dict[x[1]] = [x[0]]
    return dict

def testSendInput(keys):
    if useMarkSendInput == 0:
        print('warning cannot test SendInput, first set useMarkSendInput to 1')
    playString(keys)

if __name__ == "__main__":
    # testSendInput('abc#(){}zz')
    testSendInput('\xe9\xe9n example')
    # testSendInput(u';ydebug(lLoO9)::::')
    # testSendInput(u'U\u00e9\u0106\u00D6 character')
    #