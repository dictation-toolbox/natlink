<#
.SYNOPSIS
    Set up a natlink development environment.

.DESCRIPTION
    Creates a 64-bit Python virtual environment and installs natlink
    in editable mode with all dev/test dependencies.

    Uses uv if available (fast, supports Python version selection and download).
    Falls back to the system Python if uv is not installed.

    Can be run any way:
        . .\setup_dev.ps1          # dot-source: activates in current shell
        .\setup_dev.ps1            # regular: opens new activated shell
        double-click setup_dev.cmd # from Explorer: opens new activated shell

.EXAMPLE
    . .\setup_dev.ps1
#>

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$VenvDir = Join-Path $Root ".venv"

# Detect if we were dot-sourced (activation persists in caller's shell)
$DotSourced = $MyInvocation.InvocationName -eq '.' -or $MyInvocation.Line -match '^\.\s'

function Test-Python64 {
    param([string]$PythonExe)
    try {
        $arch = & $PythonExe -c "import struct; print(struct.calcsize('P') * 8)"
        return $arch.Trim() -eq "64"
    } catch {
        return $false
    }
}

function Enter-Venv {
    $ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    if ($DotSourced) {
        & $ActivateScript
        Write-Host "Activated in current shell."
    } else {
        Write-Host "Opening activated shell..."
        Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "& '$ActivateScript'; Set-Location '$Root'; Write-Host 'Natlink dev environment activated.'; Write-Host ''; Write-Host 'Install:       natlink install [--startup]'; Write-Host 'Uninstall:     natlink uninstall'; Write-Host 'Start tray:    natlink start'; Write-Host 'Run tests:     pytest tests -m minimal -v'; Write-Host 'Deactivate:    deactivate (virtual environment)'; Write-Host ''" -WorkingDirectory $Root
    }
}

try {
    # --- If .venv exists, just activate ---
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    if (Test-Path $VenvPython) {
        Write-Host ".venv already exists."
        $ver = & $VenvPython -c "import sys; print(sys.version)"
        Write-Host "Python: $ver"
        Enter-Venv
        return
    }

    # --- Check for uv ---
    $UseUv = $false
    try {
        $null = Get-Command uv -ErrorAction Stop
        $UseUv = $true
    } catch {}

    if ($UseUv) {
        Write-Host "Available Python versions (64-bit):"
        Write-Host ""
        $raw = uv python list 2>&1
        $entries = @()
        foreach ($line in $raw) {
            $text = "$line"
            if ($text -match "^cpython-(\d+\.\d+\.\d+)-windows-x86_64" -and $text -notmatch "freethreaded") {
                $fullVer = $Matches[1]
                $major = ($fullVer -split '\.')[0..1] -join '.'
                $majorInt = [int]($fullVer -split '\.')[1]
                if ($majorInt -ge 10) {
                    $status = "download"
                    if ($text -notmatch "<download available>") {
                        $status = "installed"
                    }
                    $entries += @{ Full = $fullVer; Major = $major; Status = $status }
                }
            }
        }

        $seen = @{}
        $choices = @()
        foreach ($e in $entries) {
            if (-not $seen.ContainsKey($e.Major)) {
                $seen[$e.Major] = $true
                $choices += $e
            }
        }

        if ($choices.Count -eq 0) {
            throw "No compatible Python versions found via uv"
        }

        for ($i = 0; $i -lt $choices.Count; $i++) {
            $e = $choices[$i]
            $tag = "(will download)"
            if ($e.Status -eq "installed") { $tag = "(installed)" }
            Write-Host "  [$($i + 1)] Python $($e.Full)  $tag"
        }

        Write-Host ""
        $choice = Read-Host "Select version (1-$($choices.Count))"
        if (-not ($choice -match "^\d+$" -and [int]$choice -ge 1 -and [int]$choice -le $choices.Count)) {
            throw "Invalid selection: $choice"
        }
        $PythonVersion = $choices[[int]$choice - 1].Full

        Write-Host ""
        Write-Host "Creating .venv with Python $PythonVersion via uv..."
        uv venv $VenvDir --python $PythonVersion --seed
        if ($LASTEXITCODE -ne 0) { throw "uv venv failed" }

        $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
        if (-not (Test-Python64 $VenvPython)) {
            throw "Created a 32-bit Python. Natlink requires 64-bit."
        }
    } else {
        $SysPython = (Get-Command python -ErrorAction Stop).Source
        Write-Host "Using system Python: $SysPython"

        if (-not (Test-Python64 $SysPython)) {
            throw "System Python is 32-bit. Natlink requires 64-bit Python."
        }

        $ver = & $SysPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        Write-Host "Python version: $ver"
        Write-Host ""
        Write-Host "Tip: Install uv for faster setup and Python version management:"
        Write-Host '  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
        Write-Host ""
        Write-Host "Creating .venv..."
        & $SysPython -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
    }

    # --- Install ---
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    $EditableSpec = "${Root}[full,test,dev]"

    Write-Host ""
    Write-Host "Installing natlink in editable mode with dev dependencies..."

    if ($UseUv) {
        uv pip install -e $EditableSpec --python $VenvPython
        if ($LASTEXITCODE -ne 0) { throw "uv pip install failed" }
    } else {
        $VenvPip = Join-Path $VenvDir "Scripts\pip.exe"
        & $VenvPip install --upgrade pip --quiet
        & $VenvPip install -e $EditableSpec
        if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
    }

    # --- Verify and activate ---
    Write-Host ""
    Write-Host "=== Development environment ready ==="
    $pyVer = & $VenvPython -c "import sys; print(sys.version)"
    Write-Host "  Python: $pyVer"
    $bits = & $VenvPython -c "import struct; print(struct.calcsize('P') * 8)"
    Write-Host "  Architecture: $bits-bit"
    Write-Host ""
    Enter-Venv
}
catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    if ([Environment]::UserInteractive -and -not $env:CI) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}
