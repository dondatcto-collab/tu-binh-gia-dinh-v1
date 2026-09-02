"""V3.0E20 schema overlay cho 吉期, giữ schema lịch sử bất biến."""
from __future__ import annotations
from typing import Any
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE


def schema_overlay_v30e20(out:dict[str,Any])->dict[str,Any]:
    out=dict(out)
    scopes=list(out.get("implemented_scopes") or [])
    if "hiep_ky_v30e20_ji_qi" not in scopes: scopes.append("hiep_ky_v30e20_ji_qi")
    out["implemented_scopes"]=scopes
    out["hiep_ky_v30e20"]={
        "extension_version":"V3_0E20_JI_QI","status":"PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",
        "activated_token":"吉期","activated_token_vi":"Cát Kỳ","calculator":"MONTH_NEXT_BRANCH_V30E20_JI_QI",
        "source_scope":"欽定協紀辨方書 卷四 · 吉期常居月建前一辰; 卷十 · 除日〈吉期〉; 卷十一 · 出行/上官赴任宜吉期",
        "coverage":COVERAGE,"decision_effect":"FAVORABLE_SUPPORT_ONLY","creates_hard_block":False,"full_classical_claim":False,
        "numeric_score":None,"numeric_score_status":"LOCKED_OFF",
    }
    return out
