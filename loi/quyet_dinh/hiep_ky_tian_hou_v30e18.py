"""V3.0E18 — Thiên Hậu (天后) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六 · 驛馬/天后.
歷例曰：天后與驛馬同位。
Vì vậy dùng cùng vị trí tháng-ngày với 驛馬, nhưng giữ token và event scope độc lập.
"""
from __future__ import annotations

from loi.quyet_dinh.hiep_ky_yi_ma_v30e17 import YI_MA_BRANCH_BY_MONTH_BRANCH

TIAN_HOU_BRANCH_BY_MONTH_BRANCH = dict(YI_MA_BRANCH_BY_MONTH_BRANCH)
VALID_BRANCHES = frozenset(TIAN_HOU_BRANCH_BY_MONTH_BRANCH)


def tian_hou_branch(month_branch: str) -> str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return TIAN_HOU_BRANCH_BY_MONTH_BRANCH[month_branch]


def active_tian_hou_tokens(month_branch: str, day_branch: str) -> tuple[str, ...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("天后",) if day_branch == tian_hou_branch(month_branch) else ()


def calculator_status() -> dict:
    return {
        "extension_version":"V3_0E18_TIAN_HOU",
        "calculator":"MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU",
        "active_tokens":("天后",),
        "numeric_score":None,
        "numeric_score_status":"LOCKED_OFF",
    }
