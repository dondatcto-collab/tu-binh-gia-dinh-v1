"""Result schema Hiệp Kỷ mở rộng có kiểm soát; giữ tương thích V2.5."""
from __future__ import annotations
from collections import Counter
from typing import Any
from loi.ket_qua.v2 import event_item, event_search
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_coverage_gate_v30e10 import v1_engine_readiness
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE

SCHEMA_VERSION="2.5-alpha.1"; STATUS="V2_5_HIEP_KY_PARTIAL_ACTIVE"; EVENT_SEARCH_CONTRACT="V2_7_COMPLETE_RESULTS"; LEGACY_V25_COVERAGE="V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"

def _rule_block(version:str,status:str,token:str,vi:str,calculator:str,source:str,effect:str)->dict:
    return {"extension_version":version,"status":status,"activated_token":token,"activated_token_vi":vi,"calculator":calculator,"source_scope":source,"coverage":COVERAGE,"decision_effect":effect,"creates_hard_block":False,"full_classical_claim":False,"numeric_score":None,"numeric_score_status":"LOCKED_OFF"}

def v25_schema_overlay(base:dict[str,Any])->dict[str,Any]:
    out=dict(base); implemented=list(out.get("implemented_scopes") or [])
    for scope in ("expanded_hiep_ky_event_search","hiep_ky_v30a_yue_xing","hiep_ky_v30b_sat_trio","hiep_ky_v30c_yue_yan","hiep_ky_v30d_shi_de","hiep_ky_v30e1_yue_de","hiep_ky_v30e2_yue_de_he","hiep_ky_v30e3_yue_en","hiep_ky_v30e4_si_xiang","hiep_ky_v30e5_tian_yuan","hiep_ky_v30e6_tian_she","hiep_ky_v30e7_tian_xi","hiep_ky_v30e8_wu_he","hiep_ky_v30e9_tian_yi","hiep_ky_v30e10_giai_than","hiep_ky_v30e11_wu_fu","hiep_ky_v30e12_wang_ri","hiep_ky_v30e13_guan_ri","hiep_ky_v30e14_xiang_ri","hiep_ky_v30e15_min_ri","hiep_ky_v30e16_lin_ri","hiep_ky_v30e17_yi_ma","hiep_ky_v1_coverage_gate"):
        if scope not in implemented: implemented.append(scope)
    pending=[x for x in (out.get("pending_scopes") or []) if x!="expanded_hiep_ky_event_search"]
    if "full_classical_hiep_ky" not in pending: pending.append("full_classical_hiep_ky")
    cap=capability_inventory(); readiness=v1_engine_readiness()
    month_calc="MONTH_BRANCH_RELATIONS_V25_V30D"; stem_calc="MONTH_BRANCH_DAY_STEM_V30E3"; season_calc="SEASON_DAY_STEM_V30E4"; pillar_calc="MONTH_BRANCH_DAY_PILLAR_V30E5"; season_pillar_calc="SEASON_DAY_PILLAR_V30E6"; season_branch_calc="SEASON_DAY_BRANCH_V30E7"; day_branch_calc="DAY_BRANCH_V30E8"; month_day_branch_calc="MONTH_BRANCH_DAY_BRANCH_V30E9"; giai_than_calc="MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN"; wu_fu_calc="MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU"; wang_ri_calc="SEASON_DAY_BRANCH_V30E12_WANG_RI"; guan_ri_calc="SEASON_DAY_BRANCH_V30E13_GUAN_RI"; xiang_ri_calc="SEASON_DAY_BRANCH_V30E14_XIANG_RI"; min_ri_calc="SEASON_DAY_BRANCH_V30E15_MIN_RI"; lin_ri_calc="MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI"; yi_ma_calc="MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA"
    out.update({
        "schema_version":SCHEMA_VERSION,"status":STATUS,"implemented_scopes":implemented,"pending_scopes":pending,
        "hiep_ky_v25":{"coverage":LEGACY_V25_COVERAGE,"effective_coverage":COVERAGE,"capability":cap,"decision_hierarchy":"HARD_BLOCK > EVENT > PERSONAL","full_classical_claim":False},"hiep_ky_v1_engine_readiness":readiness,
        "hiep_ky_v30a":_rule_block("V3_0A_YUE_XING","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","月刑","Nguyệt Hình",month_calc,"欽定協紀辨方書 卷20–31 · 月表一至十二","CAUTION_ONLY"),
        "hiep_ky_v30b":{"extension_version":"V3_0B_SAT_TRIO","status":"PARTIAL_ACTIVE_THREE_ADDITIONAL_RULES","activated_tokens":["劫煞","災煞","月煞"],"activated_tokens_vi":["Kiếp Sát","Tai Sát","Nguyệt Sát"],"calculator":month_calc,"source_scope":"欽定協紀辨方書 卷20–31 · 月表一至十二","coverage":COVERAGE,"decision_effect":"CAUTION_ONLY","creates_hard_block":False,"full_classical_claim":False,"numeric_score":None,"numeric_score_status":"LOCKED_OFF"},
        "hiep_ky_v30c":_rule_block("V3_0C_YUE_YAN","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","月厭","Nguyệt Yếm",month_calc,"欽定協紀辨方書 卷20–31 · 月表一至十二","CAUTION_ONLY"),
        "hiep_ky_v30d":_rule_block("V3_0D_SHI_DE","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","時徳","Thời Đức",month_calc,"欽定協紀辨方書 卷五 · 總要歴/歴例","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e1":_rule_block("V3_0E1_YUE_DE","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","月徳","Nguyệt Đức",stem_calc,"欽定協紀辨方書 卷五 · 月徳","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e2":_rule_block("V3_0E2_YUE_DE_HE","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","月徳合","Nguyệt Đức Hợp",stem_calc,"欽定協紀辨方書 卷五 · 月徳合; 御定星曆考原 卷三 · 月徳合","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e3":_rule_block("V3_0E3_YUE_EN","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","月恩","Nguyệt Ân",stem_calc,"御定星曆考原 卷三 · 月恩","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e4":_rule_block("V3_0E4_SI_XIANG","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","四相","Tứ Tướng",season_calc,"御定星曆考原 卷三 · 四相; 欽定協紀辨方書 卷五 · 四相","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e5":_rule_block("V3_0E5_TIAN_YUAN","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","天願","Thiên Nguyện",pillar_calc,"欽定協紀辨方書 卷五 · 天願; 御定星曆考原 卷三 · 天願","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e6":_rule_block("V3_0E6_TIAN_SHE","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","天赦","Thiên Xá",season_pillar_calc,"御定星曆考原 卷三 · 天赦; 欽定協紀辨方書 卷五 · 天赦","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e7":_rule_block("V3_0E7_TIAN_XI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","天喜","Thiên Hỷ",season_branch_calc,"御定星曆考原 卷三 · 天喜: 春午、夏丑、秋辰、冬未","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e8":_rule_block("V3_0E8_WU_HE","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","五合","Ngũ Hợp",day_branch_calc,"欽定協紀辨方書 卷五 · 五合: 歷例曰五合者寅卯日也","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e9":_rule_block("V3_0E9_TIAN_YI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","天醫","Thiên Y",month_day_branch_calc,"欽定協紀辨方書 卷五 · 天醫: 歷例曰天醫者正月起戌順行十二辰; 卷十一 · 求醫療病宜天醫","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e10":_rule_block("V3_0E10_GIAI_THAN","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","解神","Giải Thần",giai_than_calc,"欽定協紀辨方書 卷五 · 解神; 卷十一 · 求醫療病宜解神","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e11":_rule_block("V3_0E11_WU_FU","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","五富","Ngũ Phú",wu_fu_calc,"欽定協紀辨方書 卷六 · 五富: 正月起亥順行四孟; 卷十一 · 開市/立券交易/納財宜五富","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e12":_rule_block("V3_0E12_WANG_RI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","王日","Vương Nhật",wang_ri_calc,"欽定協紀辨方書 卷五 · 王官守相民日: 王日春寅、夏巳、秋申、冬亥; 卷十一","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e13":_rule_block("V3_0E13_GUAN_RI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","官日","Quan Nhật",guan_ri_calc,"欽定協紀辨方書 卷五 · 王官守相民日: 官日春卯、夏午、秋酉、冬子; 卷十一 · 上官赴任宜官日","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e14":_rule_block("V3_0E14_XIANG_RI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","相日","Tướng Nhật",xiang_ri_calc,"欽定協紀辨方書 卷五 · 王官守相民日: 相日春巳、夏申、秋亥、冬寅; 卷十一 · 上官赴任宜相日","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e15":_rule_block("V3_0E15_MIN_RI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","民日","Dân Nhật",min_ri_calc,"欽定協紀辨方書 卷五 · 王官守相民日: 民日春午、夏酉、秋子、冬卯; 卷十一 · 開市/立券交易/般移/納財宜民日","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e16":_rule_block("V3_0E16_LIN_RI","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","臨日","Lâm Nhật",lin_ri_calc,"欽定協紀辨方書 卷六 · 臨日: 正月午、二月亥、三月申、四月丑、五月戌、六月卯、七月子、八月巳、九月寅、十月未、十一月辰、十二月酉; 卷十一 · 上官赴任宜臨日","FAVORABLE_SUPPORT_ONLY"),
        "hiep_ky_v30e17":_rule_block("V3_0E17_YI_MA","PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE","驛馬","Dịch Mã",yi_ma_calc,"欽定協紀辨方書 卷六 · 驛馬: 正月起申逆行四孟; 卷十一 · 行幸遣使/般移宜驛馬","FAVORABLE_SUPPORT_ONLY"),
        "numeric_score":"LOCKED_OFF"})
    principles=list(out.get("principles") or [])
    for note in ("Hiệp Kỷ chỉ kích hoạt rule đã có bộ tính; không coi inventory cổ thư là rule đã tính được.","V1 Engine dùng coverage-first: mục tiêu khoảng 45 rule (dải 42–48) và phải cân bằng rule thuận/tránh trên các event VERIFIED; không chạy theo 81/81.","V3.0E14 mở Tướng Nhật (相日) theo mùa + Chi ngày; 守日 tạm không mở vì nội văn quyển 5 có hai phép khác nhau cần xử lý nguồn riêng; JI/HARD_BLOCK vẫn thắng và không cộng điểm.","V3.0E15 mở Dân Nhật (民日) theo mùa + Chi ngày: xuân Ngọ, hạ Dậu, thu Tý, đông Mão; chỉ tác động theo inventory event, JI/HARD_BLOCK vẫn thắng và không cộng điểm.","V3.0E16 mở Lâm Nhật (臨日) theo Chi tháng + Chi ngày theo chuỗi 12 tháng của quyển 6; hiện chỉ hỗ trợ NHAM_CHUC VERIFIED, JI/HARD_BLOCK vẫn thắng và không cộng điểm.","V3.0E17 mở Dịch Mã (驛馬) theo Chi tháng + Chi ngày: chính nguyệt khởi Thân, nghịch hành bốn Mạnh; chỉ hỗ trợ XUAT_HANH/NHAP_TRACH VERIFIED, JI/HARD_BLOCK vẫn thắng và không cộng điểm."):
        if note not in principles: principles.append(note)
    out["principles"]=principles; return out

def _enrich_item(item:dict[str,Any],src:dict[str,Any])->dict[str,Any]:
    item["schema_version"]=SCHEMA_VERSION; item["rules"]=list(src.get("rule_ids") or []); item["sources"]=list(src.get("source_ids") or [])
    technical=dict(item.get("technical") or {}); technical.update({"coverage":src.get("coverage"),"hiep_ky_extension":src.get("hiep_ky_extension"),"decision_authority":src.get("decision_authority"),"event_state_v1":src.get("event_state_v1"),"event_signal_v25":src.get("event_signal_v25"),"active_hiep_ky_tokens":src.get("active_hiep_ky_tokens") or [],"matched_yi_tokens":src.get("matched_yi_tokens") or [],"matched_ji_tokens":src.get("matched_ji_tokens") or [],"matched_evidence":src.get("matched_evidence") or []}); item["technical"]=technical; item["numeric_score"]=None; item["numeric_score_status"]="LOCKED_OFF"; return item

def event_search_v25(raw:dict[str,Any])->dict[str,Any]:
    out=event_search(raw); out["schema_version"]=SCHEMA_VERSION; out["status"]=STATUS; out["ranking_mode"]="ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL"; out["hiep_ky_coverage"]=COVERAGE; out["hiep_ky_extension"]="V3_0E17_YI_MA"; out["event_search_contract"]=EVENT_SEARCH_CONTRACT
    top_sources=list(raw.get("top") or [])
    for idx,item in enumerate(out.get("results") or []):
        if idx>=len(top_sources): break
        _enrich_item(item,top_sources[idx])
    event_code=raw.get("viec") or ""; all_sources=list(raw.get("cac_ngay") or []); all_results=[_enrich_item(event_item(src,event_code=event_code),src) for src in all_sources]
    out["all_results"]=all_results; out["result_count"]=len(all_results); out["top_result_count"]=len(out.get("results") or []); out["group_counts"]=dict(Counter((x.get("conclusion") or {}).get("label") or "Chưa đủ căn cứ" for x in all_results)); out["numeric_score"]=None; out["numeric_score_status"]="LOCKED_OFF"; return out
