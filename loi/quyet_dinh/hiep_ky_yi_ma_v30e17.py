"""V3.0E17 — Dịch Mã (驛馬) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六 · 驛馬.
李鼎祚曰：驛馬者正月起申，逆行四孟。
"""
from __future__ import annotations

YI_MA_BRANCH_BY_MONTH_BRANCH = {
    "DAN":"THAN", "MAO":"TI", "THIN":"DAN", "TI":"HOI",
    "NGO":"THAN", "MUI":"TI", "THAN":"DAN", "DAU":"HOI",
    "TUAT":"THAN", "HOI":"TI", "TY":"DAN", "SUU":"HOI",
}
VALID_BRANCHES = frozenset(YI_MA_BRANCH_BY_MONTH_BRANCH)


def yi_ma_branch(month_branch: str) -> str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return YI_MA_BRANCH_BY_MONTH_BRANCH[month_branch]


def active_yi_ma_tokens(month_branch: str, day_branch: str) -> tuple[str, ...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("驛馬",) if day_branch == yi_ma_branch(month_branch) else ()


def calculator_status() -> dict:
    return {
        "extension_version":"V3_0E17_YI_MA",
        "calculator":"MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA",
        "active_tokens":("驛馬",),
        "numeric_score":None,
        "numeric_score_status":"LOCKED_OFF",
    }
