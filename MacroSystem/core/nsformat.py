__version__ = "$Revision: 105 $, $Date: 2008-12-04 12:47:13 +0100 (do, 04 dec 2008) $, $Author: quintijn $"
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This code simulates the basic text formatting from NatSpeak.
#
# code written by Joel Gould, posted on the natpython discussion list on Wed, 28 Aug 2002
#
# inserted in the unimacro package june 2006
#

import string, types
import natlink

flag_useradded = 0
flag_varadded = 1
flag_custompron = 2
flag_nodelete = 3
flag_passive_cap_next = 4
flag_active_cap_next = 5
flag_uppercase_next = 6
flag_lowercase_next = 7
flag_no_space_next = 8
flag_two_spaces_next = 9
flag_cond_no_space = 10
flag_cap_all = 11
flag_uppercase_all = 12
flag_lowercase_all = 13
flag_no_space_all = 14
flag_reset_no_space = 15
flag_swallow_period = 16
flag_is_period = 17
flag_no_formatting = 18
flag_no_space_change = 19
flag_no_cap_change = 20
flag_no_space_before = 21
flag_reset_uc_lc_caps = 22
flag_new_line = 23
flag_new_paragraph = 24
flag_title_mode = 25
flag_beginning_title_mode = 26
flag_space_bar = 27
flag_not_in_dictation = 28
flag_guessedpron = 29
flag_topicadded = 30

#---------------------------------------------------------------------------
# This is the main formatting entry point.  It takes the old format state and
# a list of words and returns the new formatting state and the formatted
# string.
#
# If you already have the wordInfo for each word, you can pass in a list of
# tuples of (wordName,wordInfo) instead of just the list of words.

def formatWords(wordList,state=None):

     output = ''
     for entry in wordList:

         if type(entry)==type(()):
             assert( len(entry)==2 )
             wordName = entry[0]
             wordInfo = entry[1]
         else:
             wordName = entry
             wordInfo = natlink.getWordInfo(wordName)
             if wordInfo == None:
                 wordInfo = 0

         newText,state = formatWord(wordName,wordInfo,state)
         output = output + newText

     return output,state

def formatLetters(wordList,state=None):
    """this is more tricks, formats dngletters input
        input the wordList in one stroke!
        
        #flag_lowercase_next = 7
        #flag_no_space_next = 8
        initialise with:
        state = nsformat.initializeStateFlags(nsformat.flag_no_space_next)
        before you issue the command
    """
    result = []
    for w in wordList:
        res, state = formatWords([w], state)
        res = res.strip() # strip each entry, except when you have an explicit space as below:
##        print 'res: %s (len: %s), state: %s'% (res, len(res), `showStateFlags(state)`)
        if res:
            result.append(res)
        elif len(filter(None, state)) == 1 and state[8] or w.endswith('spatie') or w.endswith("space-bar"):
            # first seems to catch a space in enx, second is for a space in Dutch::::
            result.append(' ') # very strange, 8 = flag_no_space_next, but this seems to work
    res = ''.join(result)
##    print 'formatLetters res: %s'% res 
            
    return res, state
                          
#---------------------------------------------------------------------------
# This is the formatting subroutine.  It handles the formatting for a single
# word using the standard Dragon NaturallySpeaking state machine.
#
# This code was adapted from shared\resobj.cpp

def formatWord(wordName,wordInfo=None,stateFlags=None):

     #-----
     # Preparation

     if wordInfo == None:
         wordInfo = natlink.getWordInfo(wordName)
     if wordInfo == None:
         wordInfo = 0

     # for faster lookup in Python, we convert the bit arrays into real arrays
     wordFlags = []
     for i in range(32):
         if wordInfo & (1<<i):
             wordFlags.append(1)
         else:
             wordFlags.append(0)

     if stateFlags == 0:
         stateFlags = [0]*32
     elif stateFlags == None:
         stateFlags = [0]*32
         stateFlags[flag_no_space_next] = 1
         stateFlags[flag_active_cap_next] = 1

     # get the written form
     if wordName[:2] == '\\\\':
         wordName = '\\'
     else:
         slash = string.find(wordName,'\\')
         if slash >= 0:
             wordName = wordName[:slash]

     #-----
     # Compute the output string

     output = ''

     # compute the number of CRLF's
     if wordFlags[flag_new_line]:
         output = output + '\r\n'
     elif wordFlags[flag_new_paragraph]:
         output = output + '\r\n\r\n'

     # compute the leading spacing
     if ( wordFlags[flag_no_formatting] or
          stateFlags[flag_no_space_next] or
          stateFlags[flag_no_space_all] or
          wordFlags[flag_no_space_before] or
          stateFlags[flag_cond_no_space] and wordFlags[flag_cond_no_space] ):
         # no leading space
         pass
     elif stateFlags[flag_two_spaces_next]:
         output = output + '  '
     else:
         output = output + ' '

     # the no space all flag is used so we can remove the spaces from a phase
     # which may have imbeded spaces

     if not wordFlags[flag_no_formatting] and stateFlags[flag_no_space_all]:
         wordName = string.join(string.split(wordName),'')

     # compute the capitalization by looking at the long term flags; this
     # effects all the words in the phrase

     if wordFlags[flag_no_formatting]:
         # no capitalization change
         pass
     elif stateFlags[flag_lowercase_all]:
         wordName = string.lower(wordName)
     elif stateFlags[flag_uppercase_all]:
         wordName = string.upper(wordName)
     elif stateFlags[flag_cap_all] and not wordFlags[flag_title_mode]:
         words = string.split(wordName)
         words = map(string.capitalize,words)
         wordName = string.join(words)
     elif stateFlags[flag_passive_cap_next]:
         wordName = string.capitalize(wordName)

     # compute the capitalization for the first word in the phrase which
     # overrides the long term capitalization state

     if wordFlags[flag_no_formatting]:
         # no capitalization change
         pass
     elif stateFlags[flag_lowercase_next]:
         words = string.split(wordName)
         words[0] = string.lower(words[0])
         wordName= string.join(wordName)
     elif stateFlags[flag_uppercase_next]:
         words = string.split(wordName)
         words[0] = string.upper(words[0])
         wordName= string.join(wordName)
     elif stateFlags[flag_active_cap_next]:
         wordName = string.capitalize(wordName)
     elif stateFlags[flag_beginning_title_mode]:
         wordName = string.capitalize(wordName)

     output = output + wordName

     #-----
     # compute the new state flags

     # clear out the capitalization
     if not wordFlags[flag_no_cap_change]:
         stateFlags[flag_active_cap_next] = 0
         stateFlags[flag_passive_cap_next] = 0
         stateFlags[flag_uppercase_next] = 0
         stateFlags[flag_lowercase_next] = 0
         stateFlags[flag_beginning_title_mode] = 0

     # reset the state flags

     if not wordFlags[flag_no_space_change]:
         stateFlags[flag_no_space_next] = 0
         stateFlags[flag_two_spaces_next] = 0
         stateFlags[flag_cond_no_space] = 0
     elif not wordFlags[flag_no_formatting]:
         stateFlags[flag_no_space_next] = 0
         stateFlags[flag_cond_no_space] = 0

     # see if we need to reset the cap flags

     if wordFlags[flag_reset_uc_lc_caps]:
         stateFlags[flag_cap_all] = 0
         stateFlags[flag_uppercase_all] = 0
         stateFlags[flag_lowercase_all] = 0

     # see if we need to reset the no space flags

     if wordFlags[flag_reset_no_space]:
         stateFlags[flag_no_space_all] = 0

     if wordFlags[flag_cap_all]:
         stateFlags[flag_beginning_title_mode] = 0

     # these flags just get copied
     copyList = [ flag_active_cap_next, flag_passive_cap_next,
         flag_uppercase_next, flag_lowercase_next, flag_no_space_next,
         flag_two_spaces_next, flag_cond_no_space, flag_cap_all,
         flag_uppercase_all, flag_lowercase_all, flag_no_space_all,
         flag_swallow_period, flag_beginning_title_mode ]

     for i in copyList:
         if wordFlags[i]:
             stateFlags[i] = 1

     if wordFlags[flag_new_paragraph] and wordFlags[flag_is_period]:
         stateFlags[flag_new_paragraph] = 1

     return output,stateFlags

def initializeStateFlags(*args):
    """return an initial state, built up by one or more state flags

    example from natspeak_spell:
    state = nsformat.initializeStateFlags(nsformat.flag_no_space_next)


    """
    stateFlags = [0]*32
    for a in args:
        stateFlags[a] = 1
    return stateFlags


def showStateFlags(state):
    """returns an array of the state flags, that are set  (3,5) 


    """
    if type(state) != types.ListType:
        return ()
    statelist = []
    for i in range(len(state)):
        if state[i]:
            statelist.append(i)
    return tuple(statelist)


#---------------------------------------------------------------------------

def testSubroutine(state,input,output):

     words = string.split(input)
     for i in range(len(words)):
         words[i] = string.replace(words[i],'_',' ')
     actual,state = formatWords(words,state)
     if actual != output:
         print 'Expected "%s"'%output
         print 'Actually "%s"'%actual
         raise 'TestError'
     return state

#---------------------------------------------------------------------------

def testFormatting():

     state=None
     state=testSubroutine(state,
         r'this is a test sentence .\period',
         'This is a test sentence.')
     state=testSubroutine(state,
         r'\Caps-On as you can see ,\comma this yours_truly seems to work \Caps-Off well',
         '  As You Can See, This Yours Truly Seems to Work well')
     state=testSubroutine(state,
         r'an "\open-quote example of testing .\period "\close-quote hello',
         ' an "example of testing."  Hello')
     state=testSubroutine

     print 'Formatting tests passed.'

if __name__=='__main__':
     natlink.natConnect()
     try:
         testFormatting()
         natlink.natDisconnect()
     except:
         natlink.natDisconnect()
         raise

