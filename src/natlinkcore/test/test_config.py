#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

from inspect import getattr_static
from random import sample
import pytest

from natlinkcore.config import *
from natlinkcore import loader
import pathlib as p


@pytest.fixture()
def empty_config():
    config = NatlinkConfig.get_default_config()
    return config



def test_empty_config():
    """does not test really
    """
    print(f'empty_config: {empty_config}')

def sample_config(sample_name) -> 'NatlinkConfig':
    """
    load a config file from the config files subfolder
    """
    sample_ini=p.WindowsPath(os.path.dirname(__file__)) / "config_files" / sample_name
    config = NatlinkConfig.from_file(sample_ini)
    return config


#use lambda instead of def and fixture decorators, since we have a bunch of fixtures that are similar

settings1 = pytest.fixture( lambda : sample_config("settings_1.ini"))



def test_settings_1(settings1):
        test_cfg = settings1 
        #make sure we are actually getting a NatlinkConfig by checking a method
        assert hasattr(test_cfg,"directories_for_user")
        
        assert test_cfg.log_level == 0 
        assert test_cfg.load_on_mic_on == 0
        assert test_cfg.load_on_begin_utterance == 0
        assert test_cfg.load_on_startup == 0
        assert test_cfg.load_on_user_changed == 0
 

def test_config_locations():
    """tests the lists of possible config_locations and of valid_locations
    """
    locations = loader.config_locations()
    # if this fails, probably the DefaultConfig/natlink.ini is not found, or 
    assert len(locations) == 2
    config_locations = loader.config_locations()
    assert len(config_locations) > 0
    assert os.path.isfile(config_locations[0])
 

if __name__ == "__main__":
    pytest.main(['test_config.py'])
