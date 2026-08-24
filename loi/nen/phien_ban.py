"""Phiên bản và hằng số nền.

Mọi kết quả tính toán phải ghi kèm ENGINE_VERSION và RULESET_VERSION.
Đổi một trong hai thì kết quả cũ không còn so sánh trực tiếp được.
"""
from __future__ import annotations
from pathlib import Path
import os

ENGINE_VERSION = "0.4.0-zpzq-method-gate"
RULESET_VERSION = "RS-2026.08-ZPZQ.1"
SCHEMA_MIGRATIONS_TABLE = "schema_migrations"
GOC_DU_AN = Path(__file__).resolve().parents[2]
DUONG_DAN = {
    "goc": GOC_DU_AN,
    "migrations": GOC_DU_AN / "loi" / "kho_du_lieu" / "migrations",
    "mam": GOC_DU_AN / "du_lieu" / "mam",
    "ca_vang": GOC_DU_AN / "du_lieu" / "ca_vang",
    "kho": GOC_DU_AN / "du_lieu" / "kho",
    "lich_phap": GOC_DU_AN / "cau_hinh" / "lich_phap",
    "cham_diem": GOC_DU_AN / "cau_hinh" / "cham_diem",
}
DB_MAC_DINH = Path(os.environ.get("XEMNGAY_DB_PATH", str(DUONG_DAN["kho"] / "xemngay.sqlite3")))
