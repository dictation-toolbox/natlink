
#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

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

@pytest.fixture()
def few_settings():
    return sample_config("few_settings.ini")

def test_load_an_ini_file(few_settings):
        test_ini = few_settings
        print(f"{test_ini}")

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
