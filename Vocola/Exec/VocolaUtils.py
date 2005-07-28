# VocolaUtils.py - Classes used by Vocola's generated Python code
#
# This file is copyright (c) 2002-2003 by Rick Mohr. It may be redistributed 
# in any way as long as this copyright notice remains.

import natlink
from types import *

# The Value class represents a sequence of strings and/or function
# calls. Vocola's generated Python code uses this class to build up an
# action sequence to be performed. It also uses this class to build up
# an argument to a function call (which may be constructed from several
# pieces but must resolve to a single string).

NestingError = "Calls to built-in Dragon functions may not be nested"

class Value:
    def __init__(self):
        self.values = []
        self.lastValueType = ''

    # Append to this Value object an integer, a string, a Call object,
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
        elif v.__class__.__name__ == 'Call':
            # combine adjacent calls if possible
            if self.lastValueType == 'Call':
                self.values[-1].addCall(v)
            else:
                self.values.append(v)
            self.lastValueType = 'Call'
        elif v.__class__.__name__ == 'Value':
            for value in v.values: self.augment(value)
        else: print "unexpected argument to augment", type(v)

    def perform(self):
        for value in self.values:
            if type(value) is StringType:
                natlink.playString(value)
            elif value.__class__.__name__ == 'Call':
                value.perform()

    def __str__(self):
        if len(self.values) == 1 and type(self.values[0]) is StringType:
            return self.values[0]
        else: raise NestingError

# The Call class represents a Vocola function call. Vocola's generated
# Python code uses this class to build up a string containing the
# function name and arguments, which is then interpreted. Note that
# calls to built-in Dragon functions get interpreted by Dragon's
# "execScript", while calls to Vocola user-defined functions get
# interpreted by Python's "eval". The "UserCall" subclass below handles
# calls to user-defined functions, implementing the necessary syntax
# differences between these two interpreters.

class Call:
    def __init__(self, functionName):
        self.functionName = functionName
        self.argumentString = ''

    def addArgument(self, value):
        argument = str(value)
        if self.argumentString != '':
            self.argumentString += ','
        # Strings must be quoted (except in certain dragon functions),
        # and numbers must not be quoted
        if not self.isNumber(argument) or self.functionName in ['HeardWord', 'MenuPick']:
            argument = self.prepareArgumentForEvaluation(argument)
        self.argumentString += ' ' + argument

    def prepareArgumentForEvaluation(self, argument):
        return '"' + argument + '"'

    def finalize(self):
        self.script = self.functionName + self.argumentString

    def addCall(self, call):
        self.script += '\n' + call.script

    def perform(self):
        #print '[' + self.script + ']'
        natlink.execScript(self.script)

    def isNumber(self, string):  # private
        try:
            long(string)
            return 1
        except ValueError:
            return 0

class UserCall(Call):
    def getCall(self):
        return self.functionName + '(' + self.argumentString + ')'

    def prepareArgumentForEvaluation(self, argument):
        return 'r"' + argument + '"'

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
        # Convert to number if possible
        try:    self.variables[self.nextName] = long(string)
        except: self.variables[self.nextName] = string

    def evaluate(self, expression):
        string = 'str(' + expression + ')'
        #print 'Evaluating expression:  ' + string
        return eval(string, self.variables)



