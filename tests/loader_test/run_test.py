"""Test three loaders running simultaneously, each loading a grammar.

Usage:
    python -m tests.loader_test.run_test

Requires Dragon to be running.
"""
import sys
sys.coinit_flags = 2  # STA

import logging
logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s][%(name)s] %(message)s",
                    stream=sys.stderr)
logging.getLogger("comtypes").setLevel(logging.WARNING)

import natlink


def main():
    # Empty discovered_loaders gives a deterministic environment — no
    # entry-point loaders leak in from the host machine.
    with natlink.natConnect(discovered_loaders=[]):
        from tests.loader_test import loader_a, loader_b, loader_c

        for loader in [loader_a, loader_b, loader_c]:
            natlink.add_loader(loader)

        loaders = natlink.get_loaders()
        assert len(loaders) == 3, f"Expected 3 loaders, got {len(loaders)}"

        # Verify each grammar is loaded in Dragon
        from natlink_compat._state import _state as st
        grammar_count = len(st.grammar_registry)
        assert grammar_count == 3, f"Expected 3 grammars, got {grammar_count}"

        print(f"PASS: {len(loaders)} loaders, {grammar_count} grammars", file=sys.stderr)


if __name__ == "__main__":
    main()
