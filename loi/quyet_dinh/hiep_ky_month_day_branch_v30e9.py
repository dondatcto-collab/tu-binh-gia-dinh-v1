"""V3.0E9 — bộ tính Thiên Y (天醫) theo Chi tháng + Chi ngày.

Nguồn khóa: 《欽定協紀辨方書》卷五 · 天醫:
- 總要歷: 天醫 là thần y, ngày này hợp thỉnh thuốc/trị bệnh.
- 歷例: 天醫者正月起戌順行十二辰 — tháng Giêng bắt đầu ở Tuất, thuận 12 Chi.

Quy ước tháng tiết khí của app: Dần = 正月, Mão = 二月 ... Sửu = 十二月.
Rule không phụ thuộc Can ngày. Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

TIAN_YI_BRANCH_BY_MONTH_BRANCH = {
    "DAN": "TUAT",
    "MAO": "HOI",
    "THIN": "TY",
    "TI": "SUU",
    "NGO": "DAN",
    "MUI": "MAO",
    "THAN": "THIN",
    "DAU": "TI",
    "TUAT": "NGO",
    "HOI": "MUI",
    "TY": "THAN",
    "SUU": "DAU",
}


def _chuan_chi(chi: str) -> str:
    value = str(chi or "").strip().upper()
    if value not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return value


def tian_yi_branch(month_branch: str) -> str:
    return TIAN_YI_BRANCH_BY_MONTH_BRANCH[_chuan_chi(month_branch)]


def active_month_day_branch_tokens(month_branch: str, day_branch: str) -> tuple[str, ...]:
    month = _chuan_chi(month_branch)
    day = _chuan_chi(day_branch)
    return ("天醫",) if TIAN_YI_BRANCH_BY_MONTH_BRANCH[month] == day else ()


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_BRANCH_V30E9",
        "active_tokens": ("天醫",),
        "source_rule": "欽定協紀辨方書卷五 · 天醫: 歷例曰天醫者正月起戌順行十二辰",
        "extension_version": "V3_0E9_TIAN_YI",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
