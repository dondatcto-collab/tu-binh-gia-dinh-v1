"""V3.0E22 — 除神 (Trừ Thần).

Nguồn Hiệp Kỷ: 五離〈除神〉, 申酉日. Chỉ tính theo Chi ngày.
"""
from __future__ import annotations

VALID_BRANCHES={"TY","SUU","DAN","MAO","THIN","TI","NGO","MUI","THAN","DAU","TUAT","HOI"}
CHU_SHEN_DAY_BRANCHES=frozenset({"THAN","DAU"})


def active_chu_shen_tokens(chi_ngay:str)->tuple[str,...]:
    if chi_ngay not in VALID_BRANCHES:
        raise ValueError("chi_ngay khong hop le")
    return ("除神",) if chi_ngay in CHU_SHEN_DAY_BRANCHES else ()


def calculator_status()->dict:
    return {"calculator":"DAY_BRANCH_V30E22_CHU_SHEN","active_tokens":("除神",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
