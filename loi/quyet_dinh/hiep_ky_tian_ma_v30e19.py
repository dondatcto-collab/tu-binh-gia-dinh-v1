"""V3.0E19 — Thiên Mã (天馬) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷六 · 天馬.
李鼎祚曰：天馬者正月起午，順行六陽辰。
"""
from __future__ import annotations

TIAN_MA_BRANCH_BY_MONTH_BRANCH={
    "DAN":"NGO","MAO":"THAN","THIN":"TUAT","TI":"TY","NGO":"DAN","MUI":"THIN",
    "THAN":"NGO","DAU":"THAN","TUAT":"TUAT","HOI":"TY","TY":"DAN","SUU":"THIN",
}
VALID_BRANCHES=frozenset(TIAN_MA_BRANCH_BY_MONTH_BRANCH)

def tian_ma_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES: raise ValueError(f"invalid month branch: {month_branch}")
    return TIAN_MA_BRANCH_BY_MONTH_BRANCH[month_branch]

def active_tian_ma_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES: raise ValueError(f"invalid day branch: {day_branch}")
    return ("天馬",) if day_branch==tian_ma_branch(month_branch) else ()

def calculator_status()->dict:
    return {"extension_version":"V3_0E19_TIAN_MA","calculator":"MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA","active_tokens":("天馬",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
