"""V3.0E14 — Tướng Nhật (相日) theo mùa + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷五 · 王官守相民日.
Công thức: 相日春巳、夏申、秋亥、冬寅.
"""
from __future__ import annotations

SEASON_BY_MONTH_BRANCH={
    "DAN":"SPRING","MAO":"SPRING","THIN":"SPRING",
    "TI":"SUMMER","NGO":"SUMMER","MUI":"SUMMER",
    "THAN":"AUTUMN","DAU":"AUTUMN","TUAT":"AUTUMN",
    "HOI":"WINTER","TY":"WINTER","SUU":"WINTER",
}
XIANG_RI_BRANCH_BY_SEASON={"SPRING":"TI","SUMMER":"THAN","AUTUMN":"HOI","WINTER":"DAN"}
VALID_BRANCHES=frozenset(SEASON_BY_MONTH_BRANCH)


def xiang_ri_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid month branch: {month_branch}")
    return XIANG_RI_BRANCH_BY_SEASON[SEASON_BY_MONTH_BRANCH[month_branch]]


def active_xiang_ri_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES:
        raise ValueError(f"invalid day branch: {day_branch}")
    return ("相日",) if day_branch==xiang_ri_branch(month_branch) else ()


def calculator_status()->dict:
    return {"extension_version":"V3_0E14_XIANG_RI","calculator":"SEASON_DAY_BRANCH_V30E14_XIANG_RI","active_tokens":("相日",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
