"""V3.0E21 schema overlay cho 天倉."""
from __future__ import annotations
from typing import Any
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE

def schema_overlay_v30e21(out:dict[str,Any])->dict[str,Any]:
    out=dict(out); scopes=list(out.get("implemented_scopes") or [])
    if "hiep_ky_v30e21_tian_cang" not in scopes: scopes.append("hiep_ky_v30e21_tian_cang")
    out["implemented_scopes"]=scopes
    out["hiep_ky_v30e21"]={"extension_version":"V3_0E21_TIAN_CANG","status":"PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","activated_token":"天倉","activated_token_vi":"Thiên Thương","calculator":"MONTH_REVERSE_BRANCH_V30E21_TIAN_CANG","source_scope":"欽定協紀辨方書 卷六 · 天倉正月起寅逆行十二辰; 可納財","coverage":COVERAGE,"decision_effect":"FAVORABLE_SUPPORT_ONLY","creates_hard_block":False,"full_classical_claim":False,"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
    return out
