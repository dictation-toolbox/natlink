"""reading and writing files with unicode strings, handles encodings.

when reading a file, a 3 tuple (encoding, bom, content is returned.
With utf-8, the bom mark could be present. a 3 byte raw string

readAnything(source, filetype=None, tryAlternatives=True)
    (works best if filetype is NOT given. c
     Common alternatives for tryAlternatives are given by default, but utf-8 should be first)


when writing a file, these three parameters should be passed again,
    bom: None if no bom mark is present or wanted
    
writeAnything(filepath, encoding, bom, content # if encoding is None take 'ASCII'
                                               # if bom is None use no bom 

Quintijn Hoogenboom, 2018, January

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
    
    # next step with chardet removed for the time being...
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
        bom = None
        for codingscheme in codingschemes:
            result = decodeencode(tRaw, codingscheme)
            if not result is False:
                if codingscheme == 'latin-1':
                    pass
                if result and ord(result[0]) == 65279:  # BOM, remove
                    result = result[1:]
                    bom = tRaw[0:3]
                return codingscheme, bom, result
        # print 'readAnything: file %s is not ascii, utf-8 or latin-1, continue with chardet'% filename
        # chardetResult = chardet.detect(tRaw)
        # guessedType = chardetResult['encoding']
        # confidence = chardetResult['confidence']
        # result = decodeencode(tRaw, guessedType)
        print 'readAnything: no valid encoding found for file: %s' % sourceslash
        return None, None, None
    else:
        # consider source als stream of text
        # print 'readAnything, continue with text: %s'% makeReadable(source)
        return None, None, source

def writeAnything(filepath, encoding, bom, content):
    """write unicode or list of unicode to file
    use any of the encodings eg ['ascii', 'utf-8'],
    if they all fail, use xmlcharrefreplace in order to output all
    take "ASCII" if encoding is None
    take "" if bom is None
    """
    if type(content) in (types.ListType, types.TupleType):
        content = '\n'.join(content)
    if type(content) != types.UnicodeType:
        raise TypeError("writeAnything, content should be Unicode, not %s (%s)"% (type(content), filepath))
    if encoding in [None, 'ascii']:
        encodings = ['ascii', 'latin-1']  # could change to cp1252, or utf-8
                                          # this is only if the encoding is new or read as ascii, and accented characters are introduced
                                          # in the text to output.
    elif type(encoding) in (types.ListType, types.TupleType):
        encodings = copy.copy(encoding)
    else:
        encodings = [encoding]

    for encoding in encodings:
        try:
            tRaw = content.encode(encoding=encoding)
        except UnicodeEncodeError:
            continue
        else:
            # if len(encodings) > 1:
            #     print 'did encoding %s (%s)'% (encoding, filepath)
            break
    else:
        print 'fail to encode file %s with encoding(s): %s. Use xmlcharrefreplace'% (filepath, encodings)
        tRaw = content.encode(encoding=encoding, errors='xmlcharrefreplace')
    if bom:
        print 'add bom for tRaw'
        tRaw = bom + tRaw 
    io.open(filepath, 'wb').write(tRaw)
    pass


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
            encoding, bom, t = result
            print 'file: %s, encoding: %s, bom: %s'% (filename, encoding, bom)
            print 'content: %s'% t
            print '-'*40
            outfilename = 'out' + filename
            outfilepath = os.path.join(testdir, outfilename)
            if encoding == 'ascii':
                encodings = ['ascii', 'latin-1']
            else:
                encodings = [encoding]   # can also take ['ascii', encoding], then, if no more non-ascii characters
                                         # the encoding goes back to ascii
            # test should go wrong:
            encoding = 'ascii'
            # writeAnything(outfilepath, encoding, t)
            writeAnything(outfilepath, encodings, bom, t)
        else:
            print 'file: %s, no result'

    testfile = r'C:/natlink/rudiger/acoustic.ini'
    result = readAnything(testfile)
    if result:
        encoding, bom, t = result
        print 'testfile: %s, encoding: %s, bom: %s'% (testfile, encoding, repr(bom))
        outfile = r'C:/natlink/rudiger/bomacoustic.ini'
        writeAnything(outfile, encoding, bom, t)
        result2 = readAnything(outfile)
        enc2, bom2, t2 = result2
        print 'enc2: %s, (equal? %s)'% (enc2, encoding == enc2)
        print 'bom2: %s, (equal? %s)'% (repr(bom2), bom == bom2)
        print 'text2: %s, (equal? %s)'% (t2, t == t2)
        
    