"""V3.0E1 — bộ tính Nguyệt Đức (月徳) theo Chi tháng + Can ngày.

Nguồn khóa: 《欽定協紀辨方書》卷五 · 月徳; đối chiếu 《淵海子平》.
Quy tắc: 寅午戌月丙、亥卯未月甲、申子辰月壬、巳酉丑月庚.
Không suy rộng sang 月徳合 hoặc cát thần Can-ngày khác. Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CAN, CHI

YUE_DE_STEM_BY_MONTH_BRANCH = {
    "DAN": "BINH", "NGO": "BINH", "TUAT": "BINH",
    "HOI": "GIAP", "MAO": "GIAP", "MUI": "GIAP",
    "THAN": "NHAM", "TY": "NHAM", "THIN": "NHAM",
    "TI": "CANH", "DAU": "CANH", "SUU": "CANH",
}


def _chuan_chi(chi: str) -> str:
    x = str(chi or "").strip().upper()
    if x not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return x


def _chuan_can(can: str) -> str:
    x = str(can or "").strip().upper()
    if x not in CAN:
        raise ValueError(f"CAN_KHONG_HOP_LE: {can}")
    return x


def yue_de_stem(chi_thang: str) -> str:
    return YUE_DE_STEM_BY_MONTH_BRANCH[_chuan_chi(chi_thang)]


def active_stem_tokens(chi_thang: str, can_ngay: str) -> tuple[str, ...]:
    m, d = _chuan_chi(chi_thang), _chuan_can(can_ngay)
    return ("月徳",) if d == YUE_DE_STEM_BY_MONTH_BRANCH[m] else ()


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_STEM_V30E1",
        "active_tokens": ("月徳",),
        "source_rule": "卷五 · 月徳: 寅午戌月丙、亥卯未月甲、申子辰月壬、巳酉丑月庚",
        "extension_version": "V3_0E1_YUE_DE",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
