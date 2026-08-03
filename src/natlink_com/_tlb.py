"""Type library wrapper loading — vendored comtypes-generated modules.

Imports the pre-generated interface wrappers for the version-appropriate
Dragon TLB (v13/14 or v15/16).  No runtime codegen or cache directory needed.

Call flow:
  1. First ``get_tlb()`` call → ``load_tlb()`` → auto-detect version from
     registry → import correct ``_gen_*`` module → cache it.
  2. ``DragonConnection.connect()`` calls ``load_tlb(version_hint=N)`` with
     the detected version.  If it matches the cached module, no-op.  If it
     differs (shouldn't happen — same registry), logs a warning and switches.
  3. All subsequent ``get_tlb()`` calls return the cached module.

The auto-detection uses ``detect_dragon_major()`` from ``_config.py``,
which reads natlink.ini / Windows uninstall registry (cached per-process).
No circular-import risk — ``_config.py`` has no dependency on ``_tlb.py``.
"""

import logging

log = logging.getLogger("natlink.com.tlb")

_tlb_mod = None
_tlb_variant = None  # "v13_v14" or "v15_v16"


def get_tlb():
    """Return the cached TLB module, loading it on first access."""
    if _tlb_mod is None:
        load_tlb()
    return _tlb_mod


def _pick_variant(major):
    """Return (module, variant_name) for the given Dragon major version."""
    if major and major <= 14:
        from . import _gen_v13_v14 as mod
        return mod, "v13_v14"
    else:
        from . import _gen_v15_v16 as mod
        return mod, "v15_v16"


def load_tlb(version_hint=None):
    """Load the vendored Dragon interface wrappers.

    Selects the version-appropriate module based on detected Dragon version:
      DNS 13-14 → _gen_v13_v14
      DPI 15-16 → _gen_v15_v16

    When called without version_hint, auto-detects from the registry via
    _detect_dragon_major() (cached, cheap).  When called with a hint that
    matches the already-loaded variant, returns the cached module.
    """
    global _tlb_mod, _tlb_variant

    major = version_hint
    if major is None:
        if _tlb_mod is not None:
            return _tlb_mod
        try:
            from ._config import detect_dragon_major
            major = detect_dragon_major()
        except Exception:
            major = 0

    log.info("Loading TLB wrappers (Dragon major=%d, hint=%s)",
             major or 0, version_hint)
    mod, variant = _pick_variant(major)

    # Already loaded the correct variant — no-op
    if variant == _tlb_variant:
        log.debug("TLB variant %s already loaded — no-op", variant)
        return _tlb_mod

    # Switching variants after initial load (shouldn't happen in production)
    if _tlb_variant is not None:
        log.warning("Switching TLB variant from %s to %s (Dragon %d)",
                    _tlb_variant, variant, major or 0)

    _tlb_mod = mod
    _tlb_variant = variant
    log.info("Loaded vendored TLB wrappers: %s (Dragon %d)",
             variant, major or 0)
    return _tlb_mod
