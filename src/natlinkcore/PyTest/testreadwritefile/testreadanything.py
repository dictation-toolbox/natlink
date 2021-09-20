from __future__ import unicode_literals
import io
import chardet
# from utilsqh import fixwordquotes
import os

def readAnything(source, filetype=None, tryAlternatives=True):
    """take any file and decode to unicode string
    
    works best if filetype is NOT given.
    First try ascii.
    If this fails, try utf-8.
    Then fix a few invalid bytes, 91-92, '" and space, fixwordquotes (utilsqh)
    If this fails, ask chardet. If it seems a Latin-1 variant, use Latin-1
    otherwise use the encoding as guessed by chardet.
    """
    sourceslash = source.replace('\\', '/')
    filename = os.path.split(sourceslash)[-1]
    
    if os.path.isfile(sourceslash):
        tRaw = io.open(sourceslash, 'rb').read()
        # tRaw = fixwordquotes(tRaw)
        if filetype:
            codingschemes = [filetype]
        else:
            codingschemes = ['ascii', 'utf-8', 'latin-1']
        for codingscheme in codingschemes:
            result = decodeencode(tRaw, codingscheme)
            if not result is False:
                return codingscheme, result
        print('file %s is not ascii, utf-8 or latin-1, continue with chardet'% filename)
        chardetResult = chardet.detect(tRaw)
        guessedType = chardetResult['encoding']
        confidence = chardetResult['confidence']
        result = decodeencode(tRaw, guessedType)
        if not result is False:
            return guessedType, result
        print('readAnything: no valid encoding found for file: %s (chardet gave: %s)' % (sourceslash, guessedType))
        return ''
    else:
        # consider source als stream of text
        print('continue with text: %s'% makeReadable(source))
        return None, source

def makeReadable(t):
    """squeeze text for readability"""
    t = t.strip()
    t = t.replace('\n', '\\\\')
    if len(t) > 100:
        return t[:50] + ' ... ' + t[-50:]
    else:
        return t
        
def decodeencode(tRaw, filetype):
    """return the decoded string or False
    """
    try:
        tDecoded = tRaw.decode(filetype)
    except UnicodeDecodeError:
        return False
    encodedAgain = tDecoded.encode(filetype)
    if encodedAgain == tRaw:
        return tDecoded
    else:
        return False
    

##test openn file

def testFromTestInivars(D):
    """test procedure from 3 tiny files in testIniVars directory
    
    Note: when no types are given, the result is 100% correct!
    First guess ascii, then guess utf-8, then try chardet.
    """
    ftypes = [('normal ascii.txt', None), ('utfimetpuntjes.txt', None), ('latin1ccedille.txt', None),
        ('normal ascii.txt', 'utf-8'),('normal ascii.txt', 'latin-1'),
         ('utfimetpuntjes.txt', 'utf8'), ('utfimetpuntjes.txt', 'utf-8'),
        ('utfimetpuntjes.txt', 'latin-1'),
         ('latin1ccedille.txt', 'latin-1'), 
        ('latin1ccedille.txt', 'utf-8'), ('latin1ccedille.txt', 'utf8'),
        ('latin1ccedille.txt', 'latin1')]
    for filename, encoding in ftypes:
        print('----------------test %s met encoding %s'% (filename, encoding))
        filepath = os.path.join(D, filename)
        filepath = filepath.replace('\\', '/')
        if not os.path.isfile(filepath):
            print('not a valid file: %s'% filepath)
            continue
        result = readAnything(filepath, filetype=encoding)
    
def testFromWebsiteInput(D):
    '''test all txt files from input of website
    '''
    for dirpath, dirnames, filenames in os.walk(D):
        txtFiles = [t for t in filenames if t.endswith('.txt')]
        if not txtFiles: continue
        print('-------- directory: %s'% dirpath)
        for t in txtFiles:
            filepath = os.path.join(dirpath, t)
            print('---- testing with %s'% t)
            result = readAnything(filepath)

def testStreamOfText(D):
    """reading a non-valid filename should produce itself
    """
    for dirpath, dirnames, filenames in os.walk(D):
        txtFiles = [t for t in filenames if t.endswith('.txt')]
        if not txtFiles: continue
        print('-------- directory: %s'% dirpath)
        for t in txtFiles:
            filepath = os.path.join(dirpath, t)
            print('---- testing with %s'% t)
            codingscheme, result = readAnything(filepath)
            newcodingscheme, result2 = readAnything(result)
            if result != result2:
                print('reading from stream not same!')
    


if __name__ == '__main__':
    # this test gives the encodings, including wrong ones:
    # D = 'C:/projects/unittest/testinivars'
    # testFromTestInivars(D)
    # this one shows the speed and hopefully the correctness of all txt files in a directory:
    D = r'C:\websites'
    testFromWebsiteInput(D)
    # testStreamOfText(D)
    print('klaar')