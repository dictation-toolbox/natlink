#
#
# # Calls the unload member function of a given module.  Does not make the call
# # if the function does not exist and cleans up in the case of errors.
# def safelyCall(modName, funcName):
#     try:
#         func = getattr(sys.modules[modName], funcName)
#     except AttributeError:
#         # unload function does not exist
#         return None
#     try:
#         func(*[])
#     except:
#         sys.stderr.write('Error calling ' + modName + '.' + funcName + '\n')
#         traceback.print_exc()
#         return None
#
#
# def changeCallback(Type, args):
#     global userName, DNSuserDirectory, language, userLanguage, userTopic, \
#         BaseModel, BaseTopic, DNSmode, changeCallbackUserFirst, shiftkey
#
#     if Type == 'mic' and args == 'on':
#         moduleInfo = natlink.getCurrentModule()
#         findAndLoadFiles()
#         beginCallback(moduleInfo, checkAll=1)
#         loadModSpecific(moduleInfo)
#
#     ## user: at start and at user switch:
#     if Type == 'user' and userName != args[0]:
#         moduleInfo = natlink.getCurrentModule()
#
#         unloadEverything()
#
#     changeCallbackLoadedModules(Type, args)
#
#
# def changeCallbackLoadedModules(Type, args):
#     """BJ added, in order to intercept in a grammar (oops, repeat, control) in eg mic changed
#
#     in those cases the cancelMode can be called, so exclusiveMode is finished
#     """
#     sysmodules = sys.modules
#     for x in list(loadedFiles.keys()):
#         if loadedFiles[x]:
#             try:
#                 func = getattr(sysmodules[x], 'changeCallback')
#             except AttributeError:
#                 pass
#             else:
#                 func(*[Type, args])
#
#
# def start_natlink(doNatConnect=None):
#
#     if not natlink.isNatSpeakRunning():
#         print('start Dragon first, then rerun the script natlinkmain...')
#         time.sleep(10)
#         return
#
#     if not doNatConnect is None:
#         if doNatConnect:
#             print('start_natlink, do natConnect with option 1, threading')
#             natlink.natConnect(1)  # 0 or 1, should not be needed when automatic startup
#         else:
#             print('start_natlink, do natConnect with option 0, no threading')
#             natlink.natConnect(0)  # 0 or 1, should not be needed when automatic startup
#
#         print("----natlink.natConnect succeeded")
#
#     findAndLoadFiles()
#     natlink.setBeginCallback(beginCallback)
#     natlink.setChangeCallback(changeCallback)


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
from types import ModuleType
from typing import List, Dict, Set, Iterable, Any

import natlink


class NoGoodConfigFoundException(Exception):
    pass


class NatlinkMain:
    def __init__(self, logger: logging.Logger, config: configparser.ConfigParser):
        self.logger = logger
        self.config = config
        self.loaded_modules: Dict[str, ModuleType] = {}
        self.bad_modules: Set[str] = set()
        self.load_attempt_times: Dict[str, float] = {}

    @property
    def directories(self) -> List[str]:
        if self.config.has_section('directories'):
            return list(self.config['directories'].values())
        else:
            return []

    @property
    def module_names(self) -> List[str]:
        return self.module_names_in_dirs(self.directories)

    @classmethod
    def config_from_file(cls, fn: str) -> configparser.ConfigParser:
        return cls.config_from_first_found_file([fn])

    @staticmethod
    def config_from_first_found_file(files: Iterable[str]) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        for fn in files:
            if config.read(fn):
                return config
        raise NoGoodConfigFoundException(f'No good config found, did you define your ~/.natlink?')

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

    def load_modules(self, mod_names: Iterable[str]) -> None:
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
            self.load_modules(self.module_names)

    def start(self) -> None:
        self.logger.info('starting natlinkmain')
        self.add_dirs_to_path(self.directories)
        self.load_modules(self.module_names)
        natlink.setChangeCallback(self.on_change_callback)

    def setup_logger(self) -> None:
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.propagate = False
        if self.config.has_section('settings'):
            level = self.config['settings'].get('log_level')
            logging_levels = {
                'CRITICAL': logging.CRITICAL,
                'FATAL': logging.FATAL,
                'ERROR': logging.ERROR,
                'WARN': logging.WARNING,
                'WARNING': logging.WARNING,
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'NOTSET': logging.NOTSET,
            }
            log_level = logging_levels.get(level)
            if log_level is not None:
                self.logger.setLevel(level)
                self.logger.debug(f'set log level to: {level}')
            else:
                self.logger.error(f'Tried to set log level to {log_level}, '
                                  f'valid choices are {list(logging_levels.keys())}')


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
    config = NatlinkMain.config_from_first_found_file(config_locations())
    main = NatlinkMain(logger, config)
    main.setup_logger()
    main.start()
