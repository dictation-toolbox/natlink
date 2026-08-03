$ErrorActionPreference = "Stop"

# Re-launch elevated if not admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    return
}

Write-Host "Stopping Dragon Logger service..."
Stop-Service DragonLoggerService -ErrorAction SilentlyContinue

Write-Host "Clearing Dragon logs..."
Get-ChildItem "$env:ProgramData\Nuance\NaturallySpeaking*\logs" -Directory -ErrorAction SilentlyContinue |
    ForEach-Object {
        Remove-Item "$($_.FullName)\*\*.log" -ErrorAction SilentlyContinue
        Write-Host "  Cleared: $($_.FullName)"
    }

Write-Host "Clearing natlink logs..."
Remove-Item "$env:LOCALAPPDATA\natlink\*.log" -ErrorAction SilentlyContinue

Write-Host "Starting Dragon Logger service..."
Start-Service DragonLoggerService

Write-Host "Done."
