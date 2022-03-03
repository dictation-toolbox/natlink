
#pylint:disable= C0114, C0116
import os
import configparser
# import pytest
from natlink.readwritefile import ReadWriteFile

thisFile = __file__
thisDir, Filename = os.path.split(thisFile)
testDir = os.path.join(thisDir, 'readwritefiletest')


def test_read_file():
    for F in os.listdir(testDir):
        if F.endswith('.ini'):
            F_path = os.path.join(testDir, F)
            rwfile = ReadWriteFile()
            text = rwfile.readAnything(F_path)
            print(f'F: "{F}", encoding: {rwfile.encoding}, bom: {rwfile.bom}')
            print(f'len text: {len(text)}')
            print('-'*80)
            if rwfile.bom:
                print(f'{rwfile.bom}')
                print(f'{rwfile.rawText}')

def test_read_write_file():
    listdir, join, splitext = os.listdir, os.path.join, os.path.splitext
    for F in listdir(testDir):
        if F.endswith('.ini'):
            F_path = join(testDir, F)
            rwfile = ReadWriteFile()
            text = rwfile.readAnything(F_path)
            print(f'F: "{F}", encoding: {rwfile.encoding}, bom: {rwfile.bom}')
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
    test_read_file()
    test_read_write_file()
    test_read_config_file()
    