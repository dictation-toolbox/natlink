# Testing

Audience: contributors and maintainers validating natlink changes.

Run commands from the repo root — `uv run` finds the `.venv` automatically.
Or activate the venv first (`.venv\Scripts\activate`) and omit `uv run`.

See also:

- [Contributing](contributing.md)
- [Developer Debugging](developer-debugging.md)

## Default Behavior

Pytest is configured in `pyproject.toml` with:

- `--capture=tee-sys`
- `--cov --cov-report=term-missing:skip-covered` (coverage via pytest-cov)
- test discovery under `tests/`
- support for `src` and `tests` on `PYTHONPATH`

## Markers

| Marker | Meaning |
|--------|---------|
| `online` | requires a live Dragon connection; skips automatically otherwise |
| `offline` | requires Dragon not running; skips automatically otherwise |
| `minimal` | fast regression guard, one test per feature |
| `experimental` | slower or less reliable tests, opt-in |
| `nsformat` | Dragon text-formatting tests, opt-in |

## Common Commands

```powershell
uv run pytest tests -q                              # all tests
uv run pytest tests -m minimal -v                   # fast regression guard
uv run pytest tests -m online -v                    # live Dragon tests only
uv run pytest tests -m nsformat -v                  # Dragon formatting tests
uv run pytest tests\test_natlink_compat.py -q       # compatibility layer only
uv run pytest tests --no-cov -q                     # skip coverage measurement
```

## Which Slice To Run

- docs-only changes: rebuild docs (`.\scripts\docs.ps1 -Build`)
- targeted compatibility/API changes: `uv run pytest tests\test_natlink_compat.py -q`
- broad Python-side changes: `uv run pytest tests -q`
- live Dragon behavior changes: include `-m online`
- changes that should only run without Dragon: include `-m offline`

## Microphone Handling

The test suite starts with the microphone off. `recognitionMimic` works
regardless of mic state so most tests never touch it. Tests that specifically
exercise mic state control (e.g. `test_system_info`, `test_syncops`) save and
restore the mic state around their assertions.

## Coverage

Coverage is measured automatically via pytest-cov. To generate an HTML report:

```powershell
uv run pytest tests --cov-report=html:htmlcov
```

## Skips

Many tests auto-skip based on whether Dragon is available. That is normal and
expected. Contributors should note when a relevant test class could not be run
because the necessary Dragon state was unavailable.
