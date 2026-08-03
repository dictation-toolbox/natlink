<#
.SYNOPSIS
    Build all native artifacts from IDL sources.

.DESCRIPTION
    Rebuilds everything that derives from the Dragon IDL files:

      1. Stops Dragon and the natlink launcher (files are locked otherwise)
      2. Builds 64-bit marshal DLLs via CMake/MIDL (also produces .tlb files)
      3. Regenerates vendored comtypes Python wrappers from the .tlb files

    This is the single command to run after any .idl change.

    Requires:
      - CMake 3.20+
      - Visual Studio 2019/2022/2026 with C++ Desktop workload
      - uv (https://docs.astral.sh/uv/) with the project venv set up

.EXAMPLE
    .\build.ps1                # Release (default)
    .\build.ps1 -Config Debug  # Debug
    .\build.ps1 -SkipDll       # Regenerate Python wrappers only (TLBs must exist)
#>

param(
    [ValidateSet("Release", "Debug")]
    [string]$Config = "Release",

    [switch]$SkipDll
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PkgDir = Join-Path $RepoRoot "src\natlink_com"
$ScriptsDir = $PSScriptRoot
$PushedLocation = $false

# --- Stop natlink launcher via shutdown event (clean) ---

function Stop-NatlinkLauncher {
    try {
        $event = [System.Threading.EventWaitHandle]::OpenExisting("NatlinkShutdown")
        Write-Host "Signaling natlink launcher to shut down..."
        $event.Set()
        $event.Close()
        Start-Sleep -Seconds 3
    }
    catch [System.Threading.WaitHandleCannotBeOpenedException] {
        # Event doesn't exist — no launcher running
    }

    # Fallback: force-kill if still running
    $procs = Get-CimInstance Win32_Process -Filter "Name like 'python%' and CommandLine like '%natlink_com%_launcher%'" -ErrorAction SilentlyContinue
    foreach ($proc in $procs) {
        Write-Host "Force-stopping natlink launcher (PID $($proc.ProcessId))..."
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}

# --- Stop Dragon ---

function Stop-Dragon {
    $dragon = Get-Process natspeak -ErrorAction SilentlyContinue
    if ($dragon) {
        Write-Host "Stopping Dragon NaturallySpeaking..."
        Stop-Process -Name natspeak -Force
        Start-Sleep -Seconds 2
    }
}

# --- Verify build outputs are not locked ---

$DllOutputs = @(
    "marshal64_v13_v14.dll", "marshal64_v15_v16.dll",
    "dragon_interfaces_v13_v14.tlb", "dragon_interfaces_v15_v16.tlb"
)

function Test-OutputsUnlocked {
    foreach ($file in $DllOutputs) {
        $path = Join-Path $PkgDir $file
        if (Test-Path $path) {
            try {
                [IO.File]::Open($path, 'Open', 'ReadWrite', 'None').Close()
            }
            catch {
                throw "$file is locked by another process. Close it and try again."
            }
        }
    }
}

# --- Detect VS generator ---

function Get-VSPreset {
    $vsVersions = @(
        @{ Configure = "vs2026"; Release = "Release-vs2026"; Debug = "Debug-vs2026" },
        @{ Configure = "vs2022"; Release = "Release";         Debug = "Debug" },
        @{ Configure = "vs2019"; Release = "Release-vs2019"; Debug = "Debug-vs2019" }
    )
    foreach ($vs in $vsVersions) {
        $out = cmake --preset $vs.Configure 2>&1
        if ($LASTEXITCODE -eq 0) { return $vs }
    }
    throw "No supported Visual Studio installation found"
}

# --- Main ---

try {
    Push-Location $RepoRoot
    $PushedLocation = $true

    if (-not $SkipDll) {
        Stop-NatlinkLauncher
        Stop-Dragon
        Test-OutputsUnlocked

        # --- Step 1: Build marshal DLLs + TLBs ---
        Write-Host "`n=== Step 1: Building 64-bit marshal DLLs ($Config) ===`n"

        $preset = Get-VSPreset
        $buildPreset = $preset[$Config]

        cmake --build --preset $buildPreset
        if ($LASTEXITCODE -ne 0) { throw "CMake build failed" }

        Write-Host "`nDLL outputs:"
        foreach ($file in $DllOutputs) {
            $path = Join-Path $PkgDir $file
            if (Test-Path $path) {
                $size = [math]::Round((Get-Item $path).Length / 1024)
                Write-Host "  $file  (${size}KB)"
            }
        }
    }
    else {
        Write-Host "`n=== Skipping DLL build (--SkipDll) ==="
        # Verify TLBs exist
        foreach ($variant in @("v13_v14", "v15_v16")) {
            $tlb = Join-Path $PkgDir "dragon_interfaces_$variant.tlb"
            if (-not (Test-Path $tlb)) {
                throw "TLB not found: $tlb (run without -SkipDll first)"
            }
        }
    }

    # --- Step 2: Generate vendored Python wrappers ---
    Write-Host "`n=== Step 2: Generating vendored comtypes wrappers ===`n"

    uv run (Join-Path $ScriptsDir "gen_tlb_wrappers.py")
    if ($LASTEXITCODE -ne 0) { throw "TLB wrapper generation failed" }

    # --- Step 3: Smoke test ---
    Write-Host "`nVerifying imports..."
    uv run python -c @"
import sys; sys.coinit_flags = 2; sys.path.insert(0, 'src')
from natlink_com._tlb import get_tlb
tlb = get_tlb()
assert hasattr(tlb, 'ISRCentralW'), 'Missing ISRCentralW'
assert hasattr(tlb, 'SDATA'), 'Missing SDATA'
from natlink_com._action_sink import create_action_sink
from natlink_com._engine_sink import create_engine_sink
print('  All imports OK')
"@
    if ($LASTEXITCODE -ne 0) { throw "Smoke test failed" }

    Write-Host "`n=== Build complete ===" -ForegroundColor Green
}
catch {
    Write-Host "`nERROR: $_" -ForegroundColor Red
}
finally {
    if ($PushedLocation) {
        Pop-Location
    }
    Read-Host "`nPress Enter to exit"
}
