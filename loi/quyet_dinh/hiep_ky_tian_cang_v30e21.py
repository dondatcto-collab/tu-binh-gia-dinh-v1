"""V3.0E21 — Thiên Thương (天倉) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六: 天倉者正月起寅逆行十二辰.
"""
from __future__ import annotations

TIAN_CANG_BRANCH_BY_MONTH_BRANCH={
    "DAN":"DAN","MAO":"SUU","THIN":"TY","TI":"HOI","NGO":"TUAT","MUI":"DAU",
    "THAN":"THAN","DAU":"MUI","TUAT":"NGO","HOI":"TI","TY":"THIN","SUU":"MAO",
}
VALID_BRANCHES=frozenset(TIAN_CANG_BRANCH_BY_MONTH_BRANCH)

def tian_cang_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES: raise ValueError(f"invalid month branch: {month_branch}")
    return TIAN_CANG_BRANCH_BY_MONTH_BRANCH[month_branch]

def active_tian_cang_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES: raise ValueError(f"invalid day branch: {day_branch}")
    return ("天倉",) if day_branch==tian_cang_branch(month_branch) else ()

def calculator_status()->dict:
    return {"extension_version":"V3_0E21_TIAN_CANG","calculator":"MONTH_REVERSE_BRANCH_V30E21_TIAN_CANG","active_tokens":("天倉",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
