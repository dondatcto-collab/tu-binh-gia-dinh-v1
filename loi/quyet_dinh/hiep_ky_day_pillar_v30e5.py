"""V3.0E5 — calculator Thiên Nguyện (天願) theo Chi tháng + đủ Can Chi ngày.

Nguồn khóa:
- 《欽定協紀辨方書》卷五 · 天願
- 《御定星曆考原》卷三 · 天願

正月甲午、二月甲戌、三月乙酉、四月丙子、五月丁丑、六月戊午、
七月甲寅、八月丙辰、九月辛卯、十月戊辰、十一月甲子、十二月癸未。

Quy đổi tháng theo Chi tháng tiết khí hiện hành: Dần = chính nguyệt ... Sửu = tháng 12.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CAN, CHI

TIAN_YUAN_DAY_PILLAR_BY_MONTH_BRANCH: dict[str, tuple[str, str]] = {
    "DAN": ("GIAP", "NGO"),
    "MAO": ("GIAP", "TUAT"),
    "THIN": ("AT", "DAU"),
    "TI": ("BINH", "TY"),
    "NGO": ("DINH", "SUU"),
    "MUI": ("MAU", "NGO"),
    "THAN": ("GIAP", "DAN"),
    "DAU": ("BINH", "THIN"),
    "TUAT": ("TAN", "MAO"),
    "HOI": ("MAU", "THIN"),
    "TY": ("GIAP", "TY"),
    "SUU": ("QUY", "MUI"),
}


def tian_yuan_day_pillar(month_branch: str) -> tuple[str, str]:
    if month_branch not in CHI:
        raise ValueError(f"invalid month branch: {month_branch}")
    return TIAN_YUAN_DAY_PILLAR_BY_MONTH_BRANCH[month_branch]


def active_day_pillar_tokens(month_branch: str, day_stem: str, day_branch: str) -> tuple[str, ...]:
    if month_branch not in CHI:
        raise ValueError(f"invalid month branch: {month_branch}")
    if day_stem not in CAN:
        raise ValueError(f"invalid day stem: {day_stem}")
    if day_branch not in CHI:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("天願",) if (day_stem, day_branch) == tian_yuan_day_pillar(month_branch) else ()


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_PILLAR_V30E5",
        "active_tokens": ("天願",),
        "extension_version": "V3_0E5_TIAN_YUAN",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
