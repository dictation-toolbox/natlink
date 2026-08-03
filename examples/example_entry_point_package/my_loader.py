"""Example entry_point loader — auto-discovered by natlink on startup.

Install this package with: pip install -e examples/example_entry_point_package

Natlink discovers it via the "natlink.loaders" entry_points group
in pyproject.toml. The lifecycle is:

  1. setup() — called after import, before natConnect (optional)
  2. start() — called after COM connection succeeds
  3. stop()  — called before COM teardown

No manual add_loader() call needed — just pip install and go.
"""

import logging
import os

log = logging.getLogger(__name__)

_instance = None


class MyLoader:
    """Loader that prints a message on start/stop."""

    def __init__(self, config_dir):
        self.config_dir = config_dir

    def start(self):
        log.info("MyLoader started (config: %s)", self.config_dir)
        # Load your grammars here...

    def stop(self):
        log.info("MyLoader stopped")
        # Unload your grammars here...


def setup():
    """Called after import, before natConnect — set custom UI here.

    Example:
        import natlink
        natlink.set_ui_provider(MyCustomUI())
    """
    pass  # This loader uses the default UI


def start():
    """Called after COM connection succeeds — start your loader."""
    global _instance
    config_dir = os.path.expanduser("~/.my-natlink-loader")
    _instance = MyLoader(config_dir)
    _instance.start()


def stop():
    """Called before COM teardown — stop your loader."""
    global _instance
    if _instance:
        _instance.stop()
        _instance = None
