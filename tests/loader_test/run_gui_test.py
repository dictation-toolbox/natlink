"""Test three loaders through the full GUI (tray icon + messages window).

Usage:
    python -m tests.loader_test.run_gui_test

Requires Dragon to be running. Patches loader discovery so the three
test loaders are found without needing real entry points.
"""
import sys
sys.coinit_flags = 2  # STA — must be set before any COM import

import logging
logging.basicConfig(level=logging.DEBUG,
                    format="[%(levelname)s][%(name)s] %(message)s",
                    stream=sys.stderr)
logging.getLogger("comtypes").setLevel(logging.WARNING)

from unittest.mock import patch

# The three test loaders live under tests.loader_test.*
_TEST_LOADERS = [
    ("loader_a", "tests.loader_test.loader_a"),
    ("loader_b", "tests.loader_test.loader_b"),
    ("loader_c", "tests.loader_test.loader_c"),
]


def main():
    with patch("natlink_compat._loaders.get_all_loader_names",
               return_value=_TEST_LOADERS):
        from natlink_compat._launcher import run
        run()


if __name__ == "__main__":
    main()
