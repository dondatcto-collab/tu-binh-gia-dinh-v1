"""V3.0E4 — bộ tính Tứ Tướng (四相) theo mùa + Can ngày.

Nguồn khóa:
- 《御定星曆考原》卷三 · 四相: 春丙丁、夏戊己、秋壬癸、冬甲乙.
- 《欽定協紀辨方書》卷五 · 四相, cùng công thức.

Quy ước tháng tiết khí hiện hành:
- Xuân: Dần, Mão, Thìn
- Hạ: Tỵ, Ngọ, Mùi
- Thu: Thân, Dậu, Tuất
- Đông: Hợi, Tý, Sửu

Chỉ trả token 四相 khi Can ngày thuộc cặp Can của mùa. Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CAN, CHI

SI_XIANG_STEMS_BY_MONTH_BRANCH: dict[str, tuple[str, str]] = {
    "DAN": ("BINH", "DINH"),
    "MAO": ("BINH", "DINH"),
    "THIN": ("BINH", "DINH"),
    "TI": ("MAU", "KY"),
    "NGO": ("MAU", "KY"),
    "MUI": ("MAU", "KY"),
    "THAN": ("NHAM", "QUY"),
    "DAU": ("NHAM", "QUY"),
    "TUAT": ("NHAM", "QUY"),
    "HOI": ("GIAP", "AT"),
    "TY": ("GIAP", "AT"),
    "SUU": ("GIAP", "AT"),
}


def _chuan_chi(chi: str) -> str:
    value = str(chi or "").strip().upper()
    if value not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return value


def _chuan_can(can: str) -> str:
    value = str(can or "").strip().upper()
    if value not in CAN:
        raise ValueError(f"CAN_KHONG_HOP_LE: {can}")
    return value


def si_xiang_stems(chi_thang: str) -> tuple[str, str]:
    return SI_XIANG_STEMS_BY_MONTH_BRANCH[_chuan_chi(chi_thang)]


def active_season_stem_tokens(chi_thang: str, can_ngay: str) -> tuple[str, ...]:
    month = _chuan_chi(chi_thang)
    day_stem = _chuan_can(can_ngay)
    return ("四相",) if day_stem in SI_XIANG_STEMS_BY_MONTH_BRANCH[month] else ()


def calculator_status() -> dict:
    return {
        "calculator": "SEASON_DAY_STEM_V30E4",
        "active_tokens": ("四相",),
        "source_rule": "御定星曆考原卷三 / 欽定協紀辨方書卷五 · 四相: 春丙丁、夏戊己、秋壬癸、冬甲乙",
        "extension_version": "V3_0E4_SI_XIANG",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
