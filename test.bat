@echo off
REM Pull latest and launch ChromaScape
REM Double-click this file or run from PowerShell

cd /d "%~dp0"
git pull

cd ChromaScape
call gradlew.bat bootRun
