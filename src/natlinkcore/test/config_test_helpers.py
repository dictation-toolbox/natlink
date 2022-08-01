import pytest

from natlinkcore.config import *
from natlinkcore import loader
import pathlib as p

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

print(f"loading {__file__}")