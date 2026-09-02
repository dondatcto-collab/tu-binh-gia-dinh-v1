"""Capability gate cho token Hiệp Kỷ.

Có tên trong cổ thư != đã có bộ tính. Chỉ token có calculator rõ mới ACTIVE_CALCULABLE.
V3.0E21 mở 天倉 theo Chi tháng + Chi ngày; các token chưa có calculator vẫn PENDING_CALCULATOR.
"""
from __future__ import annotations
from loi.quyet_dinh.hiep_ky_evidence_v25 import all_evidence

TRUC_TOKEN_TO_CODE={"建日":"KIEN","除日":"TRU","滿日":"MAN","平日":"BINH","定日":"DINH","執日":"CHAP","破日":"PHA","危日":"NGUY","成日":"THANH","收日":"THU","開日":"KHAI","閉日":"BE"}
MONTH_BRANCH_TOKENS=frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})
MONTH_BRANCH_DAY_STEM_TOKENS=frozenset({"月徳","月徳合","月恩"}); SEASON_DAY_STEM_TOKENS=frozenset({"四相"}); MONTH_BRANCH_DAY_PILLAR_TOKENS=frozenset({"天願"}); SEASON_DAY_PILLAR_TOKENS=frozenset({"天赦"}); SEASON_DAY_BRANCH_TOKENS=frozenset({"天喜"}); DAY_BRANCH_TOKENS=frozenset({"五合"}); MONTH_BRANCH_DAY_BRANCH_TOKENS=frozenset({"天醫"}); PAIRED_MONTH_DAY_BRANCH_TOKENS=frozenset({"解神"}); QUARTERED_MONTH_DAY_BRANCH_TOKENS=frozenset({"五富"}); SEASON_WANG_RI_TOKENS=frozenset({"王日"}); SEASON_GUAN_RI_TOKENS=frozenset({"官日"}); SEASON_XIANG_RI_TOKENS=frozenset({"相日"}); SEASON_MIN_RI_TOKENS=frozenset({"民日"}); MONTH_LIN_RI_TOKENS=frozenset({"臨日"}); MONTH_YI_MA_TOKENS=frozenset({"驛馬"}); MONTH_TIAN_HOU_TOKENS=frozenset({"天后"}); MONTH_TIAN_MA_TOKENS=frozenset({"天馬"}); MONTH_JI_QI_TOKENS=frozenset({"吉期"}); MONTH_TIAN_CANG_TOKENS=frozenset({"天倉"})

def token_capability(token:str)->dict:
    groups=((TRUC_TOKEN_TO_CODE,"12_TRUC_EXISTING_V1"),(MONTH_BRANCH_TOKENS,"MONTH_BRANCH_RELATIONS_V25_V30D"),(MONTH_BRANCH_DAY_STEM_TOKENS,"MONTH_BRANCH_DAY_STEM_V30E3"),(SEASON_DAY_STEM_TOKENS,"SEASON_DAY_STEM_V30E4"),(MONTH_BRANCH_DAY_PILLAR_TOKENS,"MONTH_BRANCH_DAY_PILLAR_V30E5"),(SEASON_DAY_PILLAR_TOKENS,"SEASON_DAY_PILLAR_V30E6"),(SEASON_DAY_BRANCH_TOKENS,"SEASON_DAY_BRANCH_V30E7"),(DAY_BRANCH_TOKENS,"DAY_BRANCH_V30E8"),(MONTH_BRANCH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E9"),(PAIRED_MONTH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN"),(QUARTERED_MONTH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU"),(SEASON_WANG_RI_TOKENS,"SEASON_DAY_BRANCH_V30E12_WANG_RI"),(SEASON_GUAN_RI_TOKENS,"SEASON_DAY_BRANCH_V30E13_GUAN_RI"),(SEASON_XIANG_RI_TOKENS,"SEASON_DAY_BRANCH_V30E14_XIANG_RI"),(SEASON_MIN_RI_TOKENS,"SEASON_DAY_BRANCH_V30E15_MIN_RI"),(MONTH_LIN_RI_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI"),(MONTH_YI_MA_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA"),(MONTH_TIAN_HOU_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU"),(MONTH_TIAN_MA_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA"),(MONTH_JI_QI_TOKENS,"MONTH_NEXT_BRANCH_V30E20_JI_QI"),(MONTH_TIAN_CANG_TOKENS,"MONTH_REVERSE_BRANCH_V30E21_TIAN_CANG"))
    for group,calculator in groups:
        if token in group:
            normalized=TRUC_TOKEN_TO_CODE[token] if group is TRUC_TOKEN_TO_CODE else token
            return {"token":token,"calculator":calculator,"calculator_status":"ACTIVE_CALCULABLE","normalized_code":normalized}
    return {"token":token,"calculator":None,"calculator_status":"PENDING_CALCULATOR","normalized_code":None}

def capability_inventory()->dict:
    tokens=sorted({item.token for item in all_evidence()}); rows=[token_capability(t) for t in tokens]; active=[x for x in rows if x["calculator_status"]=="ACTIVE_CALCULABLE"]; pending=[x for x in rows if x["calculator_status"]=="PENDING_CALCULATOR"]
    return {"token_count":len(rows),"active_calculable_count":len(active),"pending_calculator_count":len(pending),"active_tokens":tuple(x["token"] for x in active),"pending_tokens":tuple(x["token"] for x in pending),"decision_expansion_status":"PARTIAL_ACTIVE","coverage":"V3_0E21_41_ACTIVE","extension_version":"V3_0E21_TIAN_CANG","numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
