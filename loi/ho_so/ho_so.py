"""Hồ sơ gia đình.

Đơn giản nhất có thể: không tài khoản, không mật khẩu.
Một máy, một nhà, nhiều hồ sơ.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

NGUOI_DUNG_MAC_DINH = "U-GIA-DINH"


class HoSoError(Exception):
    pass


@dataclass(frozen=True)
class HoSo:
    profile_id: str
    full_name: str
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    birth_place_text: str
    timezone_name: str
    time_certainty: str = "KNOWN"
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "full_name": self.full_name,
            "gender": self.gender,
            "birth": {
                "year": self.birth_year, "month": self.birth_month,
                "day": self.birth_day, "hour": self.birth_hour,
                "minute": self.birth_minute,
            },
            "birth_place_text": self.birth_place_text,
            "timezone_name": self.timezone_name,
            "time_certainty": self.time_certainty,
            "note": self.note,
        }


def bao_dam_nguoi_dung(conn: sqlite3.Connection) -> str:
    conn.execute(
        "INSERT INTO users (user_id, display_name) VALUES (?, 'Gia đình') "
        "ON CONFLICT(user_id) DO NOTHING", (NGUOI_DUNG_MAC_DINH,))
    conn.commit()
    return NGUOI_DUNG_MAC_DINH


def _kiem(d: dict[str, Any]) -> list[str]:
    loi = []
    if not str(d.get("full_name", "")).strip():
        loi.append("Chưa nhập tên.")
    if d.get("gender") not in ("NAM", "NU"):
        loi.append("Giới tính phải là NAM hoặc NU.")
    try:
        datetime(int(d["birth_year"]), int(d["birth_month"]), int(d["birth_day"]),
                 int(d["birth_hour"]), int(d["birth_minute"]))
    except (KeyError, ValueError, TypeError):
        loi.append("Ngày giờ sinh không hợp lệ.")
    if not str(d.get("birth_place_text", "")).strip():
        loi.append("Chưa nhập nơi sinh.")
    if not str(d.get("timezone_name", "")).strip():
        loi.append("Chưa có múi giờ.")
    return loi


def tao(conn: sqlite3.Connection, **d: Any) -> HoSo:
    loi = _kiem(d)
    if loi:
        raise HoSoError("; ".join(loi))
    uid = bao_dam_nguoi_dung(conn)
    pid = d.get("profile_id") or f"P-{uuid.uuid4().hex[:10]}"
    conn.execute(
        "INSERT INTO profiles (profile_id, user_id, full_name, gender, note) "
        "VALUES (?,?,?,?,?)",
        (pid, uid, d["full_name"].strip(), d["gender"], d.get("note")))
    conn.execute(
        """INSERT INTO birth_data (birth_data_id, profile_id, birth_year, birth_month,
               birth_day, birth_hour, birth_minute, birth_place_text,
               timezone_name, time_certainty)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (f"B-{pid}", pid, int(d["birth_year"]), int(d["birth_month"]),
         int(d["birth_day"]), int(d["birth_hour"]), int(d["birth_minute"]),
         d["birth_place_text"].strip(), d["timezone_name"],
         d.get("time_certainty", "KNOWN")))
    conn.commit()
    return lay(conn, pid)


def lay(conn: sqlite3.Connection, profile_id: str) -> HoSo:
    r = conn.execute(
        """SELECT p.profile_id, p.full_name, p.gender, p.note, b.*
             FROM profiles p JOIN birth_data b ON b.profile_id = p.profile_id
            WHERE p.profile_id = ?""", (profile_id,)).fetchone()
    if r is None:
        raise HoSoError(f"KHONG_CO_HO_SO: {profile_id}")
    return HoSo(
        profile_id=r["profile_id"], full_name=r["full_name"], gender=r["gender"],
        birth_year=r["birth_year"], birth_month=r["birth_month"],
        birth_day=r["birth_day"], birth_hour=r["birth_hour"],
        birth_minute=r["birth_minute"], birth_place_text=r["birth_place_text"],
        timezone_name=r["timezone_name"] or "Asia/Ho_Chi_Minh",
        time_certainty=r["time_certainty"], note=r["note"])


def danh_sach(conn: sqlite3.Connection) -> list[HoSo]:
    rows = conn.execute(
        "SELECT profile_id FROM profiles ORDER BY created_at, full_name").fetchall()
    return [lay(conn, r["profile_id"]) for r in rows]


def sua(conn: sqlite3.Connection, profile_id: str, **d: Any) -> HoSo:
    cu = lay(conn, profile_id).to_dict()
    moi = {
        "full_name": d.get("full_name", cu["full_name"]),
        "gender": d.get("gender", cu["gender"]),
        "birth_year": d.get("birth_year", cu["birth"]["year"]),
        "birth_month": d.get("birth_month", cu["birth"]["month"]),
        "birth_day": d.get("birth_day", cu["birth"]["day"]),
        "birth_hour": d.get("birth_hour", cu["birth"]["hour"]),
        "birth_minute": d.get("birth_minute", cu["birth"]["minute"]),
        "birth_place_text": d.get("birth_place_text", cu["birth_place_text"]),
        "timezone_name": d.get("timezone_name", cu["timezone_name"]),
    }
    loi = _kiem(moi)
    if loi:
        raise HoSoError("; ".join(loi))
    conn.execute(
        "UPDATE profiles SET full_name=?, gender=?, note=?, updated_at=datetime('now') "
        "WHERE profile_id=?",
        (moi["full_name"].strip(), moi["gender"], d.get("note", cu["note"]), profile_id))
    conn.execute(
        """UPDATE birth_data SET birth_year=?, birth_month=?, birth_day=?,
               birth_hour=?, birth_minute=?, birth_place_text=?, timezone_name=?,
               updated_at=datetime('now')
             WHERE profile_id=?""",
        (int(moi["birth_year"]), int(moi["birth_month"]), int(moi["birth_day"]),
         int(moi["birth_hour"]), int(moi["birth_minute"]),
         moi["birth_place_text"].strip(), moi["timezone_name"], profile_id))
    conn.commit()
    return lay(conn, profile_id)


def xoa(conn: sqlite3.Connection, profile_id: str) -> None:
    lay(conn, profile_id)
    conn.execute("DELETE FROM profiles WHERE profile_id = ?", (profile_id,))
    conn.commit()
