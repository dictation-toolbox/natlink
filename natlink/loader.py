import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
import time
import traceback
import winreg
from pathlib import Path
from types import ModuleType
from typing import List, Dict, Set, Iterable, Any, Tuple

import natlink
from natlink.config import LogLevel, NatlinkConfig


class NatlinkMain:
    def __init__(self, logger: logging.Logger, config: NatlinkConfig):
        self.logger = logger
        self.config = config
        self.loaded_modules: Dict[Path, ModuleType] = {}
        self.bad_modules: Set[Path] = set()
        self.load_attempt_times: Dict[Path, float] = {}

    @property
    def module_paths(self) -> List[Path]:
        return self.module_paths_in_dirs(self.config.directories)

    @staticmethod
    def module_paths_in_dirs(directories: Iterable[str]) -> List[Path]:

        def is_script(f: Path) -> bool:
            return f.is_file() and f.name.startswith('_') and f.name.endswith('.py')

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
    def add_dirs_to_path(directories: Iterable[str]) -> None:
        for d in directories:
            if d not in sys.path:
                sys.path.insert(0, d)

    def unload_module(self, module: ModuleType) -> None:
        unload = getattr(module, 'unload', None)
        if unload is not None:
            self.logger.info(f'unloading module: {module.__name__}')
            try:
                unload()
            except Exception:
                self.logger.exception(traceback.format_exc())

    @staticmethod
    def import_module_from_path(mod_path: Path) -> ModuleType:
        mod_name = mod_path.stem
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        if spec is None:
            raise FileNotFoundError(f'Could not find spec for: {mod_name}')
        loader = spec.loader
        if loader is None:
            raise FileNotFoundError(f'Could not find loader for: {mod_name}')
        elif not isinstance(loader, importlib.machinery.SourceFileLoader):
            raise ValueError(f'module {mod_name} does not have a SourceFileLoader loader')
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def load_or_reload_module(self, mod_path: Path, force_load: bool = False) -> None:
        mod_name = mod_path.stem
        last_attempt_time = self.load_attempt_times.get(mod_path, 0.0)
        self.load_attempt_times[mod_path] = time.time()
        try:
            if mod_path in self.bad_modules:
                last_modified_time = mod_path.stat().st_mtime
                if force_load or last_attempt_time < last_modified_time:
                    self.logger.info(f'loading previously bad module: {mod_name}')
                    module = self.import_module_from_path(mod_path)
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
                    module = self.import_module_from_path(mod_path)
                    self.loaded_modules[mod_path] = module
                    return
                else:
                    module = maybe_module
                    last_modified_time = mod_path.stat().st_mtime
                    if force_load or last_attempt_time < last_modified_time:
                        self.logger.info(f'reloading module: {mod_name}')
                        self.unload_module(module)
                        del module
                        module = self.import_module_from_path(mod_path)
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
        seen: Set[Path] = set()
        for mod_path in mod_paths:
            if mod_path in seen:
                self.logger.warning(f'Attempting to load duplicate module: {mod_path})')
            self.load_or_reload_module(mod_path)
            seen.add(mod_path)

    def remove_modules_that_no_longer_exist(self) -> None:
        mod_paths = self.module_paths
        for mod_path in set(self.loaded_modules).difference(mod_paths):
            self.logger.info(f'unloading removed module {mod_path.stem}')
            old_module = self.loaded_modules.pop(mod_path)
            self.load_attempt_times.pop(mod_path)
            self.unload_module(old_module)
            del old_module
        for mod_path in self.bad_modules.difference(mod_paths):
            self.logger.debug(f'bad module was removed: {mod_path.stem}')
            self.bad_modules.remove(mod_path)
            self.load_attempt_times.pop(mod_path)

        importlib.invalidate_caches()

    def on_change_callback(self, change_type: str, args: Any) -> None:
        self.logger.debug(f'on_change_callback called with: change:{change_type}, args:{args}')
        if change_type == 'mic' and args == 'on':
            if self.config.load_on_mic_on:
                self.remove_modules_that_no_longer_exist()
                self.load_or_reload_modules(self.module_paths)

    def on_begin_callback(self, module_info: Tuple[str, str, int]) -> None:
        self.logger.debug(f'on_begin_callback called with: moduleInfo:{module_info}')
        if self.config.load_on_begin_utterance:
            self.remove_modules_that_no_longer_exist()
            self.load_or_reload_modules(self.module_paths)

    def start(self) -> None:
        self.logger.info('starting natlink loader')
        self.add_dirs_to_path(self.config.directories)
        if self.config.load_on_startup:
            self.load_or_reload_modules(self.module_paths)
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
    try:
        yield get_natlink_system_config_filename()
    except OSError:
        # installed locally
        pass


def run() -> None:
    logger = logging.getLogger('natlink')
    config = NatlinkConfig.from_first_found_file(config_locations())
    main = NatlinkMain(logger, config)
    main.setup_logger()
    main.start()
