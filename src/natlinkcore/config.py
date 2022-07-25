#pylint:disable=C0114, C0115, C0116, R0913, E1101
import configparser
import logging
import os
from enum import IntEnum
from typing import List, Iterable, Dict
from natlink import _natlink_core as natlink

class NoGoodConfigFoundException(natlink.NatError):
    pass

class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class NatlinkConfig:
    def __init__(self, directories_by_user: Dict[str, List[str]], log_level: LogLevel, load_on_mic_on: bool,
                 load_on_begin_utterance: bool, load_on_startup: bool, load_on_user_changed: bool):
        self.directories_by_user = directories_by_user  # maps user profile names to directories, '' for global
        self.log_level = log_level
        self.load_on_mic_on = load_on_mic_on
        self.load_on_begin_utterance = load_on_begin_utterance
        self.load_on_startup = load_on_startup
        self.load_on_user_changed = load_on_user_changed
        self.config_path = ''  # to be defined in from_config_parser

    def __repr__(self) -> str:
        return f'NatlinkConfig(directories_by_user={self.directories_by_user}, log_level={self.log_level}, ' \
               f'load_on_mic_on={self.load_on_mic_on}, load_on_startup={self.load_on_startup}, ' \
               f'load_on_user_changed={self.load_on_user_changed}'

    @staticmethod
    def get_default_config() -> 'NatlinkConfig':
        return NatlinkConfig(directories_by_user=dict(),
                             log_level=LogLevel.NOTSET,
                             load_on_mic_on=True,
                             load_on_begin_utterance=False,
                             load_on_startup=True,
                             load_on_user_changed=True)

    @property
    def directories(self) -> List[str]:
        dirs: List[str] = []
        for _u, directories in self.directories_by_user.items():
            dirs.extend(directories)
        return dirs

    def directories_for_user(self, user: str) -> List[str]:
        dirs: List[str] = []
        for u, directories in self.directories_by_user.items():
            if u in ['', user]:
                dirs.extend(directories)
        return dirs

    @staticmethod
    def from_config_parser(config: configparser.ConfigParser, config_path: str) -> 'NatlinkConfig':
        ret = NatlinkConfig.get_default_config()
        ret.config_path = config_path
        sections = config.sections()
        for section in sections:
            if section.endswith('-directories'):
                user = section[:-len('-directories')]
                ret.directories_by_user[user] = list(config[section].values())
            elif section == 'directories':
                directories = []
                for name, directory in config[section].items():
                    ## allow environment variables (or ~) in directory
                    directory_expanded = expand_path(directory)
                    if not os.path.isdir(directory_expanded):
                        if directory_expanded == directory:
                            print(f'from_config_parser: skip "{directory}" ("{name}"): is not a valid directory')
                        else:
                            print(f'from_config_parser: skip "{directory}" ("{name}"):\n\texpanded to directory "{directory_expanded}" is not a valid directory')
                        continue
                    directories.append(directory_expanded)

                ret.directories_by_user[''] = directories
        if config.has_section('settings'):
            settings = config['settings']
            level = settings.get('log_level')
            if level is not None:
                ret.log_level = LogLevel[level.upper()]
            ret.load_on_mic_on = settings.getboolean('load_on_mic_on', fallback=ret.load_on_mic_on)
            ret.load_on_begin_utterance = settings.getboolean('load_on_begin_utterance',
                                                              fallback=ret.load_on_begin_utterance)
            ret.load_on_startup = settings.getboolean('load_on_startup', fallback=ret.load_on_startup)
            ret.load_on_user_changed = settings.getboolean('load_on_user_changed', fallback=ret.load_on_user_changed)

        return ret

    @classmethod
    def from_file(cls, fn: str) -> 'NatlinkConfig':
        return cls.from_first_found_file([fn])

    @classmethod
    def from_first_found_file(cls, files: Iterable[str]) -> 'NatlinkConfig':
        isfile = os.path.isfile
        config = configparser.ConfigParser()
        for fn in files:
            if not isfile(fn):
                continue
            if config.read(fn):
                return cls.from_config_parser(config, config_path=fn)
        # should not happen, because of DefaultConfig (was InstallTest)
        raise NoGoodConfigFoundException('No natlink config file found, please run configure natlink program\n\t(***configurenatlink***)')

def expand_path(input_path: str) -> str:
    r"""expand path if it starts with "~" or has environment variables (%XXXX%)
    
    Use home ("~") or "%natlink_userdir%"
    
    The Documents directory can be found by "~\Documents" 
    
    When nothing to expand, return input
    """
    expanduser, expandvars, normpath = os.path.expanduser, os.path.expandvars, os.path.normpath
    
    if input_path.startswith('~'):
        home = expanduser('~')
        env_expanded = home + input_path[1:]
        # print(f'expand_path: "{input_path}" include "~": expanded: "{env_expanded}"')
        return normpath(env_expanded)
    env_expanded = expandvars(input_path)
    # print(f'env_expanded: "{env_expanded}", from envvar: "{input_path}"')
    return normpath(env_expanded)


    
