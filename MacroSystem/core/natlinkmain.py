import configparser
import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
import time
import traceback
import winreg
from enum import IntEnum
from types import ModuleType
from typing import List, Dict, Set, Iterable, Any

import natlink


class NoGoodConfigFoundException(Exception):
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
    def __init__(self, directories: List[str], log_level: LogLevel, load_on_mic_on: bool, load_on_begin: bool):
        self.directories = directories
        self.log_level = log_level
        self.load_on_mic_on = load_on_mic_on
        self.load_on_begin = load_on_begin

    @staticmethod
    def from_config_parser(config: configparser.ConfigParser) -> 'NatlinkConfig':
        directories: List[str] = []
        log_level = LogLevel.NOTSET
        load_on_mic_on = True
        load_on_begin = False

        if config.has_section('directories'):
            directories = list(config['directories'].values())
        if config.has_section('settings'):
            settings = config['settings']
            level = settings.get('log_level')
            if level is not None:
                log_level = LogLevel[level.upper()]
            load_on_mic_on = settings.getboolean('load_on_mic_on', fallback=load_on_mic_on)
            load_on_begin = settings.getboolean('load_on_begin', fallback=load_on_begin)

        return NatlinkConfig(directories=directories, log_level=log_level, load_on_mic_on=load_on_mic_on,
                             load_on_begin=load_on_begin)

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


class NatlinkMain:
    def __init__(self, logger: logging.Logger, config: NatlinkConfig):
        self.logger = logger
        self.config = config
        self.loaded_modules: Dict[str, ModuleType] = {}
        self.bad_modules: Set[str] = set()
        self.load_attempt_times: Dict[str, float] = {}

    @property
    def module_names(self) -> List[str]:
        return self.module_names_in_dirs(self.config.directories)

    @staticmethod
    def module_names_in_dirs(directories: Iterable[str]) -> List[str]:

        def is_script(f: str) -> bool:
            return f.startswith('_') and f.endswith('.py')

        init = '__init__.py'

        mod_names: List[str] = []
        for d in directories:
            scripts = os.listdir(d)
            scripts = sorted(filter(is_script, scripts))
            if init in scripts:
                scripts.remove(init)
                scripts.insert(0, init)
            names = [f[:-len('.py')] for f in scripts]
            mod_names.extend(names)

        return mod_names

    @staticmethod
    def add_dirs_to_path(directories: Iterable[str]) -> None:
        for d in directories:
            if d not in sys.path:
                sys.path.append(d)

    def unload_module(self, module: ModuleType) -> None:
        unload = getattr(module, 'unload', None)
        if unload is not None:
            self.logger.info(f'unloading module: {module.__name__}')
            unload()

    def load_or_reload_modules(self, mod_names: Iterable[str]) -> None:
        for mod_name in mod_names:
            last_attempt_time = self.load_attempt_times.get(mod_name, 0.0)
            self.load_attempt_times[mod_name] = time.time()
            try:
                if mod_name in self.bad_modules:
                    spec = importlib.util.find_spec(mod_name)
                    if spec is None:
                        raise FileNotFoundError(f'Could not find spec for: {mod_name}')
                    loader = spec.loader
                    if loader is None:
                        raise FileNotFoundError(f'Could not find loader for: {mod_name}')
                    elif not isinstance(loader, importlib.machinery.SourceFileLoader):
                        raise ValueError(f'module {mod_name} does not have a SourceFileLoader loader')
                    last_modified_time = loader.path_stats(loader.path)['mtime']
                    if last_attempt_time < last_modified_time:
                        self.logger.info(f'loading previously bad module: {mod_name}')
                        module = importlib.import_module(mod_name)
                        self.bad_modules.remove(mod_name)
                    else:
                        self.logger.info(f'skipping unchanged bad module: {mod_name}')
                        continue
                else:
                    maybe_module = self.loaded_modules.get(mod_name)
                    if maybe_module is None:
                        self.logger.info(f'loading module: {mod_name}')
                        module = importlib.import_module(mod_name)
                    else:
                        module = maybe_module
                        loader = module.__loader__
                        if not isinstance(loader, importlib.machinery.SourceFileLoader):
                            raise ValueError(f'module {mod_name} does not have a SourceFileLoader loader')
                        last_modified_time = loader.path_stats(loader.path)['mtime']
                        if last_attempt_time < last_modified_time:
                            self.unload_module(module)
                            self.logger.info(f'reloading module: {mod_name}')
                            module = importlib.reload(module)
                        else:
                            self.logger.debug(f'skipping unchanged loaded module: {mod_name}')
                            continue
                self.loaded_modules[mod_name] = module
            except Exception:
                self.logger.exception(traceback.format_exc())
                self.bad_modules.add(mod_name)
                if mod_name in self.loaded_modules:
                    del self.loaded_modules[mod_name]

    def on_change_callback(self, change_type: str, args: Any) -> None:
        self.logger.debug(f'on_change_callback called with: change:{change_type}, args:{args}')
        if change_type == 'mic' and args == 'on':
            if self.config.load_on_mic_on:
                self.load_or_reload_modules(self.module_names)

    def on_begin_callback(self, module_info: Any) -> None:
        self.logger.debug(f'on_begin_callback called with: moduleInfo:{module_info}')
        if self.config.load_on_begin:
            self.load_or_reload_modules(self.module_names)

    def start(self) -> None:
        self.logger.info('starting natlinkmain')
        self.add_dirs_to_path(self.config.directories)
        self.load_or_reload_modules(self.module_names)
        natlink.setBeginCallback(self.on_begin_callback)
        natlink.setChangeCallback(self.on_change_callback)

    def setup_logger(self) -> None:
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.propagate = False
        log_level = self.config.log_level
        if log_level is not LogLevel.NOTSET:
            self.logger.setLevel(log_level.value)
            self.logger.debug(f'set log level to: {log_level.name}')


def get_natlink_system_config_filename() -> str:
    hive, key, flags = (winreg.HKEY_LOCAL_MACHINE, r'Software\Natlink', winreg.KEY_WOW64_32KEY)
    with winreg.OpenKeyEx(hive, key, access=winreg.KEY_READ | flags) as natlink_key:
        core_path, _ = winreg.QueryValueEx(natlink_key, "coreDir")
        return core_path


def config_locations() -> Iterable[str]:
    yield os.path.expanduser('~/.natlink')
    yield get_natlink_system_config_filename()


def run() -> None:
    logger = logging.getLogger('natlink')
    config = NatlinkConfig.from_first_found_file(config_locations())
    main = NatlinkMain(logger, config)
    main.setup_logger()
    main.start()
