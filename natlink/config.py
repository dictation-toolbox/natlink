import configparser
import logging
from collections import OrderedDict
from enum import IntEnum
from typing import List, Iterable, Dict

import natlink


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

    def __repr__(self) -> str:
        return f'NatlinkConfig(directories_by_user={self.directories_by_user}, log_level={self.log_level}, ' \
               f'load_on_mic_on={self.load_on_mic_on}, load_on_startup={self.load_on_startup}, ' \
               f'load_on_user_changed={self.load_on_user_changed}'

    @staticmethod
    def get_default_config() -> 'NatlinkConfig':
        return NatlinkConfig(directories_by_user=OrderedDict(),
                             log_level=LogLevel.NOTSET,
                             load_on_mic_on=True,
                             load_on_begin_utterance=False,
                             load_on_startup=True,
                             load_on_user_changed=True)

    @property
    def directories(self) -> List[str]:
        dirs: List[str] = []
        for u, directories in self.directories_by_user.items():
            dirs.extend(directories)
        return dirs

    def directories_for_user(self, user: str) -> List[str]:
        dirs: List[str] = []
        for u, directories in self.directories_by_user.items():
            if u in ['', user]:
                dirs.extend(directories)
        return dirs

    @staticmethod
    def from_config_parser(config: configparser.ConfigParser) -> 'NatlinkConfig':
        ret = NatlinkConfig.get_default_config()

        sections = config.sections()
        for section in sections:
            if section.endswith('-directories'):
                user = section[:-len('-directories')]
                ret.directories_by_user[user] = list(config[section].values())
            elif section == 'directories':
                ret.directories_by_user[''] = list(config[section].values())
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
        config = configparser.ConfigParser()
        for fn in files:
            if config.read(fn):
                return cls.from_config_parser(config)
        raise NoGoodConfigFoundException(f'No good config found, did you define your ~/.natlink?')
