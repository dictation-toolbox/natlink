#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# transcribe.py
#   This is a sample python script which will transcribe a directory of 
#   compressed wave files from a Dragon NaturallyMobile recorder.
#
# June 14, 1999
#   - initial version
#
# TODO rename temp files with better file names and delete old ones from 
# previous runs.
#

import os
import string
import glob
import struct
import tempfile
import calendar
import natlink
import mobiletools
from natlinkutils import *

TranscribeError = 'TranscribeError'

#
# For simplicity in this sample script, I hardcoded the input names.
#

# finished: 'd:\\Grand Canyon Recordings\\Card 1\\File 0*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 1\\File 1*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 1\\File [2-3]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 1\\File 4*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 1\\File [5-6]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [0]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [1]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [2]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [3]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [4]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [5]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [6-7]*.sri'
# finished: 'd:\\Grand Canyon Recordings\\Card 2\\File [8-9]*.sri'
fileSpecs = 'd:\\Grand Canyon Recordings\\Card 3\\File *.sri'

#---------------------------------------------------------------------------

def doTranscription():

    # compute a list of all files to be processed
    allFiles = glob.glob(fileSpecs)

    # open each file and extract the header information; convert the list of
    # files into a list of tuples of this information plus the filename
    fileInfo = []
    for fileName in allFiles:
        sriFile = open(fileName,'rb')
        fileInfo.append( (fileName,) + decodeHeader(sriFile) )
        sriFile.close()
        
    # sort this array
    fileInfo.sort(sortFunc)

    # process each file
    for file in fileInfo:
        processFile(file[0])

#---------------------------------------------------------------------------
# This fill decode the header of an open SRI file.  Details of the SRI file
# header are from the VoiceIt documentation.  It returns a tuple with the
# following information:
#
#   creation year   (i.e. 1992)
#   creation month  (1-12)
#   creation day    (1-31)
#   creation hour   (0-23)
#   creation minute (0-59)
#   creation second (0-59)
#   number of frames

sriHeaderSize = 212
sriFrameSize = 18
wavFrameSize = 240

def decodeHeader(sriFile):
    header = sriFile.read(sriHeaderSize)

    headerSize,headerID,unused,fileFormat,coderFormat = struct.unpack("H3sBBB",header[0:8])
    if headerSize != sriHeaderSize or headerID != 'SRI':
        raise TranscribeError,'File is not a valid SRI file'
    
    year,month,day,hour,minute,second = struct.unpack("BBBBBB",header[12:18])
    year = year + 1992

    packetSize,packetCount = struct.unpack("LL",header[32:40])
    if packetSize != sriFrameSize * 9 + 1:
        raise TranscribeError,'Unexpected packet size in header'

    return (year,month,day,hour,minute,second,packetCount)

#---------------------------------------------------------------------------=
# File sorting function.  We sort based on date.

def sortFunc(one,two):
    for x in range(1,7):
        if one[x] != two[x]:
            return cmp(one[x],two[x])
    return 0

#---------------------------------------------------------------------------
# Process one file

def processFile(fileName):

    # this create a decoder object
    sx96 = mobiletools.SX96Codec()

    # open the file and get the header information again (this has the side
    # effect of skipping past the header)
    sriFile = open(fileName,'rb')
    year,month,day,hour,minute,second,packetCount = decodeHeader(sriFile)

    # compute the size of the data for the output file
    frameCount = packetCount * 9
    outDataSize = frameCount * wavFrameSize
    
    # open an output wave file and write out a header
    tempFileName = tempfile.mktemp() + '.wav'
    wavFile = open(tempFileName,'wb')
    writeHeader(wavFile,outDataSize)

    # iterate over each packet (9 frames) in the input file, convert the data
    # and write the converted data into the output file
    for i in range(packetCount):
        for j in range(9):
            frame = sriFile.read(sriFrameSize)
            wavData = sx96.decode(frame)
            wavFile.write(wavData)
        # discard the extra packet descriptor byte
        sriFile.read(1)

    wavFile.close()
    wavFile = None

    sriFile.close()
    sriFile = None

    # now we transcribe this file in NatSpeak
    natlink.execScript('AppBringUp "NatSpeak"')
    natlink.playString(formatDate(year,month,day,hour,minute,second))
    natlink.inputFromFile(tempFileName)

#---------------------------------------------------------------------------
# Create a standard Microsoft (RIFF) wave file header
#
#   DWORD mainChunkType     'RIFF'
#   DWORD mainChunkSize     size of data plus 34
#   DWORD formType          'WAVE'
#
#   DWORD fmtChunkType      'fmt '
#   DWORD fmtChunkSize      size of this chunk (18)
#   WORD  wFormatTag        1 (WAVE_FORMAT_PCM)
#   WORD  nChannels         1
#   DWORD nSamplesPerSec    11025
#   DWORD nAvgBytesPerSec   22050
#   WORD  nBlockAlign       2
#   WORD  wBitsPerSample    16
#   WORD  cbSize            0
#
#   DWORD dataChunkType     'data'
#   DWORD dataChunkSize     size of data

def writeHeader(wavFile,dataSize):
    chunk1 = struct.pack("4sL4s",'RIFF',dataSize+34,'WAVE')
    chunk2 = struct.pack("4sLHHLLHHH",'fmt ',18,1,1,11025,22050,2,16,0)
    chunk3 = struct.pack("4sL",'data',dataSize)
    header = chunk1 + chunk2 + chunk3
    wavFile.write(header)

#---------------------------------------------------------------------------
# Formats the header on a transacribed block and returns a string.

def formatDate(year,month,day,hour,minute,second):
    monthName = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    dayName = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    weekDay = calendar.weekday(year,month,day)
    hourName = 'am'
    if hour > 12:
        hour = hour - 12
        hourName = 'pm'
    return '\n\n%s, %s %d, %d:%.2d%s) ' % (dayName[weekDay],monthName[month],day,hour,minute,hourName)

#---------------------------------------------------------------------------
# run
#
# This is the main entry point.  It will connect to NatSpeak and train
# a new user.  In the case of an error, it will cleanly disconnect from 
# NatSpeak and print the exception information,

def run():
    if not natlink.isNatSpeakRunning():
        raise TranscribeError,'NatSpeak should be running before transcribing files'
    try:
        natlink.natConnect()
        doTranscription()
    finally:
        natlink.natDisconnect()

if __name__=='__main__':
    run()
