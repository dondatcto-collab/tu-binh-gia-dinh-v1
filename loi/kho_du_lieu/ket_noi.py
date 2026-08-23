"""Mở kết nối cơ sở dữ liệu và chạy bộ chuyển đổi lược đồ."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from loi.nen.phien_ban import DB_MAC_DINH, DUONG_DAN, SCHEMA_MIGRATIONS_TABLE


def mo_ket_noi(duong_dan: Path | str | None = None) -> sqlite3.Connection:
    """Mở kết nối. Luôn bật kiểm tra khoá ngoại — không có ngoại lệ."""
    dich = Path(duong_dan) if duong_dan else DB_MAC_DINH
    if dich != Path(":memory:"):
        dich.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(dich), timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _bao_dam_bang_migration(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_MIGRATIONS_TABLE} (
            filename    TEXT PRIMARY KEY,
            checksum    TEXT NOT NULL,
            applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def danh_sach_migration(thu_muc: Path | None = None) -> list[Path]:
    thu_muc = thu_muc or DUONG_DAN["migrations"]
    return sorted(thu_muc.glob("*.sql"))


def chay_migration(
    conn: sqlite3.Connection, thu_muc: Path | None = None
) -> list[str]:
    """Chạy các tệp chuyển đổi chưa chạy. Trả về danh sách tệp vừa chạy.

    Nếu một tệp đã chạy nhưng nội dung bị đổi, dừng ngay và báo lỗi.
    Không cho phép sửa lịch sử lược đồ.
    """
    _bao_dam_bang_migration(conn)
    da_chay = {
        r["filename"]: r["checksum"]
        for r in conn.execute(f"SELECT filename, checksum FROM {SCHEMA_MIGRATIONS_TABLE}")
    }

    vua_chay: list[str] = []
    for tep in danh_sach_migration(thu_muc):
        noi_dung = tep.read_text(encoding="utf-8")
        checksum = hashlib.sha256(noi_dung.encode("utf-8")).hexdigest()
        if tep.name in da_chay:
            if da_chay[tep.name] != checksum:
                raise RuntimeError(
                    f"MIGRATION_DA_BI_SUA: {tep.name} đã chạy nhưng nội dung khác. "
                    "Phải tạo tệp chuyển đổi mới, không sửa tệp cũ."
                )
            continue
        conn.executescript(noi_dung)
        conn.execute(
            f"INSERT INTO {SCHEMA_MIGRATIONS_TABLE} (filename, checksum) VALUES (?, ?)",
            (tep.name, checksum),
        )
        conn.commit()
        vua_chay.append(tep.name)

    # executescript có thể tắt pragma; bật lại cho chắc.
    conn.execute("PRAGMA foreign_keys = ON")
    return vua_chay


def danh_sach_bang(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return {r["name"] for r in rows}
