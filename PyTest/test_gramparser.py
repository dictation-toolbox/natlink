import pytest

from natlink.gramparser import GramParser, packGrammar, GrammarSyntaxError, splitApartLines


def test_packGrammar():
    gramSpec = ['<rule> exported = action;']
    parser = GramParser(gramSpec)
    parser.doParse()
    parser.checkForErrors()
    assert parser.knownRules == {'rule': 1}
    assert parser.knownWords == {'action': 1}
    assert parser.exportRules == {'rule': 1}
    assert parser.ruleDefines == {'rule': [('word', 1)]}

    assert packGrammar(parser) == b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00' \
                                  b'\x01\x00\x00\x00rule\x00\x00\x00\x00\x02\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00' \
                                  b'\x00\x01\x00\x00\x00action\x00\x00\x03\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00' \
                                  b'\x00\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00'


def test_packGrammar_with_list():
    gramSpec = ['<ruleList> exported = action {List};']
    parser = GramParser(gramSpec)
    parser.doParse()
    parser.checkForErrors()
    assert parser.knownRules == {'ruleList': 1}
    assert parser.knownLists == {'List': 1}
    assert parser.knownWords == {'action': 1}
    assert parser.exportRules == {'ruleList': 1}
    assert parser.ruleDefines == {'ruleList': [('start', 1), ('word', 1), ('list', 1), ('end', 1)]}

    assert packGrammar(parser) == b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x14\x00\x00\x00\x14\x00\x00\x00' \
                                  b'\x01\x00\x00\x00ruleList\x00\x00\x00\x00\x06\x00\x00\x00\x10\x00\x00\x00\x10\x00' \
                                  b'\x00\x00\x01\x00\x00\x00List\x00\x00\x00\x00\x02\x00\x00\x00\x10\x00\x00\x00\x10' \
                                  b'\x00\x00\x00\x01\x00\x00\x00action\x00\x00\x03\x00\x00\x00(\x00\x00\x00(\x00\x00' \
                                  b'\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00' \
                                  b'\x00\x06\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'


def test_packGrammar_with_two_lines():
    gramSpec = ['<rule1> exported = action one;', '<rule2> exported = action two;']
    parser = GramParser(gramSpec)
    parser.doParse()
    parser.checkForErrors()
    assert parser.knownRules == {'rule1': 1, 'rule2': 2}
    assert parser.knownWords == {'action': 1, 'one': 2, 'two': 3}
    assert parser.exportRules == {'rule1': 1, 'rule2': 2}
    assert parser.ruleDefines == {'rule1': [('start', 1), ('word', 1), ('word', 2), ('end', 1)],
                                  'rule2': [('start', 1), ('word', 1), ('word', 3), ('end', 1)]}

    assert packGrammar(parser) == b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00 \x00\x00\x00\x10\x00\x00\x00\x01' \
                                  b'\x00\x00\x00rule1\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x00rule2\x00\x00\x00' \
                                  b'\x02\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00action\x00\x00\x0c' \
                                  b'\x00\x00\x00\x02\x00\x00\x00one\x00\x0c\x00\x00\x00\x03\x00\x00\x00two\x00\x03' \
                                  b'\x00\x00\x00P\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00' \
                                  b'\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x02\x00' \
                                  b'\x00\x00\x01\x00\x00\x00(\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00' \
                                  b'\x00\x03\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00' \
                                  b'\x00\x01\x00\x00\x00'


def test_recognition_mimic_grammar():
    gramSpec = '''
    <runone> exported = mimic runone;
    <runtwo> exported = mimic two {colors};
    <runthree> exported = mimic three <extraword>;
    <runfour> exported = mimic four <extrawords>;
    <runfive> exported = mimic five <extralist>;
    <runsix> exported = mimic six {colors}+;
    <runseven> exported = mimic seven <wordsalternatives>;
    <runeight> exported = mimic eight <wordsalternatives> [<wordsalternatives>+];
    <optional>  = very | small | big;
    <extralist> = {furniture};
    <extraword> = painting ;
    <extrawords> = modern painting ;
    <wordsalternatives> = house | tent | church | tower;
    '''
    parser = GramParser(gramSpec)
    parser.doParse()
    parser.checkForErrors()
    assert parser.knownRules == {'extralist': 8, 'extraword': 4, 'extrawords': 6, 'optional': 13, 'runeight': 12,
                                 'runfive': 7, 'runfour': 5, 'runone': 1, 'runseven': 10, 'runsix': 9, 'runthree': 3,
                                 'runtwo': 2, 'wordsalternatives': 11}
    assert parser.knownLists == {'colors': 1, 'furniture': 2}
    assert parser.knownWords == {'big': 12, 'church': 17, 'eight': 9, 'five': 6, 'four': 5, 'house': 15, 'mimic': 1,
                                 'modern': 14, 'painting': 13, 'runone': 2, 'seven': 8, 'six': 7, 'small': 11,
                                 'tent': 16, 'three': 4, 'tower': 18, 'two': 3, 'very': 10}
    assert parser.exportRules == {'runeight': 12, 'runfive': 7, 'runfour': 5, 'runone': 1, 'runseven': 10, 'runsix': 9,
                                  'runthree': 3, 'runtwo': 2}
    assert parser.ruleDefines == {'extralist': [('list', 2)],
                                  'extraword': [('word', 13)],
                                  'extrawords': [('start', 1), ('word', 14), ('word', 13), ('end', 1)],
                                  'optional': [('start', 2), ('word', 10), ('word', 11), ('word', 12), ('end', 2)],
                                  'runeight': [('start', 1), ('word', 1), ('word', 9), ('rule', 11), ('start', 4),
                                               ('start', 3), ('rule', 11), ('end', 3), ('end', 4), ('end', 1)],
                                  'runfive': [('start', 1), ('word', 1), ('word', 6), ('rule', 8), ('end', 1)],
                                  'runfour': [('start', 1), ('word', 1), ('word', 5), ('rule', 6), ('end', 1)],
                                  'runone': [('start', 1), ('word', 1), ('word', 2), ('end', 1)],
                                  'runseven': [('start', 1), ('word', 1), ('word', 8), ('rule', 11), ('end', 1)],
                                  'runsix': [('start', 1), ('word', 1), ('word', 7), ('start', 3), ('list', 1),
                                             ('end', 3), ('end', 1)],
                                  'runthree': [('start', 1), ('word', 1), ('word', 4), ('rule', 4), ('end', 1)],
                                  'runtwo': [('start', 1), ('word', 1), ('word', 3), ('list', 1), ('end', 1)],
                                  'wordsalternatives': [('start', 2), ('word', 15), ('word', 16), ('word', 17),
                                                        ('word', 18), ('end', 2)]}


def test_parse_error():
    gramSpec = "badvalue;"
    parser = GramParser(gramSpec)
    with pytest.raises(GrammarSyntaxError):
        parser.doParse()


def test_splitApartLines():
    actual = splitApartLines(["This is line one\nThis is line two", "This is line three"])
    expected = ["This is line one", "This is line two", "This is line three"]
    assert actual == expected


def test_splitApartLines_the_first_line_is_ignored():
    actual = splitApartLines("\n     <start> exported = d\xe9mo sample one; \n")
    expected = ['<start> exported = démo sample one;']
    assert actual == expected


def test_splitApartLines_first_line_does_not_influence_stripping_of_others():
    actual = splitApartLines(["This is line one\n This is line two, one space", "  This is line three, one more space"])
    expected = ['This is line one', 'This is line two, one space', ' This is line three, one more space']
    assert actual == expected


def test_splitApartLines_first_line_does_influence_if_it_starts_with_space():
    actual = splitApartLines([" This is line one, one space\n  This is line two, two spaces"])
    expected = ['This is line one, one space', ' This is line two, two spaces']
    assert actual == expected


def test_splitApartLines_complex_indentation():
    actual = splitApartLines(["Initial line\n    This is line two indented\n        This is line three extra indented",
                              "Second string no indent\n    But second line indented four"])
    expected = ['Initial line', 'This is line two indented', '    This is line three extra indented',
                'Second string no indent', 'But second line indented four']
    assert actual == expected
