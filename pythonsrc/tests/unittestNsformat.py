#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# unittestNsformat.py
#   This script performs tests of the nsformat module, which was provided by Joel Gould and put into the
#   natlink Core folder by Quintijn, 2009
#
# run from a (preferably clean) US user profile, easiest from IDLE.
# do not run from pythonwin. See also README.txt in PyTest folder
#
# October, 2009, QH, added tests for nsformat
#pylint:disable=W0401, W0614, C0209, W0622, C0200, W0122, W0123
#pylint:disable=E1101
import time
import pytest
import natlink
# from natlinkcore import gramparser
# from natlinkcore.natlinkutils import *
from natlinkcore.nsformat import *

@pytest.mark.fixture


def dotest_formatting(state, Input, Output):

    words = Input.split()
    for i, _word in enumerate(words):
        words[i] = words[i].replace('_', ' ')
    actual,state = formatWords(words,state)
    if actual != Output:
        print(f'Expected {"Output"}')
        print(f'Actually {"actual"}')
        raise ValueError("test error")
    return state


def test_basic_formatting():

    state=None
    # assume english, two spaces after .:
    # note _ is converted into a space, inside a word ()

    state=dotest_formatting(state,
        r'first .\period\period next',
        'First.  Next')
    # continuing the previous:
    state=dotest_formatting(state,
        r'this is a second sentence .\period\period',
        ' this is a second sentence.')
    state=dotest_formatting(state,
        r'\caps-on\Caps-On as you can see ,\comma\comma this yours_truly works \caps-off\caps_off well',
        '  As You Can See, This Yours Truly Works well')




#---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # This utility subroutine executes a Python command and makes sure that
    # an exception (of the expected type) is raised.  Otherwise a TestError
    # exception is raised

    # Utility function which calls a routine and tests the return value

    def doTestFuncReturn(self, expected,command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars is None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if actual != expected:
            time.sleep(1)
        self.assertEqual(expected, actual, 'Function call "%s" returned unexpected result\nExpected: %s, got: %s'%
                          (command, expected, actual))

    def doTestFormatting(self, state, input, output):
        """do the testing, with input state, input and expected output
        
        this is the test from Joel, from the nsformat.py module
        
        NOTE: returns the output state!!!
        """
        words = input.split()
        inputState = copy.copy(state)
        for i in range(len(words)):
            words[i] = words[i].replace('_', ' ')
        actual,state = formatWords(words,state)
        self.assertEqual(output, actual, "output not as expected: expected: |%s|, actual output: |%s|\n\t\t(input: %s, state in: %s, state out: %s)"%
                                (output, actual, words, inputState, state))
        return state

    def doTestFormatLetters(self, input, output):
        """do the testing, with no inputState (this is fixed for this function)
        
        """
        words = input.split()
        for i in range(len(words)):
            words[i] = words[i].replace('_', ' ')
        actual = formatLetters(words)
        self.assertEqual(output, actual, "output of formatLetters not as expected: expected: |%s|, actual output: |%s|\n\t\t(input: %s)"%
                                (output, actual, words))

    #---------------------------------------------------------------------------
    def testFormatWord(self):
        r"""all words with normal (0) state as input.
        
        .\point results in ' .'
        """
        words =             ['.', r'.\period\period', r'.\dot\dot', r',\comma\comma', r':\colon\colon', r'-\hyphen\hyphen', 'normal']
        formattedExpected = [' .', '.',        '.',       ',',        ':',        '-', ' normal']
        stateExpected =      [(), (9, 4),      (8, 10),    (),       (),           (8,), ()]
        for word, expectedWord, expectedState in zip(words,  formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=None, stateFlags=set())
            print('stateFlages after formatting of %s: %s (%s)'% (word, repr(newState), repr(showStateFlags(newState))))
            self.assertTrue(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            expSet = set(expectedState)
            self.assertTrue(expSet == newState, "state after %s (%s) not as expected\nActual: %s, Expected: %s"%
                         (word, formattedResult, repr(newState), repr(expSet)))

    def testFormatLetters(self):
        r"""all words with normal (0) state as input.
        
        .\point results in ' .'
        """
        testFunc = self.doTestFormatLetters
        words =   r'x\spelling-letter\X_ray y\spelling-letter\Yankee !\spelling-exclamation-mark\exclamation_mark'
        state=testFunc(words, 'xy!')
        assert state == 0
       
    def testFlagsLike(self):
        """tests the different predefined flags in nsformat"""
        wfList = [(r'.\period\period', 'period'),
                (r',\comma\comma', 'comma'),
                (r'-\hyphen\hyphen', 'hyphen'),
                #( (10,), 'number'),  ## testing number later
                  ]
        gwi = getWordInfo
        for w,t in wfList:
            varInNsformat = 'flags_like_%s'% t
            if isinstance(w, tuple):
                flags = w
            else:
                wInfo = gwi(w)
                self.assertTrue(wInfo is not None, "word info for word: %s could not be found. US user???"% w)
                flags = wordInfoToFlags(wInfo)
                flags.discard(3)
                flags = tuple(flags) # no delete flag not interesting
            fromNsFormat = globals()[varInNsformat]
            self.assertTrue(fromNsFormat == flags, "flags_like variable |%s| not as expected\nIn nsformat.py: %s (%s)\nFrom actual word infoExpected: %s (%s)"%
                         (varInNsformat, fromNsFormat, showStateFlags(fromNsFormat), flags, showStateFlags(flags)))
            
    def testInitializeStateFlags(self):
        """test helper functions of nsformat"""
        result = initializeStateFlags()
        expected = set()
        self.assertTrue(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))

        result = initializeStateFlags(flag_cond_no_space)
        expected = set([10])
        self.assertTrue(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))
        
        result = initializeStateFlags(flag_cond_no_space, flag_no_formatting)
        expected =set([10, 18])
        self.assertTrue(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))
        readable = showStateFlags(result)
        expectedReadable = ('flag_cond_no_space', 'flag_no_formatting')
        self.assertTrue(expectedReadable == readable, "initialised state flags readable were not as expected\nActual: %s, Expected: %s"%
                     (readable, expectedReadable))
        
            
            
    def testFormatNumbers(self):
        """words with input of previous word, influencing numbers, to be kept together
        
        needs testing again, oct 2010 QH
        
        """
        if DNSVersion < 10:
            words =             [r'3\three', r'.\point', r'5\five', r'by', r'4\four', 'centimeter',
                                 r',\comma', 'proceeding']
        else:
            # does not work for Dragon 11
            return
        formattedExpected = [' 3', '.',        '5', ' by', ' 4', ' centimeter', ',', ' proceeding']
        wordInfos = [(flag_cond_no_space,), None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, None, None]
        stateExpected = [(10,), (8, 10), (10,), (), (10,), (), (), (), ()]
        newState = 0
        totalResult = []
        for word, info, expectedWord, expectedState in zip(words,  wordInfos, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=info, stateFlags=newState)
            totalResult.append(formattedResult)
            print('showStateFlages of %s: %s'% (word, repr(showStateFlags(newState))))
            self.assertTrue(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            expectedState = set(expectedState)  # changes QH oct 2011
            self.assertTrue(expectedState == newState, "state of %s (%s) not as expected\nActual: %s, expected: %s"%
                         (word, formattedResult, repr(newState), repr(expectedState)))
        expected = " 3.5 by 4 centimeter, proceeding"
        actual = ''.join(totalResult)
        self.assertTrue(expected == actual, "total result of first test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))




        # point without flag_cond_no_space around:
        words =             [r'the', r'.\point', r'is', r'.\period']
        formattedExpected = ['The', ' .',        'is', '.']
        stateExpected =     [(),   (8, 10),      (),  (9, 4)]
        newState = None  # start of buffer
        totalResult = []
        for word, expectedWord, expectedState in zip(words, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=None, stateFlags=newState)
            totalResult.append(formattedResult)
            print('showStateFlages of %s: %s'% (word, repr(showStateFlags(newState))))
            self.assertTrue(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assertTrue(expectedState == newState, "state of %s (%s) not as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, repr(newState), repr(expectedState)))

        expected = "The .is."
        actual = ''.join(totalResult)
        self.assertTrue(expected == actual, "total result of second test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))


        # words, numbers, words
        words =             [r'the', r'test', r'is', r'3\three', r'.\point', r'4\four', 'by', r'5\five', 'centimeter']
        wordInfos = [None, None, None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, None, None]
        formattedExpected = ['The', ' test', ' is', ' 3', '.', '4', ' by', ' 5', ' centimeter']
        stateExpected =     [(),      (),      (),  (10,), (8, 10), (10,), (), (10,), ()]
        newState = None  # start of buffer
        totalResult = []
        for word, wordInfo, expectedWord, expectedState in zip(words, wordInfos, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=wordInfo, stateFlags=newState)
            totalResult.append(formattedResult)
            print('showStateFlages of %s: %s'% (word, repr(showStateFlags(newState))))
            self.assertTrue(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assertTrue(expectedState == newState, "state of %s (%s) not as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, repr(newState), repr(expectedState)))

        expected = "The test is 3.4 by 5 centimeter"
        actual = ''.join(totalResult)
        self.assertTrue(expected == actual, "total result of third test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))

    def testSpacebar(self):
        """spacebar with dicate is handled ok, spacebar alone should produce a single space
        """
        testSubroutine = self.doTestFormatting
        
        if DNSVersion <= 10:
            state = -1
            state=testSubroutine(state,
                r'\space-bar',
                ' ')
            state = -1
            state=testSubroutine(state,
                r'\space-bar hello',
                ' hello')
            state = -1
            state=testSubroutine(state,
                r'hello \space-bar',
                'hello ')
        else:
            state = -1
            state=testSubroutine(state,
                r'\space-bar\space-bar',
                ' ')

            state = -1
            state=testSubroutine(state,
                r'\space-bar\space-bar hello',
                ' hello')
            state = -1
            state=testSubroutine(state,
                r'hello \space-bar\space-bar',
                'hello ')
            state = -1
            state=testSubroutine(state,
                r'space hello space',
                '  hello ')
        


            
    def testStartConditionsFormatWords(self):
        """testing the initial states that can be passed
        
        a set of numbers, or
        
        None:  ([flag_no_space_next, flag_active_cap_next])  ([8, 5])
        0: empty set (continue with a space in front)
        -1: special, no capping, but no space in front: set(flag_no_space_next) or ([8])
        """
        testFunc = self.doTestFormatting
        
        testFunc(None, 'hello', 'Hello')
        testFunc(0, 'this', ' this')
        testFunc(-1, 'is', 'is')
        testFunc(set(), 'good', ' good')
      
        testFunc(set([8, 5]),  'testing', 'Testing')
        testFunc(set([8]), 'with', 'with')

        # uppercase all (12)
        testFunc(set([8, 12]),  'testing more words', 'TESTING MORE WORDS')

        # capitalize all (11)
        testFunc(set([8, 11]),  'capitalize words in a title', 'Capitalize Words In A Title')

        # lowercase all (13) and no-spacing all (14)
        
        testFunc(set([13, 14]),  'Dakar @\\at-sign\\at_sign world .com\\dot_com', 'dakar@world.com')

        
        # and special, go to lowercase
        testFunc(set([7, 8]), 'Dakar', 'dakar')  # lowercase next...



    def testFormatting10(self):
        """these are a lot of tests for Dragon 10 (and before)
        
        study the words tested below!
        """

        if DNSVersion >= 11:
            return # for Dragon 11 and beyond
    
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
        state = None
        
        # special signs:
        state=testSubroutine(state,
            r'an example with many signs :\colon ;\semicolon and @\at-sign and [\left-bracket',
            r'An example with many signs:; and@and [')
            
        state = None
        state=testSubroutine(state,
            r'and continuing with ]\right-bracket and -\hyphen and -\minus-sign .\period',
            'And continuing with] and-and -.')
        state=testSubroutine
    
        # capping and spacing:
        state = None
        # after the colon is incorrect (at least different actual dictate result)!
        state=testSubroutine(state,
            r'hello \No-Space there and no spacing :\colon \No-Space-On Daisy Dakar and more \No-Space-Off and normal Daila_Lama again .\period',
            'Hellothere and no spacing:DaisyDakarandmore and normal Daila Lama again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'\No-Caps Daisy Dakar lowercase example \No-Caps-On Daisy DAL Daila_Lama and Dakar \No-Caps-Off and Dakar and Dalai_Lama again .\period',
            'daisy Dakar lowercase example daisy dal daila lama and dakar and Dakar and Dalai Lama again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'\Cap uppercase example and normal and \Caps-On and continuing with an uppercase example and \Caps-Off ,\comma normal again .\period',
            'Uppercase example and normal and and Continuing with an Uppercase Example and, normal again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'\All-Caps examples and normal and \All-Caps-On and continuing with \All-Caps-Off ,\comma normal again .\period',
            'EXAMPLES and normal and AND CONTINUING WITH, normal again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'combined \All-Caps-On hello \No-Space there and \No-Space-On back again and \All-Caps-Off continuing no spacing \No-Space-Off now normal again .\period',
            'Combined HELLOTHERE ANDBACKAGAINANDcontinuingnospacing now normal again.')
    
        # propagating the properties:
        state = None
        state=testSubroutine(state,
            r'\All-Caps-On this is a test',
            'THIS IS A TEST')
        state=testSubroutine(state,
            r'continuing in the next phrase \No-Space-On with no \All-Caps-Off spacing',
            ' CONTINUING IN THE NEXT PHRASEWITHNOspacing')
        state=testSubroutine(state,
            r'and resuming like that .\period this  \No-Space-Off is now at last normal .\period',
            'andresuminglikethat.This is now at last normal.')
    
        # new line, new paragraph:
        state = None
        state=testSubroutine(state,
            r'Now for the \New-Line and for the \New-Paragraph testing .\period',
            'Now for the\r\nand for the\r\n\r\nTesting.')
        
    def testFormatting11(self):
        """these are a lot of tests for Dragon 11 (and possibly beyond)
        
        study the words tested below!
        """
        if DNSVersion <= 10:
            return # for Dragon 11 and beyond
        testSubroutine = self.doTestFormatting
    
        state=None
        # assume english, two spaces after .:
        # note _ is converted into a space, inside a word ()

        # custom word added (*\\modulo)    
        state=testSubroutine(state,
            r'hello *\\modulo world',
            'Hello * world')
        
        state=None
        state=testSubroutine(state,
            r'first .\period\period next',
            'First.  Next')
        # continuing the previous:
        state=testSubroutine(state,
            r'this is a second sentence .\period\period',
            ' this is a second sentence.')
        state=testSubroutine(state,
            r'and a third sentence .\period\period',
            '  And a third sentence.')
        state=testSubroutine(state,
            r'\caps-on\Caps-On as you can see ,\comma\comma this yours_truly works \caps-off\caps_off well',
            '  As You Can See, This Yours Truly Works well')
    
        state=testSubroutine(state,
            r'an "\left-double-quote\open-quote example of testing .\period\period "\right-double-quote\close_quote hello',
            ' an "example of testing."  Hello')
        state=testSubroutine

        state = None
        state=testSubroutine(state,
            r'a hello .\dot\dot test message .\period\period and proceed with more .\dot\dot testing .\period\period',
            'A hello.test message.  And proceed with more.testing.')
        state=testSubroutine
    
        # special signs:
        state = None
        state=testSubroutine(state,
            r'an example with many signs :\colon\colon ;\semicolon\semicolon and @\at-sign\at_sign and [\left-square-bracket\left_bracket',
            r'An example with many signs:; and@and [')
            
        state = None
        state=testSubroutine(state,
            r'and continuing with ]\right-square-bracket\right_bracket and -\hyphen\hyphen and -\minus-sign\minus_sign .\period\period',
            'And continuing with] and-and -.')
        state=testSubroutine
    
        # capping and spacing:
        state = None
        # after the colon is incorrect (at least different actual dictate result)!
        state=testSubroutine(state,
            r'hello \no-space\no_space there and no spacing :\colon\colon \no-space-on\no_space_on Daisy Dakar and more \no-space-off\no_space_off and normal Daila_Lama again .\period\period',
            'Hellothere and no spacing:DaisyDakarandmore and normal Daila Lama again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'\no-caps\no_caps Daisy Dakar lowercase example \no-caps-on\no_caps_on Daisy DAL Daila_Lama and Dakar \no-caps-off\no_caps_off and Dakar and Dalai_Lama again .\period\period',
            'daisy Dakar lowercase example daisy dal daila lama and dakar and Dakar and Dalai Lama again.')
        state=testSubroutine
    
        state = None
        # note the capping of title words, can not be prevented here...!!
        state=testSubroutine(state,
            r'\cap\Cap uppercase example and normal and \caps-on\caps_on and continuing with an uppercase example and \caps-off\caps_off ,\comma\comma normal again .\period\period',
            'Uppercase example and normal and And Continuing With An Uppercase Example And, normal again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'\all-caps\all_caps examples and normal and \all-caps-on\all_caps_on and continuing with \all-caps-off\all_caps_off ,\comma\comma normal again .\period\period',
            'EXAMPLES and normal and AND CONTINUING WITH, normal again.')
        state=testSubroutine
    
        state = None
        state=testSubroutine(state,
            r'combined \all-caps-on\all_caps_on hello \no-space\no_space there and \no-space-on\no_space_on back again and \all-caps-off\all_caps_off continuing no spacing \no-space-off\no_space_off now normal again .\period\period',
            'Combined HELLOTHERE ANDBACKAGAINANDcontinuingnospacing now normal again.')
    
        # propagating the properties:
        state = None
        state=testSubroutine(state,
            r'\all-caps-on\all_caps_on this is a test',
            'THIS IS A TEST')
        state=testSubroutine(state,
            r'continuing in the next phrase \no-space-on\no_space_on with no \all-caps-off\all_caps_off spacing',
            ' CONTINUING IN THE NEXT PHRASEWITHNOspacing')
        state=testSubroutine(state,
            r'and resuming like that .\period\period this  \no-space-off\no_space_off is now at last normal .\period\period',
            'andresuminglikethat.This is now at last normal.')
    
        # new line, new paragraph:
        state = None
        state=testSubroutine(state,
            r'Now for the \new-line\new_line and for the \new-paragraph\new_paragraph testing .\period\period',
            'Now for the\r\nand for the\r\n\r\nTesting.')
    

if __name__ == "__main__":
    pytest.run()
