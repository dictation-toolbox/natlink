"""reading and writing files handling different possible encodings.

Make an instance of the input_path:
>>> rwfile = ReadWriteFile()
>>> result = rwfile.readAnything(input_path)
>>> print(f'encoding: "{rwfile.encoding}", bom: "{rwfile.bom}")
>>> output_string = result + 'new text\n'
>>> output_path = ....
>>> rwfile.writeAnything(output_path, output_string)

The "bom mark" is sometimes/especially the case with the ini files of the Dragon program

### using this with configparser:

Quintijn Hoogenboom, 2018, January/March 2022

"""
import os
import sys

class ReadWriteFile:
    """read a file into a string
    
    collect encoding and bom mark (byte order mark, sometimes in Windows)
    
    a file can read via this class, and write back another string, using the same encoding and bom mark
    """
    def __init__(self, codingschemes=None, encoding=None):
        self.input_path = ''
        self.encoding = encoding or 'ascii'
        self.bom = ''
        self.text = ''
        self.rawText = b''
        self.codingschemes = codingschemes or ['ascii', 'utf-8', 'cp1252',  'latin-1']
    
    def readAnything(self, input_path, encoding=None):
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
        self.input_path = input_path
        if encoding:
            self.codingschemes = [encoding]
            
        if os.path.isfile(self.input_path):
            with open(self.input_path, mode='rb') as file: # b is important -> binary
                self.rawText = file.read()
            ## TODOQH handle utf-16le (with null characters...)
            tRaw = fixCrLf(self.rawText)

            # utf16le for nssystem.ini of Dragon15 cannot get this working: 'utf_16le', 'utf_16be', 'utf_16',
            # chardetResult = chardet.detect(tRaw)
            # guessedType = chardetResult['encoding']
            # confidence = chardetResult['confidence']
            #
            for codingscheme in self.codingschemes:
                result = DecodeEncode(tRaw, codingscheme)
                if not result is False:
                    if codingscheme in ('cp1252', 'latin-1'):
                        pass
                    if result and ord(result[0]) == 65279:  # BOM, remove
                        result = result[1:]
                        self.bom = tRaw[0:3]
                    self.text = result
                    self.encoding = codingscheme
                    return result
            # print 'readAnything: file %s is not ascii, utf-8 or latin-1, continue with chardet'% filename
            # chardetResult = chardet.detect(tRaw)
            # guessedType = chardetResult['encoding']
            # confidence = chardetResult['confidence']
            # result = DecodeEncode(tRaw, guessedType)
            print('readAnything: no valid encoding found for file: %s' % input_path)
            self.text = ''
            return ''
        # consider input_path als stream of text
        # print 'readAnything, continue with text: %s'% makeReadable(input_path)
        self.text = input_path
        return input_path
    
    def writeAnything(self, filepath, content):
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

        if self.encoding == 'ascii':
            i = self.codingschemes.index(self.encoding)
            # take 'ascii' and next encoding (will be 'utf-8')
            tryEncodings = self.codingschemes[i:i+2]
        else:
            tryEncodings = [self.encoding]
            
    
        for enc in tryEncodings:
            try:
                tRaw = content.encode(encoding=enc)
            except UnicodeEncodeError:
                print(f'warning writing back with encoding "{enc}" failed, try next from codingschemes')
                continue
            else:
                # if len(encodings) > 1:
                #     print 'did encoding %s (%s)'% (encoding, filepath)
                break
        else:
            enc = self.encoding
            print(f'writeAnything: fail to encode file "{filepath}" with encoding(s): {self.codingschemes[i:]}.\n\tUse xmlcharrefreplace, and original encoding: "{enc}"')
            tRaw = content.encode(encoding=enc, errors='xmlcharrefreplace')
            
        if sys.platform == 'win32':
            tRaw = tRaw.replace(b'\n', b'\r\n')
            tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
            
        if self.bom:
            # print('add bom for tRaw')
            tRaw = self.bom + tRaw 
        outfile = open(filepath, 'wb')
        # what difference does a bytearray make? (QH)
        outfile.write(bytearray(tRaw))
        outfile.close()
    
def fixCrLf(tRaw):
    """replace crlf into lf
    """
    if b'\r\r\n' in tRaw:
        print('readAnything, fixCrLf: fix crcrlf')
        tRaw = tRaw.replace(b'\r\r\n', b'\r\n')
    if b'\r' in tRaw:
        # print 'readAnything, self.fixCrLf, remove cr'
        tRaw = tRaw.replace(b'\r', b'')
    return tRaw
    
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
        rwfile = ReadWriteFile()
        Result = rwfile.readAnything(Filepath)
        if Result:
            print(f'file: "{Filepath}", Encoding: "{rwfile.encoding}", Bom: "{rwfile.bom}"')
            print(f'===content:\n{Result}\n')
            print('-'*40)
            outFilename = 'out' + Filename
            outFilepath = os.path.join(testdir, outFilename)
            rwfile.writeAnything(outFilepath, Result)
        else:
            print(f'file: "{Filepath}, no Result')

    # ## TODOQH see if this is still relevant. Probably a utf-16be ????
    # testfile = r'C:/natlink/rudiger/acoustic.ini'
    # Result = readAnything(testfile)
    # if Result:
    #     Encoding, Bom, t = Result
    #     print('testfile: %s, Encoding: %s, Bom: %s'% (testfile, Encoding, repr(Bom)))
    #     Outfile = r'C:/natlink/rudiger/Bomacoustic.ini'
    #     writeAnything(Outfile, Encoding, Bom, t)
    #     Result2 = readAnything(Outfile)
    #     enc2, Bom2, t2 = Result2
    #     print('enc2: %s, (equal? %s)'% (enc2, Encoding == enc2))
    #     print('Bom2: %s, (equal? %s)'% (repr(Bom2), Bom == Bom2))
    #     print('text2: %s, (equal? %s)'% (t2, t == t2))
        
    