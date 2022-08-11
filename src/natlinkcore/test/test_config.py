#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

import pathlib as p
import sys
import sysconfig
from pprint import pprint
import pytest

import importlib.util as u

from natlinkcore.config import *
from natlinkcore import loader
def sample_config(sample_name) -> 'NatlinkConfig':
    """
    load a config file from the config files subfolder
    """
    sample_ini=p.WindowsPath(os.path.dirname(__file__)) / "config_files" / sample_name
    config = NatlinkConfig.from_file(sample_ini)
    return config
#easier than using the decorator syntax
def make_sample_config_fixture(settings_filename):
    return pytest.fixture(lambda : sample_config(settings_filename))

@pytest.fixture()
def empty_config():
    config = NatlinkConfig.get_default_config()
    return config


def test_empty_config():
    """does not test really
    """
    print(f'empty_config: {empty_config}')



settings1 =  make_sample_config_fixture("settings_1.ini")
settings2 = make_sample_config_fixture("settings_2.ini")
packages_samples = make_sample_config_fixture('package_samples.ini') 
package_load_test1 = make_sample_config_fixture('package_load_test1.ini')

@pytest.fixture()
def mock_syspath(monkeypatch):
    """Add a tempory path to mock modules in sys.pythonpath"""
    mock_folder=p.WindowsPath(os.path.dirname(__file__)) / "mock_packages"
    print(f"Mock Folder {mock_folder}")
    monkeypatch.syspath_prepend(str(mock_folder))

@pytest.fixture()
def mock_userdir(monkeypatch):
    mock_folder=p.WindowsPath(os.path.dirname(__file__)) / "mock_userdir"
    print(f"Mock Userdir Folder {mock_folder}")
    monkeypatch.setenv("natlink_userdir",str(mock_folder))


def test_settings_1(mock_syspath,settings1):
    test_cfg = settings1 
    #make sure we are actually getting a NatlinkConfig by checking a method
    assert hasattr(test_cfg,"directories_for_user")

    #made_up=fake_package1
    #made_up_2 = c:\
    #made_up_3 = nonexistant   #this one should be discarded so there should be 2 directories on load.

    def filt(s,sub):
        return s.find(sub) >=0

    filt1=lambda s : filt(s, "fake_package1")
    filt2=lambda s : filt(s, "C:\\")
    filt3 = lambda s:  filt(s,"nonexistant")   #gets loaded anyway even though doesnt exist.

    assert test_cfg.filter

    test_cfg.directiories_by_user.filter(filt1) >0
    test_cfg.directiories_by_user.filter(filt2) >0
    test_cfg.directiories_by_user.filter(filt3) >0 

        
    assert test_cfg.log_level is LogLevel.DEBUG 
    assert test_cfg.load_on_mic_on is False
    assert test_cfg.load_on_begin_utterance is False
    assert test_cfg.load_on_startup is True
    assert test_cfg.load_on_user_changed is True
 
def test_settings_2(mock_syspath,settings2):
    test_cfg = settings2 
    #make sure we are actually getting a NatlinkConfig by checking a method
    assert hasattr(test_cfg,"directories_for_user")

      
    assert test_cfg.log_level == LogLevel.WARNING 
    assert test_cfg.load_on_mic_on is True
    assert test_cfg.load_on_begin_utterance is True
    assert test_cfg.load_on_startup is False
    assert test_cfg.load_on_user_changed is False




def test_expand_path(mock_syspath,mock_userdir):
    """test the different expand_path possibilities, including finding a directory along   sys.path 
    since we know users might pip a package to  a few different spots depending on whether they are in an elevated shell.
    We specifically aren't testing unimacro and vocola2 since they might be in the sys.path or maybe not""" 


    #use only directories that we know will be available when running the test.
    #we put a few packages in mock_packages subfolder and we know pytest must  be installed to be running this test.


    result=expand_path('fake_package1')
    assert os.path.isdir(result)

    result=expand_path('pytest')
    assert os.path.isdir(result)
    

    # assume UnimacroGrammars is a valid directory:
    result = expand_path('natlink_userdir/FakeGrammars')
    assert os.path.isdir(result)
    
    # invalid directory
    result = expand_path('natlink_userdir/invalid_dir')
    assert not os.path.isdir(result)

def test_config_locations():
    """tests the lists of possible config_locations and of valid_locations
    """
    locations = loader.config_locations()
    # if this fails, probably the DefaultConfig/natlink.ini is not found, or 
    assert len(locations) == 2
    config_locations = loader.config_locations()
    assert len(config_locations) > 0
    assert os.path.isfile(config_locations[0])
 
def test_mocks_actually_work(mock_syspath):
    pass
    spec = u.find_spec('fake_package1')
    assert not spec is None
    print(f'\nspec for fake_package1 {spec}')









if __name__ == "__main__":
    sysconfig._main()
    print("This is your Python system path sys.path:")
    print("-----------------------------------------")
    pprint(sys.path)

    pytest.main(['test_config.py'])
