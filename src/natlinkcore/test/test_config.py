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


def test_settings_1(settings1,mock_syspath):
    test_cfg = settings1 
    #make sure we are actually getting a NatlinkConfig by checking a method
    assert hasattr(test_cfg,"directories_for_user")
        
    assert test_cfg.log_level is LogLevel.DEBUG 
    assert test_cfg.load_on_mic_on is False
    assert test_cfg.load_on_begin_utterance is False
    assert test_cfg.load_on_startup is True
    assert test_cfg.load_on_user_changed is True
 
def test_settings_2(settings2,mock_syspath):
    test_cfg = settings2 
    #make sure we are actually getting a NatlinkConfig by checking a method
    assert hasattr(test_cfg,"directories_for_user")

      
    assert test_cfg.log_level == LogLevel.WARNING 
    assert test_cfg.load_on_mic_on is True
    assert test_cfg.load_on_begin_utterance is True
    assert test_cfg.load_on_startup is False
    assert test_cfg.load_on_user_changed is False


def test_read_directories(packages_samples):
    """

    """
    test_cfg=packages_samples
    expected_e=["fake_package1"]
    d=test_cfg.disabled_packages
    expected_d=["unimacro","fake_package2","fake_package3"]
    assert e == expected_e
    assert d == expected_d

# def test_read_directories(directory_settings):
#     test_cfg = directory_settings
#     dirs = test_cfg.directories
#     expected_dirs = ["unimacro","fake_module2","fake_module3"]
#     
#     assert dirs  == expected_dirs

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

def test_packages_added_to_paths(mock_syspath,package_load_test1):
        mock_package_folder=p.WindowsPath(os.path.dirname(__file__)) / "mock_packages"
        print(f"System Path {sys.path}")
        test_cfg=package_load_test1
        print(f'test config {test_cfg}')       
        #there should be exactly 4 directories for
        #the '' key (all languages)
        #two for the [packages\ and two for
        #[directories]
        dirs = test_cfg.directories_by_user['']
        print(f"directories for '': {dirs}" )
        assert len(dirs) == 4
        for mp in ['fake_package2','fake_package1']:
            ms=str(p.Path(u.find_spec(mp).origin).parent)
            assert ms in dirs







if __name__ == "__main__":
    sysconfig._main()
    print("This is your Python system path sys.path:")
    print("-----------------------------------------")
    pprint(sys.path)

    pytest.main(['test_config.py'])
