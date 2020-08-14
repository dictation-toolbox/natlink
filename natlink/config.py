import configparser
import logging
from enum import IntEnum
from typing import List, Iterable

import natlink


class NoGoodConfigFoundException(natlink.NatError):
    pass


class LogLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARN = logging.WARNING
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class NatlinkConfig:
    def __init__(self, directories: List[str], log_level: LogLevel, load_on_mic_on: bool,
                 load_on_begin_utterance: bool, load_on_startup: bool):
        self.directories = directories
        self.log_level = log_level
        self.load_on_mic_on = load_on_mic_on
        self.load_on_begin_utterance = load_on_begin_utterance
        self.load_on_startup = load_on_startup

    @staticmethod
    def from_config_parser(config: configparser.ConfigParser) -> 'NatlinkConfig':
        directories: List[str] = []
        log_level = LogLevel.NOTSET
        load_on_mic_on = True
        load_on_begin_utterance = False
        load_on_startup = True

        if config.has_section('directories'):
            directories = list(config['directories'].values())
        if config.has_section('settings'):
            settings = config['settings']
            level = settings.get('log_level')
            if level is not None:
                log_level = LogLevel[level.upper()]
            load_on_mic_on = settings.getboolean('load_on_mic_on', fallback=load_on_mic_on)
            load_on_begin_utterance = settings.getboolean('load_on_begin_utterance', fallback=load_on_begin_utterance)
            load_on_startup = settings.getboolean('load_on_startup', fallback=load_on_startup)

        return NatlinkConfig(directories=directories, log_level=log_level, load_on_mic_on=load_on_mic_on,
                             load_on_begin_utterance=load_on_begin_utterance, load_on_startup=load_on_startup)

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
