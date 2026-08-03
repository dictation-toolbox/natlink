"""Pluggable loader protocol for natlink.

Third-party loaders (e.g. natlinkcore) implement this protocol.
Discovery order: runtime add_loader() > entry_points.
Multiple loaders can be active simultaneously.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class LoaderProtocol(Protocol):
    """Contract for natlink loader plugins.

    A loader manages grammar discovery and hot-reload for a set of user
    directories. It is started once a COM connection exists, and stopped
    before natDisconnect() tears COM down.

    Implementations may be class instances or modules with module-level
    functions.

    **Required:** ``start()`` — or ``run()``, the natlinkcore-compatible
    spelling. ``add_loader()`` accepts either.

    Only ``start`` is declared below. ``runtime_checkable`` protocols test for
    the presence of *every* declared member, so declaring the optional ones
    would make ``isinstance()`` reject loaders natlink runs happily — any
    loader without a ``stop()``. A ``run()``-only loader is valid but still
    will not satisfy ``isinstance``; use :func:`is_loader` for the acceptance
    test natlink itself applies.

    Optional members, each used when present:

    ``run()``
        Legacy alternative to ``start()``.
    ``stop()``
        Unload grammars and stop watching. Called before COM teardown.
    ``unload_all_loaded_modules()``
        Fallback teardown when there is no ``stop()``. natlinkcore 5.4.1
        ships this and neither ``stop()`` nor ``finish()``.
    ``trigger_load(force_load=True)``
        Fast path for reload; without it natlink stops and restarts.
    ``setup()``
        Module-level hook called during discovery, before ``start()``.
    ``natlink_manage_logging`` (bool)
        Set False to stop natlink replacing the loader's log handlers.
        Default True (log output is routed to the messages window).
    """

    def start(self) -> None:
        """Begin watching directories and loading grammars."""
        ...


def is_loader(obj) -> bool:
    """True if natlink would accept *obj* as a loader.

    This is the check ``add_loader()`` applies. It is broader than
    ``isinstance(obj, LoaderProtocol)``, which cannot express "start() or
    run()", so prefer this when validating a loader before registering it.
    """
    return hasattr(obj, "start") or hasattr(obj, "run")
