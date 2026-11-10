@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Stepwise Learn...
where python >nul 2>nul
if %errorlevel%==0 (
  python -X utf8 start.py %*
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -X utf8 start.py %*
  ) else (
    echo.
    echo [!] 未找到 Python。请先安装 Python 3.9 或更新版本，
    echo     安装时勾选 "Add Python to PATH"，然后重新双击本文件。
    echo     下载地址: https://www.python.org/downloads/
    echo.
  )
)
pause
