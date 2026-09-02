"""V3.0E15 — Dân Nhật (民日) theo mùa + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷五 · 王官守相民日.
Phép cổ: 民日春午、夏酉、秋子、冬卯.
"""
from __future__ import annotations

SEASON_BY_MONTH_BRANCH={
    "DAN":"SPRING","MAO":"SPRING","THIN":"SPRING",
    "TI":"SUMMER","NGO":"SUMMER","MUI":"SUMMER",
    "THAN":"AUTUMN","DAU":"AUTUMN","TUAT":"AUTUMN",
    "HOI":"WINTER","TY":"WINTER","SUU":"WINTER",
}
MIN_RI_BRANCH_BY_SEASON={"SPRING":"NGO","SUMMER":"DAU","AUTUMN":"TY","WINTER":"MAO"}
VALID_BRANCHES=frozenset(SEASON_BY_MONTH_BRANCH)


def min_ri_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return MIN_RI_BRANCH_BY_SEASON[SEASON_BY_MONTH_BRANCH[month_branch]]


def active_min_ri_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("民日",) if day_branch==min_ri_branch(month_branch) else ()


def calculator_status()->dict:
    return {"extension_version":"V3_0E15_MIN_RI","calculator":"SEASON_DAY_BRANCH_V30E15_MIN_RI","active_tokens":("民日",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
