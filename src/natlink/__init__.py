"""natlink — drop-in replacement for the original natlink C extension.

This package delegates to natlink_compat (which wraps the natlink_com
COM backend) so that natlinkcore and user grammars can ``import natlink``
and get a working implementation on 64-bit Python.

natlinkcore-style loader registration:
  natlinkcore sets ``natlink.active_loader = self`` to publish itself.
  This compatibility pattern is intercepted and routed to the loaders list.
  New code should use ``natlink.add_loader()`` instead.
"""
import sys
import types

import natlink_compat as _compat
from natlink_compat import *          # noqa: F401,F403
from natlink_compat import __all__    # noqa: F401


class _NatlinkModule(types.ModuleType):
    """Module wrapper intercepting natlinkcore-style loader registration."""

    def __setattr__(self, name, value):
        if name == "active_loader":
            # natlinkcore sets this inside
            # start(). The loader is already running — just register it
            # without calling start again.
            from natlink_compat._loaders import register_running_loader
            register_running_loader(value)
            return
        super().__setattr__(name, value)

    def __getattr__(self, name):
        if name == "active_loader":
            # natlinkcore reads this back
            # (e.g. .bad_modules).
            loaders = _compat.get_loaders()
            return loaders[0] if loaders else None
        raise AttributeError(f"module 'natlink' has no attribute {name}")


_self = sys.modules[__name__]
_wrapper = _NatlinkModule(__name__)
_wrapper.__dict__.update(_self.__dict__)
_wrapper.__path__ = _self.__path__   # required for package identity
sys.modules[__name__] = _wrapper
