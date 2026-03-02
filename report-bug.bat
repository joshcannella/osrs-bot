@echo off
REM Report a bug: copy log, open template, commit and push
REM Usage: report-bug.bat <script-id>
REM Example: report-bug.bat al-kharid-iron-mining

if "%~1"=="" (
    echo Usage: report-bug.bat ^<script-id^>
    echo Example: report-bug.bat al-kharid-iron-mining
    exit /b 1
)

set SCRIPT_ID=%~1
set SPEC_DIR=.kiro\specs\scripts\%SCRIPT_ID%

if not exist "%SPEC_DIR%" (
    echo Error: %SPEC_DIR% does not exist
    exit /b 1
)

REM Copy runtime log if it exists
if exist "ChromaScape\logs\chromascape.log" (
    copy "ChromaScape\logs\chromascape.log" "%SPEC_DIR%\runtime.log" >nul
    echo Copied runtime log to %SPEC_DIR%\runtime.log
) else (
    echo No log file found at ChromaScape\logs\chromascape.log
)

REM Create bug report from template if it doesn't exist
if not exist "%SPEC_DIR%\bug-report.md" (
    copy ".kiro\specs\scripts\BUG-TEMPLATE.md" "%SPEC_DIR%\bug-report.md" >nul
)

REM Open bug report in default editor
echo Opening bug report — fill it in, save, then close the editor
start /wait notepad "%SPEC_DIR%\bug-report.md"

REM Commit and push
git add "%SPEC_DIR%\bug-report.md" "%SPEC_DIR%\runtime.log" 2>nul
git commit -m "bug report: %SCRIPT_ID%"
git push

echo Done — switch to Linux, pull, and ask osrs-scripter to fix it
