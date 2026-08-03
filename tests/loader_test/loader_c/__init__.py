"""Loader C — loads grammar charlie."""
import importlib
import logging
import os
import sys

log = logging.getLogger(__name__)
_modules = {}


def start():
    grammar_dir = os.path.join(os.path.dirname(__file__), "grammars")
    log.info("Loader C starting, grammar dir: %s", grammar_dir)
    if grammar_dir not in sys.path:
        sys.path.insert(0, grammar_dir)
    for name in sorted(os.listdir(grammar_dir)):
        if name.startswith("_") and name.endswith(".py"):
            mod_name = name[:-3]
            try:
                mod = importlib.import_module(mod_name)
                _modules[mod_name] = mod
                log.info("Loader C loaded: %s", mod_name)
            except Exception:
                log.exception("Loader C failed to load: %s", mod_name)
    log.info("Loader C started: %d grammars", len(_modules))


def stop():
    for name, mod in _modules.items():
        if hasattr(mod, "unload"):
            try:
                mod.unload()
            except Exception:
                log.debug("unload failed: %s", name, exc_info=True)
    _modules.clear()
    log.info("Loader C stopped")
