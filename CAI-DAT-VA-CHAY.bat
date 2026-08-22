@echo off
chcp 65001 >nul
setlocal
title Tu Binh Gia Dinh - V1
cd /d "%~dp0"

echo ============================================================
echo   TU BINH GIA DINH - V1
echo ============================================================
echo.

py -3.11 --version >nul 2>&1
if errorlevel 1 (
  python --version >nul 2>&1
  if errorlevel 1 (
    echo [LOI] May chua co Python 3.11 tro len.
    echo Hay cai Python tai https://www.python.org/downloads/
    echo Khi cai nho tick "Add Python to PATH".
    pause
    exit /b 1
  )
  set PY=python
) else (
  set PY=py -3.11
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Tao moi truong rieng .venv ...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
) else (
  echo [1/4] Moi truong .venv da co.
)

set VPY=.venv\Scripts\python.exe

echo [2/4] Cai/kiem tra thu vien ...
%VPY% -m pip install --quiet --upgrade pip
%VPY% -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo [LOI] Khong cai duoc thu vien. Kiem tra ket noi Internet va thu lai.
  pause
  exit /b 1
)

%VPY% -c "import astronomy, pymeeus, fastapi, uvicorn, yaml; print('Thu vien: OK')"
if errorlevel 1 goto :fail

echo [3/4] Chuan bi kho du lieu ...
%VPY% -c "from loi.kho_du_lieu.ket_noi import mo_ket_noi,chay_migration; from loi.kho_du_lieu.nap_mam import nap_mam; c=mo_ket_noi(); chay_migration(c); nap_mam(c); c.close(); print('Kho du lieu: OK')"
if errorlevel 1 goto :fail

echo [4/4] Khoi dong ung dung ...
echo.
echo   Trang chu : http://127.0.0.1:8000
echo   Huong dan : http://127.0.0.1:8000/huong-dan
echo   Dung app   : bam Ctrl+C trong cua so nay.
echo ============================================================
start "" http://127.0.0.1:8000
%VPY% -m kich_ban.chay_app
exit /b 0

:fail
echo.
echo [LOI] Qua trinh cai dat/chay bi dung. Hay chup man hinh loi de kiem tra.
pause
exit /b 1
