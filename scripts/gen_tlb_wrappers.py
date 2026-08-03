"""Generate vendored comtypes TLB wrappers from Dragon type libraries.

Reads the .tlb files in src/natlink_com/ and generates _gen_v13_v14.py
and _gen_v15_v16.py — pre-generated comtypes interface wrappers that
ship with the package instead of being generated at runtime.

Usage:
    python scripts/gen_tlb_wrappers.py

Requires: comtypes (pip install comtypes)
"""

import os
import re
import subprocess
import sys
import textwrap

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(REPO_ROOT, "src", "natlink_com")

VARIANTS = [
    ("dragon_interfaces_v13_v14.tlb", "_gen_v13_v14.py", "DNS 13 / DPI 14"),
    ("dragon_interfaces_v15_v16.tlb", "_gen_v15_v16.py", "DPI 15 / DPI 16"),
]


def generate_one(tlb_filename, out_filename, description):
    """Generate a vendored wrapper from a single TLB file."""
    tlb_path = os.path.join(PKG_DIR, tlb_filename)
    out_path = os.path.join(PKG_DIR, out_filename)

    if not os.path.isfile(tlb_path):
        print(f"  SKIP  {tlb_filename} (not found)")
        return False

    # Run generation in a subprocess so each TLB gets a clean comtypes state.
    # comtypes caches modules globally, so generating both variants in the
    # same process produces incorrect results for the second one.
    worker = textwrap.dedent(f"""\
        import sys, os, tempfile, shutil
        sys.coinit_flags = 2
        import comtypes.client
        import comtypes.gen

        tlb_path = {tlb_path!r}
        gen_dir = tempfile.mkdtemp(prefix="natlink_gen_")
        comtypes.client.gen_dir = gen_dir
        comtypes.gen.__path__.insert(0, gen_dir)
        with open(os.path.join(gen_dir, "__init__.py"), "w") as f:
            f.write("")

        # Replace comtypes.gen.__path__ entirely so comtypes won't find
        # previously cached modules in site-packages
        comtypes.gen.__path__ = [gen_dir]

        comtypes.client.GetModule(tlb_path)

        # Find the main wrapper by Dragon LIBID prefix:
        #   v13_v14: DD100101  →  _DD100101_*.py
        #   v15_v16: DD100100  →  _DD100100_*.py
        main_files = [fn for fn in os.listdir(gen_dir)
                      if fn.startswith("_DD10010") and fn.endswith(".py")]
        if not main_files:
            print("ERROR: no generated files in " + gen_dir, file=sys.stderr)
            print("  Contents: " + str(os.listdir(gen_dir)), file=sys.stderr)
            sys.exit(1)

        best_path = os.path.join(gen_dir, main_files[0])
        with open(best_path, "r", encoding="utf-8", errors="replace") as f:
            sys.stdout.write(f.read())

        shutil.rmtree(gen_dir, ignore_errors=True)
    """)

    result = subprocess.run(
        [sys.executable, "-c", worker],
        capture_output=True, text=True, encoding="utf-8", errors="replace")

    if result.returncode != 0:
        print(f"  FAIL  {tlb_filename}: {result.stderr.strip()}")
        return False

    code = result.stdout

    # Scrub: replace stdole IUnknown reference with comtypes.IUnknown
    code = code.replace(
        "import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0",
        "import comtypes")
    code = code.replace(
        "comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.IUnknown",
        "comtypes.IUnknown")
    code = code.replace(
        "comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0.GUID",
        "GUID")

    # Scrub: remove absolute typelib_path
    code = re.sub(
        r"typelib_path = '.*?'",
        "typelib_path = ''  # vendored — no TLB path needed",
        code)

    # Add header
    header = f'''\
# -*- coding: utf-8 -*-
"""Vendored comtypes-generated wrappers for Dragon interfaces ({description}).

Auto-generated from {tlb_filename} via comtypes.client.GetModule().
Scrubbed: absolute paths removed, stdole references replaced with comtypes.IUnknown.

DO NOT EDIT BY HAND — regenerate with: python scripts/gen_tlb_wrappers.py
"""
'''
    # Replace any existing coding line
    code = re.sub(r"^#.*coding.*\n", "", code)
    code = header + code

    # Verify no remaining stdole references
    remaining = [line for line in code.split("\n") if "_00020430" in line]
    if remaining:
        print(f"  WARN  {len(remaining)} remaining stdole references in {out_filename}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)

    lines = code.count("\n")
    print(f"  OK    {out_filename} ({lines} lines)")
    return True


def main():
    print(f"Generating vendored TLB wrappers in {PKG_DIR}")
    print()

    ok = sum(1 for tlb, out, desc in VARIANTS if generate_one(tlb, out, desc))

    print()
    print(f"Done: {ok}/{len(VARIANTS)} wrappers generated.")
    if ok < len(VARIANTS):
        sys.exit(1)


if __name__ == "__main__":
    main()
