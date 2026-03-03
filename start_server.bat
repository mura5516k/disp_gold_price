@echo off
setlocal

cd /d "%~dp0"

echo [INFO] Starting gold price web server...
echo [INFO] Open: http://localhost:8000

after_start:
python server.py
if %errorlevel% neq 0 (
  echo [ERROR] Failed to start with "python". Trying "py -3"...
  py -3 server.py
)

if %errorlevel% neq 0 (
  echo [ERROR] Could not start server. Please check Python installation.
  pause
)

endlocal
