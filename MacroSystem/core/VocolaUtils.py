# VocolaUtils.py - Classes used by Vocola's generated Python code
#
# This file is copyright (c) 2002-2009 by Rick Mohr.  It may be redistributed 
# in any way as long as this copyright notice remains.

import natlink
from types import *
import string


class ConversionError(Exception):
    pass

class DragonError(Exception):
    pass



# The UserCall class represents a Vocola user function call.  Vocola's
# generated Python code uses this class to build up a string
# (self.getCall()) containing the function's translated name and the
# function's arguments, which is then interpreted by Python's "eval".

class UserCall:
    def __init__(self, functionName):
        self.functionName = functionName
        self.argumentString = ''

    def addArgument(self, value):
        # for now, coerce arguments to strings:
        argument = str(value)
        if self.argumentString != '':
            self.argumentString += ','
        self.argumentString += ' ' + self.quoteAsPythonString(argument)

    def quoteAsPythonString(self, argument):
        q = string.replace(argument, '\\', '\\\\')
        q = string.replace(q, '"', '\\"')
        q = string.replace(q, '\n', '\\n')
        return '"' + q + '"'

    def getCall(self):
        return self.functionName + '(' + self.argumentString + ')'



# The Value class represents a sequence of strings and/or Dragon 
# calls.  Vocola's generated Python code uses this class to build up an
# action sequence to be performed.  It also uses this class to build up
# an argument to a function call (which may be constructed from several
# pieces).

class Value:
    def __init__(self):
        self.values = []
        self.lastValueType = ''

    # Append to this Value object an integer, a string, a DragonCall object,
    # or another Value object
    def augment(self, v):
        if type(v) is IntType:
            self.augment(str(v))
        elif type(v) is StringType:
            # combine adjacent strings if possible
            if self.lastValueType == 'String':
                self.values[-1] += v
            else:
                self.values.append(v)
            self.lastValueType = 'String'
        elif v.__class__.__name__ == 'DragonCall':
            # combine adjacent Dragon calls if possible
            if self.lastValueType == 'DragonCall':
                self.values[-1].addDragonCall(v)
            else:
                self.values.append(v)
            self.lastValueType = 'DragonCall'
        elif v.__class__.__name__ == 'Value':
            for value in v.values: self.augment(value)
        else: print "unexpected argument to augment", type(v)

    def perform(self):
        for value in self.values:
            if type(value) is StringType:
                natlink.playString(value)
            elif value.__class__.__name__ == 'DragonCall':
                value.perform()

    def as_string(self):
        if len(self.values) == 0:
            return "(no actions)"
        result = ""
        for value in self.values:
            if len(result) > 0:
                result += "; "
            if type(value) is StringType:
                q = string.replace(value, '"', '""')
                result += '"' + q + '"'
            else:
                q = value.as_string()
                result += string.replace(q, "\n", "; ")
        return result
                
    # Attempt to coerce us to a string:
    def __str__(self):
        if len(self.values) == 0:
            return ""
        elif len(self.values) == 1 and type(self.values[0]) is StringType:
            return self.values[0]
        else:
            message = "unable to convert value " + self.as_string() \
                    + " into a string due to the presence of a Dragon call"
            raise ConversionError(message)
                
    # Attempt to coerce us to an integer:
    def __int__(self):
        if len(self.values) == 0:
            raise ConversionError(
                  "unable to convert empty value into an integer")
        elif len(self.values) == 1 and type(self.values[0]) is StringType:
            s = self.values[0]
            try:
                return long(s)
            except ValueError:
                raise ConversionError(
                      "unable to convert value " + self.as_string() \
                      + " into an integer")
        else:
            message = "unable to convert value " + self.as_string() \
                    + " into an integer due to the presence of a Dragon call"
            raise ConversionError(message)



# The DragonCall class represents a (delayed) Vocola Dragon
# call.  Vocola's generated Python code uses this class to build up a
# string containing the function name and arguments, which is then
# interpreted by Dragon's "execScript" when the call is finally
# performed.

class DragonCall:
    def __init__(self, functionName, argumentTypes):
        self.functionName = functionName
        self.argumentTypes = argumentTypes
        self.argumentString = ''
        self.argumentNumber = -1

    def addArgument(self, value):
        self.argumentNumber += 1
        argumentType = self.argumentTypes[self.argumentNumber]

        if argumentType == 'i':
            argument = str(int(value))
        elif argumentType == 's':
            argument = self.quoteAsVisualBasicString(str(value))
        else:
            # there is a vcl2py.pl bug if this happens:
            raise ValueError("Unknown data type specifier '" + argument +
                             "' supplied for a Dragon procedure argument")
        
        if self.argumentString != '':
            self.argumentString += ','
        self.argumentString += ' ' + argument

    def quoteAsVisualBasicString(self, argument):
        q = argument
        q = string.replace(q, '"', '""')
        q = string.replace(q, "\n", '" + chr$(10) + "')
        q = string.replace(q, "\r", '" + chr$(13) + "')
        return '"' + q + '"'

    def finalize(self):
        self.script = self.functionName + self.argumentString

    def as_string(self):
        return self.script
    
    def addDragonCall(self, dragon_call):
        self.script += '\n' + dragon_call.script

    def perform(self):
        #print '[' + self.script + ']'
        try:
            natlink.execScript(self.script)
        except natlink.SyntaxError, details:
            message = "Dragon reported a syntax error when Vocola attempted" \
                    + " to execute the Dragon procedure '" + self.script \
                    + "'; details: " + str(details)
            raise DragonError(message)

 

# The Evaluator class represents a Vocola "Eval" expression.  Vocola's
# generated Python code uses this class to build up a string containing
# a Python expression to be evaluated, and then evaluates it.

class Evaluator:
    def __init__(self):
        self.variables = {}

    def setNextVariableName(self, name):
        self.nextName = name

    def setVariable(self, value):
        string = str(value)
        # Convert to number if has form of a canonical number:
        if self.isCanonicalNumber(string):
            self.variables[self.nextName] = long(string)
        else: self.variables[self.nextName] = string

    def evaluate(self, expression):
        string = 'str(' + expression + ')'
        #print 'Evaluating expression:  ' + string
        return eval(string, self.variables)

    # is string the canonical representation of a long?
    def isCanonicalNumber(self, string):  # private
        try:
            return str(long(string)) == string
        except ValueError:
            return 0



# Massage recognition results to make a single entry for each
# <dgndictation> result.

def combineDictationWords(fullResults):
    i = 0
    inDictation = 0
    while i < len(fullResults):
        if fullResults[i][1] == "dgndictation":
            # This word came from a "recognize anything" rule.
            # Convert to written form if necessary, e.g. "@\at-sign" --> "@"
            word = fullResults[i][0]
            backslashPosition = string.find(word, "\\")
            if backslashPosition > 0:
                word = word[:backslashPosition]
            if inDictation:
                fullResults[i-1] = [fullResults[i-1][0] + " " + word, "dgndictation"]
                del fullResults[i]
            else:
                fullResults[i] = [word, "dgndictation"]
                i = i + 1
            inDictation = 1
        else:
            i = i + 1
            inDictation = 0
    return fullResults
