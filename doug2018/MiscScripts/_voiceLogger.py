# Natlink recognition logger.
#     (c) 2005 Daniel J. Rocco
#
# Logs NaturallySpeaking's recognition history to the specified file.
# Format:
#        timestamp        current_user        current_module        window_title        (recognized word list | '*REJECT*')
#
# modeled on Joel Gould's "repeat that" grammar.
#
# $Id$

import natlink, time, string
from natlinkutils import *


logFile = r'C:\dev\DotNetProjects\NatLink\macrosystem\voice.log'

def logMessageToFile (filename, message):
   output = "%s\t%s\n" % (time.strftime ('%m.%d.%Y %H:%M:%S'), message)
   out = open (filename,'a')
   out.write (output)
   out.close()


class LoggerGrammar(GrammarBase):
   gramSpec = """
       <logger> exported = {emptyList};
   """
   def initialize(self):
       self.load(self.gramSpec,allResults=1)
       self.activateAll()
   def gotResultsObject(self,recogType,resObj):
       global logFile
       currentUser=natlink.getCurrentUser()[0]
       if recogType == 'reject':
           message = "*REJECT*"
       else:
           message = resObj.getWords(0)

       currentModule=natlink.getCurrentModule()
       windowTitle =string.replace(currentModule[1],"\t"," ")
       message ="%s\t%s\t%s"% (currentModule[0],windowTitle,message)
       logMessageToFile (logFile, "%s\t%s" % (currentUser, message))

loggerGrammar = LoggerGrammar()
loggerGrammar.initialize()

def unload():
   global loggerGrammar
   if loggerGrammar:
       loggerGrammar.unload()
   loggerGrammar = None
