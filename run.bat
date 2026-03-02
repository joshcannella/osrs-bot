@echo off
REM Pull latest and launch ChromaScape
REM Double-click this file or run from PowerShell

cd /d "%~dp0"
git pull
git submodule update --init --recursive

cd ChromaScape
start http://localhost:8080
call gradlew.bat bootRun
