@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Stepwise Learn...

REM 用 goto 标签而非嵌套括号：cmd 会提前展开块内的 %errorlevel%，嵌套判断会误判
where python >nul 2>nul
if %errorlevel%==0 goto RUN_PYTHON
where py >nul 2>nul
if %errorlevel%==0 goto RUN_PY
goto NO_PYTHON

:RUN_PYTHON
python -X utf8 start.py %*
goto END

:RUN_PY
py -3 -X utf8 start.py %*
goto END

:NO_PYTHON
echo.
echo [!] 未找到 Python。请先安装 Python 3.9 或更新版本，
echo     安装时勾选 "Add Python to PATH"，然后重新双击本文件。
echo     下载地址: https://www.python.org/downloads/
echo.

:END
pause
