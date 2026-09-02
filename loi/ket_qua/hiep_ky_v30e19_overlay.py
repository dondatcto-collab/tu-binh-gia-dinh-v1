"""V3.0E19 overlay: công khai E18/E19 mà không phá contract V2.5 cũ."""
from __future__ import annotations
from typing import Any
from loi.ket_qua.hiep_ky_v25_result import event_search_v25, v25_schema_overlay
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE


def schema_overlay_v30e19(base:dict[str,Any])->dict[str,Any]:
    out=v25_schema_overlay(base)
    scopes=list(out.get("implemented_scopes") or [])
    for scope in ("hiep_ky_v30e18_tian_hou","hiep_ky_v30e19_tian_ma"):
        if scope not in scopes: scopes.append(scope)
    out["implemented_scopes"]=scopes
    out["hiep_ky_v30e18"]={
        "extension_version":"V3_0E18_TIAN_HOU","status":"PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",
        "activated_token":"天后","activated_token_vi":"Thiên Hậu","calculator":"MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU",
        "source_scope":"欽定協紀辨方書 卷六 · 天后與驛馬同位; 卷十/十一 · 求醫療病宜天后",
        "coverage":COVERAGE,"decision_effect":"FAVORABLE_SUPPORT_ONLY","creates_hard_block":False,"full_classical_claim":False,
        "numeric_score":None,"numeric_score_status":"LOCKED_OFF",
    }
    out["hiep_ky_v30e19"]={
        "extension_version":"V3_0E19_TIAN_MA","status":"PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",
        "activated_token":"天馬","activated_token_vi":"Thiên Mã","calculator":"MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA",
        "source_scope":"欽定協紀辨方書 卷六 · 天馬: 正月起午順行六陽辰; 卷十/十一 · 行幸遣使般移宜天馬",
        "coverage":COVERAGE,"decision_effect":"FAVORABLE_SUPPORT_ONLY","creates_hard_block":False,"full_classical_claim":False,
        "numeric_score":None,"numeric_score_status":"LOCKED_OFF",
    }
    principles=list(out.get("principles") or [])
    note="V3.0E19 mở Thiên Mã (天馬) theo chính nguyệt khởi Ngọ, thuận hành sáu Dương chi; chỉ hỗ trợ XUAT_HANH/NHAP_TRACH VERIFIED, JI/HARD_BLOCK vẫn thắng và score OFF."
    if note not in principles: principles.append(note)
    out["principles"]=principles
    return out


def event_search_v30e19(raw:dict[str,Any])->dict[str,Any]:
    out=event_search_v25(raw)
    out["hiep_ky_coverage"]=COVERAGE
    out["hiep_ky_extension"]="V3_0E19_TIAN_MA"
    return out
