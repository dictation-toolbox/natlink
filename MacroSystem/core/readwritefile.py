"""reading and writing files with unicode strings, handles encodings.
"""

import io
import os
import os.path
import types
import copy


def fixCrLf(tRaw):
    """replace crlf into lf
    """
    if b'\r\r\n' in tRaw:
        print 'readAnything, fixCrLf: fix crcrlf'
        tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
    if b'\r' in tRaw:
        # print 'readAnything, fixCrLf, remove cr'
        tRaw = tRaw.replace(b'\r', b'')
    return tRaw

def readAnything(source, filetype=None, tryAlternatives=True):
    """take any file and decode to unicode string
    
    works best if filetype is NOT given.
    Try in arow ascii, utf-8, 'cp1252' latin-1
    SKIP THIS: then fix a few invalid bytes, 91-92, '" and space SKIP THIS
    IN FAVOUR OF: cp1252, a microsoft superset of latin-1.
    
    If this fails, ask chardet and try. In my guess this should rarely happen,
    as the first three nearly always do the job
    (tried in test scripts/testreadanything.py)
    """    
    sourceslash = source.replace('\\', '/')
    filename = os.path.split(sourceslash)[-1]
    
    if os.path.isfile(sourceslash):
        
        tRaw = io.open(sourceslash, 'rb').read()
        tRaw = fixCrLf(tRaw)

        if filetype:
            codingschemes = [filetype]
        else:
            codingschemes = ['utf-8', 'cp1252',  'latin-1']
        # chardetResult = chardet.detect(tRaw)
        # guessedType = chardetResult['encoding']
        # confidence = chardetResult['confidence']
        # 
        for codingscheme in codingschemes:
            result = decodeencode(tRaw, codingscheme)
            if not result is False:
                if codingscheme == 'latin-1':
                    pass
                if result and ord(result[0]) == 65279:  # BOM, remove
                    result = result[1:]
                return codingscheme, result
        print 'readAnything: file %s is not ascii, utf-8 or latin-1, continue with chardet'% filename
        chardetResult = chardet.detect(tRaw)
        guessedType = chardetResult['encoding']
        confidence = chardetResult['confidence']
        result = decodeencode(tRaw, guessedType)
        if not result is False:
            print 'readAnything: encoding %s succesfull (%s)'% (guessedType, sourceslash)
            return guessedType, result
        print 'readAnything: no valid encoding found for file: %s (chardet gave: %s)' % (sourceslash, guessedType)
        return ''
    else:
        # consider source als stream of text
        # print 'readAnything, continue with text: %s'% makeReadable(source)
        return None, source

def writeAnything(filepath, encoding, content):
    """write unicode or list of unicode to file
    use any of the encodings eg ['ascii', 'utf-8'],
    if they all fail, use xmlcharrefreplace in order to output all.
    """
    if type(content) in (types.ListType, types.TupleType):
        content = '\n'.join(content)
    if type(content) != types.UnicodeType:
        raise TypeError("writeAnything, content should be Unicode, not %s (%s)"% (type(content), filepath))
    if type(encoding) in (types.ListType, types.TupleType):
        encodings = copy.copy(encoding)
    else:
        encodings = [encoding]

    for encoding in encodings:
        try:
            io.open(filepath, 'w', encoding=encoding).write(content)
        except UnicodeEncodeError:
            continue
        else:
            if len(encodings) > 1:
                print 'did encoding %s (%s)'% (encoding, filepath)
            return
    print 'fail to encode file %s with encoding(s): %s. Use xmlcharrefreplace'% (filepath, encodings)
    io.open(filepath, 'w', encoding=encoding, errors='xmlcharrefreplace').write(content)

def decodeencode(tRaw, filetype):
    """return the decoded string or False
    
    used by readAnything, also see testreadanything in miscqh/test scripts
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

if __name__ == '__main__':
    testdir = r'C:\NatLink\NatLink\PyTest\test_vcl_files'
    for filename in os.listdir(testdir):
        if filename.startswith('out'):
            continue
        filepath = os.path.join(testdir, filename)
        result = readAnything(filepath)
        if result:
            encoding, t = result
            print 'file: %s, encoding: %s'% (filename, encoding)
            print 'content: %s'% t
            print '-'*40
            outfilename = 'out' + filename
            outfilepath = os.path.join(testdir, outfilename)
            if encoding == 'ascii':
                encodings = ['ascii', 'utf-8']
            else:
                encodings = [encoding]   # can also take ['ascii', encoding], then, if no more non-ascii characters
                                         # the encoding goes back to ascii
            # test should go wrong:
            encoding = 'ascii'
            # writeAnything(outfilepath, encoding, t)
            writeAnything(outfilepath, encodings, t)
        else:
            print 'file: %s, no result'
