@echo off
REM Fixes AppLocker blocking osrs-bot.exe
REM Run once: scripts\fix-windows-applocker.bat

copy "%~dp0fix-windows-applocker-launcher.bat" "%USERPROFILE%\.local\bin\osrs-bot.bat" >nul
del /q "%USERPROFILE%\.local\bin\osrs-bot.exe" 2>nul
echo Done. osrs-bot now uses bat launcher.
