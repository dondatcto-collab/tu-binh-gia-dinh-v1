"""V3.0E10 — Giải Thần (解神) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷五 · 解神
歷例曰：正二月申，三四月戌，五六月子，七八月寅，九十月辰，十一月十二月午也。
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

GIAI_THAN_BRANCH_BY_MONTH_BRANCH = {
    "DAN": "THAN", "MAO": "THAN",
    "THIN": "TUAT", "TI": "TUAT",
    "NGO": "TY", "MUI": "TY",
    "THAN": "DAN", "DAU": "DAN",
    "TUAT": "THIN", "HOI": "THIN",
    "TY": "NGO", "SUU": "NGO",
}


def _chuan(chi: str) -> str:
    x = str(chi or "").strip().upper()
    if x not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return x


def giai_than_branch(chi_thang: str) -> str:
    return GIAI_THAN_BRANCH_BY_MONTH_BRANCH[_chuan(chi_thang)]


def active_giai_than_tokens(chi_thang: str, chi_ngay: str) -> tuple[str, ...]:
    m, d = _chuan(chi_thang), _chuan(chi_ngay)
    return ("解神",) if d == GIAI_THAN_BRANCH_BY_MONTH_BRANCH[m] else ()


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN",
        "active_tokens": ("解神",),
        "source_rule": "欽定協紀辨方書 卷五 · 解神: 正二月申、三四月戌、五六月子、七八月寅、九十月辰、十一十二月午",
        "extension_version": "V3_0E10_GIAI_THAN",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
