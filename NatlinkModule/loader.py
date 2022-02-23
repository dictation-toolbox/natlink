#pylint:disable=C0114, C0115, C0116, R1705, R0902, W0703, E1101
import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
import sysconfig
import time
import traceback
import winreg
from pathlib import Path
from types import ModuleType
from typing import List, Dict, Set, Iterable, Any, Tuple, Callable, Optional

import natlink
from natlink.config import LogLevel, NatlinkConfig, NATLINK_INI, expand_path, getconfigsetting

# the possible languages (for getUserLanguage) (runs at start and on_change_callback, user)
# default is "enx", some of the English dialects...
UserLanguages = {  # from config files (if not given by args in setUserInfo)
             "Nederlands": "nld",
             "Fran\xe7ais": "fra",
             "Deutsch": "deu",
             "Italiano": "ita",
             "Espa\xf1ol": "esp",
             "Dutch": "nld",
             "French": "fra",
             "German": "deu",
             "Italian": "ita",
             "Spanish": "esp",}

class NatlinkMain:
    def __init__(self, logger: logging.Logger, config: NatlinkConfig):
        self.logger = logger
        self.config = config
        self.loaded_modules: Dict[Path, ModuleType] = {}
        self.prog_names_visited: Set[str] = set()    # to enable loading program specific grammars
        self.bad_modules: Set[Path] = set()
        self.load_attempt_times: Dict[Path, float] = {}
        self._user: str = ''
        self._profile: str = ''    # at on_change_callback user
        self._pre_load_callback: Optional[Callable[[], None]] = None
        self._post_load_callback: Optional[Callable[[], None]] = None
        self.seen: Set[Path] = set()     # start empty in trigger_load


    def set_pre_load_callback(self, pre_load: Optional[Callable[[], None]]) -> None:
        if pre_load is None:
            self._pre_load_callback = None
        elif not callable(pre_load):
            raise TypeError(f'pre-load callback must be callable, got type: {type(pre_load)}')
        self._pre_load_callback = pre_load

    def set_post_load_callback(self, post_load: Optional[Callable[[], None]]) -> None:
        if post_load is None:
            self._post_load_callback = None
        elif not callable(post_load):
            raise TypeError(f'post-load callback must be callable, got type: {type(post_load)}')
        self._post_load_callback = post_load

    @property
    def module_paths_for_user(self) -> List[Path]:
        return self._module_paths_in_dirs(self.config.directories_for_user(self._user))

    def _module_paths_in_dirs(self, directories: Iterable[str]) -> List[Path]:

        def is_script(f: Path) -> bool:
            if not f.is_file():
                return False
            if not f.suffix == '.py':
                return False
            
            if f.stem.startswith('_'):
                return True
            for prog_name in self.prog_names_visited:
                if f.stem == prog_name or f.stem.startswith( prog_name + '_'):
                    return True
            return False

        init = '__init__.py'

        mod_paths: List[Path] = []
        for d in directories:
            dir_path = Path(d)
            scripts = sorted(filter(is_script, dir_path.iterdir()))
            init_path = dir_path.joinpath(init)
            if init_path in scripts:
                scripts.remove(init_path)
                scripts.insert(0, init_path)
            mod_paths.extend(scripts)

        return mod_paths

    @staticmethod
    def _add_dirs_to_path(directories: Iterable[str]) -> None:
        for d in directories:
            d_expanded = expand_path(d)
            if d_expanded not in sys.path:
                sys.path.insert(0, d_expanded)

    def _call_and_catch_all_exceptions(self, fn: Callable[[], None]) -> None:
        try:
            fn()
        except Exception:
            self.logger.exception(traceback.format_exc())

    def unload_module(self, module: ModuleType) -> None:
        unload = getattr(module, 'unload', None)
        if unload is not None:
            self.logger.debug(f'unloading module: {module.__name__}')
            self._call_and_catch_all_exceptions(unload)

    @staticmethod
    def _import_module_from_path(mod_path: Path) -> ModuleType:
        mod_name = mod_path.stem
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        if spec is None:
            raise FileNotFoundError(f'Could not find spec for: {mod_name}')
        loader = spec.loader
        if loader is None:
            raise FileNotFoundError(f'Could not find loader for: {mod_name}')
        if not isinstance(loader, importlib.machinery.SourceFileLoader):
            raise ValueError(f'module {mod_name} does not have a SourceFileLoader loader')
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def load_or_reload_module(self, mod_path: Path, force_load: bool = False) -> None:
        mod_name = mod_path.stem
        if mod_path in self.seen:
            self.logger.warning(f'Attempting to load duplicate module: {mod_path})')
            return
        
        last_attempt_time = self.load_attempt_times.get(mod_path, 0.0)
        self.load_attempt_times[mod_path] = time.time()
        try:
            if mod_path in self.bad_modules:
                last_modified_time = mod_path.stat().st_mtime
                if force_load or last_attempt_time < last_modified_time:
                    self.logger.info(f'loading previously bad module: {mod_name}')
                    module = self._import_module_from_path(mod_path)
                    self.bad_modules.remove(mod_path)
                    self.loaded_modules[mod_path] = module
                    return
                else:
                    self.logger.info(f'skipping unchanged bad module: {mod_name}')
                    return
            else:
                maybe_module = self.loaded_modules.get(mod_path)
                if maybe_module is None:
                    self.logger.info(f'loading module: {mod_name}')
                    module = self._import_module_from_path(mod_path)
                    self.loaded_modules[mod_path] = module
                    return
                else:
                    module = maybe_module
                    last_modified_time = mod_path.stat().st_mtime
                    if force_load or last_attempt_time < last_modified_time:
                        self.logger.info(f'reloading module: {mod_name}')
                        self.unload_module(module)
                        del module
                        module = self._import_module_from_path(mod_path)
                        self.loaded_modules[mod_path] = module
                        return
                    else:
                        self.logger.debug(f'skipping unchanged loaded module: {mod_name}')
                        return
        except Exception:
            self.logger.exception(traceback.format_exc())
            self.bad_modules.add(mod_path)
            if mod_path in self.loaded_modules:
                old_module = self.loaded_modules.pop(mod_path)
                self.unload_module(old_module)
                del old_module
                importlib.invalidate_caches()

    def load_or_reload_modules(self, mod_paths: Iterable[Path]) -> None:
        for mod_path in mod_paths:
            self.load_or_reload_module(mod_path)
            self.seen.add(mod_path)

    def remove_modules_that_no_longer_exist(self) -> None:
        mod_paths = self.module_paths_for_user
       
        for mod_path in set(self.loaded_modules).difference(mod_paths):
            self.logger.info(f'unloading removed or not-for-this-user module {mod_path.stem}')
            old_module = self.loaded_modules.pop(mod_path)
            self.load_attempt_times.pop(mod_path)
            self.unload_module(old_module)
            del old_module
        for mod_path in self.bad_modules.difference(mod_paths):
            self.logger.debug(f'bad module was removed: {mod_path.stem}')
            self.bad_modules.remove(mod_path)
            self.load_attempt_times.pop(mod_path)

        importlib.invalidate_caches()

    def trigger_load(self) -> None:
        self.seen.clear()
        self.logger.debug('triggering load/reload process')
        self.remove_modules_that_no_longer_exist()

        mod_paths = self.module_paths_for_user
        if self._pre_load_callback is not None:
            self.logger.debug('calling pre-load callback')
            self._call_and_catch_all_exceptions(self._pre_load_callback)
        self.load_or_reload_modules(mod_paths)
        if self._post_load_callback is not None:
            self.logger.debug('calling post-load callback')
            self._call_and_catch_all_exceptions(self._post_load_callback)
        loaded_diff = set(self.module_paths_for_user).difference(self.loaded_modules.keys())
        if loaded_diff:
            self.logger.debug(f'second round, load new grammar files: {loaded_diff}')
        
        for mod_path in loaded_diff:
            self.logger.debug(f'new module in second round: {mod_path}')
            self.load_or_reload_module(mod_path)

    def on_change_callback(self, change_type: str, args: Any) -> None:
        """on_change_callback, when another user profile is chosen, or when the mic state changes
        """

        if change_type == 'user':
            user, profile = args
            if not isinstance(user, str):
                raise TypeError(f'unexpected args given to change callback: {args}')
            self._user = user
            self._profile = profile
            self.logger.debug(f'on_change_callback, user "{self._user}", profile: "{self._profile}"')
            value = getUserLanguage(self._profile)
            self.logger.debug(f'value from getUserLanguage: "{value}"')

            if self.config.load_on_user_changed:
                self.trigger_load()
        elif change_type == 'mic' and args == 'on':
            self.logger.debug('on_change_callback called with: "mic", "on"')
            if self.config.load_on_mic_on:
                self.trigger_load()
        else:
            self.logger.debug(f'on_change_callback unhandled: change_type: "{change_type}", args: "{args}"')
            

    def on_begin_callback(self, module_info: Tuple[str, str, int]) -> None:
        self.logger.debug(f'on_begin_callback called with: moduleInfo: {module_info}')
        prog_name = Path(module_info[0]).stem
        if prog_name not in self.prog_names_visited:
            self.prog_names_visited.add(prog_name)
            self.trigger_load()
        elif self.config.load_on_begin_utterance:
            self.trigger_load()

    def start(self) -> None:
        self.logger.info(f'starting natlink loader from config file:\n\t"{self.config.config_path}"')
        natlink.active_loader = self
        if not self.config.directories:
            self.logger.warning(f'Starting Natlink, but no directories to load are specified.\n\tPlease add one or more directories\n\tin config file: "{self.config.config_path}".')
            return
        self._add_dirs_to_path(self.config.directories)  
        if self.config.load_on_startup:
            self.trigger_load()
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

def _getLastUsedAcoustics(DNSuserDirectory):
    """get name of last used acoustics, must have DNSuserDirectory passed
    
    called when on_change_callback, the user changes. used by getLanguage
    """
    isfile, isdir = os.path.isfile, os.path.isdir
    if not (DNSuserDirectory and isdir(DNSuserDirectory)):
        print('getLastUsedAcoustics, no DNSuserDirectory passed, probably Dragon is not running')
        return ''
    optionsini = os.path.join(DNSuserDirectory, 'options.ini')
    if not (optionsini and isfile(optionsini)):
        raise OSError(f'getLastUsedAcoustics, not a valid options inifile is found: "{optionsini}"')

    section = "Options"
    keyname = "Last Used Acoustics"
    value = getconfigsetting(optionsini, section, keyname)

    return value

def getUserLanguage(DNSuserDirectory):
    """return the user language (default "enx") from Dragon inifiles
        
    like "nld" for Dutch, etc.
    """
    isfile = os.path.isfile
    keyToModel = _getLastUsedAcoustics(DNSuserDirectory)
    acoustic_init_path = os.path.join(DNSuserDirectory, 'acoustic.ini')
    section = "Base Acoustic"
    if not (acoustic_init_path and isfile(acoustic_init_path)):
        print(f'getUserLanguag: warning: user language cannot be found from Dragon Inifile: "{acoustic_init_path}",\n\tprobably Dragon is not running, return "enx"')
        return 'enx'

    value = getconfigsetting(acoustic_init_path, section, keyToModel)
    print(' bingo: language: "{value}"')
    if value in UserLanguages:
        return UserLanguages[value]
    return "enx"



def get_natlink_system_config_filename() -> str:
    return get_config_info_from_registry('installPath')

def get_config_info_from_registry(key_name: str) -> str:
    hive, key, flags = (winreg.HKEY_LOCAL_MACHINE, r'Software\Natlink', winreg.KEY_WOW64_32KEY)
    with winreg.OpenKeyEx(hive, key, access=winreg.KEY_READ | flags) as natlink_key:
        result, _ = winreg.QueryValueEx(natlink_key, key_name)
        return result

def config_locations() -> Iterable[str]:
    join, expanduser, getenv = os.path.join, os.path.expanduser, os.getenv
    home = expanduser('~')
    config_sub_dir = '.natlink'
    # config_filename == NATLINK_INI (in config.py)

    # try NATLINK_INI setting:
    natlink_ini_from_env = getenv("NATLINK_INI")
    if natlink_ini_from_env:
        natlink_ini_from_env_path = expand_path(natlink_ini_from_env)
        if os.path.isfile(natlink_ini_from_env_path):
            return [natlink_ini_from_env_path]
        else:
            if natlink_ini_from_env_path == natlink_ini_from_env:
                raise OSError(f'You defined environment variable "NATLINK_INI" to "{natlink_ini_from_env}", but this is not a valid file.\n\tPlease remove or correct this environment variable')
            raise OSError(f'You defined environment variable "NATLINK_INI" to "{natlink_ini_from_env}",\n\texpanded to "{natlink_ini_from_env_path}"\n\tBut this is not a valid file.\n\tPlease remove or correct this environment variable')

    # try DICTATIONTOOLBOXHOME    
    dictation_toolbox_home = getenv('DICTATIONTOOLBOXHOME')
    
    if dictation_toolbox_home:
        dictation_toolbox_home_path = expand_path(dictation_toolbox_home)
        subdir = join(dictation_toolbox_home_path, '.natlink')
        config_file_path = join(dictation_toolbox_home_path, '.natlink', "natlink.ini")
        if not os.path.isdir(dictation_toolbox_home_path):
            raise OSError(f'You set environment variable: "DICTATIONTOOLBOXHOME",\n\tBut it does not point to a valid directory: "{dictation_toolbox_home_path}".\n\tPlease create this directory and subdirectory ".natlink"\n\tand copy a valid version of "natlink.ini" into this directory,\n\t\tor fix/remove this environment variable.')
        if not os.path.isdir(subdir):
            raise OSError(f'You set environment variable: "DICTATIONTOOLBOXHOME",\n\tBut this directory "{dictation_toolbox_home_path}" should contain a subdirectory ".natlink".\n\tPlease create this directory\n\tand copy a valid version of "natlink.ini" into this directory,\n\t\tor fix/remove this environment variable.')
        if not os.path.isfile(config_file_path):
            raise OSError(f'You set environment variable: "DICTATIONTOOLBOXHOME",\n\tBut this directory "{dictation_toolbox_home_path}" should contain a subdirectory ".natlink" containing config file "natlink.ini".\n\tPlease create this directory\n\tand copy a valid version of "natlink.ini" into this directory,\n\t\tor fix/remove this environment variable.')
        return [join(dictation_toolbox_home, '.natlink', NATLINK_INI)]
                         
    # choose between home and FallbackConfigDir
    possible_dirs = [join(home, config_sub_dir),    ### join(home, 'Documents', config_sub_dir),
                     join(get_natlink_system_config_filename(), "DefaultConfig")]

    return [join(loc, NATLINK_INI) for loc in possible_dirs]

def run() -> None:
    logger = logging.getLogger('natlink')
    try:
        # TODO: remove this hack. As of October 2021, win32api does not load properly, except if
        # the package pywin32_system32 is explictly put on new dll_directory white-list
        pywin32_dir = os.path.join(sysconfig.get_path('platlib'), "pywin32_system32")
        if os.path.isdir(pywin32_dir):
            os.add_dll_directory(pywin32_dir)
        
        config = NatlinkConfig.from_first_found_file(config_locations())
        main = NatlinkMain(logger, config)
        main.setup_logger()
        main.start()
    except Exception as exc:
        print(f'Exception: "{exc}" in loader.run', file=sys.stderr)
        print(traceback.format_exc())
        raise Exception from exc
    
if __name__ == "__main__":
    run()
    