# Developer Debugging

Audience: contributors and maintainers debugging natlink itself.

Purpose: document debugger setup, interactive testing, and docs workflow for
development work.

See also:

- [Troubleshooting](troubleshooting.md)
- [Program Flow](program_flow.md)
- [Testing](testing.md)

## Debuggers

Natlink runs as a standard Python process, but the main thread owns the Win32
message pump. Pausing that thread at the wrong time can stall Dragon callbacks.

### VS Code (`debugpy`)

1. Install `debugpy`
2. Add a listener in your startup path
3. Attach from VS Code

```python
import debugpy
debugpy.listen(("localhost", 5678))
# debugpy.wait_for_client()
```

### `pdb`

```python
import pdb; pdb.set_trace()
```

This is useful only when natlink is launched from a terminal.

## Interactive Testing

```python
import sys
sys.coinit_flags = 2

import natlink as n
with n.natConnect():
    print("User:", n.getCurrentUser())
    print("Mic:", n.getMicState())
    n.playString("hello world")
```

## Documentation Workflow

Build and serve the docs (default):

```powershell
.\scripts\docs.ps1
```

Build only or serve only:

```powershell
.\scripts\docs.ps1 -Build
.\scripts\docs.ps1 -Serve
```

If the preview script fails to bind the port or crashes during startup, the
window stays open and waits for input so the error remains visible.
