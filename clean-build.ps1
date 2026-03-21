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

# Check for RuneLite holding KInput.dll
Write-Host "Checking for processes locking build files..."
$runeliteProcs = Get-Process -Name RuneLite -ErrorAction SilentlyContinue
if ($runeliteProcs) {
    Write-Host "Found RuneLite process(es) that may be locking DLL files:"
    $runeliteProcs | ForEach-Object { Write-Host "  - PID $($_.Id): $($_.ProcessName)" }
    Write-Host "Stopping RuneLite..."
    $runeliteProcs | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Delete build directory
if (Test-Path $buildDir) {
    Write-Host "Deleting $buildDir..."
    try {
        Remove-Item -Recurse -Force $buildDir -ErrorAction Stop
        Write-Host "Build directory deleted successfully."
    } catch {
        Write-Host "ERROR: Failed to delete build directory. Diagnosing..."
        
        # Find what's still locking files
        $lockedFiles = Get-ChildItem -Path $buildDir -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object { 
                try { 
                    [System.IO.File]::OpenWrite($_.FullName).Close()
                    $false 
                } catch { 
                    $true 
                }
            }
        
        if ($lockedFiles) {
            Write-Host "Locked files detected:"
            $lockedFiles | ForEach-Object { Write-Host "  - $($_.FullName)" }
        }
        
        # Try to find processes with handles to build directory
        Write-Host "`nProcesses that may be holding locks:"
        Get-Process | Where-Object { 
            $_.Modules.FileName -like "*$buildDir*" -or 
            $_.ProcessName -like "*java*" -or 
            $_.ProcessName -like "*gradle*" -or
            $_.ProcessName -like "*RuneLite*"
        } | Select-Object ProcessName, Id | Format-Table
        
        throw "Cannot delete build directory. Kill remaining processes manually and retry."
    }
}

Write-Host "Running osrs-bot build..."
osrs-bot build

Write-Host "Done. Run 'osrs-bot run' to start."
