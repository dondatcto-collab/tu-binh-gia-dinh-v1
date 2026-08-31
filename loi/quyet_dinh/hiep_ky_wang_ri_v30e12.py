"""V3.0E12 — Vương Nhật (王日) theo mùa + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷五 · 王官守相民日.
Bản định của sách giữ phép cổ: 王日春寅、夏巳、秋申、冬亥.
Chỉ tạo tín hiệu thuận khi token 王日 đã có trong 宜 của event inventory VERIFIED.
"""
from __future__ import annotations

SEASON_BY_MONTH_BRANCH = {
    "DAN":"SPRING","MAO":"SPRING","THIN":"SPRING",
    "TI":"SUMMER","NGO":"SUMMER","MUI":"SUMMER",
    "THAN":"AUTUMN","DAU":"AUTUMN","TUAT":"AUTUMN",
    "HOI":"WINTER","TY":"WINTER","SUU":"WINTER",
}
WANG_RI_BRANCH_BY_SEASON = {
    "SPRING":"DAN","SUMMER":"TI","AUTUMN":"THAN","WINTER":"HOI",
}
VALID_BRANCHES = frozenset(SEASON_BY_MONTH_BRANCH)


def wang_ri_branch(month_branch: str) -> str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return WANG_RI_BRANCH_BY_SEASON[SEASON_BY_MONTH_BRANCH[month_branch]]


def active_wang_ri_tokens(month_branch: str, day_branch: str) -> tuple[str, ...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("王日",) if day_branch == wang_ri_branch(month_branch) else ()


def calculator_status() -> dict:
    return {
        "extension_version":"V3_0E12_WANG_RI",
        "calculator":"SEASON_DAY_BRANCH_V30E12_WANG_RI",
        "active_tokens":("王日",),
        "numeric_score":None,
        "numeric_score_status":"LOCKED_OFF",
    }
