@echo off
chcp 65001 > nul
echo Starting Strix v2.0...
python "%~dp0strix.py"
if errorlevel 1 (
    echo.
    echo Error: Failed to start Strix
    echo Please make sure Python is installed and added to PATH
    pause
)
