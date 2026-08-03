# Contributing

Audience: contributors and maintainers working on natlink itself.

Purpose: document the core development workflow for setting up the repo,
running tests, and building documentation.

See also:

- [Developer Debugging](developer-debugging.md)
- [Testing](testing.md)
- [Architecture](architecture.md)

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (package manager)
- Windows 10 or 11

## Development Setup

Create a virtual environment and install all dependencies:

```powershell
uv venv .venv --python 3.14
uv pip install -e .[dev] --python .venv\Scripts\python.exe

.venv\Scripts\activate
or
uv run natlink-ui --install-shortcuts
```

## Building the Package

Build sdist + wheel:

```powershell
uv build
```

Output goes to `dist/`.

## Building Marshal DLLs and TLB Wrappers

After changing `.idl` files, rebuild the marshal DLLs and regenerate the
vendored comtypes wrappers:

```powershell
.\scripts\build.ps1                  # full rebuild: DLLs + TLBs + vendored wrappers
.\scripts\build.ps1 -SkipDll         # regenerate Python wrappers only (TLBs must exist)
```

This single script runs MIDL to produce marshal DLLs and type libraries,
then generates the vendored comtypes Python wrappers (`_gen_v13_v14.py`,
`_gen_v15_v16.py`) from those TLBs. The `.tlb` files remain in the repo
for regeneration but are not shipped in the wheel.

## Changing Dragon COM Interfaces

When adding, removing, or modifying a Dragon COM interface, several files
must be updated in a specific order. This section walks through each scenario.

### Files involved

| File | Role | Updated by |
|------|------|------------|
| `src/natlink_com/*.idl` | Interface definitions (source of truth) | You, by hand |
| `src/natlink_com/*.tlb` | Type libraries (compiled from IDL) | `build.ps1` (MIDL) |
| `src/natlink_com/marshal64_*.dll` | Proxy/stub DLLs for cross-bitness marshaling | `build.ps1` (CMake) |
| `src/natlink_com/_gen_*.py` | Vendored comtypes wrappers (interfaces + structs) | `build.ps1` (comtypes) |
| `src/natlink_com/_guids.py` | IIDs used for raw QueryInterface / QueryService | You, by hand |
| `src/natlink_com/_marshaling.py` | IIDs registered for cross-process marshaling | You, by hand |

### Adding a new interface

1. **Add the interface to the IDL** — define it in
   `dragon_interfaces_v15_v16.idl` (and `v13_v14.idl` if Dragon 13 needs it).
   Include the IID, method signatures, and any new structs.

2. **Rebuild** — run `.\scripts\build.ps1`. This compiles the IDL via MIDL,
   rebuilds the marshal DLLs, and regenerates the vendored Python wrappers.

3. **Register for marshaling** — if the interface is used cross-process
   (Python ↔ Dragon), add its IID to the `MARSHAL_INTERFACES` dict in
   `_marshaling.py`. Without this, `CoRegisterPSClsid` won't register a
   proxy/stub for the interface and cross-process calls will fail with
   `E_NOINTERFACE`.

4. **Add the IID to `_guids.py`** — if you need to call `qi_raw()` or
   `call_query_service()` with the new IID (raw vtable calls that bypass
   comtypes), add a `GUID` constant.

5. **Write consumer code** — use the interface via `get_tlb()`:
   ```python
   tlb = get_tlb()
   iface = obj.QueryInterface(tlb.IMyNewInterface)
   iface.MyMethod(args)
   ```

### Modifying an existing interface

1. **Edit the IDL** — change the method signature. Be careful with parameter
   order and types — the vtable slot indices are positional, and existing
   callers will crash if the layout changes unexpectedly.

2. **Rebuild** — `.\scripts\build.ps1`

3. **Update consumer code** — any Python code calling the modified method
   must match the new signature.

Struct changes are picked up automatically — the vendored wrappers contain
all struct definitions, and consumer code accesses them via `get_tlb()`.

### Adding a new struct

1. **Define it in the IDL** — structs are defined as MIDL typedefs.

2. **Rebuild** — `.\scripts\build.ps1`

3. **Use it** — the struct is available via `get_tlb().MyNewStruct`.

### Removing an interface

1. **Remove from IDL**, rebuild, then remove the IID from `_marshaling.py`
   and `_guids.py`, and delete all consumer code.

### Common mistakes

- **Forgetting `_marshaling.py`** — the interface works in-process but fails
  cross-process with `E_NOINTERFACE`. This is the most common oversight.
- **IID mismatch** — the IID in `_guids.py` must exactly match the IDL.
  Copy-paste from the IDL `uuid(...)` attribute.
- **Version variants** — if the interface differs between Dragon 13 and
  Dragon 15, it needs entries in both `v13_v14.idl` and `v15_v16.idl`.
  The vendored wrappers are version-specific; `_tlb.py` selects the
  correct one at runtime.

## Building Documentation

Build and serve the docs (default):

```powershell
.\scripts\docs.ps1
```

Build only or serve only:

```powershell
.\scripts\docs.ps1 -Build
.\scripts\docs.ps1 -Serve
```

The rendered site is written to `site/`. The preview server binds to
`http://127.0.0.1:8001/`.

