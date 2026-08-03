<#
.SYNOPSIS
    Run the project's contracts: layering, docs, tests.

.DESCRIPTION
    There is no CI, so these only run when someone runs them. Each check is
    already configured in the repo but silent until invoked:

      lint-imports          the three-layer import contract
                            (pyproject.toml [tool.importlinter])
      mkdocs build --strict warns become errors, so a stale API reference or
                            a page missing from the nav fails
      pytest                the suite; live tests auto-skip without Dragon

    Opt-in groups are deselected by default and are not run here:
    `pytest -m teardown` (disconnects the shared session to observe sink
    release; costs ~70s), `-m experimental`, `-m nsformat`.

    Runs all three by default and reports every failure rather than stopping
    at the first, so one pass tells you everything that is broken.

.PARAMETER Imports
    Run only the import-linter contract.

.PARAMETER Docs
    Run only the strict docs build.

.PARAMETER Tests
    Run only the test suite.

.PARAMETER RestartDragon
    Pass --restart-dragon to pytest: restarts Dragon and waits until it
    accepts a COM connection. Use for measurement runs -- Dragon carries
    state between sessions, which skews the refcount assertions in
    tests/test_resource_release.py.

.EXAMPLE
    .\scripts\check.ps1
    .\scripts\check.ps1 -Tests -RestartDragon
#>
param(
    [switch]$Imports,
    [switch]$Docs,
    [switch]$Tests,
    [switch]$RestartDragon
)

$repoRoot = Split-Path -Parent $PSScriptRoot

# No switches given: run everything.
if (-not $Imports -and -not $Docs -and -not $Tests) {
    $Imports = $true; $Docs = $true; $Tests = $true
}

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

$failures = @()

function Invoke-Check {
    param([string]$Name, [scriptblock]$Body)
    Write-Host ""
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    & $Body
    if ($LASTEXITCODE -ne 0) {
        $script:failures += $Name
        Write-Host "$Name FAILED" -ForegroundColor Red
    } else {
        Write-Host "$Name ok" -ForegroundColor Green
    }
}

Push-Location $repoRoot
try {
    if ($Imports) {
        Invoke-Check "import contract" {
            # Declared in the dev extra but not installed by default.
            & $python -c "import importlinter" 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "installing import-linter..." -ForegroundColor Yellow
                & $python -m pip install --quiet "import-linter>=2.0"
            }
            & $python -m importlinter.cli lint-imports
        }
    }

    if ($Docs) {
        Invoke-Check "docs (strict)" { & $python -m mkdocs build --strict }
    }

    if ($Tests) {
        Invoke-Check "tests" {
            $args = @("-m", "pytest", "tests", "-q", "--no-cov")
            if ($RestartDragon) { $args += "--restart-dragon" }
            & $python @args
        }
    }

    Write-Host ""
    if ($failures.Count -gt 0) {
        Write-Host ("FAILED: " + ($failures -join ", ")) -ForegroundColor Red
        exit 1
    }
    Write-Host "All checks passed." -ForegroundColor Green
}
finally {
    Pop-Location
}
