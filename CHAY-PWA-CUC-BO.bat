@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.11 -m venv .venv 2>nul || py -3 -m venv .venv
  if errorlevel 1 goto :err
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :err
)
start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m kich_ban.chay_app
exit /b 0
:err
echo.
echo Khong cai/chay duoc. Kiem tra Python 3.11+ va Internet.
pause
exit /b 1
