
#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

import pytest

from natlink.config import *
from natlink import loader

@pytest.fixture()
def empty_config():
    config = NatlinkConfig.get_default_config()
    return config

def test_empty_config():
    """does not test really
    """
    print(f'empty_config: {empty_config}')

def test_config_locations():
    """tests the lists of possible config_locations and of valid_locations
    """
    locations = loader.config_locations()
    assert len(locations) == 2
    valid_locations = loader.valid_config_locations()
    assert len(valid_locations) > 0
    assert os.path.isfile(valid_locations[0])


if __name__ == "__main__":
    pytest.main(['test_config.py'])
