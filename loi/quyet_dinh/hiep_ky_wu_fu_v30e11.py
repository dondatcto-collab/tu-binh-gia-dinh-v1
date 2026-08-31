"""V3.0E11 — Ngũ Phú (五富) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六 · 五富
總要歷曰：五富者，富盛之神也，其日宜興舉運動估市經求。
歷例曰：正月起亥，順行四孟。

Quy ước tháng của project dùng Chi tháng:
Dần=tháng 1, Mão=2, Thìn=3, Tỵ=4, Ngọ=5, Mùi=6,
Thân=7, Dậu=8, Tuất=9, Hợi=10, Tý=11, Sửu=12.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

WU_FU_BRANCH_BY_MONTH_BRANCH = {
    "DAN": "HOI", "MAO": "DAN", "THIN": "TI", "TI": "THAN",
    "NGO": "HOI", "MUI": "DAN", "THAN": "TI", "DAU": "THAN",
    "TUAT": "HOI", "HOI": "DAN", "TY": "TI", "SUU": "THAN",
}


def _chuan(chi: str) -> str:
    x = str(chi or "").strip().upper()
    if x not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return x


def wu_fu_branch(chi_thang: str) -> str:
    return WU_FU_BRANCH_BY_MONTH_BRANCH[_chuan(chi_thang)]


def active_wu_fu_tokens(chi_thang: str, chi_ngay: str) -> tuple[str, ...]:
    m, d = _chuan(chi_thang), _chuan(chi_ngay)
    return ("五富",) if d == WU_FU_BRANCH_BY_MONTH_BRANCH[m] else ()


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU",
        "active_tokens": ("五富",),
        "source_rule": "欽定協紀辨方書 卷六 · 五富: 歷例曰正月起亥順行四孟",
        "extension_version": "V3_0E11_WU_FU",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
