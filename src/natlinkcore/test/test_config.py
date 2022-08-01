#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

from inspect import getattr_static
from random import sample
import pytest

from natlinkcore.config import *
from natlinkcore import loader

import pathlib as p
import sys
import sysconfig
from pprint import pprint

import importlib.util as u

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

def test_settings_1(settings1):
        test_cfg = settings1 
        #make sure we are actually getting a NatlinkConfig by checking a method
        assert hasattr(test_cfg,"directories_for_user")
        
        assert test_cfg.log_level == LogLevel.DEBUG 
        assert test_cfg.load_on_mic_on == False
        assert test_cfg.load_on_begin_utterance == False
        assert test_cfg.load_on_startup == True
        assert test_cfg.load_on_user_changed == True
 
def test_settings_2(settings2):
        test_cfg = settings2 
        #make sure we are actually getting a NatlinkConfig by checking a method
        assert hasattr(test_cfg,"directories_for_user")

        #make sure these required modules lists exist
        assert hasattr(test_cfg,"enabled_packages")
        assert hasattr(test_cfg,"disabled_packages")
        
        assert test_cfg.log_level == LogLevel.WARNING 
        assert test_cfg.load_on_mic_on == True
        assert test_cfg.load_on_begin_utterance == True
        assert test_cfg.load_on_startup == False
        assert test_cfg.load_on_user_changed == False

def test_read_packages(packages_samples):
    test_cfg=packages_samples
    e=test_cfg.enabled_packages
    expected_e=["vocola2","fake_package1"]
    d=test_cfg.disabled_packages
    expected_d=["unimacro","fake_package2","fake_package3"]
    assert(e==expected_e)
    assert(d==expected_d)

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
    spec = u.find_spec('fake_package1, sys.path is {sys.path}')
    print(f'spec for fake_package1')
    assert  not spec is None

def test_packages_added_to_paths(package_load_test1,mock_syspath):
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
            ms=p.Path(u.find_spec(mp).origin).parent
            assert ms in dirs







if __name__ == "__main__":
    sysconfig._main()
    print("This is your Python system path sys.path:")
    print("-----------------------------------------")
    pprint(sys.path)

    pytest.main(['test_config.py'])
