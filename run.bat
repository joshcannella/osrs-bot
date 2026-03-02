@echo off
REM Pull latest and launch ChromaScape
REM Usage: run.bat [--launch-browser]

cd /d "%~dp0"
git pull
git submodule update --init --recursive

cd ChromaScape
call gradlew.bat clean compileJava

if "%1"=="--launch-browser" start http://localhost:8080

call gradlew.bat bootRun
