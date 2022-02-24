"""reading and writing files handling different possible encodings.

When reading a file, a 3 tuple (encoding, bom, content) is returned.
With utf-8, the bom mark could be present, a 3 byte raw string.
This especially is the case with the ini files of the Dragon program


readAnything(inputfile, filetype=None)
    (works best if filetype is NOT given,
     in that case, the list of "common encodings" is followed,
     until a probable hit is found. )

### example:
    from natlink.readwritefile import readAnything
    result = readAnything(testfile)
    if result:
        encoding, bom, text = result

### using this with configparser:




when writing a file, these three parameters should be passed again,
    bom: None if no bom mark is present or wanted

from natlink.readwritefile import writeAnything    
writeAnything(filepath, encoding, bom, content # if encoding is None take 'ASCII'
                                               # if bom is None use no bom 

Quintijn Hoogenboom, 2018, January/ February 2022

"""
import os
import copy
import sys

def fixCrLf(tRaw):
    """replace crlf into lf
    """
    if b'\r\r\n' in tRaw:
        print('readAnything, fixCrLf: fix crcrlf')
        tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
    if b'\r' in tRaw:
        # print 'readAnything, fixCrLf, remove cr'
        tRaw = tRaw.replace(b'\r', b'')
    return tRaw

def readAnything(inputfile, filetype=None):
    """take any file and decode to unicode string
    
    works best if filetype is NOT given.

    Try subsequently ascii, utf-8, cp1252, latin-1
    
    SKIP THIS: then fix a few invalid bytes, 91-92, '" and space SKIP THIS
    IN FAVOUR OF: cp1252, a microsoft superset of latin-1.
    
    # the next step with chardet is removed for the time being...
    If this fails, ask chardet and try. In my guess this should rarely happen,
    as the first three nearly always do the job
    (tried in test scripts/testreadanything.py)
    """    
    if os.path.isfile(inputfile):
        with open(inputfile, mode='rb') as file: # b is important -> binary
            tRaw = file.read()
        ## TODOQH handle utf-16le (with null characters...)
        tRaw = fixCrLf(tRaw)

        if filetype:
            codingschemes = [filetype]
        else:
            codingschemes = ['ascii', 'utf-8', 'cp1252',  'latin-1']
        # utf16le for nssystem.ini of Dragon15 cannot get this working: 'utf_16le', 'utf_16be', 'utf_16',
        # chardetResult = chardet.detect(tRaw)
        # guessedType = chardetResult['encoding']
        # confidence = chardetResult['confidence']
        #
        bom = None
        for codingscheme in codingschemes:
            result = DecodeEncode(tRaw, codingscheme)
            if not result is False:
                if codingscheme in ('cp1252', 'latin-1'):
                    pass
                if result and ord(result[0]) == 65279:  # BOM, remove
                    result = result[1:]
                    bom = tRaw[0:3]
                return codingscheme, bom, result
        # print 'readAnything: file %s is not ascii, utf-8 or latin-1, continue with chardet'% filename
        # chardetResult = chardet.detect(tRaw)
        # guessedType = chardetResult['encoding']
        # confidence = chardetResult['confidence']
        # result = DecodeEncode(tRaw, guessedType)
        print('readAnything: no valid encoding found for file: %s' % inputfile)
        return None, None, None
    # consider inputfile als stream of text
    # print 'readAnything, continue with text: %s'% makeReadable(inputfile)
    return None, None, inputfile

def writeAnything(filepath, encoding, bom, content):
    """write str or list of str to file
    use any of the encodings eg ['ascii', 'utf-8'],
    if they all fail, use xmlcharrefreplace in order to output all
    take "ASCII" if encoding is None
    take "" if bom is None
    """
    if isinstance(content, (list, tuple)):
        content = '\n'.join(content)

    if not isinstance(content, str):
        raise TypeError("writeAnything, content should be str, not %s (%s)"% (type(content), filepath))
    if encoding in [None, 'ascii']:
        encodings = ['ascii', 'latin-1']  # could change to cp1252, or utf-8
                                          # this is only if the encoding is new or read as ascii, and accented characters are introduced
                                          # in the text to output.
    elif isinstance(encoding, (list, tuple)):
        encodings = copy.copy(encoding)
    else:
        encodings = [encoding]

    for enc in encodings:
        try:
            tRaw = content.encode(encoding=enc)
        except UnicodeEncodeError:
            continue
        else:
            # if len(encodings) > 1:
            #     print 'did encoding %s (%s)'% (encoding, filepath)
            break
    else:
        enc = encodings[0]
        print(f'writeAnything: fail to encode file "{filepath}" with encoding(s): {encodings}.\n\tUse xmlcharrefreplace, and encoding: "{enc}"')
        tRaw = content.encode(encoding=enc, errors='xmlcharrefreplace')
        
    if sys.platform == 'win32':
        tRaw = tRaw.replace(b'\n', b'\r\n')
        tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
        
    if bom:
        # print('add bom for tRaw')
        tRaw = bom + tRaw 
    outfile = open(filepath, 'wb')
    # what difference does a bytearray make? (QH)
    outfile.write(bytearray(tRaw))
    outfile.close()

def DecodeEncode(tRaw, filetype):
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
    return False


if __name__ == '__main__':
    testdir = r'C:\Natlink\Natlink\PyTest\test_vcl_files'
    for Filename in os.listdir(testdir):
        if Filename.startswith('out'):
            continue
        Filepath = os.path.join(testdir, Filename)
        Result = readAnything(Filepath) 
        if Result:
            Encoding, Bom, t = Result
            print('file: %s, Encoding: %s, Bom: %s'% (Filename, Encoding, Bom))
            print('content: %s'% t)
            print('-'*40)
            outFilename = 'out' + Filename
            outFilepath = os.path.join(testdir, outFilename)
            if Encoding == 'ascii':
                Encodings = ['ascii', 'latin-1']
            else:
                Encodings = [Encoding]   # can also take ['ascii', Encoding], then, if no more non-ascii characters
                                         # the Encoding goes back to ascii
            # test should go wrong:
            Encoding = 'ascii'
            # writeAnything(outFilepath, Encoding, t)
            writeAnything(outFilepath, Encodings, Bom, t)
        else:
            print('file: %s, no Result')

    ## TODOQH see if this is still relevant. Probably a utf-16be ????
    testfile = r'C:/natlink/rudiger/acoustic.ini'
    Result = readAnything(testfile)
    if Result:
        Encoding, Bom, t = Result
        print('testfile: %s, Encoding: %s, Bom: %s'% (testfile, Encoding, repr(Bom)))
        Outfile = r'C:/natlink/rudiger/Bomacoustic.ini'
        writeAnything(Outfile, Encoding, Bom, t)
        Result2 = readAnything(Outfile)
        enc2, Bom2, t2 = Result2
        print('enc2: %s, (equal? %s)'% (enc2, Encoding == enc2))
        print('Bom2: %s, (equal? %s)'% (repr(Bom2), Bom == Bom2))
        print('text2: %s, (equal? %s)'% (t2, t == t2))
        
    