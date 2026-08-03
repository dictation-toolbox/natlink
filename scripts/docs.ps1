param(
    [switch]$Build,
    [switch]$Serve
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

# Default: build + serve
if (-not $Build -and -not $Serve) {
    $Build = $true
    $Serve = $true
}

Push-Location $repoRoot
try {
    if ($Build) {
        uv run mkdocs build -f mkdocs.yml
    }
    if ($Serve) {
        uv run mkdocs serve -f mkdocs.yml -a 127.0.0.1:8001
    }
}
catch {
    Write-Host ""
    Write-Host "Failed:" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    Write-Host ""
    if ($Serve) { Read-Host "Press Enter to close" }
    throw
}
finally {
    Pop-Location
}
