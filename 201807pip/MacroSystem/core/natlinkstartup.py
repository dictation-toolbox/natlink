from   stat import *    # file statistics
import os               # access to file information
import os.path          # to parse filenames
import re
import shutil
import string
import sys

import natlinkstatus


#
# This function is called by natlinkmain when starting up just before
# loading grammars for the first time:
#
def start():
    print 'start of natlinkstartup'
    updateUnimacroHeaderIfNeeded()
    create_new_language_subdirectory_if_needed()



##
## Update user's copy of Unimacro.vch if a more recent version is
## available
##

def updateUnimacroHeaderIfNeeded():
    status = natlinkstatus.NatlinkStatus()
    if not status.getVocolaTakesUnimacroActions(): 
        return
        
    destDir              = status.getVocolaUserDirectory()
    coreFolder           = os.path.split(__file__)[0]
    sourceDir            = os.path.normpath(os.path.join(coreFolder, "..", "..", "..",
                                        "Unimacro", 'vocola_compatibility'))
    destPath             = os.path.join(destDir,   'Unimacro.vch')
    sourcePath           = os.path.join(sourceDir, 'Unimacro.vch')
    sourceTime, destTime = vocolaGetModTime(sourcePath), \
                           vocolaGetModTime(destPath)

    if not (sourceTime or destTime):
        print >> sys.stderr, """\n
Error: The option "Vocola Takes Unimacro Actions" is switched on, but
no file "Unimacro.vch" is found.

Please fix the configuration of NatLink/Vocola/Unimacro and restart
Dragon.  Either ensure the source file is at:
    "%s",
or switch off the option "Vocola Takes Unimacro Actions".
"""% sourceDir
        return
        
    if destTime < sourceTime:
        try:
            shutil.copyfile(sourcePath, destPath)
        except IOError:
            print >> sys.stderr, """\n
Warning: Could not copy example "Unimacro.vch" to:
    "%s".

There is a valid "Unimacro.vch" available, but a newer file is
available at: "%s".

Please fix the configuration of NatLink/Vocola/Unimacro and restart
Dragon, if you want to use the updated version of this file."""% (destDir, sourceDir)
        else:
            print 'Succesfully copied "Unimacro.vch" from\n\t"%s" to\n\t"%s".'% (sourceDir, destDir)

# Returns the modification time of a file or 0 if the file does not exist:
def vocolaGetModTime(file):
    try: return os.stat(file)[ST_MTIME]
    except OSError: return 0        # file not found

## 
## Quintijn's unofficial multiple language kludge:
## 

def create_new_language_subdirectory_if_needed():
    status        = natlinkstatus.NatlinkStatus()
    VocolaEnabled = not not status.getVocolaUserDirectory()
    language      = status.getLanguage()
    commandFolder = natlinkstatus.NatlinkStatus().getVocolaUserDirectory()
    if not os.path.isdir(commandFolder):                      
        commandFolder = None

    if VocolaEnabled and status.getVocolaTakesLanguages():
        if language != 'enx' and commandFolder:
            uDir  = commandFolder
            uDir2 = os.path.join(uDir, language)
            if not os.path.isdir(uDir2):
                print 'creating Vocola command subfolder for language %s' % language
                os.mkdir(uDir2)
                copyToNewSubDirectory(uDir, uDir2)

def copyToNewSubDirectory(trunk, subdirectory):
    for f in os.listdir(trunk):
        if f.endswith('.vcl'):
            copyVclFileLanguageVersion(os.path.join(trunk, f),
                                       os.path.join(subdirectory, f))

def copyVclFileLanguageVersion(Input, Output):
    """copy to another location, keeping the include files one directory above
    """
    # let include lines to relative paths point to the folder above ..\
    # so you can take the same include file for the alternate language.
    reInclude = re.compile(r'^(\s*include\b\s*[\'\"]?)([^\s;=][^;=\n]*\s*;.*)$')
    Input     = os.path.normpath(Input)
    Output    = os.path.normpath(Output)
    input     = open(Input, 'r').read()
    output    = open(Output, 'w')
    language      = natlinkstatus.NatlinkStatus().getLanguage()
    output.write("# vocola file for alternate language: %s\n"% language)
    lines = map(string.strip, str(input).split('\n'))
    for line in lines:
        m = reInclude.match(line)
        if m:
            line = m.group(1) + "..\\" + m.group(2) 
        output.write(line + '\n')
    output.close()                
