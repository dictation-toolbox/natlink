#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# trainuser.py
#   This is a sample python script which will create a new trained user
#   from a series of recorded sessions.
#

########################################################################
#
# This script takes the following things as input:
#
# (1) A set of NWV files which contain recordings made by speaking
#   to Dragon NaturallySpeaking.
#
#   An NWV file is a industry standard NIST wave file.  Such files can be
#   created by running the SaveWave program which comes with Dragon
#   NaturallySpeaking then using NatSpeak normally.
#
# (2) A corresponding set of LST files which contain the transcripts
#   for the recordings in the NWV files.  There should be one LST file
#   for every NWV file (with the same filename).  The LST file must have
#   one line for every separate utterance in the NWV file.  That line
#   should contain the transcript of the utterance.
#
#   When you run SaveWave, it create a LST file which contains the recognized
#   transacript.  If there have been recognition errors this transacript
#   will be wrong and need to be corrected before the LST file is used
#   for training.
#
#   To exclude an utterance from training (for example, because it was
#   garbled), you should make the corresponding line in the LST file blank.
#
#   The spelling of words in the transcripts in the LST file need to be
#   modified in some cases.  Specifically, a space character is used to
#   delimit words so if there are any spaces inside of words (like the
#   word "New York"), those spaces need to be converted into underscores.
#
#   For completeness, underscores are converted into the two character
#   sequence tilde-underscore (~_) and tilde characters are converted into
#   the two character sequence tilde-tilde (~~).  Finally, some older files
#   use the two character sequence tilde-right parenthesisinstead of a single
#   right parenthesis.  This is supported but not required.
#
# (3) The name of a user to create.
#
# (4) The name of the base models to use to create the user.  The base
#   models can be found in the registry under the key:
#
#       HKEY_LOCAL_MACHINE\Software\Dragon Systems\NaturallySpeaking\
#       Professional 3.0\System\Base Models
#
#   For the Preferred version, the key contains the string "Preferred 3.0"
#   instead of "Professional 3.0".  International version will also have
#   a different edition name.
#
#   For Professional 3.02 and 3.52 versions, the following base models
#   are available:
#       BestMatch Model
#       Standard Model
#
# (5) The name of the base topic to use to create the user.  The base
#   topics can also be found in the registry in the same place except for
#   the name of the last key:
#
#       ...\System\Base Topics
#
#   For Professional 3.02 and 3.52 versions, the following base models
#   are available:
#
#       General English - BestMatch
#       General English - BestMatch 64k+
#       General English - Standard
#
########################################################################

import string
import sys              # for stdout
import glob             # file name parsing
import traceback        # for printing exceptions
import os.path          # for filename parsing

import wavtools         # for convertBack
import natlink
from natlinkutils import *

#
# Miscelleanous additional global stuff
#

TrainingError = 'TrainingError'

#---------------------------------------------------------------------------
# trainUser
#
# This is the main entry subroutine.  It creates and trains a new user
# from recorded utterances and transcripts.

def doTraining(fileSpecs,userName='',baseModel='',baseTopic=''):
    if not userName:
        userName = 'Created from Python'

    #
    # Expand the file specification list into a list of files without
    # extensions
    #

    allFiles = []
    if type(fileSpecs) == type(''):
        allFiles = expandFiles(fileSpecs)
    else:
        for fileSpec in fileSpecs:
            allFiles = allFiles + expandFiles(fileSpec)

    if not len(allFiles):
        print "No files found which match fileSpec:"
        print "  ",fileSpecs
        raise TrainingError,'no files'

    #
    # Create a new user.  Make sure the new user is active.
    #

    createNewUser(userName,baseModel,baseTopic)

    #
    # Read the LST files from disk into Python arrays.  As we read the LST
    # files, we need to convert the format of words from underscores (using
    # tilde as an escape character) into spaces.
    #
    # We build up a master array which contains one entry per input file.
    # Each file entry is an array with one entry per utterance.  Each
    # utterance entry is an array of strings representing the words
    # recognized.
    #

    allWords = []
    for fileName in allFiles:
        allWords.append(loadWords(fileName))

    #
    # The NIST wave files have to converted into NatSpeak result objects.
    # The easiest way to do this is to build a dictation grammar and recognize
    # all of the utterances in the NIST wave files.
    #

    allResults = []
    for fileName in allFiles:
        allResults.append(loadResults(fileName))

    #
    # Produce a single array which contains tuples representing the results
    # object and the transcript.  Skip over any results which have blank
    # transcripts.  Print an error if the two arrays sizes do not match
    #

    combinedResults = []
    fileCount = len(allFiles)
    for fileNum in range(fileCount):
        lstSize = len(allWords[fileNum])
        nwvSize = len(allResults[fileNum])
        if lstSize != nwvSize:
            print 'The number of utterances in',
            print allFiles[fileNum]+'.nwv','('+str(nwvSize)+')',
            print 'does not match',
            print 'the number of lines in',
            print allFiles[fileNum]+'.lst','('+str(lstSize)+')'
        for resNum in range(lstSize):
            words = allWords[fileNum][resNum]
            resObj = allResults[fileNum][resNum]
            if len(words) and resObj:
                combinedResults.append((words,resObj))

    #
    # Perform calibration on the first N utterances (20 maximum)
    #

    trainingPass(combinedResults[:20],'calibrate')

    #
    # Perform batch adaptation on the entire set of utterances.
    #

    trainingPass(combinedResults,'longtrain')

    #
    # Perform training on the entire set of utterances.
    #

    trainingPass(combinedResults,'batchadapt')

    #
    # Save the user.
    #

    print 'Saving the user...'
    natlink.saveUser()
    print 'All done.'

#---------------------------------------------------------------------------
# expandFile
#
# We take a single file specification and use the glob function to look up
# all files in the filesystem which match that specification.  Then for each
# filename we remove the extension and add that filename to a list which is
# returned.

def expandFiles(fileSpec):
    # force the extension of the fileSpec
    fileSpec = os.path.splitext(fileSpec)[0] + '.nwv'

    files = []
    for fileName in glob.glob(fileSpec):
        files.append( os.path.splitext(fileName)[0] )
    return files

#---------------------------------------------------------------------------
# createNewUser
#
# Create, then open a new user in NatSpeak.  When debugging or using the
# most common error is if the user already exists and is currently active.
# In that case we just make sure that it has not been trained.  (Note that
# we can not easily detect whether the user exists but is not active with
# the current natlink code but an error will be thrown).

def createNewUser(userName,baseModel,baseTopic):
    if natlink.getCurrentUser()[0] == userName:
        print 'Training existing user:',userName
    else:
        print 'Creating user:',userName
        if baseModel:
            print '  using baseModel:',baseModel
        else:
            print '  using baseModel: (default)'
        if baseTopic:
            print '  using baseTopic:',baseTopic
        else:
            print '  using baseTopic: (default)'
        natlink.createUser(userName,baseModel,baseTopic)
        natlink.openUser(userName)
    if natlink.getUserTraining():
        print 'Error: user is already at least partially trained.'
        raise TrainingError,'user is trained'

#---------------------------------------------------------------------------
# loadWords
#
# We take the name of a single input file (without extension), open the
# corresponding LST file and extract all the transcripts.  We return a
# list of lines.  Each line being a list of words.  Each word is converted
# from underscore/tilde encoded format to normal spelling with optional
# internal spaces.
#
# Note 1: we use a LS2 file if it exists instead of a LST file.
# Note 2: is the transcript is *deleted* then we make the transcript blank
#   (also [reject])

def loadWords(fileName):
    if os.access(fileName+'.ls2',4):
        fileName = fileName + '.ls2'
    elif os.access(fileName+'.lst',4):
        fileName = fileName + '.lst'
    else:
        raise TrainingError,'Unable to find LST or LS2 file for %s'%fileName

    print 'Loading words from '+fileName
    allWords = []
    for line in open(fileName,'r').readlines():
        if not line or string.lower(line[:7]) in ['*delete','[reject']:
            allWords.append([])
            continue
        words = []
        for word in string.split(line):
            words.append(wavtools.convertBack(word))
        allWords.append(words)
    return allWords

#---------------------------------------------------------------------------
# Here we create an array of results objects for every 
 
def loadResults(fileName):
    print 'Recognizing from '+fileName+'.nwv...'
    print '>',' '*70,
    grammar = DictationGrammar()
    grammar.initialize()
    
    # Here we force recognition to happen.  The results objects will be
    # created for each utterance in the wave file and passed to the callback
    # function (callback.func) where they will be collected in an array
    natlink.inputFromFile(fileName+'.nwv')

    print ''
    grammar.unload()
    return grammar.results

# This is a dictation grammar.  We set the special allResults flag on the
# load call which allows us to get results objects even when the recognition
# is rejected or belongs to another grammar.  Then we set our grammar to be
# exclusive to make sure that no other grammar in the system gets our
# recognition results.
#
# When we get the results object after every recognition, we add it to an
# array.

class DictationGrammar(GrammarBase):

    # this is the specification of a normal dictation grammar (the special
    # global rule called dgndictation implements dictation).

    gramSpec = """
        <dgndictation> imported;
        <Start> exported = <dgndictation>;
    """

    # during initialization we load the grammar and activate it

    def initialize(self):
        self.results = []
        if not self.load(self.gramSpec,allResults=1): 
            return None
        self.activate('Start',exclusive=1)

    # this callback is where we get the results object

    def gotResultsObject(self,recogType,resObj):
        self.results.append(resObj)
        if recogType != 'reject':
            words = string.ljust(string.join(resObj.getWords(0)),70)
            print '\b'*72,
            print words[0:70],

#---------------------------------------------------------------------------
# trainingPass
#
# This does a training pass on all the utterances or a subset of the 
# utterances.  This routine is suitable for all three types of training
# passes

def trainingPass(combinedResults,trainingType):
    count = len(combinedResults)
    print 'Performing %s on %d utterances...           ' % (trainingType,count),
    natlink.startTraining(trainingType)
    for result in combinedResults:
        result[1].correction(result[0])
        count = count - 1
        sys.stdout.write('\b\b\b\b\b\b\b\b\b\b%5d left' % count)
    natlink.finishTraining()
    print ''

#---------------------------------------------------------------------------
# parseArgs
#
# Parse command line arguments.  Prints help message if necessary.
# Returns fileSpecs,userName,baseModel,baseTopic where fileSpecs will
# be None to exit.

def parseArgs(args):
    if not( 1<=len(args)<=4 ) or args[0]=='?':
        print ''
        print 'Trainuser.py creates a new NatSpeak user by simulating enrollment'
        print '  using recordings with corrected transcripts.'
        print ''
        print 'Usage: trainuser.py fileSpecs [userName [baseModel [baseTopic]]]'
        print '  fileSpecs = name of NWV source file(s), wildcards allowed'
        print '  userName = name for user to be created'
        print '  baseModel = name of base acoustic models to use, one of:'
        print '    "Standard Model"         or standard'
        print '    "BestMatch Model"        or bestmatch'
        print '    "BestMatch III Model"    or bestmatch3'
        print '    "Student Standard Model" or student'
        print '  baseTopic = name of base vocabulary to use, one of:'
        print '    "US General English - Standard"            or standard'
        print '    "US General English - BestMatch"           or bestmatch'
        print '    "US General English - BestMatch Plus"      or plus'
        print '    "Student General English - Standard"'
        print '    "Student General English - BestMatch"      or student'
        print '    "Student General English - BestMatch Plus"'
        return None,None,None,None

    fileSpecs = args[0]
    if len(args)<2:
        return fileSpecs,'','',''

    userName = args[1]
    if len(args)<3:
        return fileSpecs,userName,'',''

    baseModelDict = {
        'standard':'Standard Model',
        'bestmatch':'BestMatch Model',
        'bestmatch3':'BestMatch III Model',
        'student':'Student Standard Model',
    }
    baseModel = baseModelDict.get(args[2],args[2])
    if len(args)<3:
        return fileSpecs,userName,baseModel,''

    baseTopicDict = {
        'standard':'US General English - Standard',
        'bestmatch':'US General English - BestMatch',
        'plus':'US General English - BestMatch Plus',
        'student':'Student General English - BestMatch',
    }
    baseTopic = baseTopicDict.get(args[3],args[3])

    return fileSpecs,userName,baseModel,baseTopic

#---------------------------------------------------------------------------
# run
#
# This is the main entry point.  It will connect to NatSpeak and train
# a new user.  In the case of an error, it will cleanly disconnect from
# NatSpeak and print the exception information,

def run(args):
    fileSpecs,userName,baseModel,baseTopic = parseArgs(args)
    if not fileSpecs:
        return
    try:
        natlink.natConnect()
        doTraining(fileSpecs,userName,baseModel,baseTopic)
        natlink.natDisconnect()
    except TrainingError,message:
        natlink.natDisconnect()
        print ''
        print 'TrainingError:',message
    except:
        natlink.natDisconnect()
        print ''
        traceback.print_exc()

if __name__=='__main__':
    run(sys.argv[1:])
