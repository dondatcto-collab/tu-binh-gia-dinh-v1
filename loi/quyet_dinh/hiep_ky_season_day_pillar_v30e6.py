"""V3.0E6 — calculator Thiên Xá (天赦) theo mùa tiết khí + đủ Can Chi ngày.

Nguồn khóa:
- 《御定星曆考原》卷三 · 天赦: 春戊寅、夏甲午、秋戊申、冬甲子
- 《欽定協紀辨方書》卷五 · 天赦

Quy ước mùa theo Chi tháng tiết khí hiện hành:
- Xuân: Dần, Mão, Thìn
- Hạ: Tỵ, Ngọ, Mùi
- Thu: Thân, Dậu, Tuất
- Đông: Hợi, Tý, Sửu
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CAN, CHI

TIAN_SHE_DAY_PILLAR_BY_MONTH_BRANCH: dict[str, tuple[str, str]] = {
    "DAN": ("MAU", "DAN"),
    "MAO": ("MAU", "DAN"),
    "THIN": ("MAU", "DAN"),
    "TI": ("GIAP", "NGO"),
    "NGO": ("GIAP", "NGO"),
    "MUI": ("GIAP", "NGO"),
    "THAN": ("MAU", "THAN"),
    "DAU": ("MAU", "THAN"),
    "TUAT": ("MAU", "THAN"),
    "HOI": ("GIAP", "TY"),
    "TY": ("GIAP", "TY"),
    "SUU": ("GIAP", "TY"),
}


def tian_she_day_pillar(month_branch: str) -> tuple[str, str]:
    if month_branch not in CHI:
        raise ValueError(f"invalid month branch: {month_branch}")
    return TIAN_SHE_DAY_PILLAR_BY_MONTH_BRANCH[month_branch]


def active_season_day_pillar_tokens(month_branch: str, day_stem: str, day_branch: str) -> tuple[str, ...]:
    if month_branch not in CHI:
        raise ValueError(f"invalid month branch: {month_branch}")
    if day_stem not in CAN:
        raise ValueError(f"invalid day stem: {day_stem}")
    if day_branch not in CHI:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("天赦",) if (day_stem, day_branch) == tian_she_day_pillar(month_branch) else ()


def calculator_status() -> dict:
    return {
        "calculator": "SEASON_DAY_PILLAR_V30E6",
        "active_tokens": ("天赦",),
        "extension_version": "V3_0E6_TIAN_SHE",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
