# -*- coding: iso-8859-1 -*-
#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
#pylint:disable=C0116, C0114, C0115, R0902, R0912
r"""gramparser.py
 
  This module contains the Python code to convert the textual representation
  of a command and control grammar in the standard SAPI CFG binary format.

Grammar format

  Rule Definition:
      <RuleName> imported ;
      <RuleName> = Expression ;
      <RuleName> exported = Expression ;

  A rule needs the keyword "exported" in order to be activated or visible
  to other grammars for importing.

  Expression:
      <RuleName>                  // no spaces
      {ListName}                  // no spaces
      Word
      "Word"
      ( Expression )
      [ Expression ]              // optional
      Expression +                // repeat
      Expression Expression       // sequence
      Expression | Expression     // alternative

When building grammars there are three built in rules which can be imported:

  <dgnletters>    Contains all the letters of the alphabet for spelling.
      Letters are spelled like "a\\l", "b\\l", etc.

  <dgnwords>      The set of all words active during dictation.

  <dgndictation>  A special rule which corresponds to dictation.  It is
      roughly equivalent to ( <dgnwords> | "\(noise)" )+  However, the
      noise words is filtered out from any results reported to clients.
"""
import copy
import locale
import os
import os.path
import pprint
import re
from collections import OrderedDict
from enum import unique, IntEnum
from struct import pack

from typing import Optional, List, Iterator, Tuple, Dict, Iterable, Union, Any, Generator, TypeVar, Generic

preferredencoding = locale.getpreferredencoding()

reAlphaNumeric = re.compile(r'\w+$')
reValidName = re.compile(r'^[a-zA-Z0-9-_]+$')


class GrammarParserError(Exception):
    """these exceptions all expect the scanObj as second parameter
    in order to produce the correct message info
    """

    def __init__(self, message: str, scanObj: Optional['GramScanner'] = None) -> None:
        super().__init__(message)
        self.message = message
        self.scanObj = scanObj

    def __str__(self) -> str:
        """return special info for scanner or parser exceptions.
        """
        if self.scanObj is None:
            return self.message

        gramName = self.scanObj.grammarName or ""
        L = []
        if self.scanObj.phase == 'scanning':
            line = self.scanObj.line + 1
            startPos, charPos = self.scanObj.start + 1, self.scanObj.char + 1
            if startPos == charPos:
                pos = str(charPos)
            elif charPos - startPos == 1:
                pos = str(charPos)
            else:
                pos = '%s-%s' % (startPos, charPos)
            errorMarker = self.scanObj.getError()
            if gramName:
                L.append('in grammar "%s", line %s, position %s:' % (gramName, line, pos))
            else:
                L.append('in grammar, line %s, position %s:' % (line, pos))
            L.append(self.message)
            L.append(errorMarker)
        else:
            if gramName:
                L.append('in grammar "%s", %s scanning/parsing:' % (gramName, self.scanObj.phase))
            else:
                L.append('in grammar, %s scanning/parsing:' % self.scanObj.phase)
            L.append(self.message)

        return '\n'.join(L)

    def dumpToFile(self) -> None:
        """dump grammar and traceback to a file for debugging purposes
        """
        if self.scanObj is None:
            raise ValueError('Cannot dump without a scanObj')

        gramName = self.scanObj.grammarName
        dirName = os.path.dirname(__file__)
        if gramName:
            filename = 'error_info_grammar_%s.txt' % gramName
        else:
            filename = 'error_info_natlink_grammar.txt'
        filepath = os.path.join(dirName, filename)
        L = []
        if gramName:
            L.append('Info about scanner/parser error of Natlink grammar "%s"\n' % gramName)
        else:
            L.append('Info about scanner/parser error of Natlink grammar\n')

        L.append('\nThe complete grammar:\n')
        if self.scanObj.phase == 'scanning':
            for i, line in enumerate(self.scanObj.text):
                if i == self.scanObj.line:
                    L.append(self.scanObj.getError())
                elif i == len(self.scanObj.text) - 1 and not line.strip():
                    L.append("%.2s: %s" % (i + 1, line))

        else:
            L.extend(self.scanObj.text)
        L.append('')

        with open(filepath, 'w') as f:
            f.write('\n'.join(L))


class GrammarSyntaxError(GrammarParserError):
    pass


class LexicalError(GrammarParserError):
    pass


class SymbolError(GrammarParserError):
    pass


class GrammarError(GrammarParserError):
    pass


@unique
class ElementCode(IntEnum):
    SeqCode = 1  # sequence
    AltCode = 2  # alternative
    RepCode = 3  # repeat
    OptCode = 4  # optional


class GramScanner:
    """
    This is the lexical scanner.

    We take a list of strings as input (such as would be returned by readlines).

    After every call to getAnotherToken or testAndEatToken the variables token
    and value will contain the details about the next token in the input stream.
    """

    def __init__(self, text: Optional[List[str]] = None, grammarName: Optional[str] = None) -> None:
        self.token: Optional[str] = None
        self.value: Optional[str] = None
        self.line: int = 0
        self.char: int = 0
        self.start: int = 0
        if text:
            self.text = copy.copy(text)
            if self.text[-1] != '\0':
                self.text.append('\0')
        else:
            self.text = ['\0']
        self.lastWhiteSpace: str = ""  # for gramscannerreverse
        self.grammarName: str = grammarName or ""
        self.phase: str = "before"

    def newText(self, text: List[str]) -> None:
        GramScanner.__init__(self, text)

    def getError(self) -> str:
        if self.token == '\0' or self.text[self.line][0] == '\0':
            errorLine = '=> (end of input)\n'
        else:
            spacing = ' ' * self.start
            hats = '^' * (self.char - self.start)
            if not hats:
                hats = '^'
            errorLine = '=> ' + self.text[self.line] + '\n=> ' + spacing + hats + '\n'
        return errorLine

    def testAndEatToken(self, token: str) -> Optional[str]:
        if self.token != token:
            raise GrammarSyntaxError("expecting '%s'" % token, self)
        value = self.value
        self.getAnotherToken()
        return value

    def skipWhiteSpace(self) -> None:
        """skip whitespace and comments, but keeps the leading comment/whitespace
        in variable self.lastWhiteSpace (QH, july 2012)
        """
        ch = self.char
        oldPos = ch
        oldLine = self.line
        while 1:
            ln = self.text[self.line]
            lnLen = len(ln)
            while ch < lnLen and not ln[ch].strip():  # in string.whitespace:
                ch = ch + 1
            if ch < lnLen and ln[ch] != '#':
                break
            self.line = self.line + 1
            self.text[self.line] = self.text[self.line].replace('\t', ' ')
            self.text[self.line] = self.text[self.line].replace('\n', ' ')
            ch = 0
        self.char = ch
        if self.line == oldLine:
            self.lastWhiteSpace = ln[oldPos:ch]
        else:
            L = [self.text[oldLine][oldPos:]]
            for l in range(oldLine + 1, self.line):
                L.append(self.text[l])
            L.append(self.text[self.line][:ch])
            self.lastWhiteSpace = '\n'.join(L)

    def getAnotherToken(self) -> None:
        """return a token and (if appropriate) the corresponding value
        
        token can be '=', '|', '+', ';', '(', ')', '[', ']' (with value None)
        or 'list' (value without {})
        or 'rule' (value without <>)
        or 'sqword', 'dqword', 'word'  (a word, in single quotes, double quotes or unquoted)
        Note "exported" and "imported" and list names and rule names must have token 'word'
        Grammar words can have dqword or sqword too. (dqword and sqword added by QH, july 2012)
        
        """

        if self.token == '\0':
            return

        self.value = None

        self.skipWhiteSpace()  # now leaves self.lastWhiteSpace
        ch = self.char
        ln = self.text[self.line]
        lnLen = len(ln)

        self.start = ch

        if ln[ch] in ['(', ')', '[', ']', '|', '+', '=', ';', '\0']:
            self.token = ln[ch]
            ch = ch + 1

        elif ln[ch] == '"':
            self.token = 'dqword'
            ch = ch + 1
            while ch < lnLen and ln[ch] != '"':
                ch = ch + 1
            if ch >= lnLen:
                raise LexicalError("expecting closing quote in word name", self)
            self.value = ln[self.start + 1:ch]
            ch = ch + 1

        elif ln[ch] == "'":
            self.token = 'sqword'
            ch = ch + 1
            while ch < lnLen and ln[ch] != "'":
                ch = ch + 1
            if ch >= lnLen:
                raise LexicalError("expecting closing quote in word name", self)
            self.value = ln[self.start + 1:ch]
            ch = ch + 1

        elif ln[ch] == '<':
            self.token = 'rule'
            ch = ch + 1
            while ch < lnLen and ln[ch] != '>':
                ch = ch + 1
            if ch >= lnLen:
                raise LexicalError("expecting closing angle bracket in rule name", self)
            self.value = ln[self.start + 1:ch]
            ch = ch + 1

        elif ln[ch] == '{':
            self.token = 'list'
            ch = ch + 1
            while ch < lnLen and ln[ch] != '}':
                ch = ch + 1
            if ch >= lnLen:
                raise LexicalError("expecting closing brace in list name", self)
            self.value = ln[self.start + 1:ch]
            ch = ch + 1

        elif isCharOrDigit(ln[ch]):
            self.token = 'word'
            while ch < lnLen and isCharOrDigit(ln[ch]):
                ch = ch + 1
            self.value = ln[self.start:ch]

        else:
            raise LexicalError("unknown character found", self)

        self.char = ch


class GramScannerReverse(GramScanner):
    """
    generator function, scanning the tokens and whitespace of a gramspec:
    this class can scan a grammar, return the tokens in a generator function
    and put back the results exactly the same
    """

    def __init__(self, text: List[str]):
        text2 = splitApartLines(text)
        GramScanner.__init__(self, text2)
        self.returnList: List[str] = []

    def gramscannergen(self) -> Iterator[Tuple[str, Optional[str], Optional[str]]]:
        """
        this generator function gives all whitespace, token, value tuples
        end with (whitespace, '\0', None)
        """
        while 1:
            self.getAnotherToken()
            token = self.token
            if token == '\0':
                yield self.lastWhiteSpace.rstrip('\n'), '\0', None
                return
            value = self.value
            whitespace = self.lastWhiteSpace
            yield whitespace, token, value

    def appendToReturnList(self, whitespace: str, token: str, value: Optional[str]) -> None:
        """add to the returnList, to produce equal result or translation
        """
        L = self.returnList
        if whitespace:
            L.append(whitespace)
        if token == '\0':
            return

        if token == 'rule':
            L.append('<%s>' % value)
        elif token == 'list':
            L.append('{%s}' % value)
        elif token == 'word':
            assert isinstance(value, str)
            if reAlphaNumeric.match(value):
                L.append(value)
            elif "'" in value:
                L.append('"%s"' % value)
            else:
                L.append("'%s'" % value)
        elif token == 'sqword':
            L.append("'%s'" % value)
        elif token == 'dqword':
            L.append('"%s"' % value)
        elif value is None:
            L.append(token)
        else:
            L.append(value)

    def mergeReturnList(self) -> str:
        return ''.join(self.returnList)


Definition = List[Tuple[str, int]]


class GramParser:
    """
    This is a rule parser.  It builds up data structures which contain details
    about the rules in the parsed text.

    The definition of a rule is an array which contains tuples.  The array
    contains the rule elements in sequence.  The tuples are pairs of element
    type and element value
    """

    def __init__(self, text: Union[str, List[str]], grammarName: Optional[str] = None):
        self.knownRules: Dict[str, int] = dict()
        self.knownWords: Dict[str, int] = dict()
        self.knownLists: Dict[str, int] = dict()
        self.nextRule = 1
        self.nextWord = 1
        self.nextList = 1
        self.exportRules: Dict[str, int] = dict()
        self.importRules: Dict[str, int] = dict()
        self.ruleDefines: Dict[str, Definition] = dict()
        self.grammarName: str = grammarName or ""
        text = splitApartLines(text)

        self.scanObj = GramScanner(text, grammarName=grammarName)

    def doParse(self, *text: List[str]) -> None:
        self.scanObj.phase = "scanning"
        if text:
            self.scanObj.newText(text[0])
        # try:
        self.scanObj.getAnotherToken()
        while self.scanObj.token != '\0':
            self.parseRule()
        self.scanObj.phase = "after"

    def parseRule(self) -> None:
        if self.scanObj.token != 'rule':
            raise GrammarSyntaxError("expecting rule name to start rule definition", self.scanObj)
        ruleName = self.scanObj.value
        assert isinstance(ruleName, str)
        if not isValidListOrRulename(ruleName):
            raise GrammarSyntaxError('rulename may may only contain ascii letters, digits or - or _: "%s"' % ruleName,
                                     self.scanObj)
        if ruleName in self.ruleDefines:
            raise SymbolError("rule '%s' has already been defined" % ruleName, self.scanObj)
        if ruleName in self.importRules:
            raise SymbolError("rule '%s' has already been defined as imported" % ruleName, self.scanObj)
        if ruleName in self.knownRules:
            ruleNumber = self.knownRules[ruleName]
        else:
            ruleNumber = self.nextRule
            self.nextRule = self.nextRule + 1
            self.knownRules[ruleName] = ruleNumber
        self.scanObj.getAnotherToken()
        if self.scanObj.token == 'word' and self.scanObj.value == 'imported':
            self.importRules[ruleName] = ruleNumber
            self.scanObj.getAnotherToken()
        else:
            if self.scanObj.token == 'word' and self.scanObj.value == 'exported':
                self.exportRules[ruleName] = ruleNumber
                self.scanObj.getAnotherToken()
            self.scanObj.testAndEatToken('=')
            self.ruleDefines[ruleName] = self.parseExpr()
        self.scanObj.testAndEatToken(';')

    def parseExpr(self) -> Definition:
        definition: Definition = []
        moreThanOne = 0
        while 1:
            definition = definition + self.parseExpr2()
            if self.scanObj.token != '|':
                break
            self.scanObj.getAnotherToken()
            moreThanOne = 1
        if moreThanOne:
            return [('start', ElementCode.AltCode.value)] + definition + [('end', ElementCode.AltCode.value)]
        return definition

    def parseExpr2(self) -> Definition:
        definition: Definition = []
        moreThanOne = 0
        while 1:
            definition = definition + self.parseExpr3()
            if self.scanObj.token not in ('word', 'sqword', 'dqword', 'rule', 'list', '(', '['):
                break
            moreThanOne = 1
        if moreThanOne:
            return [('start', ElementCode.SeqCode.value)] + definition + [('end', ElementCode.SeqCode.value)]
        return definition

    def parseExpr3(self) -> Definition:
        definition = self.parseExpr4()
        if self.scanObj.token == '+':
            self.scanObj.getAnotherToken()
            return [('start', ElementCode.RepCode.value)] + definition + [('end', ElementCode.RepCode.value)]
        return definition

    def parseExpr4(self) -> Definition:
        if self.scanObj.token in ['word', 'sqword', 'dqword']:
            wordName = self.scanObj.value
            if not wordName:
                raise GrammarSyntaxError("empty word name", self.scanObj)
            if wordName in self.knownWords:
                wordNumber = self.knownWords[wordName]
            else:
                wordNumber = self.nextWord
                self.nextWord = self.nextWord + 1
                self.knownWords[wordName] = wordNumber
            self.scanObj.getAnotherToken()
            return [('word', wordNumber)]

        if self.scanObj.token == 'list':
            listName = self.scanObj.value
            if not listName:
                raise GrammarSyntaxError("empty word name", self.scanObj)
            if not isValidListOrRulename(listName):
                raise GrammarSyntaxError(
                    'listname may may only contain ascii letters, digits or - or _: "%s"' % listName,
                    self.scanObj)
            if listName in self.knownLists:
                listNumber = self.knownLists[listName]
            else:
                listNumber = self.nextList
                self.nextList = self.nextList + 1
                self.knownLists[listName] = listNumber
            self.scanObj.getAnotherToken()
            return [('list', listNumber)]

        if self.scanObj.token == 'rule':
            ruleName = self.scanObj.value
            if not ruleName:
                raise GrammarSyntaxError("empty word name", self.scanObj)
            if not isValidListOrRulename(ruleName):
                raise GrammarSyntaxError(
                    'rulename may may only contain ascii letters, digits or - or _: "%s"' % ruleName,
                    self.scanObj)
            if ruleName in self.knownRules:
                ruleNumber = self.knownRules[ruleName]
            else:
                ruleNumber = self.nextRule
                self.nextRule = self.nextRule + 1
                self.knownRules[ruleName] = ruleNumber
            self.scanObj.getAnotherToken()
            return [('rule', ruleNumber)]

        if self.scanObj.token == '(':
            self.scanObj.getAnotherToken()
            definition = self.parseExpr()
            self.scanObj.testAndEatToken(')')
            return definition

        if self.scanObj.token == '[':
            self.scanObj.getAnotherToken()
            definition = self.parseExpr()
            self.scanObj.testAndEatToken(']')
            # self.reportOptionalRule(definition)
            return [('start', ElementCode.OptCode.value)] + definition + [('end', ElementCode.OptCode.value)]

        raise GrammarSyntaxError("expecting expression (word, rule, etc.)", self.scanObj)

    def reportOptionalRule(self, definition: Definition) -> None:
        """print the words that are optional, for testing BestMatch V"""
        wordsRev = OrderedDict([(v, k) for k, v in self.knownWords.items()])

        for w, number in definition:
            if w == 'word':
                print('optional word: %s' % wordsRev[number])

    def checkForErrors(self) -> None:
        if not self.exportRules:
            raise GrammarError("no rules were exported")
        for ruleName in list(self.knownRules.keys()):
            if ruleName not in self.importRules and ruleName not in self.ruleDefines:
                raise GrammarError("rule '%s' was not defined or imported" % ruleName)

    def dumpString(self) -> str:
        """returns the parts that are non empty
        """
        L: List[str] = []
        for name in ["knownRules", "knownLists", "knownWords",
                     "exportRules", "importRules", "ruleDefines"]:
            var = getattr(self, name)
            if var:
                L.append(name + ":")
                L.append(pprint.pformat(var))
        return '\n'.join(L)

    def dumpStringNice(self) -> str:
        """returns the parts that are non empty
        reverse numbers of rules and ruleDefines... must be identical in gramparserlexyacc...
        """
        L: List[str] = []
        rulesRev = OrderedDict([(v, k) for k, v in list(self.knownRules.items())])
        wordsRev = OrderedDict([(v, k) for k, v in list(self.knownWords.items())])
        listsRev = OrderedDict([(v, k) for k, v in list(self.knownLists.items())])
        codeRev: Dict[int, str] = {ElementCode.SeqCode.value: 'SeqCode',
                                   ElementCode.AltCode.value: 'AltCode',
                                   ElementCode.RepCode.value: 'RepCode',
                                   ElementCode.OptCode.value: 'OptCode'}

        for name in ["exportRules", "importRules"]:
            var = getattr(self, name)
            if var:
                L.append('%s: %s' % (name, ', '.join(var)))
        if self.ruleDefines:
            ruleDefinesNice = OrderedDict(
                [(rulename, [self.nicenItem(item, rulesRev, wordsRev, listsRev, codeRev) for item in ruleList])
                 for (rulename, ruleList) in list(self.ruleDefines.items())])

            L.append(pprint.pformat(ruleDefinesNice))
        return '\n'.join(L)

    def dumpNice(self) -> Dict[str, Any]:
        """returns the parts that are non empty
        return a dict, with keys
        knownRules, knownWords, exportRules, ruleDefines, importRules (if not empty)

        reverse numbers of rules and ruleDefines... must be identical in gramparserlexyacc...
        """
        D: Dict[str, Any] = {}
        rulesRev: Dict[int, str] = OrderedDict([(v, k) for k, v in list(self.knownRules.items())])
        wordsRev: Dict[int, str] = OrderedDict([(v, k) for k, v in list(self.knownWords.items())])
        listsRev: Dict[int, str] = OrderedDict([(v, k) for k, v in list(self.knownLists.items())])
        codeRev: Dict[int, str] = {ElementCode.SeqCode: 'SeqCode',
                                   ElementCode.AltCode: 'AltCode',
                                   ElementCode.RepCode: 'RepCode',
                                   ElementCode.OptCode: 'OptCode'}

        for name in ["exportRules", "importRules"]:
            var = getattr(self, name)
            if var:
                D[name] = list(var.keys())
        if self.ruleDefines:
            ruleDefinesNice = {(rulename, [self.nicenItem(item, rulesRev, wordsRev, listsRev, codeRev)
                                                for item in ruleList])
                                    for (rulename, ruleList) in list(self.ruleDefines.items())}
            D['ruleDefines'] = ruleDefinesNice
        return D

    @staticmethod
    def nicenItem(item: Tuple[str, int], rulesRev: Dict[int, str], wordsRev: Dict[int, str], listsRev: Dict[int, str],
                  codeRev: Dict[int, str]) -> Tuple[str, str]:
        i, v = item
        if i == 'word':
            return i, wordsRev[v]
        if i == 'list':
            return i, listsRev[v]
        if i == 'rule':
            return i, rulesRev[v]
        if i in ('start', 'end'):
            return i, codeRev[v]
        raise ValueError('invalid item in nicenItem: %s' % i)


def packGrammar(parseObj: GramParser) -> bytes:
    """
    This function takes a GramParser class which contains the parse of a grammar
    and returns a "string" object which contains the binary representation of
    that grammar.

    The binary form is standard SAPI which consists a header followed by five
    "chunks".  The first four chunks are all in the same format and are lists
    of the names and number of the exported rules, imported rules, lists and
    words respectively.

    The fifth chunk contains the details of the elements which make up each
    defined rule.
    """
    # header:
    #   DWORD dwType  = 0
    #   DWORD dwFlags = 0
    output = [pack("LL", 0, 0)]

    # various chunks
    if parseObj.exportRules:
        output.append(packGrammarChunk(4, parseObj.exportRules))
    if parseObj.importRules:
        output.append(packGrammarChunk(5, parseObj.importRules))
    if parseObj.knownLists:
        output.append(packGrammarChunk(6, parseObj.knownLists))
    if parseObj.knownWords:
        output.append(packGrammarChunk(2, parseObj.knownWords))
    if parseObj.ruleDefines:
        output.append(packGrammarRules(3, parseObj.knownRules, parseObj.ruleDefines))
    return b"".join(output)


def packGrammarChunk(chunktype: int, chunkdict: Dict) -> bytes:
    output: List[bytes] = []
    totalLen = 0

    for word, value in chunkdict.items():
        if isinstance(word, str):
            word = word.encode(preferredencoding)
        # if type(value) == str: value = value.encode()
        # chunk data entry
        #   DWORD dwSize = number of bytes in entry
        #   DWORD dwNum  = ID number for this rule/word
        #   DWORD szName = name of rule/word, zero-term'd and padded to dword
        paddedLen = (len(word) + 4) & 0xFFFC
        output.append(pack("LL%ds" % paddedLen, paddedLen + 8, value, word))
        totalLen = totalLen + paddedLen + 8

    # chunk header
    #   DWORD dwChunkID = type
    #   DWORD dwChunkSize = number of bytes in chunk not including this header
    output.insert(0, pack("LL", chunktype, totalLen))
    return b"".join(output)


def packGrammarRules(chunktype: int, names: Dict[str, int], chunkdict: Dict[str, Definition]) -> bytes:
    output: List[bytes] = []
    totalLen = 0
    elemType = {'start': 1, 'end': 2, 'word': 3, 'rule': 4, 'list': 6}

    for word, _ in chunkdict.items():
        ruleDef: List[bytes] = []
        ruleLen = 0

        for element in chunkdict[word]:
            # repeated element:
            #   WORD wType    = element type
            #   WORD wProb    = 0
            #   DWORD dwValue = element value
            ruleDef.append(pack("HHL", elemType[element[0]], 0, element[1]))
            ruleLen = ruleLen + 8

        # rule definition:
        #   DWORD dwSize = number of bytes in rule definition
        #   DWORD dwnum  = ID number of rule
        output.append(pack("LL", ruleLen + 8, names[word]))
        output.append(b"".join(ruleDef))
        totalLen = totalLen + ruleLen + 8

    # chunk header:
    #   DWORD dwChunkID = type
    #   DWORD dwChunkSize = number of bytes in chunk not including this header
    output.insert(0, pack("LL", chunktype, totalLen))
    return b"".join(output)


#
# This is a routine which was included for testing but can also be used to 
# compile grammar files.  It takes an input file name containing a grammar 
# and an output file name to write the binary into.
#

# def parseGrammarAndSave(inName, outName):
#     inFile = open(inName, 'r')
#     parseObj = GramParser()
#     parseObj.doParse(inFile.readlines())
#     inFile.close()
#     binary = packGrammar(parseObj)
#     outFile = open(outName, 'wb')
#     outFile.write(binary)
#     outFile.write("hello")
#     outFile.close()


def isCharOrDigit(ch: str) -> bool:
    """test if ch is letter or digit or - or _
    
    this is for the gramparser, which can contain words for the recogniser
    
    """
    return ch.isalpha() or ch.isdigit()


def isValidListOrRulename(word: str) -> bool:
    """test if there are no accented characters in a listname or rulename
    
    so asciiletters, digitis, - and _ are allowed
    """
    return bool(reValidName.match(word))


YieldType = TypeVar('YieldType')
SendType = TypeVar('SendType')
ReturnType = TypeVar('ReturnType')


class GeneratorWithReturnValue(Generic[YieldType, SendType, ReturnType]):

    def __init__(self, gen: Generator[YieldType, SendType, ReturnType]):
        self.gen = gen
        self._value: ReturnType

    def __iter__(self) -> Generator[YieldType, SendType, ReturnType]:
        self._value = yield from self.gen
        return self._value

    @property
    def value(self) -> ReturnType:
        return self._value


#
# This utility routine will split apart strings at linefeeds in a list of
# strings.  For example:
#
#   [ "This is line one\nThis is line two", "This is line three" ]
#
# Becomes:
#
#   [ "This is line one", "This is line two", "This is line three" ]
#
# newly written, Quintijn Hoogenboom, february 2020:
#
def splitApartLines(lines: Union[str, Iterable[str]]) -> List[str]:
    """split apart the lines of a grammar and clean up unwanted spacing
    
    all lines are rstripped (in _splitApartLinesSpacing)
    the left spacing is analysed: of each list item, if present,
    the first line is ignored, because of triple quotes strings, which can indent following lines.
    """

    gen = GeneratorWithReturnValue(_splitApartLinesSpacing(lines))
    myList = list(gen)
    leftStrip = gen.value

    # ignore empty lines at end:
    while not myList[-1]:
        myList.pop()

    if not leftStrip:
        return myList
    myLList: List[str] = []
    leftStringStr = ' ' * leftStrip
    for line in myList:
        if line.startswith(leftStringStr):
            myLList.append(line[leftStrip:])
        else:
            myLList.append(line)
    return myLList


def _splitApartLinesSpacing(lines: Union[Iterable[str], str]) -> Generator[str, None, int]:
    """yield line by line, last item is minimum left spacing of lines
    
    each yielded line is rstripped, and the number of left spaced is recorded.
    If the first line is empty lines (or only whitespace) is is not yielded
    The mimimum value is yielded as last item
    """
    minSpacing = 99
    firstLine = True
    if isinstance(lines, str):
        for line in _splitApartStr(lines):
            lSpaces = len(line) - len(line.strip())
            if firstLine:
                if lSpaces:
                    minSpacing = min(minSpacing, lSpaces)
                firstLine = False
                # first line empty or whitespace, ignore:
                if line.strip():
                    yield line
            else:
                if line.strip():
                    # empty lines inside and at end ignore for minSpacing, but yield
                    minSpacing = min(minSpacing, lSpaces)
                yield line
    else:
        for part in lines:
            if not isinstance(part, str):
                raise ValueError(
                    "_splitApartLinesSpacing, item of list should be str, not %s\n(%s)" % (type(part), part))
            firstLine = True
            for line in _splitApartStr(part):
                lSpaces = len(line) - len(line.strip())
                if firstLine:
                    if lSpaces:
                        minSpacing = min(minSpacing, lSpaces)
                    firstLine = False
                else:
                    minSpacing = min(minSpacing, lSpaces)
                yield line
    return minSpacing or 0


def _splitApartStr(lines: str) -> Iterator[str]:
    """yield the lines of a str of input, rstrip each lines
    """
    assert isinstance(lines, str)
    for line in lines.split('\n'):
        yield line.rstrip()
