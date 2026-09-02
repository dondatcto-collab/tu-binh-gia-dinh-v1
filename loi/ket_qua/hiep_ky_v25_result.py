"""Result schema Hiệp Kỷ mở rộng có kiểm soát; giữ tương thích V2.5."""
from __future__ import annotations
from collections import Counter
from typing import Any
from loi.ket_qua.v2 import event_item, event_search
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_coverage_gate_v30e10 import v1_engine_readiness
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE

SCHEMA_VERSION="2.5-alpha.1"
STATUS="V2_5_HIEP_KY_PARTIAL_ACTIVE"
EVENT_SEARCH_CONTRACT="V2_7_COMPLETE_RESULTS"
LEGACY_V25_COVERAGE="V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"

def _rule_block(version:str,status:str,token:str,vi:str,calculator:str,source:str,effect:str)->dict:
    return {"extension_version":version,"status":status,"activated_token":token,"activated_token_vi":vi,"calculator":calculator,"source_scope":source,"coverage":COVERAGE,"decision_effect":effect,"creates_hard_block":False,"full_classical_claim":False,"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}

_RULES={
"hiep_ky_v30a":("V3_0A_YUE_XING","月刑","Nguyệt Hình","MONTH_BRANCH_RELATIONS_V25_V30D","欽定協紀辨方書 卷20–31 · 月表一至十二","CAUTION_ONLY"),
"hiep_ky_v30c":("V3_0C_YUE_YAN","月厭","Nguyệt Yếm","MONTH_BRANCH_RELATIONS_V25_V30D","欽定協紀辨方書 卷20–31 · 月表一至十二","CAUTION_ONLY"),
"hiep_ky_v30d":("V3_0D_SHI_DE","時徳","Thời Đức","MONTH_BRANCH_RELATIONS_V25_V30D","欽定協紀辨方書 卷五 · 總要歴/歴例","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e1":("V3_0E1_YUE_DE","月徳","Nguyệt Đức","MONTH_BRANCH_DAY_STEM_V30E3","欽定協紀辨方書 卷五 · 月徳","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e2":("V3_0E2_YUE_DE_HE","月徳合","Nguyệt Đức Hợp","MONTH_BRANCH_DAY_STEM_V30E3","欽定協紀辨方書 卷五 · 月徳合","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e3":("V3_0E3_YUE_EN","月恩","Nguyệt Ân","MONTH_BRANCH_DAY_STEM_V30E3","御定星曆考原 卷三 · 月恩","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e4":("V3_0E4_SI_XIANG","四相","Tứ Tướng","SEASON_DAY_STEM_V30E4","欽定協紀辨方書 卷五 · 四相","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e5":("V3_0E5_TIAN_YUAN","天願","Thiên Nguyện","MONTH_BRANCH_DAY_PILLAR_V30E5","欽定協紀辨方書 卷五 · 天願","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e6":("V3_0E6_TIAN_SHE","天赦","Thiên Xá","SEASON_DAY_PILLAR_V30E6","欽定協紀辨方書 卷五 · 天赦","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e7":("V3_0E7_TIAN_XI","天喜","Thiên Hỷ","SEASON_DAY_BRANCH_V30E7","御定星曆考原 卷三 · 天喜","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e8":("V3_0E8_WU_HE","五合","Ngũ Hợp","DAY_BRANCH_V30E8","欽定協紀辨方書 卷五 · 五合","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e9":("V3_0E9_TIAN_YI","天醫","Thiên Y","MONTH_BRANCH_DAY_BRANCH_V30E9","欽定協紀辨方書 卷五 · 天醫","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e10":("V3_0E10_GIAI_THAN","解神","Giải Thần","MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN","欽定協紀辨方書 卷五 · 解神","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e11":("V3_0E11_WU_FU","五富","Ngũ Phú","MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU","欽定協紀辨方書 卷六 · 五富","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e12":("V3_0E12_WANG_RI","王日","Vương Nhật","SEASON_DAY_BRANCH_V30E12_WANG_RI","欽定協紀辨方書 卷五 · 王官守相民日","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e13":("V3_0E13_GUAN_RI","官日","Quan Nhật","SEASON_DAY_BRANCH_V30E13_GUAN_RI","欽定協紀辨方書 卷五 · 王官守相民日","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e14":("V3_0E14_XIANG_RI","相日","Tướng Nhật","SEASON_DAY_BRANCH_V30E14_XIANG_RI","欽定協紀辨方書 卷五 · 王官守相民日","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e15":("V3_0E15_MIN_RI","民日","Dân Nhật","SEASON_DAY_BRANCH_V30E15_MIN_RI","欽定協紀辨方書 卷五 · 王官守相民日","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e16":("V3_0E16_LIN_RI","臨日","Lâm Nhật","MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI","欽定協紀辨方書 卷六 · 臨日","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e17":("V3_0E17_YI_MA","驛馬","Dịch Mã","MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA","欽定協紀辨方書 卷六 · 驛馬","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e18":("V3_0E18_TIAN_HOU","天后","Thiên Hậu","MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU","欽定協紀辨方書 卷六 · 天后與驛馬同位; 卷十一 · 求醫療病","FAVORABLE_SUPPORT_ONLY"),
"hiep_ky_v30e19":("V3_0E19_TIAN_MA","天馬","Thiên Mã","MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA","欽定協紀辨方書 卷六 · 天馬: 正月起午順行六陽辰; 卷十/十一 · 行幸遣使般移","FAVORABLE_SUPPORT_ONLY"),
}

def v25_schema_overlay(base:dict[str,Any])->dict[str,Any]:
    out=dict(base); implemented=list(out.get("implemented_scopes") or [])
    scopes=["expanded_hiep_ky_event_search","hiep_ky_v30a_yue_xing","hiep_ky_v30b_sat_trio","hiep_ky_v30c_yue_yan","hiep_ky_v30d_shi_de","hiep_ky_v30e1_yue_de","hiep_ky_v30e2_yue_de_he","hiep_ky_v30e3_yue_en","hiep_ky_v30e4_si_xiang","hiep_ky_v30e5_tian_yuan","hiep_ky_v30e6_tian_she","hiep_ky_v30e7_tian_xi","hiep_ky_v30e8_wu_he","hiep_ky_v30e9_tian_yi","hiep_ky_v30e10_giai_than","hiep_ky_v30e11_wu_fu","hiep_ky_v30e12_wang_ri","hiep_ky_v30e13_guan_ri","hiep_ky_v30e14_xiang_ri","hiep_ky_v30e15_min_ri","hiep_ky_v30e16_lin_ri","hiep_ky_v30e17_yi_ma","hiep_ky_v30e18_tian_hou","hiep_ky_v30e19_tian_ma","hiep_ky_v1_coverage_gate"]
    for scope in scopes:
        if scope not in implemented: implemented.append(scope)
    pending=[x for x in (out.get("pending_scopes") or []) if x!="expanded_hiep_ky_event_search"]
    if "full_classical_hiep_ky" not in pending: pending.append("full_classical_hiep_ky")
    cap=capability_inventory(); readiness=v1_engine_readiness()
    out.update({"schema_version":SCHEMA_VERSION,"status":STATUS,"implemented_scopes":implemented,"pending_scopes":pending,"hiep_ky_v25":{"coverage":LEGACY_V25_COVERAGE,"effective_coverage":COVERAGE,"capability":cap,"decision_hierarchy":"HARD_BLOCK > EVENT > PERSONAL","full_classical_claim":False},"hiep_ky_v1_engine_readiness":readiness})
    out["hiep_ky_v30b"]={"extension_version":"V3_0B_SAT_TRIO","status":"PARTIAL_ACTIVE_THREE_ADDITIONAL_RULES","activated_tokens":["劫煞","災煞","月煞"],"activated_tokens_vi":["Kiếp Sát","Tai Sát","Nguyệt Sát"],"calculator":"MONTH_BRANCH_RELATIONS_V25_V30D","source_scope":"欽定協紀辨方書 卷20–31 · 月表一至十二","coverage":COVERAGE,"decision_effect":"CAUTION_ONLY","creates_hard_block":False,"full_classical_claim":False,"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
    for key,(version,token,vi,calc,source,effect) in _RULES.items(): out[key]=_rule_block(version,"PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",token,vi,calc,source,effect)
    out["numeric_score"]="LOCKED_OFF"
    principles=list(out.get("principles") or [])
    for note in ("Hiệp Kỷ chỉ kích hoạt rule đã có bộ tính; không coi inventory cổ thư là rule đã tính được.","V1 Engine dùng coverage-first: mục tiêu khoảng 45 rule (dải 42–48) và phải cân bằng rule thuận/tránh trên các event VERIFIED; không chạy theo 81/81.","V3.0E14 mở Tướng Nhật (相日); 守日 tạm không mở vì nguồn còn xung đột.","V3.0E19 mở Thiên Mã (天馬): chính nguyệt khởi Ngọ, thuận hành sáu Dương chi; chỉ hỗ trợ XUAT_HANH/NHAP_TRACH VERIFIED, JI/HARD_BLOCK vẫn thắng và không cộng điểm."):
        if note not in principles: principles.append(note)
    out["principles"]=principles
    return out

def _enrich_item(item:dict[str,Any],src:dict[str,Any])->dict[str,Any]:
    item["schema_version"]=SCHEMA_VERSION; item["rules"]=list(src.get("rule_ids") or []); item["sources"]=list(src.get("source_ids") or [])
    technical=dict(item.get("technical") or {}); technical.update({"coverage":src.get("coverage"),"hiep_ky_extension":src.get("hiep_ky_extension"),"decision_authority":src.get("decision_authority"),"event_state_v1":src.get("event_state_v1"),"event_signal_v25":src.get("event_signal_v25"),"active_hiep_ky_tokens":src.get("active_hiep_ky_tokens") or [],"matched_yi_tokens":src.get("matched_yi_tokens") or [],"matched_ji_tokens":src.get("matched_ji_tokens") or [],"matched_evidence":src.get("matched_evidence") or []}); item["technical"]=technical; item["numeric_score"]=None; item["numeric_score_status"]="LOCKED_OFF"; return item

def event_search_v25(raw:dict[str,Any])->dict[str,Any]:
    out=event_search(raw); out["schema_version"]=SCHEMA_VERSION; out["status"]=STATUS; out["ranking_mode"]="ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL"; out["hiep_ky_coverage"]=COVERAGE; out["hiep_ky_extension"]=capability_inventory()["extension_version"]; out["event_search_contract"]=EVENT_SEARCH_CONTRACT
    top_sources=list(raw.get("top") or [])
    for idx,item in enumerate(out.get("results") or []):
        if idx>=len(top_sources): break
        _enrich_item(item,top_sources[idx])
    event_code=raw.get("viec") or ""; all_sources=list(raw.get("cac_ngay") or []); all_results=[_enrich_item(event_item(src,event_code=event_code),src) for src in all_sources]
    out["all_results"]=all_results; out["result_count"]=len(all_results); out["top_result_count"]=len(out.get("results") or []); out["group_counts"]=dict(Counter((x.get("conclusion") or {}).get("label") or "Chưa đủ căn cứ" for x in all_results)); out["numeric_score"]=None; out["numeric_score_status"]="LOCKED_OFF"; return out
