"""Đồ dùng chung cho kiểm thử. Mỗi bài test có cơ sở dữ liệu riêng, sạch."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
if str(GOC) not in sys.path:
    sys.path.insert(0, str(GOC))

from loi.kho_du_lieu.ket_noi import chay_migration, mo_ket_noi  # noqa: E402
from loi.kho_du_lieu.nap_mam import nap_mam  # noqa: E402


@pytest.fixture
def db_trong(tmp_path) -> sqlite3.Connection:
    """Cơ sở dữ liệu đã chuyển đổi lược đồ nhưng chưa nạp mầm."""
    conn = mo_ket_noi(tmp_path / "test.sqlite3")
    chay_migration(conn)
    yield conn
    conn.close()


@pytest.fixture
def db_da_nap(db_trong) -> sqlite3.Connection:
    """Cơ sở dữ liệu đã chuyển đổi và đã nạp mầm."""
    nap_mam(db_trong)
    return db_trong
