"""Capability gate cho token Hiệp Kỷ.

Có tên trong cổ thư != đã có bộ tính. V3.0D có 11 token quan hệ Chi tháng-ngày.
V3.0E1 mở 月徳; V3.0E2 mở 月徳合; V3.0E3 mở 月恩 bằng calculator Chi tháng + Can ngày.
V3.0E4 mở 四相 bằng calculator mùa + Can ngày.
V3.0E5 mở 天願 bằng calculator Chi tháng + đủ Can Chi ngày.
V3.0E6 mở 天赦 bằng calculator mùa + đủ Can Chi ngày.
V3.0E7 mở 天喜 bằng calculator mùa + Chi ngày.
V3.0E8 mở 五合 bằng calculator Chi ngày Dần/Mão.
V3.0E9 mở 天醫 bằng calculator Chi tháng + Chi ngày.
V3.0E10 mở 解神 bằng calculator Chi tháng + Chi ngày theo cặp tháng.
V3.0E11 mở 五富 bằng calculator Chi tháng + Chi ngày theo chu kỳ bốn Mạnh.
V3.0E12 mở 王日 bằng calculator mùa + Chi ngày.
V3.0E13 mở 官日 bằng calculator mùa + Chi ngày.
V3.0E14 mở 相日 bằng calculator mùa + Chi ngày.
V3.0E15 mở 民日 bằng calculator mùa + Chi ngày.
V3.0E16 mở 臨日 bằng calculator Chi tháng + Chi ngày.
V3.0E17 mở 驛馬 bằng calculator Chi tháng + Chi ngày.
V3.0E18 mở 天后 cùng vị trí 驛馬 nhưng token/scope độc lập. Mọi token khác vẫn PENDING_CALCULATOR.
"""
from __future__ import annotations
from loi.quyet_dinh.hiep_ky_evidence_v25 import all_evidence
TRUC_TOKEN_TO_CODE={"建日":"KIEN","除日":"TRU","滿日":"MAN","平日":"BINH","定日":"DINH","執日":"CHAP","破日":"PHA","危日":"NGUY","成日":"THANH","收日":"THU","開日":"KHAI","閉日":"BE"}
MONTH_BRANCH_TOKENS=frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})
MONTH_BRANCH_DAY_STEM_TOKENS=frozenset({"月徳","月徳合","月恩"}); SEASON_DAY_STEM_TOKENS=frozenset({"四相"}); MONTH_BRANCH_DAY_PILLAR_TOKENS=frozenset({"天願"}); SEASON_DAY_PILLAR_TOKENS=frozenset({"天赦"}); SEASON_DAY_BRANCH_TOKENS=frozenset({"天喜"}); DAY_BRANCH_TOKENS=frozenset({"五合"}); MONTH_BRANCH_DAY_BRANCH_TOKENS=frozenset({"天醫"}); PAIRED_MONTH_DAY_BRANCH_TOKENS=frozenset({"解神"}); QUARTERED_MONTH_DAY_BRANCH_TOKENS=frozenset({"五富"}); SEASON_WANG_RI_TOKENS=frozenset({"王日"}); SEASON_GUAN_RI_TOKENS=frozenset({"官日"}); SEASON_XIANG_RI_TOKENS=frozenset({"相日"}); SEASON_MIN_RI_TOKENS=frozenset({"民日"}); MONTH_LIN_RI_TOKENS=frozenset({"臨日"}); MONTH_YI_MA_TOKENS=frozenset({"驛馬"}); MONTH_TIAN_HOU_TOKENS=frozenset({"天后"})

def token_capability(token:str)->dict:
    groups=((TRUC_TOKEN_TO_CODE,"12_TRUC_EXISTING_V1"),(MONTH_BRANCH_TOKENS,"MONTH_BRANCH_RELATIONS_V25_V30D"),(MONTH_BRANCH_DAY_STEM_TOKENS,"MONTH_BRANCH_DAY_STEM_V30E3"),(SEASON_DAY_STEM_TOKENS,"SEASON_DAY_STEM_V30E4"),(MONTH_BRANCH_DAY_PILLAR_TOKENS,"MONTH_BRANCH_DAY_PILLAR_V30E5"),(SEASON_DAY_PILLAR_TOKENS,"SEASON_DAY_PILLAR_V30E6"),(SEASON_DAY_BRANCH_TOKENS,"SEASON_DAY_BRANCH_V30E7"),(DAY_BRANCH_TOKENS,"DAY_BRANCH_V30E8"),(MONTH_BRANCH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E9"),(PAIRED_MONTH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN"),(QUARTERED_MONTH_DAY_BRANCH_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU"),(SEASON_WANG_RI_TOKENS,"SEASON_DAY_BRANCH_V30E12_WANG_RI"),(SEASON_GUAN_RI_TOKENS,"SEASON_DAY_BRANCH_V30E13_GUAN_RI"),(SEASON_XIANG_RI_TOKENS,"SEASON_DAY_BRANCH_V30E14_XIANG_RI"),(SEASON_MIN_RI_TOKENS,"SEASON_DAY_BRANCH_V30E15_MIN_RI"),(MONTH_LIN_RI_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI"),(MONTH_YI_MA_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA"),(MONTH_TIAN_HOU_TOKENS,"MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU"))
    for group, calculator in groups:
        if token in group:
            normalized=TRUC_TOKEN_TO_CODE[token] if group is TRUC_TOKEN_TO_CODE else token
            return {"token":token,"calculator":calculator,"calculator_status":"ACTIVE_CALCULABLE","normalized_code":normalized}
    return {"token":token,"calculator":None,"calculator_status":"PENDING_CALCULATOR","normalized_code":None}

def capability_inventory()->dict:
    tokens=sorted({item.token for item in all_evidence()}); rows=[token_capability(token) for token in tokens]; active=[x for x in rows if x["calculator_status"]=="ACTIVE_CALCULABLE"]; pending=[x for x in rows if x["calculator_status"]=="PENDING_CALCULATOR"]
    return {"token_count":len(rows),"active_calculable_count":len(active),"pending_calculator_count":len(pending),"active_tokens":tuple(x["token"] for x in active),"pending_tokens":tuple(x["token"] for x in pending),"decision_expansion_status":"PARTIAL_ACTIVE","coverage":"V3_0E18_38_ACTIVE","extension_version":"V3_0E18_TIAN_HOU","numeric_score":None,"numeric_score_status":"LOCKED_OFF"}
