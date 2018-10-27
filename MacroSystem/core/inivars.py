# -*- coding: latin-1 -*-
from __future__ import unicode_literals
"""contains class IniVars, that does inifiles

"""
import six
import win32api, types
import os, os.path, sys, re, copy, string
import utilsqh
from utilsqh import path, peek_ahead
import locale
locale.setlocale(locale.LC_ALL, '')
import readwritefile  # reading with encoding BOM mark
# from UserDict import UserDict
lineNum = 0
fileName = ''
class IniError(Exception):
    """Return the line number in the reading section, and the filename if there"""
    def __init__(self, value):
        self.value = value
        self.lineNum = lineNum
        self.fileName = fileName

    def __str__(self):
        s = ['Inivars error ']
        if fileName:
            s.append('in file %s, '%fileName)
        if lineNum:
            s.append('on line %s'%lineNum)
        s.append(': ')
        s.append(self.value)
        return u''.join(s)


DEBUG = 0
# doctest at the bottom
#reAllSections = re.compile(r'^\s*[([^]]+)\]\s*$', re.M)
#reAllKeys = re.compile(r'(^[^=\n]+)[=]', re.M)
reValidSection = re.compile(ur'\[\b([- \.\w]+)]\s*$', re.L)
reFindKeyValue = re.compile(ur'\b([- \.\w]+)\s*=(.*)$', re.L)
reValidKey = re.compile(ur'(\w[\w \.\-]*)$', re.L)
reQuotes = re.compile(ur'[\'"]')

reListValueSplit = re.compile(ur'[\n;]', re.M)
reWhiteSpace = re.compile(ur'\s+')

reDoubleQuotes = re.compile(ur'^"([^"]*)"$', re.M)
reSingleQuotes = re.compile(ur"^'([^']*)'$", re.M)

def quoteSpecial(t, extraProtect = None):
    """add quotes to string, to protect starting quotes, spaces

    extraProtect is possibly a string/list/tuple of characters that
    also need to be protected with quotes
    
    >>> quoteSpecial("abc")
    'abc'
    >>> quoteSpecial(" abc  ")
    '" abc  "'
    >>> quoteSpecial("'abc' ")
    '"\\'abc\\' "'
    
    with newlines in text:
    >>> quoteSpecial("'abc'\\n ")
    '"\\'abc\\'\\n "'
    >>> quoteSpecial(' "ab"')
    '\\' "ab"\\''

    but singular quotes inside a string are kept as they were:

    >>> quoteSpecial('a" b "c')    
    'a" b "c'
    
    with both quotes:
    >>> quoteSpecial('a" \\'b "c')    
    'a" \\'b "c'
    
    >>> quoteSpecial("'a\\" 'b \\"c'")    
    '"\\'a&quot; \\'b &quot;c\\'"'

    >>> quoteSpecial('" \\'b "c\\' xyz')    
    '"&quot; \\'b &quot;c\\' xyz"'

    >>> quoteSpecial('ab"')
    'ab"'
    >>> quoteSpecial("ab' '")
    "ab' '"
    >>> quoteSpecial("a' b 'c")    
    "a' b 'c"

    now for the list possibility:
    
    >>> quoteSpecial("a;bc", ";\\n")
    '"a;bc"'
    >>> quoteSpecial(u"ab\xe9\\nc", ";\\n")
    u'"ab\\xe9\\nc"'

    and for the dict possibility:
    
    >>> quoteSpecial("abc,", ",")
    '"abc,"'
    >>> quoteSpecial("a,bc", ",")
    '"a,bc"'
    >>> quoteSpecial("a,bc", "'|;")
    'a,bc'
    
    """
    if t is None:
        return u''
    if t.strip() != t:
        # leading or trailing spaces:
        if t.find('"') >= 0:
            if t.find("'") >= 0:
                t = t.replace('"', '&quot;')
                #raise IniError("string may not contain single AND double quotes: |%s|"% t)
            return "'%s'" % t
        else:
            return '"%s"'% t
    elif t.find('"') == 0:
        if t.find("'") >= 0:
            t = t.replace('"', '&quot;')
            #print 'Inifile warning: text contains single AND double quotes:'
            return '"%s"'% t
        return "'%s'"% t
    elif t.find("'") == 0:
        if t.find('"') >= 0:
             t = t.replace('"', '&quot;')
             #raise IniError("string may start with single quote AND contain double quotes: |%s|"% t)
        return '"%s"'% t
    elif extraProtect:
        for c in extraProtect:
            if t.find(c) >= 0:
                if t.find('"') >= 0:
                    if t.find("'") >= 0:
                        raise IniError("string contains character to protect |%s| AND single and double quotes: |%s|"% (c, t))
                    else:
                        return "'%s'"% t
                else:
                    return '"%s"'% t
    return t

def quoteSpecialDict(t):
    """quote special with additional protection of comma

    """
    return quoteSpecial(t, ',')

def quoteSpecialList(t):
    """quote special with additional protection of semicolon, newline

    """
    return quoteSpecial(t, ';\n')

def stripSpecial(t):
    """strips text string, BUT if quotes or single quotes leaves rest

    new lines are preserved, BUT all lines are stripped    

    >>> stripSpecial('""')
    ''
    >>> stripSpecial('abc')
    'abc'
    >>> stripSpecial(" x ")
    'x'
    >>> stripSpecial("' a\xe9 '")
    ' a\\xe9 '
    >>> stripSpecial(u'" a\xe9  "')
    u' a\\xe9  '

    """
    
    #if t.find('\n') >= 0:
    #    return '\n'.join(map(stripSpecial, t.split('\n')))
    #
    t = t.strip()
    if not t:
        return u''
    elif reDoubleQuotes.match(t):
        r = reDoubleQuotes.match(t)
        inside = r.group(1)
        if inside.find('"') == -1:
            return inside
        else:
            raise IniError, 'invalid double quotes in string: |%s|'% t
    elif reSingleQuotes.match(t):
        r = reSingleQuotes.match(t)
        inside = r.group(1)
        if inside.find("'") == -1:
            return inside
        else:
            raise IniError, 'invalid single quotes in string: |%s|'% t
    elif t.find("'") == 0 or t.find('"') == 0:
        raise IniError, 'starting quote without matching end quote in string: |%s|'% t
    else:
        return t

def getIniList(t, sep=(u";", u"\n")):
    """gets a list from inifile with quotes entries

    inside this function a state is maintained, for keeping track
    of the action to be taken if some character occurs:

    state = 0: start of string, or start after separator
    state = 1: normal string, including spaces
    state = 2: inside a quoted string, that everything go except
    the quote that is maintained in hadQuote
    state = 3: after a quoted string, waits for a separator or
    the end of the string. Raises error if anything else than a
    space his met

    >>> list(getIniList("a; c"))
    [u'a', u'c']
    >>> list(getIniList("a;c"))
    [u'a', u'c']
    >>> list(getIniList("a; c;"))
    [u'a', u'c', u'']
    >>> list(getIniList("'a\\"b'; c"))
    [u'a"b', u'c']
    >>> list(getIniList('"a "; c'))
    [u'a ', u'c']
    >>> list(getIniList("a ; ' c '"))
    [u'a', u' c ']
    >>> list(getIniList("';a '; ' c '"))
    [u';a ', u' c ']
    >>> list(getIniList("'a '\\n' c '"))
    [u'a ', u' c ']

    """
    i =  0
    l = len(t)
    state = 0
    hadQuote = ''
    if type(t) == six.binary_type:
        t = utilsqh.convertToUnicode(t)
##    print '---------------------------length: %s'% l
    for j in range(l):
        c = t[j]
##        print 'do c: |%s|, index: %s'% (c, j)
        if c == "'" or c == '"':
            if state == 0:
                # starting quoted state
                state = 2
                hadQuote = c
                i = j + 1
                continue
            elif state == 1:
                # quoted inside a string, let it pass
                continue
            elif state == 2:
                if c == hadQuote:
                    yield t[i:j]
                    state = 3
                    continue
            elif state == 3:
                raise IniError('invalid character |%s| after quoted string: |%s|'%
                               (c, t))
        elif c in sep:
            if state == 0:
                # yielding empty string
                yield u''
            elif state == 1:
                # end of normal string
                yield t[i:j].strip()
            elif state == 2:
                # ignore separator when in quoted string
                continue
            # reset the state now:
            state = 0
            i = j + 1
            continue

        elif c  == ' ':
            continue
        else:
            if state == 3:
                raise IniError('invalid character |%s| after quoted string: |%s|'%
                               (c, t))
            elif state == 0:
                i = j
                state = 1
                continue

    if state == 0:
        # empty string at end
        yield u''
    elif state == 1:
##        print 'yielding normal last part: |%s|, i: %s,length: %s'% (t[i:],i,l)
        yield t[i:].strip()
    elif state == 2:
        raise IniError('no end of quoted string found: |%s|'% t)


def getIniDict(t):
    """gets a dict from inifile with generator function

    provides this generator with one list item (getDict should call getIniList first)
    each time a tuple pair (key, value) is returned,
    with value being a string or a list of strings, is separated by comma's

    If more keys are provided (separated by comma's),  these result
    in different yield statements    

    >>> list(getIniDict("a"))
    [(u'a', None)]
    >>> list(getIniDict("apricot:value of a"))
    [(u'apricot', u'value of a')]
    >>> list(getIniDict("a: ' '"))
    [(u'a', u' ')]
    >>> list(getIniDict('a: "with, comma"'))
    [(u'a', u'with, comma')]
    >>> list(getIniDict("a: 'with, comma'"))
    [(u'a', u'with, comma')]
    >>> list(getIniDict('a: more, "intricate, with, comma", example'))
    [(u'a', [u'more', u'intricate, with, comma', u'example'])]
    >>> list(getIniDict("a: c, d"))
    [(u'a', [u'c', u'd'])]
    >>> list(getIniDict("a, b: c"))
    [(u'a', u'c'), (u'b', u'c')]
    >>> list(getIniDict("a,b : c, d"))
    [(u'a', [u'c', u'd']), (u'b', [u'c', u'd'])]
    """
    if type(t) == six.binary_type:
        t = utilsqh.convertToUnicode(t)
    if t.find('\n') >= 0:
        raise IniError('getIniDict must be called through getIniList, so newline chars are not possible: |%s|'%
                       t)
    if t.find(u':') >= 0:
        Keys, Values = [item.strip() for item in t.split(':', 1)]
    else:
        Keys = t.strip()
        Values = u''

    if not Values:
        Values = None
    else:
        Values = list(getIniList(Values, u","))
        if len(Values) == 1:
            Values = Values[0]

    if not Keys:
        return

    if Keys.find(u',') > 0:
        Keys = [k.strip() for k in Keys.split(u',')]
        for k in Keys:
            if not reValidKey.match(k):
                raise IniError('invalid character in key |%s| of dictionary entry: |%s|'%
                               (k, t))
            yield k, Values
    else:
        if not reValidKey.match(Keys):
            raise IniError('invalid character in key |%s| of dictionary entry: |%s|'%
                           (Keys, t))
        yield Keys, Values
        
            
        
def lensort(a, b):
    """sorts two strings, longest first, if length is equal, normal sort

    >>> lensort('a', 'b')
    -1
    >>> lensort('aaa', 'a')
    -1
    >>> lensort('zzz', 'zzzzz')
    1

    """    
    la = len(a)
    lb = len(b)
    if la == lb:
        return cmp(a, b)
    else:
        return -cmp(la, lb)

class IniSection(dict):
    """represents a section of an inivars instance"""

    def __init__(self, parent):
        """init with ignore case if given in inivars

        """
        self._parent = parent
        self._SKIgnorecase = parent._SKIgnorecase

    def __getitem__(self, key):
        '''double underscore means internal value'''
        if type(key) == six.text_type and key.startswith == '__':
            return self.__dict__[key]
        else:
            key = key.strip()
            if reWhiteSpace.search(key):
                key = reWhiteSpace.sub(' ', key)
            if self._SKIgnorecase:
                key = key.lower()
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return ""

    def __setitem__(self, key, value):
        key = key.strip()
        if reWhiteSpace.search(key):
            key = reWhiteSpace.sub(' ', key)
        if not key:
            raise IniError, '__setitem__, invalid key |%s|(false), with value |%s| in inifile: %s'% \
                  (key, value, self._parent._file)
        
        if type(key) == six.text_type and key.startswith == '__':
            self.__dict__[key] = value
        else:
            if self._SKIgnorecase:
                key = key.lower()
            dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        key = key.strip()
        if reWhiteSpace.search(key):
            key = reWhiteSpace.sub(' ', key)
        if not key:
            raise IniError, '__delitem__, invalid key |%s|(false),  inifile: %s'% \
                  (key, self._parent._file)
        
        if type(key) == six.text_type and key.startswith == '__':
            del self.__dict__[key]
        else:
            if self._SKIgnorecase:
                key = key.lower()
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass

class IniVars(dict):
    """do inivars from an .ini file, or possibly (extending this class)
    with other file types.

    File doesn't have to exist before.

    version 7:  quoting is allowed when spaces or special characters
                " or ' or ; in lists or  ; or , in dicts are found.

    version 6: change format of getDict:
               if key has value it is followed by a colon, more keys can
               be defined in one stroke

    version 6:
        options at start: sectionsLC = 1: convert all section names to lowercase (default 0)
                          keysLC = 0: convert all keys to lowercase (default 0)
        gettting of keys, with optional parameters
        

    version 5:
    In this version also a getDict, getList (was already), getInt
    getFloat and getTuple are defined.  When setting a dict, list, etc.
    inside the instance this type is conserved, when writing back
    into the inifile the appropriate formatting is done.

    version 4:    
    In this version 4 empty sections and keys are accepted, and set as
    [empty section] or

    [section]
    empty key =

    If the set command contains lists, elements are cycled through,
    If the sets command contains empty values these empty values are set like
    the example above.

    When an empty section or key is asked for [] or '' is returned.  You can see
    no difference if a section doesn't exist or is empty, as long has no default values
    are provided in the get function.

    When you get a value from a key through a list of sections, as soon as the key
    has been found (also when value is empty), this value is returned.

    second version:
    getList and setList are included

    third version, new methods:
    getSectionPostfixesWithPrefix:
                    sets a private dict _sectionPostfixesWP, see below
    getFromSectionsWithPrefix(prefix, text, key)
                    text is a string (eg a window title) in which the postfix
                    of the section name is found.
    getSectionsWithPrefix(prefix, longerText)
                    gets a list of section names, that contain prefix and postfix
                    matches a part of the longerText


    get is extended with a list of sections:
                    get(['a', 'b'], 'key'): the list of sections searched,
                    until a nonempty value is found.
                    get(['a', 'b']): returns all the keys in their respective sections,
                    without making duplicates

    getKeysOrderedFromSections gives a dictionary with the keys
                    of several sections ordered

    formatKeysOrderedFromSections gives a long string of the keys
                    of several sections ordered


    getMatchingSection gives from a section list the name of thefirst section
                    that contains the key. Returns "section not found" if not found.
                    
                
                    

>>> import os
>>> try: os.remove('empty.ini')
... except: pass
>>> ini = IniVars('empty.ini')
>>> ini.write()
>>> os.path.isfile('empty.ini')
1
>>> try: os.remove('simple.ini')
... except: pass
>>> ini = IniVars('simple.ini')
>>> ini.set('s', 'k', 'v')
>>> ini.set('s','k2','v2')
>>> ini.write()
>>> ini2 = IniVars('simple.ini')
>>> ini2.get()
[u's']
>>> ini2.get('s')
[u'k2', u'k']
>>> ini2.get('s', 'k')
u'v'
>>> ini == ini2
1
>>> ini.getFilename()
u'simple.ini'
>>> ini2 = IniVars('simple.ini', returnStrings=True)
>>> ini2.get('s', 'k')
'v'
>>> ini2.get('s')
['k2', 'k']
    """
    _SKIgnorecase = None
    
    def __init__(self, File, **kw):
        """init from valid files, raise error if invalid file

        """
        # add str function in case file is a path instance:
        file = utilsqh.convertToUnicode(File)
        self._name = os.path.basename(file)
        self._file = file
        self._ext = self.getExtension(file)
        self._changed = 0
        self._maxLength = 60
        self._SKIgnorecase = kw.get('SKIgnorecase', None)
        self._repairErrors = kw.get('repairErrors', None)
        self._codingscheme = None
        self._bom = None
        self._rawtext = ""
        self._returnStrings = False
        if kw and 'returnStrings' in kw:
            self._returnStrings = kw['returnStrings']
        #if self._repairErrors:
        #    print 'try to ignore errors in inifile: %s'% self._file
        
        
        if not self._ext:
            raise IniError, 'file has no extension: %s'% self._file

        # start with new file:
        if not os.path.isfile(file):
            return
        else:
            try:
                execstring = 'self._read%s(file)'% self._ext
                exec(execstring)
            except AttributeError:
                raise IniError, 'file has invalid extension: %s'% self._file
        if DEBUG: print 'read from INI:', self

    def __nonzero__(self):
        """always true!"""
        return True

    def getFilename(self):
        return self._file
    def getName(self):
        return self._name

    def __getitem__(self, key):
        if type(key) == six.text_type and key.startswith == '__':
            return self.__dict__[key]
        else:
            key = key.strip()
            if reWhiteSpace.search(key):
                key = reWhiteSpace.sub(' ', key)
            if self._SKIgnorecase:
                key = key.lower()
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return ""

    def __setitem__(self, key, value):
        key = key.strip()
        if reWhiteSpace.search(key):
            key = reWhiteSpace.sub(' ', key)
        if not key:
            raise IniError, '__setitem__, invalid key |%s|(false), with value |%s| in inifile: %s'% \
                  (key, value, self._file)
        
        if type(key) == six.text_type and key.startswith == '__':
            self.__dict__[key] = value
        else:
            if self._SKIgnorecase:
                key = key.lower()
            dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        key = key.strip()
        if reWhiteSpace.search(key):
            key = reWhiteSpace.sub(' ', key)
        if not key:
            raise IniError, '__delitem__, invalid key |%s|(false), with value |%s| in inifile: %s'% \
                  (key, value, self._file)
        
        if type(key) == six.text_type and key.startswith == '__':
            del self.__dict__[key]
        else:
            if self._SKIgnorecase:
                key = key.lower()
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass
            
##    def _readPy(self, file):
##
##        # prepare file for importing:
##        d, f = os.path.split(file)
##        if not d in sys.path:
##            sys.path.append(d)
##        r, t = os.path.splitext(f)
##        mod = __import__(r)
##        d = {}o
##        for k,v in mod.__dict__.items():
##            if k[0:2] != '__' and type(v) == types.DictType:
##                d[k] = v
##        if DEBUG:  'read from py:', d
##        return d
    def returnStringOrUnicode(self, returnValue):
        """if option returnStrings is set to True, only return strings
        
        This function affects only Strings (binary or text)
        other types are passed unchanged.
>>> try: os.remove('returnunicode.ini')
... except: pass
>>> ini = IniVars("returnunicode.ini")
>>> ini.set("section","string","value")
>>> ini.get("section")
[u'string']
>>> ini.get("section", 'string')
u'value'
>>> ini.set("section","number", 12)
>>> ini.get("section", 'number')
12
>>> ini.set("section","none", None)
>>> ini.get("section", 'none')
>>> ini.get("section")
[u'none', u'string', u'number']
>>> ini.get()
[u'section']


 ## now returnString=True
>>> try: os.remove('returnbinary.ini')
... except: pass
>>> ini = IniVars("returnbinary.ini", returnStrings=True)
>>> ini.set("section","string","value")
>>> ini.get("section")
['string']
>>> ini.get("section", 'string')
'value'
>>> ini.set("section","number", 12)
>>> ini.get("section", 'number')
12
>>> ini.set("section","stringnone", None)
>>> ini.get("section", 'stringnone')
>>> ini.get("section")
['stringnone', 'string', 'number']
>>> ini.get()
['section']
        """
        if type(returnValue) in (six.binary_type, six.text_type):
            if self._returnStrings and type(returnValue) == six.text_type:
                return utilsqh.convertToBinary(returnValue)
            elif (not self._returnStrings) and type(returnValue) == six.binary_type:
                return utilsqh.convertToUnicode(returnValue)
            else:
                return returnValue
        else:
            return returnValue
                                          
        
    def _readIni(self, file):
        global lineNum, fileName
        lineNum = 0
        fileName = file
        section = None
        sectionName = ''
        key = None
        keyName = ''
        sectionNameLines = {}
        self._codingscheme, self._bom, self._rawtext = readwritefile.readAnything(file)
        # if self._bom:
        #     print "file heeft een bommark: %s"% repr(self._bom)
        if self._codingscheme is None:
            raise IniError("Could not find correct encoding for this file: %s"% file)
        rawList = self._rawtext.split('\n')
        for line in rawList:
            line = line.rstrip()
            
            lineNum += 1
            m = reValidSection.match(line)
            if self._repairErrors and not m:
                # with repairErrors option, characters in front of a valid section:
                n = reValidSection.search(line)
                if n and not m:
                    print 'ignore data in front of section: "%s"\n\t(please correct later in file "%s", line %s)'% (line,
                                                                fileName, lineNum)                                                 
                    m = n
                elif not sectionName:
                    if not line:
                        continue
                    print 'no valid section found yet, skip line: "%s"\n\t(please correct later in file "%s", line %s)'% (line,
                                                                fileName, lineNum)                                                 
                    continue
            if m:
                sectionName = m.group(1).strip()
                if sectionName in self:
                    if self._repairErrors:
                        print 'Warning: duplicate section "%s" on line %s and on line %s, take latter one\n\t(please correct later in file "%s")'% (
                            sectionName, sectionNameLines[sectionName], lineNum, fileName)
                        del self[sectionName]
                    else:
                        raise IniError('Duplicate section "%s" on line %s and on line %s\n\t(please correct in file "%s")'% (
                            sectionName, sectionNameLines[sectionName], lineNum, fileName))
                self[sectionName] = IniSection(parent = self)
                section = self[sectionName]
                key = None
                sectionNameLines[sectionName] = lineNum
                continue
            m = reFindKeyValue.match(line)
            if m:
                keyName = m.group(1).strip()
                if section is None:
                    raise IniError('no section defined yet')
                if keyName in section:
                    if self._repairErrors:
                        print 'Warning: duplicate keyname "%s" in section %s on line %s, take latter one\n\t(please correct later in file "%s")'% (
                             keyName, sectionName, lineNum, fileName)
                        del section[keyName]
                    else:
                        raise IniError('Duplicate keyname "%s" in section %s on line %s\n\t(please correct in file "%s")'% (
                            keyName, sectionName, lineNum, fileName))
                    
                section[keyName] = [m.group(2)] 
                key = section[keyName]
                continue
            
            if key:
                # append to list of lines of key: stripping spaces etc.
                key.append(line.strip())
            elif line.strip():
                if section is None:
                    raise IniError('no key or section found yet')
                elif key is None:
                    if self._repairErrors:
                        print 'Warning: no key found in section "%s" on line %s, ignore\n\t(please correct later in file "%s")'% (
                             sectionName, lineNum, fileName)
                        continue
                    else:
                        raise IniError('No key found in section "%s" on line %s\n\t(please correct in file "%s")'% (
                            sectionName, lineNum, fileName))

        
        for s in self:
            section = self[s]
            for k in section:
                section[k] = listToString(section[k])

    def writeIfChanged(self, file=None):
        if self._changed:
            self.write(file=file)
            self._changed = 0
            
    def write(self, file=None):
        if not file:
            file = self._file
            ext = self._ext
        else:
            ext = self.getExtension(file)
        if ext == 'Ini':
            self._writeIni(file)
        else:
            raise IniError, 'invalid extension for writing to file: %s'% file

    def _writeIni(self, file):
        """writes to file of type ini"""
        L = []
        sections = self.get()
        sections.sort()
        hasTrailingNewline = 1   # no newline for section
        for s in sections:
            if s == 'cache next date':
                pass
            hadTrailingNewline = hasTrailingNewline
            hasTrailingNewline = 0
            if  not hadTrailingNewline:
                L.append('')    # prevent extra newlines at top or after multiline key
            L.append('[%s]'% s)
            keys = self.get(s)
            #  key char has '-', for sitegen:
            keyhashyphen = 0
            for k in keys:
                if k == 'next check date':
                    pass
                if k.find('-') > 0:
                    keyhashyphen = 1
                    break
            if keyhashyphen:
               # special case for sitegen:
                keys = sortHyphenKeys(keys)
            else:
                keys.sort()

            for k in keys:
                hadTrailingNewline = hasTrailingNewline
                hasTrailingNewline = 0
                v = self[s][k]
                if type(v) == types.IntType:
                    L.append(u'%s = %s' % (k, v))
                elif type(v) == types.FloatType:
                    L.append(u'%s = %s' % (k, v))
                elif type(v) == types.BooleanType:
                    L.append(u'%s = %s' % (k, str(v)))
                elif not v:
                    # print 'k: %s(%s)'% (k, type(k))
                    try:
                        L.append(u'%s =' % k)
                    except UnicodeDecodeError:
                        k = utilsqh.convertToUnicode(k)
                        L.append(u'%s =' % k)
                        
                elif type(v) == types.ListType or type(v) == types.TupleType:
                    valueList = map(quoteSpecialList, v)
                    startString = u'%s = '% k
                    length = len(startString)
                    listToWrite = []
                    for v in valueList:
                        if listToWrite and length + len(v) + 2 > self._maxLength:
                            L.append(u'%s%s' % (startString, '; '.join(listToWrite)))
                            listToWrite = [v]
                            startString = ' '*len(startString)
                            length = len(startString) + len(v)
                        else:
                            listToWrite.append(v)
                            length += len(v) + 2
                    if length > 72:
                        hasTrailingNewline = 1
                    L.append(u'%s%s' % (startString, '; '.join(listToWrite)))
                    L.append('')
                elif type(v) == types.DictType:
                    inverse = {}
                    for K, V in v.items():
                        if type(V) == six.binary_type:
                            V = utilsqh.convertToUnicode(V)
                            vv = quoteSpecialDict(V)                            
                        elif type(V) == six.text_type:
                            vv = quoteSpecialDict(V)                            
                        elif type(V) == types.ListType or type(V) == types.TupleType:
                            vv = ', '.join(map(quoteSpecialDict, V))
                        elif V is None:
                            vv = None
                        if vv in inverse:
                            inverse[vv].append(K)
                        else:
                            inverse[vv] = [K]
                    startString = u'%s = '% k
                    length = len(startString)
                    if not inverse:
                        L.append(u'%s' % startString)
                    else:
                        if None in inverse:
                            L.append(u'%s%s' % (startString, ', '.join(inverse[None])))
                            del inverse[None]
                            startString = ' '*len(startString)
                        if inverse:
                            for K, V in inverse.items():
##                                print 'writing back value: |%s|, startString: |%s|, keys: |%s|'% \
##                                      (K, startString, V)
                                L.append(u'%s%s: %s' % (startString, ', '.join(V), K))
                                startString = ' '*len(startString)
                    hasTrailingNewline = 1
                    L.append('')
                else:
                    if type(v) == six.binary_type:
                        v = utilsqh.convertToUnicode(v)
                    if type(v) != six.text_type:
                        v = unicode(v)
                    v = v.strip()
                    if v.find('\n') >= 0:
                        hasTrailingNewline = 1
                        V = v.split('\n')
                        if not hadTrailingNewline:
                            L.append('')    # 1 extra newline
                        L.append(u'%s =' % k)
                        spacing = ' '*4
                        for li in V:
                            if li:
                                L.append(u'%s%s' % (spacing, li))
                            else:
                                L.append('')
                        L.append('')
                    elif len(k) + len(v) > 72:
                        if not hasTrailingNewline:
                            L.append('')
                        L.append(u'%s = %s' % (k, v))
                        L.append('')
                        hasTrailingNewline = 1
                    else:
                        L.append('%s = %s' % (k, v))

            if not hadTrailingNewline:
                L.append('')
##        if path(self._file).isfile():
##            old = open(self._file).read()
##        else:
##            old = ""
        new = u'\n'.join(L)
##        if old == new:

##            pass
####            print 'no changes'
##        else:
####            self.saveOldInifile()
        readwritefile.writeAnything(file, self._codingscheme, self._bom, new)
        pass

    def saveOldInifile(self):
        """make copy -1, ..., -9 for previous versions"""
        orgfile = self._file
        for i in range(1,10):
            newfile = path('%s-%s'% (orgfile, i))
            if not newfile.isfile():
                break
        else:
            newfile.delete()
        for j in range(i,0, -1):
            pass
            

    def get(self, s=None, k=None, value=u"", stripping=stripSpecial):
        """get sections, keys or values, uin version 3 extended
        with s also being a list, examples of this far below.

        with version 6, strips more smart, see function stripSpecial below
        when setting a string, this smart quoting must also be performed.

        >>> import os
        >>> try: os.remove('get.ini')
        ... except: pass
        >>> ini = IniVars("get.ini")
        >>> ini.get()
        []
        >>> ini.get("s")
        []
        >>> ini.get()
        []
        >>> ini.get("s", "k")
        u''
        >>> ini.get("s", "k", "v")
        u'v'

        spaces in section or key name are stripped and made single:
        
        >>> ini.set(" s  t ", "a  k ", 'strange')
        >>> ini.get("s t", 'a k')
        u'strange'
        >>> ini.get("s  t ", 'a      k ')
        u'strange'
        
        >>> 
        """
        if type(s) == types.ListType or type(s) == types.TupleType:
            if k:
                if k == 'next check date':
                    pass
                if type(k) == six.binary_type:
                    k = utilsqh.convertToUnicode(k)
                k = k.strip()
                if reWhiteSpace.search(k):
                    k = reWhiteSpace.sub(' ', k)
                # look for the section with this key
                for S in s:

                    v = self.get(S, k, None, stripping=stripping)
                    if v != None:
                        return self.returnStringOrUnicode(v)
                else:
                    # key not found, return default value
                    return self.returnStringOrUnicode(value)
            else:
                # get list of all keys with these sections:
                L = []
                for S in s:
                    l = self.get(S)
                    for k in l:
                        if self._returnStrings:
                            k = utilsqh.convertToBinary(k)
                        if k not in L:
                            L.append(k)
                return L
            # not found, return default:
            if k:
                return self.returnStringOrUnicode(value)
            else:
                # asking for list of possible keys:
                return L
        if s:
            if type(s) == six.binary_type:
                s = utilsqh.convertToUnicode(s)
            s = s.strip()
            if reWhiteSpace.search(s):
                s = reWhiteSpace.sub(' ', s)

            if self.hasSection(s):
                # s exists, process key requests
                if k:
                    if type(k) == six.binary_type:
                        k = utilsqh.convertToUnicode(k)
                    k = k.strip()
                    if reWhiteSpace.search(k):
                        k = reWhiteSpace.sub(' ', k)

                    # request value from s,k
                    if self.hasKey(s, k):
                        # k exists, return value
                        v = self[s][k]
                        if type(v) == six.binary_type:
                            v = utilsqh.convertToUnicode(v)
                        if stripping and type(v) == six.text_type:
                            return self.returnStringOrUnicode(stripping(v))
                        else:
                            return self.returnStringOrUnicode(v)
                    else:
                        # no key, return default value
                        if type(value) == six.binary_type:
                            value = utilsqh.convertToUnicode(value)
                        return self.returnStringOrUnicode(value)
                else:
                    # no key given, request a list of keys
                    KeysList = self[s].keys()
                    return [self.returnStringOrUnicode(kk) for kk in KeysList]
            elif k:
                # s doesn't exist, return default value
                if type(value) == six.binary_type:
                    value = utilsqh.convertToUnicode(value)
                return self.returnStringOrUnicode(value)
            else:
                # s doesn't exist, return empty list of keys
                return []
        else:
            # no section, request section list
            Keys = self.keys()
            return [self.returnStringOrUnicode(kk) for kk in Keys]

    def set(self, s, k=None, v=None):
        """set section, key to value


        section can be a list, as can be the key.  If the value
        is not given, empty sections or keys are made.
        >>> try: os.remove('set.ini')
        ... except: pass
        >>> ini = IniVars("set.ini")
        >>> ini.set("section","key","value")
        >>> ini.get("section")
        [u'key']
        >>> ini.get("section","key")
        u'value'
        >>> ini.set('empty section')
        >>> ini.get()
        [u'section', u'empty section']
        >>> ini.set(['empty 1', 'empty 2'])
        >>> ini.get('empty 1')
        []
        >>> ini.set(['not empty 1'], ['empty key 1', 'empty key 2'])
        >>> ini.get('not empty 1', 'empty key 1')
        >>> ini.set(['not empty 1'], ['key 1', 'key 2'], ' value ')
        >>> ini.get('not empty 1', 'key 1')
        u' value '
        >>> ini.set('quotes', 'double', '" a "')
        >>> ini.get('quotes', 'double')
        u'" a "'
        >>> ini.set('quotes', 'single', "'  a  '")
        >>> ini.get('quotes', 'single')
        u"'  a  '"
        >>> ini.close()
        >>> ini = IniVars("set.ini")
        >>> L = ini.get()
        >>> L.sort()
        >>> L
        [u'empty 1', u'empty 2', u'empty section', u'not empty 1', u'quotes', u'section']
        >>> ini.get('not empty 1', 'key 1')
        u' value '
        >>> ini.get('not empty 1', 'empty key 1')
        u''
        >>> ini.get('empty 1')
        []
        >>> ini.get('quotes', 'single')
        u"'  a  '"
        >>> ini.get('quotes', 'double')
        u'" a "'
        """
        # self._changed = 1
        if type(s) == types.ListType or type(k) == types.TupleType:
            for S in s:
                self.set(S, k, v)
            return
        # now s in string:
        if type(s) != six.text_type:
            s = utilsqh.convertToUnicode(s)
        assert type(s) == six.text_type

        # now make new section if not existing before:
        s = s.strip()
        if reWhiteSpace.search(s):
            s = reWhiteSpace.sub(u' ', s).strip()

        if not reValidSection.match(u'['+s+']'):
            raise IniError("Invalid section name to set to: %s"% s)

        if not self.hasSection(s):
            self[s] = IniSection(parent = self)

        # no key: empty section:
        if k == None:
            if v != None:
                raise IniError('setting empty section with nonempty value: %s'% v)
            return
            
        if type(k) in (types.ListType, types.TupleType):
            for K in k:
                self.set(s, K, v)
            return

        if type(k) != six.text_type:
            k = utilsqh.convertToUnicode(k)
        if type(k) != six.text_type:
            raise IniError('key must be list, tuple or string, not: %s'% k)
            
        # finally set s, k, to v
        if k == 'next check date':
            pass

        k = k.strip()
        if reWhiteSpace.search(k):
            k = reWhiteSpace.sub(u' ', k)
        if reQuotes.search(k):
            k = reQuotes.sub('', k)
        if not reValidKey.match(k):
            raise IniError('key contains invalid character(s): |%s|'% repr(k))
        
        if type(v) == six.binary_type:
            v = utilsqh.convertToUnicode(v)
        # print "s: %s(%s), k: %s(%s), v: %s(%s)"% (s, type(s), k, type(k), v, type(v))
        if type(v) == six.text_type:
            v = quoteSpecial(v)
        prevV = None
        try:
            prevV = self[s][k]
        except KeyError:
            pass
        if v != prevV:
            self._changed = 1    
            self[s][k] = v

    def delete(self, s=None, k=None):
        """delete sections, keys or all

        >>> import os
        >>> try: os.remove('delete.ini')
        ... except: pass
        >>> ini = IniVars("delete.ini")
        >>> ini.set("section","key","value")
        >>> ini.get("section","key")
        u'value'
        >>> ini.delete("section","key")
        >>> ini.get("section","key")
        u''
        >>> ini.get("section")
        []
        >>> ini.set("section","key","value")
        >>> ini.get("section","key")
        u'value'
        >>> ini.delete()
        >>> ini.get("section")
        []
        >>> ini.get("section", "key")
        u''
        >>> ini.close()
        >>>
        """
        if s: s = s.strip()
        if s and reWhiteSpace.search(s):
            s = reWhiteSpace.sub(' ', s)

        if s:
            if self.hasSection(s):
                # s exists
                if k: k = k.strip()
                if k:
                    if reWhiteSpace.search(k):
                        k = reWhiteSpace.sub(' ', k)

                    # delete given key
                    if self.hasKey(s, k):
                        # k exists, delete it
                        self._changed = 1
                        del self[s][k]
                    if not self[s]:
                        self._changed = 1
                        del self[s]
                else:
                    # no key given, delete whole section
                    self._changed = 1
                    del self[s]
        else:
            # no section, delete all sections and keys
            if self.toDict():
                self._changed = 1
                self.clear()

    def hasSection(self, s):
        if reWhiteSpace.search(s):
            s = reWhiteSpace.sub(' ', s).strip()
        if self._SKIgnorecase:
            s = s.lower()
        return s in self

    def hasKey(self, s, k):
        k = k.strip()
        if reWhiteSpace.search(k):
            k = reWhiteSpace.sub(' ', k)
        s = s.strip()
        if reWhiteSpace.search(s):
            s = reWhiteSpace.sub(' ', s)
        if self._SKIgnorecase:
            s = s.lower()
            k = k.lower()

        return self.hasSection(s) and k in self[s]

    def hasValue(self, s, k, value):
        k = k.strip()
        if reWhiteSpace.search(k):
            k = reWhiteSpace.sub(' ', k)
        s = s.strip()
        if reWhiteSpace.search(s):
            s = reWhiteSpace.sub(' ', s)
        if self._SKIgnorecase:
            s = s.lower()
            k = k.lower()
            
        return hasKey(s, k) and self[s][k]

    def close(self):
        """close the instance, write data back if changes were made

        """
        if self._changed:
            self.write()

    def getExtension(self, file):
        """capitalize text part of extension,
        .ini -> Ini
        .py -> Py 
        empty string -> ''
        """
        if file:
            extension = os.path.splitext(os.path.split(file)[1])[1]
            extension = extension[1:].capitalize()
            return extension
        else:
            return u''
    
##    def __call__(self, file):
##        """calling this class constructs a new instance,
##        with file as parameter
##        
##        result: instance
##        """
##        return IniVars(file)

    def getTuple(self, section, key):
        return tuple(self.getList(section, key))

    def getList(self, section, key, default=None):
        """get a value and convert into a list
        see example above and:
        
        >>> import os
        >>> try: os.remove('getlist.ini')
        ... except: pass
        >>> ini = IniVars('getlist.ini')
        >>> ini.set('s', 'empty')
        >>> ini.getList('s', 'empty')
        []
        >>> ini.set('s', 'one', 'value')
        >>> ini.getList('s', 'one')
        [u'value']
        >>> ini.set('s', 'two', 'value; value')
        >>> ini.getList('s', 'two')
        [u'value', u'value']
        >>> ini.set('s', 'three', 'value 1\\nvalue 2\\nvalue 3 and more')
        >>> ini.getList('s', 'three')
        [u'value 1', u'value 2', u'value 3 and more']
        >>> 
        """
        if not self:
            return []
        try:
            value = self[section][key]
        except (KeyError, TypeError):
            if default == None:
                return []
            elif type(default) == types.ListType:
                return copy.copy(default)
            else:
                raise IniError('invalid type for default of getList: |%s|%`default`')
        if not value:
            return []
        if type(value) == types.ListType:
            return copy.copy(value)
        else:
            L = list(getIniList(value))
        return L

    def getDict(self, section, key, default=None):
        """get a value and convert into a dict

        first the value is split it into items like in the getList function,
        after that each item is examined:
        1. only one word: this is the key, value = None
        2. more words, look for the ":", before the ":" more keys can be defined
           at once, after the ":" is the value, two possibilities:
            a. no comma inside: value is a string
            b. comma is inside: value is a list, splitted by the comma

        >>> import os
        >>> try: os.remove('getdict.ini')
        ... except: pass
        >>> ini = IniVars('getdict.ini')
        >>> ini.set('s', 'empty')
        >>> ini.getDict('s', 'empty')
        {}
        
        default if base empty
        >>> ini.getDict('s', 'empty', {'s': None})
        {'s': None}

        setting and getting a dict:

        >>> d = {'a': 'b'}
        >>> e = {'empty': None}
        >>> ini.set('s', 'dict', d)
        >>> ini.set('s', 'empty value', e)
        >>> ini.getDict('s', 'dict')
        {'a': 'b'}
        >>> ini.getDict('s', 'empty value')
        {'empty': None}
        >>> ini.close()
        >>> ini = IniVars("getdict.ini")
        >>> ini.get('s', 'empty value')
        u'empty'
        >>> ini.get('s', 'dict')
        u'a: b'
        >>> ini.getDict('s', 'empty value')
        {u'empty': None}
        >>> ini.getDict('s', 'dict')
        {u'a': u'b'}
        
        setting and getting through direct string values:
        
        >>> ini.set('s', 'one', 'value')
        >>> ini.getDict('s', 'one')
        {u'value': None}
        >>> ini.set('s', 'two', 'key: value 1\\n key2 : value 2')
        >>> ini.getDict('s', 'two')
        {u'key2': u'value 2', u'key': u'value 1'}
        >>> ini.set('s', 'three', 'keyempty\\nkey1: value 1\\nkey2, key3: value1, value2')
        >>> ini.getDict('s', 'three')
        {u'key3': [u'value1', u'value2'], u'key2': [u'value1', u'value2'], u'key1': u'value 1', u'keyempty': None}

        also the value of the value can be a list:
        
        >>> ini.set('s', 'list', 'key: a, b, c')
        >>> ini.getDict('s', 'list')
        {u'key': [u'a', u'b', u'c']}
        >>> ini.close()
        
        """
        try:
            value = self[section][key]
        except (TypeError, KeyError):
            if default == None:
                return {}
            elif type(default) == types.DictType:
                return copy.copy(default)
            else:
                raise IniError('invalid type for default of getDict: |%s|%`default`')
        if not value:
            if default == None:
                return {}
            elif type(default) == types.DictType:
                return copy.copy(default)
            else:
                raise IniError('invalid type for default of getDict: |%s|%`default`')            
            
        elif type(value) == types.DictType:
            return copy.deepcopy(value)
        
        D = {}
        for listvalue in getIniList(value):
            for k, v in getIniDict(listvalue):
                if k in D:
                    raise IniError('duplicate key |%s| in getDict: %s'%
                                   (k, value))
                D[k] = v
            
        return D
            
    def getInt(self, section, key, default=0):
        """get a value and convert into a int


        >>> import os
        >>> try: os.remove('getint.ini')
        ... except: pass
        >>> ini = IniVars('getint.ini')
        >>> ini.set('s', 'three', 3)
        >>> ini.getInt('s', 'three')
        3
        >>> ini.getInt('s', 'unknown')
        0
        
        """
        try:
            i = self[section][key]
        except (KeyError, TypeError):
            return default

        if type(i) == types.IntType:
            return i
        if type(i) == six.binary_type:
            i = utilsqh.convertToUnicode(i)
        if type(i) == six.text_type:
            if i:
                try:
                    return int(i)
                except ValueError:
                    raise IniError('ini method getInt, value not a valid integer: %s (section: %s, key: %s)'%
                                   (section, key, i))
            else:
                return 0
        raise IniError('invalid type for getInt (probably intermediate set without write: %s)(section: %s, key: %s'%
                       (`i`, section, key))

    def getBool(self, section, key, default=False):
        """get a value and convert into boolean

t, T, true, True, Waar, waar, w, W, 1 -->> True
empty, o, f, F, False, false, Onwaar, o, none -->> False
        
        """
        try:
            i = self[section][key]
        except (KeyError, TypeError):
            return default
        if not i:
            return False
        
        if i.lower()[0] in ['t', 'w', '1']:
            return True
        if i.lower()[0] in ['f', 'o', '0']:
            return False
        raise IniError('inivars, getBool, unexpected value: "%s" (section: %s, key: %s)'%
                         (i, section, key))

    def getFloat(self, section, key, default=0.0):
        """get a value and convert into a float


        >>> import os
        >>> try: os.remove('getfloat.ini')
        ... except: pass
        >>> ini = IniVars('getfloat.ini')
        >>> ini.set('s', 'three', '3')
        >>> ini.getFloat('s', 'three')
        3.0
        >>> ini.getFloat('s', 'unknown')
        0.0
        
        """
        try:
            i = self[section][key]
        except KeyError:
            return default
        if type(i) == types.FloatType:
            return 
        if type(i) == six.binary_type:
            i = utilsqh.convertToUnicode(i)
        if type(i) == six.text_type:
            if i:
                try:
                    return float(i)
                except ValueError:
                    if ',' in i:
                        j = i.replace(',', '.')
                        try:
                            return float(j)
                        except ValueError:
                            raise IniError('ini method getFloat, value not a valid floating number (comma replaced to dot): %s (section: %s, key: %s)'%
                                       (section, key, i))
                    else:
                        raise IniError('ini method getFloat, value not a valid floating number: %s (section: %s, key: %s)'%
                                   (section, key, i))
            else:
                return 0.0
        raise IniError('invalid type for getFloat (probably intermediate set without write: %s)(section: %s, key: %s'%
                       (repr(i), section, key))
    
        
                

    def getSectionPostfixesWithPrefix(self, prefix):
        """get all postfixes of sections, sorted, with a given prefix.

        A list is returned (and also set in the private variable _sectionPostfixesWP).
        So repeated calls can be handled quicker, BUT no refreshing is done!  A static
        ini instance is supposed.

        Prefix and postfix are separated by one space, and the list that is returned
        can be empty and is sorted by longest postfix first.

        So sections [p], [p f], [p ff] give as result (in _sectionPostfixesWP['p']):
        ['ff', 'f', '']
                

        >>> ini = IniVars('simple.ini')
        >>> ini.set('pref', 'key', '1')
        >>> ini.set('pref', 'm', '1')
        >>> ini.set('pref f', 'key', '2')
        >>> ini.set('pref f', 'l', '2')
        >>> ini.set('pref foo', 'key', '4')
        >>> ini.set('pref faa', 'key', '3')
        >>> ini.set('pref eggs', 'key', '5')
        >>> ini.set('pref eggs', 'k', '6')
        >>> ini.getSectionPostfixesWithPrefix('pref')
        [u'eggs', u'faa', u'foo', u'f', u'']
        >>> ini.getSectionPostfixesWithPrefix('pr')
        []

        
        Now go and search back, longest match first!
        >>> ini.getFromSectionsWithPrefix('pr', 'foo bar eggs', 'key')
        u''
 
        >>> ini.getFromSectionsWithPrefix('pref', 'foo bar eggs', 'key')
        u'5'
        >>> ini.getFromSectionsWithPrefix('pref', 'egg foo bar', 'key')
        u'4'
        >>> ini.getFromSectionsWithPrefix('pref', '', 'key')
        u'1'
        >>> ini.getFromSectionsWithPrefix('pref', 'withfooandeggs', 'key')
        u'5'
        >>> ini.getFromSectionsWithPrefix('pref', 'completely different', 'key')
        u'2'
        >>> ini.getFromSectionsWithPrefix('pref', 'completely else', 'key')
        u'1'
        >>> ini.getFromSectionsWithPrefix('pr', 'foo bar eggs', 'key')
        u''
        >>> ini.getFromSectionsWithPrefix('pref', 'foo bar eggs', 'l')
        u'2'
        >>> ini.getFromSectionsWithPrefix('pref', 'foo bar eggs', 'm')
        u'1'

        Get a list of sections that meeting the requirements:

        >>> ini.getSectionsWithPrefix('pref')
        [u'pref eggs', u'pref faa', u'pref foo', u'pref f', u'pref']
        >>> ini.getSectionsWithPrefix('pref', 'abcd')
        [u'pref']
        >>> ini.getSectionsWithPrefix('pref', 'foo')
        [u'pref foo', u'pref f', u'pref']
        >>> ini.getSectionsWithPrefix('pref', 'egg')
        [u'pref']
        >>> ini.getSectionsWithPrefix('pr', 'egg')
        []

        for exact finding the longerText can be a list or a tuple:
        >>> ini.getSectionsWithPrefix('pref', [])
        []
        >>> ini.getSectionsWithPrefix('pref', ['foo','eggs', ''])
        [u'pref foo', u'pref eggs', u'pref']
        
        These lists can be used with the next get call,
        so if the section is a list,
        the entries of a list are searched until
        a non empty value is found!

        >>> L = ini.getSectionsWithPrefix('pref')
        >>> ini.get(L, 'key')
        u'5'
        >>> L = ini.getSectionsWithPrefix('pref', 'this foo and another thing')
        >>> ini.get(L, 'key')
        u'4'
        >>> ini.get([], 'key')
        u''
        >>> ini.get(['pref'], 'k')
        u''
        
        We can also extract a list of all possible keys,
        and also ordered in a dictionary, leaving out doubles.
        >>> L = ini.getSectionsWithPrefix('pref') # with all sections with prefix pref
        >>> ini.get(L)
        [u'k', u'key', u'l', u'm']
        >>> ini.getKeysOrderedFromSections(L)
        {u'pref': [u'm'], u'pref foo': [], u'pref f': [u'l'], u'pref eggs': [u'k', u'key'], u'pref faa': []}
        >>> L = ini.getSectionsWithPrefix('pref', 'this foo and another thing') # with selection
        >>> ini.get(L)
        [u'key', u'l', u'm']
        >>> ini.getKeysOrderedFromSections(L)
        {u'pref': [u'm'], u'pref foo': [u'key'], u'pref f': [u'l']}

        And format this dictionary into a long string:

        >>> ini.formatKeysOrderedFromSections(L)
        u'[pref foo]\\nkey\\n\\n[pref f]\\nl\\n\\n[pref]\\nm\\n'

        >>> ini.formatKeysOrderedFromSections(L, giveLength=True)
        u'[pref foo] (1)\\nkey\\n\\n[pref f] (1)\\nl\\n\\n[pref] (1)\\nm\\n'


        ## if you specify giveLength as int, only sections with more items than giveLength
        ## have the number added.
        >>> ini.formatKeysOrderedFromSections(L, giveLength=10)
        u'[pref foo]\\nkey\\n\\n[pref f]\\nl\\n\\n[pref]\\nm\\n'
                
        For debugging purposes the section that matches a key
        from a section list can be retrieved:

        >>> ini.getMatchingSection(L, 'key')
        u'pref foo'
        >>> ini.getMatchingSection(L, 'l')
        u'pref f'
        >>> ini.getMatchingSection(L, 'm')
        u'pref'
        >>> ini.getMatchingSection(L, 'no valid key')
        u'section not found'


        """
        if type(prefix) == six.binary_type:
            prefix = utilsqh.convertToUnicode(prefix)
        if '_sectionPostfixesWP' not in self.__dict__:
            self._sectionPostfixesWP = {}  # create new dictionary for remembering
        if prefix in self._sectionPostfixesWP:
            return self._sectionPostfixesWP[prefix]

        # call with new prefix, construct new entry:        
        l = []
        for s in self.get():
            if s.find(prefix) == 0:
                L = map(string.strip, s.split(' ', 1))
                if L[0] == prefix: # proceed:
                    if len(L) == 2:
                        if ' '.join(L) != s:
                            raise IniError('getting section postfixes with prefix, exactly 1 space'
                                           'required bewtween prefix and postfix: %s'% s)
                        l.append(L[1]) # combined section key "prefix rest"
                    else:
                        l.append(u'')   # section key identical prefix, adding ''
        if l:
            l.sort(lensort)

        self._sectionPostfixesWP[prefix] = l
##        print 'new entry of _sectionPostfixesWP,%s: %s'% (prefix, l)
        return self._sectionPostfixesWP[prefix]

    def getFromSectionsWithPrefix(self, prefix, longerText, key):
        """get from all possible sections, as soon as longerText is found in postfix,
        the value is returned  longerText is required, and will often be a window title.

        examples see above

        """
        if type(prefix) == six.binary_type:
            prefix = utilsqh.convertToUnicode(prefix)
        postfixes = self.getSectionPostfixesWithPrefix(prefix)
        
        for postfix  in postfixes:
            if postfix and longerText.find(postfix) >= 0:
                v = self.get(prefix + ' ' + postfix, key)
                if v:
                    return self.returnStringOrUnicode(v)
            elif not postfix:   # empty string, the section is [prefix] only
                v = self.get(prefix, key)
                if v:
                    return self.returnStringOrUnicode(v)
        return u''


    def getSectionsWithPrefix(self, prefix, longerText=None):
        """get all possible sections, as soon as (part of) longerText matches postfix,
        the value is returned. longerText will often be a window title.
        If longerText is not given, a list of all sections with this prefix is returned.

        examples and testing see above        

        """
        if type(prefix) == six.binary_type:
            prefix = utilsqh.convertToUnicode(prefix)
        if type(longerText) == six.binary_type:
            longerText = utilsqh.convertToUnicode(longerText)
        postfixes = self.getSectionPostfixesWithPrefix(prefix)
        #print 'postfixes: %s'% postfixes
        if longerText is None:
            L = [prefix + ' ' + postfix for postfix in postfixes]
        elif type(longerText) == six.text_type:
            # print 'longerText: %s (%s)'% (longerText, type(longerText))
            # for postfix in postfixes:
            #     print '---postfix: %s (%s)'% (postfix, type(postfix))
            L = [prefix + ' ' + postfix for postfix in postfixes
                                    if longerText.find(postfix) >= 0]
        elif type(longerText) in (types.ListType, types.TupleType):
            L = [prefix + ' ' + postfix for postfix in longerText if postfix in postfixes ]
        else:
            return [prefix]
        return [l.strip() for l in L]

    def getKeysOrderedFromSections(self, sectionList):
        """get all possible keys from a list of sections 

        A dictionary is returned, with keys being the section keys,
        and as values a list of keys that are taken from this section.

        examples and testing see above        

        """
        allKeys = []
        D = {}
        for s in sectionList:
            keys = self.get(s)
            D[s] = []
            for k in keys:
                if k not in allKeys:
                    D[s].append(k)
                    allKeys.append(k)
        return D

    def ifOnlyNumbersInValues(self, sectionName):
        """if the values are only numbers, return first and last key
        otherwise return None, see formatReverseNumbersDict
        """
        Keys = self.get(sectionName)
        if not Keys: return
        D = {}
        for k in Keys:
            v = self.get(sectionName, k)
            if not v: return
            try:
                v = int(v)
            except (ValueError, TypeError):
                return 
            # now we now v is an integer number
            D.setdefault(v, []).append(k)
        # when here, a numbers dict is found
        items = [(k,v) for k,v in D.items()]
        return formatReverseNumbersDict(dict(items))
        
            

    def formatKeysOrderedFromSections(self, sectionList, lineLen=60, sort=1, giveLength=None):
        """formats in a long string all possible keys from a list of sections 

        The dictionary of the function "getKeysOrderedFromSections" is used,
        and the formatting is done with a generator function.

        examples and testing see above        

        """
        D = self.getKeysOrderedFromSections(sectionList)
        L = []
        for k in sectionList:
            if giveLength:
                lenValues = len(D[k])
                if type(giveLength) == types.IntType and lenValues < giveLength:
                        L.append('[%s]'%k)
                else:
                    L.append('[%s] (%s)'% (k, len(D[k])))
            else:
                L.append('[%s]'%k)
            L.append(utilsqh.formatListColumns(D[k], lineLen=lineLen, sort=sort))
            L.append('')
        return '\n'.join(L)
    

    def getMatchingSection(self, sectionList, key):
        """gives the section that has the key

        """
        for s in sectionList:
            if key in self.get(s):
                if type(s) == six.binary_type:
                    return utilsqh.convertToUnicode(s)
                else:
                    return s
        return u'section not found'

    def getKeysWithPrefix(self, section, prefix, glue=None, includePrefix=None):
        """get keys within a section with a fixed prefix
        
        glue can be "-"
        if possible, the list is sorted numeric, if mixed, the numbers (until 99999) go first
        if includePrefix, prefix itself is inserted at start of resulting list
        (see unittest, testKeysWithPrefix)
        
        >>> ini = IniVars('simple.ini')
        >>> ini.set('example', 'key', '1')
        >>> ini.set('example', 'key-4', '2')
        >>> ini.set('example', 'key-12', '3')

        >>> ini.getKeysWithPrefix('example', 'key', glue='-')
        [u'key-4', u'key-12']
        >>> ini.getKeysWithPrefix('example', 'key', glue='-')
        [u'key-4', u'key-12']
        >>> ini.set('mixed', 'foo', '1')
        >>> ini.set('mixed', 'foo 4', '2')
        >>> ini.set('mixed', 'foo 12', '3')
        >>> ini.set('mixed', 'foo text', '4')
        >>> ini.getKeysWithPrefix('mixed', 'foo', includePrefix=1)
        [u'foo', u'foo 4', u'foo 12', u'foo text']

        # if no glue prefix takes anything and no numeric sort, so mostly you will prefer a glue character
        # like ' ' or '-'/
        >>> ini.getKeysWithPrefix('mixed', 'fo')
        [u'foo', u'foo 12', u'foo 4', u'foo text']

        # mismatch, if glue prefix must exactly match first word:
        >>> ini.getKeysWithPrefix('mixed', 'fo', glue=' ')
        []


        
        """
        if not prefix:
            return []
        if type(prefix) == six.binary_type:
            prefix = utilsqh.convertToUnicode(prefix)
        lenprefix = len(prefix)
        rawlist = [k for k in self.get(section) if k.startswith(prefix)]
        if not rawlist: return []
        if prefix in rawlist:
            gotPrefix = 1
            rawlist.remove(prefix)
        else:
            gotPrefix = 0
            
        if not rawlist:
            if includePrefix and gotPrefix:
                return [prefix]
            else:
                return []

        dec = []
        for k in rawlist:
            if glue:
                try:
                    start, num = map(string.strip, k.rsplit(glue, 1))
                except ValueError:
                    continue
            else:
                start, num = prefix, k[lenprefix:].strip()
            try:
                num = int(num)
            except ValueError:
                num = 99999
            if start == prefix:    
                dec.append( (num, start, k) )
        if not dec:
            return []
        dec.sort()
        resultList = [k for (num, start, k) in dec]
        if includePrefix and gotPrefix:
            resultList.insert(0, prefix)
        return resultList
        
    def toDict(self, section=None):
        """for testing, return contents as a pure dict"""
        if section:
            return dict(self[section])
        # whole inifile:
        D = dict()
        for (k,v) in self.iteritems():
            D[k] = dict(v)
        return D            

    def fromDict(self, Dict, section=None):
        """enter ini data from a dict"""
        if section:
            for k, v in Dict.iteritems():
                self.set(section, k, v)
            return
        # complete file, double dict
        for section, kv in Dict.iteritems():
            if kv and type(kv) == types.DictType:
                for k, v in kv.iteritems():
                    self.set(section, k, v)
            else:
                raise TypeError('inivars, fromDict, invalid value for section "%s", should be a dict: %s'%
                                (section, repr(kv)))

def sortHyphenKeys(keys):
    """sort keys, first by trailing number (-nnn), second by trunk name (after xx-)

    for use in siteGen, if no hyphens occur in any key, or not of form en-key or key-nnn or en-key-nnn
    (en = language code, en, fr, ...)
    (nnn = a numbenaar mijnr)
    nothing happens

>>> sortHyphenKeys(['second', 'numbered-2', 'numbered-10'])
['second', 'numbered-2', 'numbered-10']

>>> sortHyphenKeys(['a', 'bbb-ccc', 'x', 'bbb'])
['a', 'bbb', 'bbb-ccc', 'x']

>>> sortHyphenKeys(['second', 'no sort'])
['no sort', 'second']
>>> sortHyphenKeys(['single', 's', 'double', 'en-double'])
['s', 'single', 'double', 'en-double']

>>> sortHyphenKeys(['single', 's', 'double', 'en-double', 'double-2', 'en-double-2', 'double-10', 'en-double-10'])
['s', 'single', 'double', 'en-double', 'double-2', 'en-double-2', 'double-10', 'en-double-10']


>>> sortHyphenKeys(['triple', 'en-triple', 'fr-triple', 'en-triple-3', 'fr-triple-3', 'triple-13', 'fr-triple-13', 'single', 's', 'double', 'en-double', 'double-2', 'en-double-2', 'double-10', 'en-double-10'])
['s', 'single', 'double', 'en-double', 'triple', 'en-triple', 'fr-triple', 'double-2', 'en-double-2', 'triple-3', 'en-triple-3', 'fr-triple-3', 'double-10', 'en-double-10', 'triple-13', 'fr-triple-13']


    """
        
    D  = {}
    for k in keys:
        parts = k.split('-')
        try:
            index = int(parts[ - 1])
        except ValueError:
            D.setdefault(0, []).append(k)
        else:
            D.setdefault(index, []).append(k)
    mainKeys = D.keys()
    mainKeys.sort()
    sortedKeys = []
    for mainKey in mainKeys:
        sortedKeys.extend(sortLanguageKeys(D[mainKey]))
    return sortedKeys

def reverseDictWithDuplicates(D):
    """for testing, values are lists always
    """
    reverseD = {}
    for k,v  in D.items():
        reverseD.setdefault(v, []).append(k)
    return reverseD

def formatReverseNumbersDict(D):
    """format as efficient as possible

    keys: the spoken words possibly with equivalents
    value: a list of numbers, to be ordered rising order
    
    (reverse with reverseDictWithDuplicates)
    
    one ... twenty or one, two, twice, three ... ten
    """
    #reverseD = {}
    #for k,v in D.items():
    #    reverseD.setdefault(v, []).append(k)
        
    
    items = [(k,v) for k,v in D.items()]
    items.sort()
    # print 'items: %s'% items
    it = peek_ahead(items)
    kPrev = None
    L = []
    increment = 1
    for k, v in it:
        preview = it.preview
        if preview != it.sentinel:
            knext, vnext = preview
        if preview == it.sentinel or len(vnext) > 1 or knext != k + increment:
            # close current item
            if kPrev is None:
                if L: L.append(', ')
                L.append(', '.join(v))
            elif k - kPrev != increment:
                L.append(' ... %s'% ', '.join(v))
                increment = k - kPrev
            else:
                # next item only:
                L.append(', %s'% ', '.join(v))
            kPrev = None
        else:
            # there is a next, consisting of one text item
            if kPrev != None:
                continue
            elif len(v) > 1:
                if L: L.append(', ')
                L.append(', '.join(v))
            else:
                # one item of longer possibly ... separated sequence
                if L: L.append(', ')
                try:
                    L.append(u'%s'% v[0])
                except UnicodeDecodeError:
                    # print('inivars, formatReverseNumbersDict fails: %s (type: %s)'% (ord(v[0][0]), type(v[0])))
                    vv = utilsqh.convertToUnicode(v[0])
                    L.append(vv)
                kPrev = k
    # for line in L:
    #     print 'line: %s (%s_)'% (line, type(line))
    return u''.join(L)

    ###???
    #minNum, maxNum = min(nums), max(nums)
    ##print 'min: %s, max: %s, nums: %s'% (minNum, maxNum, nums)
    #hadPrev = 0
    #L = []
    #for i in range(minNum, maxNum+1):
    #    v = D.get(i, None)
    #    if v == None:
    #        hadPrev = 0
    #    if len(v) > 1:
    #        L.append(', '.join(v))
    #    if hadPrev:
    #        i
    #        
    #if nums == range(minNum, maxNum+1):
    #    return (D[minNum], D[maxNum])


def sortLanguageKeys(keys):
    """sort single keys first, then language keys, with neutral on top"""

    langKeys = [k for k in keys if len(k) > 2 and k[2] == '-']
    trunkKeys = set([k[3:] for k in langKeys])
    trunkKeys = list(trunkKeys)
    nonLangKeys = [k for k in keys if k not in langKeys]
    singleKeys = [k for k in nonLangKeys if k not in trunkKeys]
    trunkKeys.sort()
    singleKeys.sort()
    total = singleKeys[:]
    for trunk in trunkKeys:
        # get trunk + accompanying language keys:
        accompany = [k for k in langKeys if k.find(trunk) == 3]
        accompany.sort()
        total.append(trunk)
        for k in accompany:
            total.append(k)
            langKeys.remove(k)
    if langKeys:
        langKeys.sort()
        total.extend(langKeys)
    return total

def listToString(valueList):
    """convert list of items (from _readIni) into a string

    utility for readIni function.    

    first strip off empty lines at beginning or end
    second if 1 line: return stripped state
    third: in more lines: return join of lines, only right strip now

>>> listToString([''])
''
>>> listToString(['   '])
''
>>> listToString(['', ' abc ', '', 'def    ', ''])
' abc\\n\\ndef'
>>> listToString(['', '  stripped ', '', '', '  ', '\\t \\t'])
'stripped'

    """
    if len(valueList) == 0:
        raise IniError('empty keylist')
    while len(valueList) > 0 and not valueList[0].strip():
        valueList.pop(0)
    while  len(valueList) > 0 and not valueList[-1].strip():
        valueList.pop()
    if len(valueList) == 1:
        return valueList[0].strip()
    return '\n'.join(map(string.rstrip, valueList))

# patterns for runPythonCode:

def testReSearch(reExpression, texts):
    res = []
    for t in texts:
        if reExpression.search(t):
            res.append(1)
        else:
            res.append(0)
    return res

def testReSub(reExpression, texts, replacement):
    res = []
    for t in texts:
        if reExpression.search(t):
            res.append(reExpression.sub(replacement, t))
        else:
            res.append(t)
    return res

def testReMatch(reExpression, texts):
    res = []
    for t in texts:
        if reExpression.match(t):
            res.append(1)
        else:
            res.append(0)
    return res
def readExplicit(ini,mode=None ):
    """Read all sections and keys, and set them back in the ini instance

    Mode can also be list or dict.
    """
    for s in ini:
        for k in ini.get(s):
            if mode == "list":
                v = ini.getList(s, k)
            elif mode == "dict":
                v = ini.getDict(s, k)
            elif mode == None:
                v = ini.get(s, k)
            else:
                raise InivarsError('invalid mode for test function readExplicit: %s'% mode)
            ini.set(s, k, v)
        
retest = '''

>>> testReMatch(reValidSection,  ['[valid section]', '[a3]', '[x]','[3x]', '[x - y]', '[X. Y.]'])
[1, 1, 1, 1, 1, 1]


>>> testReMatch(reValidSection,  [' [invalid section]',  '[-x3]', '[.xyz]'])
[0, 0, 0]

>>> testReMatch(reValidKey,  ['valid key ',  '3x', 'A. B. C.'])
[1, 1, 1]


>>> testReMatch(reValidKey,  [' invalid key]',  'x[s]', '-x'])
[0, 0, 0]

>>> testReMatch(reFindKeyValue,  ['valid key = ',  '3x =', 'A. B. C. ='])
[1, 1, 1]


>>> testReMatch(reFindKeyValue,  [' invalid key=]',  'x[s]=', '-x='])
[0, 0, 0]


>>> testReSearch(reWhiteSpace,  [' abc', '  a', 'a  b'])
[1, 1, 1]



White Space:

>>> testReSearch(reWhiteSpace,  [' abc', '  a', 'a  b'])
[1, 1, 1]

>>> testReSub(reWhiteSpace, ['abc', ' a b', ' a b   c'], '')
['abc', 'ab', 'abc']

>>> testReSearch(reWhiteSpace,  ['abc'])
[0]


'''




goodfilesTest = '''
>>> r = 'projects/miscqh/testinivars'
>>> root = utilsqh.getRoot('c:/'+r, 'd:/'+r)
>>> test = root/'test'
>>> utilsqh.makeEmptyFolder(test)

basic testing:

>>> L = ['basic', 'multiplelines']
>>> for n in L:
...     ini = IniVars(root/(n+'.ini'))
...     readExplicit(ini)
...     ini.write(root/'test'/(n+'.ini'))
...     ini2 = IniVars(root/'test'/(n+'.ini'))
...     readExplicit(ini2)
...     print 'testFile: %s, result: %s'% (n, ini == ini2)
testFile: basic, result: True
testFile: multiplelines, result: True

list:

>>> L = ['list']
>>> for n in L:
...     ini = IniVars(root/(n+'.ini'))
...     readExplicit(ini, mode = 'list')
...     ini.write(root/'test'/(n+'.ini'))
...     ini2 = IniVars(root/'test'/(n+'.ini'))
...     readExplicit(ini2, mode = 'list')
...     print 'testFile, list: %s, result: %s'% (n, ini == ini2)
testFile, list: list, result: True



dict:

>>> L = ['dict']
>>> for n in L:
...     ini = IniVars(root/(n+'.ini'))
...     readExplicit(ini, mode = 'dict')
...     ini.write(root/'test'/(n+'.ini'))
...     ini2 = IniVars(root/'test'/(n+'.ini'))
...     readExplicit(ini2, mode = 'dict')
...     print 'testFile, dict: %s, result: %s'% (n, ini == ini2)
testFile, dict: dict, result: True


whatSKIgnorecase:

>>> L = ['uckey', 'ucsection']
>>> for n in L:
...     ini = IniVars(root/(n+'.ini'), SKIgnorecase=1)
...     readExplicit(ini)
...     ini.set('New Section', 'New Key', 'New Value')
...     ini.write(root/'test'/(n+'.ini'))
...     ini2 = IniVars(root/'test'/(n+'.ini'))
...     readExplicit(ini2)
...     print 'ini2, sections, keys lowercase:%s'% ini2
...     print 'testFile, SKIgnorecase: %s, result: %s'% (n, ini == ini2)
ini2, sections, keys lowercase:{'section': {'key with capitals': 'v'}, 'new section': {'new key': 'New Value'}}
testFile, SKIgnorecase: uckey, result: True
ini2, sections, keys lowercase:{'section': {'k': 'v'}, 'new section': {'new key': 'New Value'}}
testFile, SKIgnorecase: ucsection, result: True


spaces:

>>> L = ['spacing']
>>> for n in L:
...     ini = IniVars(root/(n+'.ini'))
...     readExplicit(ini)
...     ini.write(root/'test'/(n+'.ini'))
...     ini2 = IniVars(root/'test'/(n+'.ini'))
...     readExplicit(ini2)
...     print 'ini2: look at the spacing of: %s'% n
...     strini2 = str(ini2)
...     strini2 = strini2.replace('\\\\n', '|')
...     print 'spacing (|): %s'% strini2
...     print 'result (identical?): %s'% (ini == ini2,)
ini2: look at the spacing of: spacing
spacing (|): {'spacing section': {'one line': 'value', 'multiple lines': 'first line|second line||third line is new paragaph|fourth line has no leading spaces'}}
result (identical?): True

'''

#
#__test__ = {'regular expressions': retest,
#            'good files': goodfilesTest}

def test():
    import doctest
    return doctest.testmod()


if __name__ == "__main__":
    test()

