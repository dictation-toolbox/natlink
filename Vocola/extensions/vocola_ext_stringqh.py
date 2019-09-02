import os
import nsformat

# QH, two string functions:
# extract part before the first ":" in String.GetName
# extract the latter part, so after the first ":" in String.GetPassword
# also: format _anything

# Vocola function: String.GetName
def getname(name):
    return name.split(":")[0]

# Vocola function: String.GetPassword
def getpassword(name):
    return name.split(":", 1)[1]

# Vocola function: String.NsformatCapitalize
def nsformatcapitalize(name):
    words = name.split()
    formattedOutput, outputState = nsformat.formatWords(words, state=None)  # no space, cap next
    return formattedOutput

# Vocola function: String.Capitalize
def capitalize(name):
    formattedOutput, outputState = nsformat.formatWords(words, state=None)  # no space, cap next
    print "String.Capitalize: %s"% name.capitalize
    return name.capitalize()