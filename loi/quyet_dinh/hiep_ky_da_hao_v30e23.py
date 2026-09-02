"""V3.0E23 — 大耗 (Đại Hao).

Nguồn Hiệp Kỷ: 月破〈大耗〉, 正月起申順行十二辰.
Đây là quan hệ đối xung Chi tháng-ngày, nhưng giữ token/calculator riêng để truy vết.
"""
from __future__ import annotations

VALID_BRANCHES=("TY","SUU","DAN","MAO","THIN","TI","NGO","MUI","THAN","DAU","TUAT","HOI")
DA_HAO_BRANCH_BY_MONTH_BRANCH={
    "DAN":"THAN","MAO":"DAU","THIN":"TUAT","TI":"HOI","NGO":"TY","MUI":"SUU",
    "THAN":"DAN","DAU":"MAO","TUAT":"THIN","HOI":"TI","TY":"NGO","SUU":"MUI",
}


def da_hao_branch(chi_thang:str)->str:
    if chi_thang not in DA_HAO_BRANCH_BY_MONTH_BRANCH:
        raise ValueError("chi_thang khong hop le")
    return DA_HAO_BRANCH_BY_MONTH_BRANCH[chi_thang]


def active_da_hao_tokens(chi_thang:str,chi_ngay:str)->tuple[str,...]:
    if chi_ngay not in VALID_BRANCHES:
        raise ValueError("chi_ngay khong hop le")
    return ("大耗",) if chi_ngay==da_hao_branch(chi_thang) else ()


def calculator_status()->dict:
    return {"calculator":"MONTH_OPPOSITION_V30E23_DA_HAO","active_tokens":("大耗",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
