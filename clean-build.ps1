# Clean and rebuild ChromaScape after stale output / locked file errors
# Usage: Right-click → Run with PowerShell, or: powershell -File clean-build.ps1

$ErrorActionPreference = "Stop"
$buildDir = Join-Path $PSScriptRoot "ChromaScape\build"

# Kill any running Java processes
$javaProcs = Get-Process -Name java, javaw -ErrorAction SilentlyContinue
if ($javaProcs) {
    Write-Host "Stopping Java processes..."
    $javaProcs | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Delete build directory
if (Test-Path $buildDir) {
    Write-Host "Deleting $buildDir..."
    Remove-Item -Recurse -Force $buildDir
}

Write-Host "Running osrs-bot build..."
osrs-bot build

Write-Host "Done. Run 'osrs-bot run' to start."
