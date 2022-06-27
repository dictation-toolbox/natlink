"""Python Macro Language for Dragon NaturallySpeaking
   (c) Copyright 1999 by Joel Gould
   Portions (c) Copyright 1999 by Dragon Systems, Inc.

   This code simulates the basic text formatting from NatSpeak.

   code written by Joel Gould, posted on the natpython discussion list on Wed, 28 Aug 2002

 removed pre 11 things,
 now for python3 version, with (normally) DNSVersion 15 (QH, June 2020)/Febr 2022
"""
#pylint:disable=C0116, C0123, R0911, R0912, R0915, R0916
import copy
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

flagNames = {}
name = ''
for name in globals():
    if name.startswith('flag_') and isinstance(globals()[name], int) and 0 < globals()[name] < 32:
        flagNames[globals()[name]] = name    
#
flags_like_period = (9, 4, 21, 17)  # flag_two_spaces_next = 9,  flag_passive_cap_next = 4, flag_no_space_before = 21
flags_like_comma = (21, )  # flag_no_space_before = 21  (flag_nodelete = 3 we just ignore here, so leave out)
flags_like_number = (10,)
flags_like_point = (8, 10, 21)  # no spacing (combination with numbers seems
                                # obsolete (cond_no_space = 10)
flags_like_hyphen = (8, 21)  # no spacing before and after
flags_like_open_quote = (8, 20) # no space next and no cap change
flags_like_close_quote = (21, 20, 19) # no space before, no cap change and no space change (??)

# word flags from properties part of the word:
# Dragon 11...
propDict = {}
propDict['space-bar'] = (flag_space_bar, flag_no_space_next, flag_no_formatting,
                         flag_no_cap_change, flag_no_space_before) #  (8, 18, 20, 21, 27)

propDict['period'] = flags_like_period
propDict['point'] = flags_like_point
propDict['dot'] = flags_like_point
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

# spelling props:
propDict['spelling-cap'] = propDict['cap']
propDict['letter'] = (flag_no_space_next,)   # lowercase is hardcoded in below.
propDict['spelling-letter'] = (flag_no_space_next,)   # lowercase is hardcoded in below.
propDict['uppercase-letter'] = (flag_no_space_next,)

#---------------------------------------------------------------------------
# This is the main formatting entry point.  It takes the old format state and
# a list of words and returns the new formatting state and the formatted
# string.
#
# If you already have the wordInfo for each word, you can pass in a list of
# tuples of (wordName,wordInfo) instead of just the list of words.

def formatWords(wordList,state=None):
    """return the formatted words and the state at end.
    
    when passing this state in the next call, the spacing and capitalization
    will be maintained.
    """
    #pylint:disable=W0603
    global flags_like_period
    language = 'enx'
    if language != 'enx':
        flags_like_period = (4, 21, 17) # one space after period.
        
    gwi = getWordInfo

    output = ''
    for entry in wordList:
        if entry == 'space':
            entry = r'\space-bar\space-bar'
        if isinstance(entry, tuple):
            assert len(entry)==2 
            wordName = entry[0]
            wordInfo = entry[1]
        else:
            if entry.find('\\letter\\') > 0:
                entry = entry.lower()  # letters lowercase...
            wordName = entry
            wordInfo = gwi(wordName)
        if wordInfo is None:
            wordInfo = set()
        if isinstance(wordInfo, set):
            wordInfo = wordInfoToFlags(wordInfo)

        # init state to a set:
        if state == 0:
            state = set([])
        elif state == -1:
            #print "no space next at start"
            state = set([flag_no_space_next])
        elif state is None:
            state = set([flag_no_space_next, flag_active_cap_next])
        elif isinstance(state, (list, tuple)):
            state = set(state)
        elif not isinstance(state, set):
            state = wordInfoToFlags(state)
            #print 'formatWords starting with: %s'% state

        newText, state = formatWord(wordName,wordInfo,state)
        output = output + newText

    return output, state

countDict= dict(one=1, two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9,
                een=1, twee=2, drie=3, vier=4, vijf=5, zes=6, zeven=7, acht=8, negen=9)


def formatPassword(wordList):
    """format the words, no spaces capping each word, getting the numbers and repeating the @ etc
>>> formatPassword(['small', 'bird', 'three', '@'])
'SmallBird3@@@'

    """
    nextRepeat = 0
    outList = []
    for w in wordList:
        if nextRepeat:
            while nextRepeat:
                outList.append(w)
                nextRepeat -= 1
        elif w in countDict:
            nextRepeat = countDict[w]
            outList.append(str(nextRepeat))
        else:
            outList.append(w.capitalize())
    return ''.join(outList)
        
def formatLetters(wordList):
    """just return the letters, in practice the first letter of each word
    
        do as input the flag_no_space_all!
        return only the resulting string!!
    """
    inputState = (flag_no_space_all,)
    res, _state = formatWords(wordList, inputState)
            
    return res
                          
#---------------------------------------------------------------------------
# This is the formatting subroutine.  It handles the formatting for a single
# word using the standard Dragon NaturallySpeaking state machine.
#
# This code was adapted from shared\resobj.cpp
def formatWord(wordName,wordInfo=None,stateFlags=None, gwi=None):
    ##adapted: wordInfo and stateFlags are now sets of state flags
    if gwi is None:
        gwi = getWordInfo
    #-----
    # Preparation
    # assume wordInfo is a set already
    if isinstance(wordInfo, set):
        wordFlags = wordInfo
    else:
        # should not come here:
        wordFlags = gwi(wordName)

    # for faster lookup in Python, we convert the bit arrays am array of
    # bits that are set:
    # uncomment when more info is wanted:
    #print 'wordFlags of |%s| are: %s (%s)'% (wordName, `wordFlags`, `showStateFlags(wordFlags)`)
    if isinstance(stateFlags, set):
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
        elif isinstance(state, (list, tuple)):
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
    elif flag_space_bar in wordFlags:  # fix QH, oct 2011
        output = output + ' '

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
        words = wordName.split()
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

    return output, stateFlags

def getWordInfo(word):
    r"""new getWordInfo function, extracts the word flags from
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
        if prop.startswith('left-'):
            return set(propDict['left-double-quote'])
        if prop.startswith('right-'):
            return set(propDict['right-double-quote'])
        print('getWordInfo11, unknown word property: "%s" ("%s")'% (prop, word))          
        return set()  # empty tuple
    # should not come here
    return set()

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
    if wordInfo is None:
        return emptySet
    if wordInfo == 0:
        return emptySet
    wordFlags = set()
    if isinstance(wordInfo, int):
        if  wordInfo:
            for i in range(32):
                if wordInfo & (1<<i):
                    wordFlags.add(i)
    elif isinstance(wordInfo, (tuple, list)):
        wordFlags = set(wordInfo)
    elif isinstance(wordInfo, set):
        wordFlags = copy.copy(wordInfo)
    return wordFlags

def showStateFlags(state):
    """returns an array of the state flags, that are set  (3,5) 


    """
    return tuple([flagNames[num] for num in state])


#---------------------------------------------------------------------------

def testSubroutine(state, Input, Output):

    words = Input.split()
    for i, _word in enumerate(words):
        words[i] = words[i].replace('_', ' ')
    actual,state = formatWords(words,state)
    if actual != Output:
        print('Expected "%s"'%Output)
        print('Actually "%s"'%actual)
        raise ValueError("test error")
    return state

#---------------------------------------------------------------------------
def testFormatting():

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

    print('Example Formatting tests (11) passed, more in unittestNsformat (in PyTest directory)')

if __name__=='__main__':
    import doctest
    natlink.natConnect()
    doctest.testmod()
    
    ## offline (without Dragon) testing ok:
    testFormatting()
    
    ## online testing (with Dragon) should be tried again
    ##
    
    natlink.natDisconnect()
    

