# Natlink

Python interface to Dragon NaturallySpeaking on Windows.

Natlink connects to Dragon as an out-of-process 64-bit COM client, so modern
Python versions can integrate with Dragon without the old in-process C extension
model.

## Quick Start

```powershell
mkdir C:\natlink
cd C:\natlink
uv venv --python 3.14
uv pip install natlink
uv run natlink-ui
```

See the [full documentation](https://natlink.readthedocs.io/) for configuration,
CLI reference, and third-party integration.

## License

GPL-2.0-or-later. See [LICENSE](LICENSE).
