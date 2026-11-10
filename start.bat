@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Stepwise Learn...
python -X utf8 start.py %*
pause
