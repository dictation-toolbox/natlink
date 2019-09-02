#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# wavtools.py
#
# A collection of routines which help in dealing with NIST wave files.
#
#----------
# File Formats
#
# The file format used by speech researchs for recorded speech is called a
# NIST wave file.  Although outside of Dragon, NIST wave files usually have
# an extension of ".wav", Dragon Systems uses an extension of ".nwv" to
# avoid confusing NIST wave files with Microsoft wave files.
#
# Audio files recorded under Microsoft Windows (ex: using the sound
# recorder) are in a format called RIFF wave format and have a standard
# extension or ".wav".
#
# Microsoft (RIFF) wave files are just one big block of recorded speech
# including silence as well.  Each RIFF wave file has a single header
# followd by the speech data.
#
# NIST wave files, on the other hand, break the speech up into utterances
# which are blocks of speech which were separated by silence when they were
# recorded.  NIST wave files are a concatented list of single utterances
# where each utterance has a header followed by the wave data.
#
# The binary data is compatible between RIFF and NIST wave files but the
# headers are not.  It is theoreticly possible to replace the header in a
# RIFF wave file to get a NIST wave file but then the NIST wave file would
# contain just one utterance even if the RIFF wave file represents many
# utterances with interveening silence.
#
#----------
# Word Spelling Conventions
#
# Words as returned by Dragon NaturallySpeaking in results objects are
# spelled according to SAPI spelling conventions.  SAPI spelling conventions
# allow for internal spaces.  However, some of Dragon's analysis tools do
# not deal with words which have internal spaces since they assume that the
# space character is used as a word separator in a string.
#
# Instead, for post processing of results, we use a different spelling
# convention for sords called the SDAPI format (for historical reasons). The
# basic idea is to replace spaces with underscores.  The actual
# transformation rules are as follows.  This is a reversable transformation.
#
#   SAPI --> SDAPI
#   ' '  --> '_'
#   '~'  --> '~~'
#   '_'  --> '~_'
#
# Some programs also escape right parens ')' -> '~)'.  This optional and is
# not done by this program but the reverse transform handles it fine.
#
#----------
# This file contains the following utility functions.
#
# convertWord(word)
#   returns a string which represents the input word converted from SAPI to
#   SDAPI format.  In other words, spaces are replaced by underscores.
#
# convertBack(word)
#   reverse of convertWord, returns the original SAPI format word.
#
# formatNistWave(file,riffWave,transcription,speaker,dateTime)
#   Converts an utterances from Microsoft RIFF wave format into NIST wave
#   format, and returns a string which is the NIST wave format of that
#   utterance.
#
#   The riffWave usually comes from a call to ResObj.getWave() although
#   it can come from a wav file as long as the wav file was recorded in the
#   correct format (16 bit, 11.025KHz, mono).
#
#   The transcription, speaker and dateTime are all optional and will be
#   included in the NIST wave header.  The dateTime should be a standard
#   Python time value (seconds since EPOC).
#
# loadNistFile(fileName)
#   Opens a NIST wave file and returns a list of NistWave objects
#   which correspond to the contents of the file.
#
# saveNistFile(fileName,waves)
#   Creates a new NIST wave file and writes out the NistWave objects.
#   This is the reverse of loadNistFile.  Warning: the header fields
#   may be written in a different order then when they were loaded.
#
# class NistWave
#   Class which encapuslates a NIST wave header and data.  An instance
#   of this class has a number of data members which directly represent
#   the data from the header.  This list includes (usually):
#       channel_count (integer)
#       sample_count (integer)
#       sample_n_bytes (integer)
#       sample_byte_format (string)
#       sample_coding (string)
#       sample_checksum (integer)
#       sample_rate (integer)
#       speaker_name (string)
#       recognized_text (string)
#       record_time (string)
#   Access these data members using dictionary lookup.  For example:
#       value = nist['channel_count']
#
#   The binary data is stored in a string attribute called "data".
#
#   You can create a NistWave object from a binary string using the
#   load function.  Pass in a binary buffer with offset to the start
#   of the data.  This function returns an offset past the data used.
#
#   Use the dump() function to get a binary string which represents
#   the Nist wave data for writing into a file.
#   

import re
import time
import string
import struct
import cStringIO

#---------------------------------------------------------------------------
# Convert word from SAPI format with embeded spaces to SDAPI format with
# underscores instead of spaces and tilde characters to escape underscores,
# tildes and close parenthesis.

def convertWord(word):
    word = string.replace(word,'~','~~')
    word = string.replace(word,'_','~_')
    word = string.replace(word,' ','_')
    return word

#---------------------------------------------------------------------------
# Convert word from SDAPI format without embeded spaces to SAPI format.

def convertBack(word):
    return re.sub('~.|_',convertSub,word)

def convertSub(matchObj):
    chars = matchObj.group(0)
    if chars  == '_': return ' '
    else: return chars[1:]

#---------------------------------------------------------------------------
# Given a Microsoft RIFF wave file (assumed to be in standard NatSpeak
# formmat) this returns a string which represents the NIST wave version.

def formatNistWave(waveData,transcript=None,speaker=None,dateTime=None):

    if transcript==None:
        transcript = '(unknown)'
    if speaker==None:
        speaker = '(unknown)'
    if dateTime==None:
        dateTime = time.time()

    # decode the riff wave header.  It is enough to know that the riff wave
    # header is 44 bytes long and that the data at offset 40 is a unsigned
    # long which is the length of the wave data
    dataLength = int(struct.unpack("L",waveData[40:44])[0])
    waveData = waveData[44:]

    # calculate the checksum
    checksum = 0
    for i in range(dataLength/2):
        checksum = checksum + struct.unpack('h',waveData[i*2:i*2+2])[0]
	checksum = checksum & 0xFFFF

    # make sure the transcript and speaker names are not too long; this
    # ensures that the NIST header does not get too long
    transcript = transcript[:256]
    speaker = speaker[:256]
    
    # write the NIST header, for example:
    #   NIST_1A
    #       1024
    #   channel_count -i 1
    #   sample_count -i 21010
    #   sample_n_bytes -i 2
    #   sample_byte_format -s2 01
    #   sample_coding -s3 pcm
    #   sample_checksum -i 60954
    #   sample_rate -i 11025
    #   speaker_name -s10 Joel Gould
    #   recognized_text -s29 market ,\comma \New-Paragraph
    #   record_time -s20 23-07-1999, 09:13:54
    #   end_head
    outBuf = cStringIO.StringIO()
    outBuf.write('NIST_1A\n')
    outBuf.write('   1024\n')
    outBuf.write('channel_count -i 1\n')
    outBuf.write('sample_count -i %d\n'%(dataLength/2))
    outBuf.write('sample_n_bytes -i 2\n')
    outBuf.write('sample_byte_format -s2 01\n')
    outBuf.write('sample_coding -s3 pcm\n')
    outBuf.write('sample_checksum -i %d\n'%checksum)
    outBuf.write('sample_rate -i 11025\n')
    outBuf.write('speaker_name -s%d %s\n'%(len(speaker),speaker))
    outBuf.write('recognized_text -s%d %s\n'%(len(transcript),transcript))
    outBuf.write('record_time -s20 %s\n'%time.strftime('%d-%m-%Y, %H:%M:%S',time.localtime(dateTime)))
    outBuf.write('end_head\n')
    
    curSize = len(outBuf.getvalue())

    # pad the header with zeros up to 1024 bytes
    outBuf.write('\0'*(1024-curSize))

    # write out the data
    outBuf.write(waveData[:dataLength])

    return outBuf.getvalue()

#---------------------------------------------------------------------------

class NistWave:

    def __init__(self):
        self.fields = {}
        self.data = None

    # load the data from a binary buffer, return an offset just past the end
    # of the data used.
    def load(self,dataIn,headerStart):
        # The start of the NIST wave header should be NIST_1A followed by
        # the size of the header
        res = re.match('NIST_1A\n\\s*(\\d+)\n',dataIn[headerStart:headerStart+32])
        if not res:
            raise TypeError,'Unable to find start of NIST wave header in data'
        headerSize = int(res.group(1))
        if headerSize > len(dataIn)+headerStart:
            raise TypeError,'Header size is smaller than size of data buffer'

        # Now we can extract the header and split it into lines
        headerEnd = string.find(dataIn,'end_head',headerStart,headerStart+headerSize)
        if headerEnd < 0:
            raise TypeError,'Missing end_head string in header'
            
        headerLines = string.split(dataIn[headerStart:headerEnd],'\n')

        # extract all the variables until reaching the 'end_head'
        for line in headerLines[2:]:
            if not line:
                continue
            tagName,tagType,tagData = string.split(line,' ',2)
            if tagType[:2] == '-i' or tagType[:2] == '-l':
                self.fields[tagName] = int(tagData)
            elif tagType[:2] == '-s':
                self.fields[tagName] = tagData
                if int(tagType[2:]) != len(tagData):
                    raise TypeError,'String length error for %s in NIST header'%tagName
            else:
                raise TypeError,'Unknown field type %s in NIST header'%tagType

        # compute the length of the data block
        dataSize = self.fields.get('channel_count',1) * \
                   self.fields.get('sample_count',1) * \
                   self.fields.get('sample_n_bytes',1)

        self.data = dataIn[headerStart+headerSize:headerStart+headerSize+dataSize]
        return headerStart+headerSize+dataSize

    # Return a binary string which represents the NistWave data.
    def dump(self):
        if not self.data:
            raise ValueError,'No data has been loaded'
    
        # compute the necessary length of the header
        sizeNeeded = 64
        for key,value in self.fields.items():
            sizeNeeded = sizeNeeded + len(key) + 10
            if type(value)==type(''):
                sizeNeeded = sizeNeeded + len(value)
        headerSize = 1024 * ( (sizeNeeded + 1023) / 1024 )

        outBuf = cStringIO.StringIO()
        outBuf.write('NIST_1A\n')
        outBuf.write('   %4d\n'%headerSize)
        for key,value in self.fields.items():
            if type(value)==type(''):
                outBuf.write('%s -s%s %s\n'%(key,len(value),value))
            else:
                outBuf.write('%s -i %s\n'%(key,value))
        outBuf.write('end_head\n')
        
        # pad the header with zeros
        curSize = len(outBuf.getvalue())
        outBuf.write('\0'*(headerSize-curSize))

        # add the data and return
        outBuf.write(self.data)
        return outBuf.getvalue()

    def __getitem__(self,item):
        return self.fields[item]

    def __setitem__(self,item,value):
        self.fields[item] = value

    def __delitem__(self,item):
        del self.fields[item]

#---------------------------------------------------------------------------

def loadNistFile(fileName):
    allData = open(fileName,'rb').read()
    output = []
    dataStart = 0
    while dataStart < len(allData):
        nistWave = NistWave()
        dataStart = nistWave.load(allData,dataStart)
        output.append(nistWave)
    return output

#---------------------------------------------------------------------------

def saveNistFile(fileName,waves):
    file = open(fileName,'wb')
    for wave in waves:
        file.write(wave.dump())
    file.close() 

#---------------------------------------------------------------------------
# The code below here is used to test the functionality of this module.

TestError = 'TestError'

def testConvertWord(word):
    if word != convertBack(convertWord(word)):
        raise TestError,'Convertion of "%s" is not reversable'%word
    
def test():
    testConvertWord('hello')
    testConvertWord('New York')
    testConvertWord('_\\underscore')
    testConvertWord('~\\tilde')
    testConvertWord('A messy_example~_~ !')
    testConvertWord('_1__2_~_3_ _4 ~ 5')
    testConvertWord('~~x~~~x~~~~x~~~~~x~~~~~~')
    testConvertWord('~~_~~~_~~~~_~~~~~_~~~~~~')
    testConvertWord('_~__~___~____~_____')
    print 'Test of wavtools passed.'
