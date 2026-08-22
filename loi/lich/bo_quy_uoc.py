"""Bộ tải và kiểm định bộ quy ước lịch.

Nguyên tắc: phần tính toán KHÔNG được chứa hằng số về mốc đổi năm, đổi tháng,
đổi ngày. Muốn biết mốc nào thì phải hỏi lớp BoQuyUocLich này.

Có một hàm canh cửa là `kiem_khong_hard_code` để chứng minh điều đó bằng test.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from loi.nen.phien_ban import DUONG_DAN

KHOA_BAT_BUOC = (
    "YEAR_BOUNDARY",
    "MONTH_BOUNDARY",
    "DAY_BOUNDARY",
    "TRUE_SOLAR_TIME",
    "LOCAL_TIMEZONE",
    "HISTORICAL_TIMEZONE",
    "HOUR_STEM_LATE_ZI",
    "GANZHI_RULESET",
    "HOUR_STEM_LATE_ZI_STATUS",
    "HOUR_STEM_LATE_ZI_SCORING",
)

GIA_TRI_CHO_PHEP = {
    "YEAR_BOUNDARY": {"LI_CHUN", "SOLAR_NEW_YEAR", "LUNAR_NEW_YEAR"},
    "MONTH_BOUNDARY": {"JIE", "QI", "LUNAR_MONTH"},
    "HOUR_STEM_LATE_ZI": {"DUNG_CAN_NGAY_HIEN_TAI", "DUNG_CAN_NGAY_HOM_SAU"},
    "HOUR_STEM_LATE_ZI_STATUS": {"VERIFIED", "NOT_VERIFIED"},
    "HOUR_STEM_LATE_ZI_SCORING": {"FOR_GOLDEN_SCORING", "NOT_FOR_GOLDEN_SCORING"},
}

MAU_GIO = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


class CalendarRulesetError(Exception):
    pass


@dataclass(frozen=True)
class ThietLap:
    key: str
    value: str
    value_type: str
    notes: str | None = None


@dataclass(frozen=True)
class BoQuyUocLich:
    calendar_ruleset_id: str
    version: str
    name_vi: str
    status: str
    is_default: bool
    source_id: str | None
    notes: str | None
    settings: dict[str, ThietLap]

    # -- cách duy nhất để phần tính toán lấy thiết lập ------------------
    def lay(self, key: str) -> str:
        if key not in self.settings:
            raise CalendarRulesetError(
                f"THIEU_THIET_LAP: bộ lịch {self.calendar_ruleset_id} không có khoá {key}"
            )
        return self.settings[key].value

    def lay_bool(self, key: str) -> bool:
        return self.lay(key).strip().lower() in {"true", "1", "on", "yes"}

    @property
    def moc_doi_ngay(self) -> str:
        return self.lay("DAY_BOUNDARY")

    @property
    def moc_doi_ngay_phut(self) -> int:
        """Mốc đổi ngày quy ra số phút kể từ 00:00. Dùng để so sánh 00:00 với 23:00."""
        gio, phut = self.moc_doi_ngay.split(":")
        return int(gio) * 60 + int(phut)

    @property
    def doi_ngay_luc_nua_dem(self) -> bool:
        return self.moc_doi_ngay_phut == 0

    @property
    def gio_ty_dem_da_xac_minh(self) -> bool:
        return self.lay("HOUR_STEM_LATE_ZI_STATUS") == "VERIFIED"

    @property
    def gio_ty_dem_duoc_cham_diem(self) -> bool:
        return self.lay("HOUR_STEM_LATE_ZI_SCORING") == "FOR_GOLDEN_SCORING"


# ---------------------------------------------------------------
# Tải từ tệp cấu hình
# ---------------------------------------------------------------

def tai_tu_tep(duong_dan: Path) -> BoQuyUocLich:
    raw: dict[str, Any] = yaml.safe_load(duong_dan.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise CalendarRulesetError(f"CAU_HINH_HONG: {duong_dan.name} không phải bảng khoá-giá trị")

    settings_raw = raw.get("settings") or {}
    settings = {
        k: ThietLap(
            key=k,
            value=str(v["value"]),
            value_type=str(v.get("type", "STRING")).upper(),
            notes=v.get("notes"),
        )
        for k, v in settings_raw.items()
    }

    bo = BoQuyUocLich(
        calendar_ruleset_id=raw["calendar_ruleset_id"],
        version=str(raw["version"]),
        name_vi=raw["name_vi"],
        status=raw.get("status", "ACTIVE"),
        is_default=bool(raw.get("is_default", False)),
        source_id=raw.get("source_id"),
        notes=raw.get("notes"),
        settings=settings,
    )
    kiem_bo_quy_uoc(bo)
    return bo


def tai_tat_ca(thu_muc: Path | None = None) -> dict[str, BoQuyUocLich]:
    thu_muc = thu_muc or DUONG_DAN["lich_phap"]
    ket_qua: dict[str, BoQuyUocLich] = {}
    for tep in sorted(thu_muc.glob("*.yaml")):
        bo = tai_tu_tep(tep)
        if bo.calendar_ruleset_id in ket_qua:
            raise CalendarRulesetError(f"TRUNG_ID: {bo.calendar_ruleset_id}")
        ket_qua[bo.calendar_ruleset_id] = bo

    mac_dinh = [b for b in ket_qua.values() if b.is_default]
    if len(mac_dinh) != 1:
        raise CalendarRulesetError(
            f"MAC_DINH_SAI: phải có đúng một bộ lịch mặc định, đang có {len(mac_dinh)}"
        )
    return ket_qua


# ---------------------------------------------------------------
# Kiểm định
# ---------------------------------------------------------------

def kiem_bo_quy_uoc(bo: BoQuyUocLich) -> None:
    thieu = [k for k in KHOA_BAT_BUOC if k not in bo.settings]
    if thieu:
        raise CalendarRulesetError(
            f"THIEU_KHOA: {bo.calendar_ruleset_id} thiếu {', '.join(thieu)}"
        )

    for key, cho_phep in GIA_TRI_CHO_PHEP.items():
        gia_tri = bo.settings[key].value
        if gia_tri not in cho_phep:
            raise CalendarRulesetError(
                f"GIA_TRI_LA: {bo.calendar_ruleset_id}.{key} = {gia_tri}"
            )

    moc = bo.settings["DAY_BOUNDARY"].value
    if not MAU_GIO.match(moc):
        raise CalendarRulesetError(
            f"MOC_DOI_NGAY_SAI: {bo.calendar_ruleset_id}.DAY_BOUNDARY = {moc}, cần dạng HH:MM"
        )

    for key in ("TRUE_SOLAR_TIME", "LOCAL_TIMEZONE", "HISTORICAL_TIMEZONE"):
        if bo.settings[key].value.strip().lower() not in {"true", "false"}:
            raise CalendarRulesetError(
                f"GIA_TRI_BOOL_SAI: {bo.calendar_ruleset_id}.{key}"
            )

    if bo.status == "EXPERIMENTAL" and bo.is_default:
        raise CalendarRulesetError(
            f"THU_NGHIEM_LAM_MAC_DINH: {bo.calendar_ruleset_id} đang thử nghiệm mà đặt mặc định"
        )


# ---------------------------------------------------------------
# Đồng bộ vào cơ sở dữ liệu
# ---------------------------------------------------------------

def dong_bo_vao_db(conn: sqlite3.Connection, bo: BoQuyUocLich) -> None:
    conn.execute(
        """
        INSERT INTO calendar_rulesets
            (calendar_ruleset_id, version, name_vi, source_id, status, is_default, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(calendar_ruleset_id) DO UPDATE SET
            version = excluded.version,
            name_vi = excluded.name_vi,
            status  = excluded.status,
            is_default = excluded.is_default,
            notes   = excluded.notes,
            updated_at = datetime('now')
        """,
        (bo.calendar_ruleset_id, bo.version, bo.name_vi, bo.source_id,
         bo.status, int(bo.is_default), bo.notes),
    )
    for st in bo.settings.values():
        conn.execute(
            """
            INSERT INTO calendar_ruleset_settings
                (calendar_ruleset_id, setting_key, setting_value, value_type, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(calendar_ruleset_id, setting_key) DO UPDATE SET
                setting_value = excluded.setting_value,
                value_type    = excluded.value_type,
                notes         = excluded.notes
            """,
            (bo.calendar_ruleset_id, st.key, st.value, st.value_type, st.notes),
        )


def tai_tu_db(conn: sqlite3.Connection, calendar_ruleset_id: str) -> BoQuyUocLich:
    row = conn.execute(
        "SELECT * FROM calendar_rulesets WHERE calendar_ruleset_id = ?",
        (calendar_ruleset_id,),
    ).fetchone()
    if row is None:
        raise CalendarRulesetError(f"KHONG_CO_BO_LICH: {calendar_ruleset_id}")

    rows = conn.execute(
        "SELECT * FROM calendar_ruleset_settings WHERE calendar_ruleset_id = ?",
        (calendar_ruleset_id,),
    ).fetchall()
    settings = {
        r["setting_key"]: ThietLap(r["setting_key"], r["setting_value"],
                                   r["value_type"], r["notes"])
        for r in rows
    }
    bo = BoQuyUocLich(
        calendar_ruleset_id=row["calendar_ruleset_id"],
        version=row["version"],
        name_vi=row["name_vi"],
        status=row["status"],
        is_default=bool(row["is_default"]),
        source_id=row["source_id"],
        notes=row["notes"],
        settings=settings,
    )
    kiem_bo_quy_uoc(bo)
    return bo


def bo_mac_dinh(conn: sqlite3.Connection) -> BoQuyUocLich:
    row = conn.execute(
        "SELECT calendar_ruleset_id FROM calendar_rulesets WHERE is_default = 1"
    ).fetchone()
    if row is None:
        raise CalendarRulesetError("KHONG_CO_BO_LICH_MAC_DINH")
    return tai_tu_db(conn, row["calendar_ruleset_id"])


# ---------------------------------------------------------------
# Canh cửa: cấm nhét mốc lịch vào mã tính toán
# ---------------------------------------------------------------

# Cấm GIÁ TRỊ của mốc lịch, không cấm TÊN KHOÁ.
# Đọc khoá từ cấu hình là việc bắt buộc; chép sẵn giá trị mới là vi phạm.
CAC_TU_CAM = ("LI_CHUN", "SOLAR_NEW_YEAR", "LUNAR_NEW_YEAR",
              "23:00", "00:00", "1380")

# Tầng phiên dịch cấu hình được phép nhắc tên giá trị.
TEP_DUOC_MIEN = {"bo_quy_uoc.py", "quy_uoc_can_chi.py"}


# Chỉ bắt khi giá trị đứng thành một chuỗi TRỌN VẸN, ví dụ "00:00".
# Không bắt khi nó là một phần của chuỗi khác, ví dụ "+00:00" trong mốc ISO.
_MAU_VI_PHAM = tuple(
    re.compile(r"""(?P<q>["'])""" + re.escape(tu) + r"""(?P=q)""")
    for tu in CAC_TU_CAM
)


def kiem_khong_hard_code(goc: Path | None = None) -> list[str]:
    """Quét mã trong `loi/` xem có ai tự nhét GIÁ TRỊ mốc lịch vào không.

    Trả về danh sách vi phạm. Rỗng nghĩa là sạch.
    """
    goc = goc or DUONG_DAN["goc"] / "loi"
    vi_pham: list[str] = []
    for tep in goc.rglob("*.py"):
        if tep.name in TEP_DUOC_MIEN:
            continue
        noi_dung = tep.read_text(encoding="utf-8")
        for dong_so, dong in enumerate(noi_dung.splitlines(), start=1):
            ma = dong.split("#", 1)[0]
            for tu, mau in zip(CAC_TU_CAM, _MAU_VI_PHAM):
                if mau.search(ma):
                    vi_pham.append(f"{tep.relative_to(goc.parent)}:{dong_so} chứa {tu!r}")
    return vi_pham
