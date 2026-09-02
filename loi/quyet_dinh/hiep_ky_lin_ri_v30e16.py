"""V3.0E16 — Lâm Nhật (臨日) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六 · 臨日.
歷例曰：正月午、二月亥、三月申、四月丑、五月戌、六月卯、七月子、八月巳、九月寅、十月未、十一月辰、十二月酉。
"""
from __future__ import annotations

LIN_RI_BRANCH_BY_MONTH_BRANCH = {
    "DAN":"NGO", "MAO":"HOI", "THIN":"THAN", "TI":"SUU",
    "NGO":"TUAT", "MUI":"MAO", "THAN":"TY", "DAU":"TI",
    "TUAT":"DAN", "HOI":"MUI", "TY":"THIN", "SUU":"DAU",
}
VALID_BRANCHES = frozenset(LIN_RI_BRANCH_BY_MONTH_BRANCH)


def lin_ri_branch(month_branch: str) -> str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return LIN_RI_BRANCH_BY_MONTH_BRANCH[month_branch]


def active_lin_ri_tokens(month_branch: str, day_branch: str) -> tuple[str, ...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("臨日",) if day_branch == lin_ri_branch(month_branch) else ()


def calculator_status() -> dict:
    return {
        "extension_version":"V3_0E16_LIN_RI",
        "calculator":"MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI",
        "active_tokens":("臨日",),
        "numeric_score":None,
        "numeric_score_status":"LOCKED_OFF",
    }
