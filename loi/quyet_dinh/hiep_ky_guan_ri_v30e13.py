"""V3.0E13 — Quan Nhật (官日) theo mùa + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷五 · 王官守相民日.
Phép cổ: 官日春卯、夏午、秋酉、冬子.
"""
from __future__ import annotations

SEASON_BY_MONTH_BRANCH={
    "DAN":"SPRING","MAO":"SPRING","THIN":"SPRING",
    "TI":"SUMMER","NGO":"SUMMER","MUI":"SUMMER",
    "THAN":"AUTUMN","DAU":"AUTUMN","TUAT":"AUTUMN",
    "HOI":"WINTER","TY":"WINTER","SUU":"WINTER",
}
GUAN_RI_BRANCH_BY_SEASON={"SPRING":"MAO","SUMMER":"NGO","AUTUMN":"DAU","WINTER":"TY"}
VALID_BRANCHES=frozenset(SEASON_BY_MONTH_BRANCH)


def guan_ri_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return GUAN_RI_BRANCH_BY_SEASON[SEASON_BY_MONTH_BRANCH[month_branch]]


def active_guan_ri_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("官日",) if day_branch==guan_ri_branch(month_branch) else ()


def calculator_status()->dict:
    return {"extension_version":"V3_0E13_GUAN_RI","calculator":"SEASON_DAY_BRANCH_V30E13_GUAN_RI","active_tokens":("官日",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
