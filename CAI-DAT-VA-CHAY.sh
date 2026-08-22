#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "============================================================"
echo "  TỬ BÌNH GIA ĐÌNH - V1"
echo "============================================================"
command -v python3 >/dev/null || { echo "[LỖI] Cần Python 3.11 trở lên."; exit 1; }
if [ ! -x .venv/bin/python ]; then
  echo "[1/4] Tạo môi trường riêng .venv..."
  python3 -m venv .venv
else
  echo "[1/4] .venv đã có."
fi
VPY=.venv/bin/python
echo "[2/4] Cài/kiểm tra thư viện..."
$VPY -m pip install --quiet --upgrade pip
$VPY -m pip install --quiet -r requirements.txt
$VPY -c "import astronomy, pymeeus, fastapi, uvicorn, yaml; print('Thư viện: OK')"
echo "[3/4] Chuẩn bị kho dữ liệu..."
$VPY -c "from loi.kho_du_lieu.ket_noi import mo_ket_noi,chay_migration; from loi.kho_du_lieu.nap_mam import nap_mam; c=mo_ket_noi(); chay_migration(c); nap_mam(c); c.close(); print('Kho dữ liệu: OK')"
echo "[4/4] Khởi động..."
echo "  http://127.0.0.1:8000"
echo "  Dừng: Ctrl+C"
$VPY -m kich_ban.chay_app
