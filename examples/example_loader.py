"""Example natlink loader — watches a directory for grammar scripts.

This is a minimal loader that demonstrates the LoaderProtocol.
It watches a single directory for _*.py files and loads them as
natlink grammars.

Usage:
    import natlink
    from example_loader import SimpleLoader

    natlink.natConnect()
    natlink.add_loader(SimpleLoader("C:/Users/You/grammars"))

Or register via setuptools entry_points in your pyproject.toml:

    [project.entry-points."natlink.loaders"]
    simple = "example_loader"

    Then define module-level start()/stop() functions (see bottom).
    See example_entry_point_package/ for a complete pip-installable example.
"""

import importlib
import logging
import os
import sys

log = logging.getLogger(__name__)


class SimpleLoader:
    """Minimal grammar loader — loads _*.py files from a directory."""

    def __init__(self, grammar_dir):
        self.grammar_dir = grammar_dir
        self._modules = {}

    def start(self):
        """Load all grammar scripts from the directory."""
        if not os.path.isdir(self.grammar_dir):
            log.warning("Grammar directory not found: %s", self.grammar_dir)
            return

        if self.grammar_dir not in sys.path:
            sys.path.insert(0, self.grammar_dir)

        for name in sorted(os.listdir(self.grammar_dir)):
            if name.startswith("_") and name.endswith(".py"):
                module_name = name[:-3]
                try:
                    mod = importlib.import_module(module_name)
                    self._modules[module_name] = mod
                    log.info("Loaded grammar: %s", module_name)
                except Exception:
                    log.exception("Failed to load grammar: %s", module_name)

        log.info("SimpleLoader started: %d grammars from %s",
                 len(self._modules), self.grammar_dir)

    def stop(self):
        """Unload all grammar scripts."""
        for name, mod in self._modules.items():
            # Call unload() if the grammar module defines it
            if hasattr(mod, "unload"):
                try:
                    mod.unload()
                except Exception:
                    log.debug("unload() failed for %s", name, exc_info=True)
        self._modules.clear()
        log.info("SimpleLoader stopped")


# --- Module-level entry points for setuptools discovery ---
# If this module is registered as a natlink.loaders entry_point,
# natlink calls start() at startup and stop() at shutdown.

_instance = None


def start():
    """Entry point called by natlink's entry_points discovery."""
    global _instance
    grammar_dir = os.path.expanduser("~/natlink-grammars")
    _instance = SimpleLoader(grammar_dir)
    _instance.start()


def stop():
    """Called by natlink at shutdown."""
    global _instance
    if _instance:
        _instance.stop()
        _instance = None
