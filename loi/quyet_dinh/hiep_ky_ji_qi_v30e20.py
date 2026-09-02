"""V3.0E20 — Cát Kỳ (吉期) theo Chi tháng + Chi ngày.

Nguồn: 《欽定協紀辨方書》卷四: 吉期常居月建前一辰.
Trong ví dụ cùng đoạn: Dần là Nguyệt Kiến thì Mão là vị trí trước một chi.
"""
from __future__ import annotations

BRANCH_ORDER=("TY","SUU","DAN","MAO","THIN","TI","NGO","MUI","THAN","DAU","TUAT","HOI")
VALID_BRANCHES=frozenset(BRANCH_ORDER)
JI_QI_BRANCH_BY_MONTH_BRANCH={b:BRANCH_ORDER[(i+1)%12] for i,b in enumerate(BRANCH_ORDER)}

def ji_qi_branch(month_branch:str)->str:
    if month_branch not in VALID_BRANCHES: raise ValueError(f"invalid month branch: {month_branch}")
    return JI_QI_BRANCH_BY_MONTH_BRANCH[month_branch]

def active_ji_qi_tokens(month_branch:str,day_branch:str)->tuple[str,...]:
    if day_branch not in VALID_BRANCHES: raise ValueError(f"invalid day branch: {day_branch}")
    return ("吉期",) if day_branch==ji_qi_branch(month_branch) else ()

def calculator_status()->dict:
    return {"extension_version":"V3_0E20_JI_QI","calculator":"MONTH_NEXT_BRANCH_V30E20_JI_QI","active_tokens":("吉期",),"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
