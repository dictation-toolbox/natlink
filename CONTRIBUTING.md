# Contributing

## Scope

This repository contains:

- the public `natlink` Python package
- the compatibility layer in `natlink_compat`
- the COM backend in `natlink_com`
- the MkDocs documentation site in `docs/`

## Development Setup

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

Install the project in editable mode with development dependencies:

```powershell
pip install -e .[dev,test]
```

## Tests

Run the main compat test slice:

```powershell
python -m pytest tests\test_natlink_compat.py -q
```

Run the full test suite:

```powershell
python -m pytest tests -q
```

Some tests require a live Dragon installation and will skip automatically when
Dragon is unavailable.

## Building Marshal DLLs and TLB Wrappers

After changing `.idl` files, rebuild the marshal DLLs and regenerate the
vendored comtypes wrappers:

```powershell
.\scripts\build.ps1                  # full rebuild: DLLs + TLBs + vendored wrappers
.\scripts\build.ps1 -SkipDll         # regenerate Python wrappers only (TLBs must exist)
```

## Documentation

Build and serve the docs (default):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\docs.ps1
```

Build only or serve only:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\docs.ps1 -Build
powershell -ExecutionPolicy Bypass -File .\tools\docs.ps1 -Serve
```

The rendered site is written to `site/`.

## Documentation Structure

Keep documentation ownership clear:

- `install.md`: installation and first run only
- `configuration/`: settings and config files
- `cli.md`: command-line reference
- `troubleshooting.md`: user-facing troubleshooting
- `developer-debugging.md`: contributor debugging workflow
- `third_party/`: public contracts for integrators
- `third_party/api/`: generated/reference-style API pages
- `architecture.md` and `program_flow.md`: internal explanation

Prefer linking to the owning page instead of duplicating the same material in
multiple places.

## Change Guidelines

- Keep public/internal boundaries explicit.
- Do not mix third-party contract docs with internal implementation detail.
- Prefer small, targeted changes over broad rewrites.
- When changing public behavior, update both tests and documentation.
- When changing docs navigation or page ownership, rebuild the docs before
  finishing.

## Verification

Before finishing a change, run the smallest relevant verification set:

- targeted pytest slice for code changes
- docs build for documentation changes

If something could not be verified locally, note that explicitly.
