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
# adapted for Dragon 11, oct 2011, Quintijn
#

import string, types, copy
import natlink, natlinkmain

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

flagNames = {}
name = ''
for name in globals():
    if name.startswith('flag_') and type(globals()[name]) == types.IntType and 0 < globals()[name] < 32:
        flagNames[globals()[name]] = name
        
#
flags_like_period = (9, 4, 21, 17)  # flag_two_spaces_next = 9,  flag_passive_cap_next = 4, flag_no_space_before = 21
flags_like_comma = (21, )  # flag_no_space_before = 21  (flag_nodelete = 3 we just ignore here, so leave out)
flags_like_number = (10,)
flags_like_point = (8, 10)  # no spacing when in combination with numbers flag_cond_no_space = 10
flags_like_hyphen = (8, 21)  # no spacing before and after
flags_like_open_quote = (8, 20) # no space next and no cap change
flags_like_close_quote = (21, 20, 19) # no space before, no cap change and no space change (??)

# word flags from properties part of the word:
# Dragon 11...
propDict = {}
propDict['period'] = flags_like_period
propDict['comma'] = flags_like_comma
propDict['cap'] = (19, 18, flag_active_cap_next)
propDict['caps-on'] = (19, 18,  flag_cap_all)
propDict['caps-off'] = (19, 18, flag_reset_uc_lc_caps)
propDict['all-caps'] = (19, 18, flag_uppercase_next)
propDict['all-caps-on'] = (19, 18, flag_uppercase_all)
propDict['all-caps-off'] = (19, 18, flag_reset_uc_lc_caps)
propDict['no-caps'] = (19, 18, flag_lowercase_next)
propDict['no-caps-on'] = (19, 18, flag_lowercase_all)
propDict['no-caps-off'] = (19, 18, flag_reset_uc_lc_caps)
propDict['no-space'] = (18, 20, flag_no_space_next)
propDict['no-space-on'] = (18, 20, flag_no_space_all)
propDict['no-space-off'] = (18, 20, flag_reset_no_space)
propDict['left-double-quote'] = flags_like_open_quote
propDict['right-double-quote'] = flags_like_close_quote
# left- as left-double-quote
# right- as right-double-quote

propDict['question-mark'] = flags_like_period
propDict['exclamation-mark'] = flags_like_period

propDict['hyphen'] = flags_like_hyphen
propDict['at-sign'] = flags_like_hyphen
propDict['colon'] = flags_like_comma
propDict['semicolon'] = flags_like_comma
propDict['apostrophe-ess'] = flags_like_comma

propDict['new-line'] = (flag_no_formatting, flag_no_space_next, flag_no_cap_change, flag_new_line)
propDict['new-paragraph'] = (flag_no_formatting, flag_no_space_next, flag_passive_cap_next, flag_new_paragraph)


#---------------------------------------------------------------------------
# This is the main formatting entry point.  It takes the old format state and
# a list of words and returns the new formatting state and the formatted
# string.
#
# If you already have the wordInfo for each word, you can pass in a list of
# tuples of (wordName,wordInfo) instead of just the list of words.

def formatWords(wordList,state=None):
    global flags_like_period
    language = natlinkmain.status.getLanguage()
    if language != 'enx':
        flags_like_period = (4, 21, 17) # one space after period.
        
    # get the getWordsInfo function, now returning a tuple of properties
    DNSversion = natlinkmain.DNSversion
    if DNSversion >= 11:
        gwi = getWordInfo11
    else:
        gwi = getWordInfo10

    output = ''
    emptySet = set( () )
    for entry in wordList:

        if type(entry)==type(()):
            assert( len(entry)==2 )
            wordName = entry[0]
            wordInfo = entry[1]
        else:
            wordName = entry
            wordInfo = gwi(wordName)
        if wordInfo is None:
            wordInfo = set()
        if type(wordInfo) != type(emptySet):
            wordInfo = wordInfoToFlags(wordInfo)

        # init state to a set:
        if state == 0:
            state = set()
        elif state == -1:
            state = set(flag_no_space_next)
        elif state is None:
            state = set([flag_no_space_next, flag_active_cap_next])
        elif type(state) in (types.ListType, types.TupleType):
            state = set(state)
        elif type(state) != type(emptySet):
            state = wordInfoToFlags(state)
            print 'formatWords starting with: %s'% state

        newText, state = formatWord(wordName,wordInfo,state)
        output = output + newText

    return output, state

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
def formatWord(wordName,wordInfo=None,stateFlags=None, gwi=None):
    ##adapted: wordInfo and stateFlags are now sets of state flags
    emptySet = set()
    if gwi is None:
        # get the proper getWordInfo function
        DNSversion = natlinkmain.DNSversion
        if DNSversion >= 11:
            gwi = getWordInfo11
        else:
            gwi = getWordInfo10
    #-----
    # Preparation
    # assume wordInfo is a set already
    if type(wordInfo) == type(emptySet):
        wordFlags = wordInfo
    else:
        # should not come here:
        wordFlags = gwi(wordName)

    if wordFlags == set(flags_like_open_quote):
        pass

    # for faster lookup in Python, we convert the bit arrays am array of
    # bits that are set:
    # uncomment when more info is wanted:
    #print 'wordFlags of |%s| are: %s (%s)'% (wordName, `wordFlags`, `showStateFlags(wordFlags)`)
    if type(stateFlags) == type(emptySet):
        pass
    else:
        # for testing only, this function should not be called direct, but this is
        # done from the testing routines
        state = copy.copy(stateFlags)
        if state == 0:
            state = set()
        elif state == -1:
            state = set(flag_no_space_next)
        elif state is None:
            state = set([flag_no_space_next, flag_active_cap_next])
        elif type(state) in (types.ListType, types.TupleType):
            state = set(state)
        else:
            raise ValueError("formatWord, invalid stateFlags: %s"% repr(stateFlags))
        stateFlags = copy.copy(state)

        
    # get the written form
    if wordName[:2] == '\\\\':
        wordName = '\\'
    else:
        wordName = wordName.split('\\')[0]

    #-----
    # Compute the output string
    output = ''

    # compute the number of CRLF's
    if flag_new_line in wordFlags:
        output = output + '\r\n'
    elif flag_new_paragraph in wordFlags:
        output = output + '\r\n\r\n'

    # compute the leading spacing
    if ( flag_no_formatting in wordFlags or
          flag_no_space_next in stateFlags or
          flag_no_space_all in stateFlags or
          flag_no_space_before in wordFlags or
          flag_cond_no_space in stateFlags and flag_cond_no_space in wordFlags ):
        # no leading space
        pass
    elif flag_two_spaces_next in stateFlags:
        output = output + '  '
    else:
        output = output + ' '

    # the no space all flag is used so we can remove the spaces from a phase
    # which may have imbeded spaces

    if not flag_no_formatting in wordFlags and flag_no_space_all in stateFlags:
        wordName = ''.join(wordName.split())

    # compute the capitalization by looking at the long term flags; this
    # effects all the words in the phrase

    if flag_no_formatting in wordFlags:
        # no capitalization change
        pass
    elif flag_lowercase_all in stateFlags:
        wordName = wordName.lower()
    elif flag_uppercase_all in stateFlags:
        wordName = wordName.upper()
    elif flag_cap_all in stateFlags and not flag_title_mode in wordFlags:
        words = string.split(wordName)
        words = [w.capitalize() for w in wordName.split()]
        wordName = ' '.join(words)
    elif flag_passive_cap_next in stateFlags:
        wordName = wordName.capitalize()

    # compute the capitalization for the first word in the phrase which
    # overrides the long term capitalization state

    if flag_no_formatting in wordFlags:
        # no capitalization change
        pass
    elif flag_lowercase_next in stateFlags:
        words = wordName.split()
        words[0] = words[0].lower()
        wordName= ' '.join(words)
    elif flag_uppercase_next in stateFlags:
        words = wordName.split()
        words[0] = words[0].upper()
        wordName= ' '.join(words)
    elif flag_active_cap_next in stateFlags:
        wordName = wordName.capitalize()
    elif flag_beginning_title_mode in stateFlags:
        wordName = wordName.capitalize()

    output = output + wordName

    #-----
    # compute the new state flags

    # clear out the capitalization
    if not flag_no_cap_change in wordFlags:
        stateFlags.discard(flag_active_cap_next)
        stateFlags.discard(flag_passive_cap_next)
        stateFlags.discard(flag_uppercase_next)
        stateFlags.discard(flag_lowercase_next)
        stateFlags.discard(flag_beginning_title_mode)

    # reset the state flags

    if not flag_no_space_change in wordFlags:
        stateFlags.discard(flag_no_space_next)
        stateFlags.discard(flag_two_spaces_next)
        # comment, experiment QH
        #stateFlags.discard(flag_cond_no_space)
    elif not flag_no_formatting in wordFlags:
        stateFlags.discard(flag_no_space_next)
        # comment, experiment QH
        #stateFlags.discard(flag_cond_no_space)
    # try to keep numbers and point together with this flag (QH):
    stateFlags.discard(flag_cond_no_space)

    # see if we need to reset the cap flags

    if flag_reset_uc_lc_caps in wordFlags:
        stateFlags.discard(flag_cap_all)
        stateFlags.discard(flag_uppercase_all)
        stateFlags.discard(flag_lowercase_all)

    # see if we need to reset the no space flags

    if flag_reset_no_space in wordFlags:
        stateFlags.discard(flag_no_space_all)

    if flag_cap_all in wordFlags:
        stateFlags.discard(flag_beginning_title_mode)

    # these flags just get copied
    copyList = [ flag_active_cap_next, flag_passive_cap_next,
         flag_uppercase_next, flag_lowercase_next, flag_no_space_next,
         flag_two_spaces_next, flag_cond_no_space, flag_cap_all,
         flag_uppercase_all, flag_lowercase_all, flag_no_space_all,
         flag_swallow_period, flag_beginning_title_mode ]


    for i in copyList:
        if i in wordFlags:
            stateFlags.add(i)

    if flag_new_paragraph in wordFlags and flag_is_period in wordFlags:
        stateFlags.add(flag_new_paragraph)

    return output,tuple(stateFlags)

def getWordInfo11(word):
    """new getWordInfo function, extracts the word flags from
    the middle word  like .\period\period
    
    return the resulting tuple of flags
    
    """
    if word.find('\\') == -1:
        return set()  # no flags
    wList = word.split('\\')
    if len(wList) == 3:
        prop = wList[1]
        if not prop:
            return set()
        if prop in propDict:
            return set(propDict[prop])
        elif prop.startswith('left-'):
            return set(propDict['left-double-quote'])
        elif prop.startswith('right-'):
            return set(propDict['right-double-quote'])
        else:
            print 'getWordInfo11, unknown word property: "%s" ("%s")'% (prop, word)          
            return set()  # empty tuple
    else:
        # should not come here
        return set()


def getWordInfo10(word):
    """old getWordInfo function, extracts the word flags from
    the word properties and convert to a tuple of values
    
    """
    wordInfo = natlink.getWordInfo(word)       
    wordFlags = wordInfoToFlags(wordInfo)
    print 'wordFlags of %s: %s'% (word, wordFlags)
    return wordFlags

def initializeStateFlags(*args):
    """return an initial state, built up by one or more state flags

    example from natspeak_spell:
    state = nsformat.initializeStateFlags(nsformat.flag_no_space_next)


    """
    return set(args)

def wordInfoToFlags(wordInfo):
    """convert wordInfo number into a set of flags
    
    """
    emptySet = set(())
    if wordInfo == None:
        return emptySet
    elif wordInfo == 0:
        return emptySet
    wordFlags = set()
    if type(wordInfo) == types.IntType:
        if  wordInfo:
            for i in range(32):
                if wordInfo & (1<<i):
                    wordFlags.add(i)
            else:
                pass # wordInfo == 0
    elif type(wordInfo) in (types.TupleType, types.ListType):
        wordFlags = set(wordInfo)
    elif type(wordInfo) == type(emptySet):
        wordFlags = copy.copy(wordInfo)
    return wordFlags

def showStateFlags(state):
    """returns an array of the state flags, that are set  (3,5) 


    """
    return tuple([flagNames[num] for num in state])


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

def testFormatting10():

    state = None
    state=testSubroutine(state,
        r'this is a test sentence .\period',
        'This is a test sentence.')

    state=testSubroutine(state,
        r'\Caps-On as you can see ,\comma this yours_truly seems to work \Caps-Off well',
        '  As You Can See, This Yours Truly Seems to Work well')
    state=testSubroutine(state,
        r'an "\open-quote example of testing .\period "\close-quote hello',
        ' an "example of testing."  Hello')

    print 'Example Formatting tests passed, more in unittestNsformat (in PyTest directory)'

def testFormatting11():

    state=None
    # assume english, two spaces after .:
    # note _ is converted into a space, inside a word ()

    state=testSubroutine(state,
        r'first .\period\period next',
        'First.  Next')
    # continuing the previous:
    state=testSubroutine(state,
        r'this is a second sentence .\period\period',
        ' this is a second sentence.')
    state=testSubroutine(state,
        r'\caps-on\Caps-On as you can see ,\comma\comma this yours_truly works \caps-off\caps_off well',
        '  As You Can See, This Yours Truly Works well')

    print 'Example Formatting tests (11) passed, more in unittestNsformat (in PyTest directory)'

if __name__=='__main__':
    natlink.natConnect()
    try:
        if natlinkmain.DNSversion >= 11:
            testFormatting11()
        else:
            testFormatting10()
        natlink.natDisconnect()
    except:
        natlink.natDisconnect()
        raise

