
#pylint:disable= C0114, C0116, R1732
import os
import configparser
import pytest
from natlinkcore.readwritefile import ReadWriteFile

thisFile = __file__
thisDir, Filename = os.path.split(thisFile)
testDir = os.path.join(thisDir, 'readwritefiletest')


def setup_module(module):
    pass

def teardown_module(module):
    for F in os.listdir(testDir):
        if F.startswith('output-'):
            F_path = os.path.join(testDir, F)
            os.remove(F_path)

def test_only_write_file():
    join, isfile = os.path.join, os.path.isfile
    newFile = join(testDir, 'output-newfile.txt')
    if isfile(newFile):
        os.unlink(newFile)
    rwfile = ReadWriteFile()
    text = ''
    rwfile.writeAnything(newFile, text)
    assert open(newFile, 'rb').read() == b''
 
    # read back empty file:
    rwfile = ReadWriteFile()
    text = rwfile.readAnything(newFile)
    assert rwfile.encoding == 'ascii'
    assert rwfile.bom == ''
    assert text == ''
    
def test_accented_characters_write_file():
    join, isfile = os.path.join, os.path.isfile
    newFile = join(testDir, 'output-accented.txt')
    if isfile(newFile):
        os.unlink(newFile)
    text = 'caf\xe9'
    rwfile = ReadWriteFile(encodings=['ascii'])  # optional encoding
    # this is with default errors='xmlcharrefreplace':
    rwfile.writeAnything(newFile, text)
    testTextBinary = open(newFile, 'rb').read()
    wanted = b'caf&#233;'
    assert testTextBinary == wanted
    # same, default is 'xmlcharrefreplace':
    rwfile.writeAnything(newFile, text, errors='xmlcharrefreplace')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf&#233;'
    assert len(testTextBinary) == 9

    text_back = rwfile.readAnything(newFile)
    assert text_back == 'caf&#233;'
    
    rwfile.writeAnything(newFile, text, errors='replace')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf?'
    assert len(testTextBinary) == 4
    rwfile.writeAnything(newFile, text, errors='ignore')
    testTextBinary = open(newFile, 'rb').read()
    assert testTextBinary == b'caf'
    assert len(testTextBinary) == 3
    
    rwfile_utf = ReadWriteFile(encodings=['utf-8'])
    text = 'Caf\xe9'
    rwfile_utf.writeAnything(newFile, text)
    text_back = rwfile_utf.readAnything(newFile)
    assert text == text_back

def test_other_encodings_write_file():
    join = os.path.join
    oldFile = join(testDir, 'latin1 accented.txt')
    rwfile = ReadWriteFile(encodings=['latin1'])  # optional encoding
    text = rwfile.readAnything(oldFile)
    assert text == 'latin1 café'
    
    
    


def test_latin1_cp1252_write_file():
    join = os.path.join
    _newFile = join(testDir, 'latin1.txt')
    _newFile = join(testDir, 'cp1252.txt')
    # TODO (QH) to be done, these encodings do not take all characters,
    # and need special attention.
    # (as long as the "fallback" is utf-8, all write files should go well!)

def test_read_write_file():
    listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    for F in listdir(testDir):
        if not F.startswith('output-'):
            Fout = 'output-' + F
            F_path = join(testDir, F)
            rwfile = ReadWriteFile()
            text = rwfile.readAnything(F_path)
            trunk, _ext = splitext(F)
            Fout = trunk + ".txt"
            Fout_path = join(testDir, Fout)
            rwfile.writeAnything(Fout_path, text)
            assert open(F_path, 'rb').read() == open(Fout_path, 'rb').read()
            
def test_read_config_file():
    listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    for F in listdir(testDir):
        if F.endswith('.ini'):
            if F == 'acoustics.ini':
                F_path = join(testDir, F)
                rwfile = ReadWriteFile()
                config_text = rwfile.readAnything(F_path)
                Config = configparser.ConfigParser()
                Config.read_string(config_text)
                assert Config.get('Acoustics', '2 2') == '2_2' 
                continue

            if F in ['natlink.ini', 'natlinkconfigured.ini']:
                F_path = join(testDir, F)
                rwfile = ReadWriteFile()
                config_text = rwfile.readAnything(F_path)
                Config = configparser.ConfigParser()
                Config.read_string(config_text)
                debug_level = Config.get('settings', 'log_level')
                assert debug_level == 'DEBUG'
                Config.set('settings', 'log_level', 'INFO')
                new_debug_level = Config.get('settings', 'log_level')
                assert new_debug_level == 'INFO'
                trunk, ext = splitext(F)
                Fout = trunk + 'out' + ext
                Fout_path = join(testDir, Fout)
                Config.write(open(Fout_path, 'w', encoding=rwfile.encoding))

if __name__ == "__main__":
    pytest.main(['test_readwritefile.py'])
    