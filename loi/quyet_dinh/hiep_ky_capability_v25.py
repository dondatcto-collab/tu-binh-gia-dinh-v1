"""Capability gate cho token Hiệp Kỷ.

Có tên trong cổ thư != đã có bộ tính. V3.0D có 11 token quan hệ Chi tháng-ngày.
V3.0E1 mở 月徳; V3.0E2 mở 月徳合; V3.0E3 mở 月恩 bằng calculator Chi tháng + Can ngày.
V3.0E4 mở 四相 bằng calculator mùa + Can ngày.
V3.0E5 mở 天願 bằng calculator Chi tháng + đủ Can Chi ngày.
V3.0E6 mở 天赦 bằng calculator mùa + đủ Can Chi ngày.
V3.0E7 mở 天喜 bằng calculator mùa + Chi ngày.
V3.0E8 mở 五合 bằng calculator Chi ngày Dần/Mão.
V3.0E9 mở 天醫 bằng calculator Chi tháng + Chi ngày. Mọi token khác vẫn PENDING_CALCULATOR.
"""
from __future__ import annotations

from loi.quyet_dinh.hiep_ky_evidence_v25 import all_evidence

TRUC_TOKEN_TO_CODE = {
    "建日":"KIEN","除日":"TRU","滿日":"MAN","平日":"BINH","定日":"DINH","執日":"CHAP",
    "破日":"PHA","危日":"NGUY","成日":"THANH","收日":"THU","開日":"KHAI","閉日":"BE",
}
MONTH_BRANCH_TOKENS = frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})
MONTH_BRANCH_DAY_STEM_TOKENS = frozenset({"月徳","月徳合","月恩"})
SEASON_DAY_STEM_TOKENS = frozenset({"四相"})
MONTH_BRANCH_DAY_PILLAR_TOKENS = frozenset({"天願"})
SEASON_DAY_PILLAR_TOKENS = frozenset({"天赦"})
SEASON_DAY_BRANCH_TOKENS = frozenset({"天喜"})
DAY_BRANCH_TOKENS = frozenset({"五合"})
MONTH_BRANCH_DAY_BRANCH_TOKENS = frozenset({"天醫"})


def token_capability(token: str) -> dict:
    if token in TRUC_TOKEN_TO_CODE:
        return {"token":token,"calculator":"12_TRUC_EXISTING_V1","calculator_status":"ACTIVE_CALCULABLE","normalized_code":TRUC_TOKEN_TO_CODE[token]}
    if token in MONTH_BRANCH_TOKENS:
        return {"token":token,"calculator":"MONTH_BRANCH_RELATIONS_V25_V30D","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in MONTH_BRANCH_DAY_STEM_TOKENS:
        return {"token":token,"calculator":"MONTH_BRANCH_DAY_STEM_V30E3","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in SEASON_DAY_STEM_TOKENS:
        return {"token":token,"calculator":"SEASON_DAY_STEM_V30E4","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in MONTH_BRANCH_DAY_PILLAR_TOKENS:
        return {"token":token,"calculator":"MONTH_BRANCH_DAY_PILLAR_V30E5","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in SEASON_DAY_PILLAR_TOKENS:
        return {"token":token,"calculator":"SEASON_DAY_PILLAR_V30E6","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in SEASON_DAY_BRANCH_TOKENS:
        return {"token":token,"calculator":"SEASON_DAY_BRANCH_V30E7","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in DAY_BRANCH_TOKENS:
        return {"token":token,"calculator":"DAY_BRANCH_V30E8","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    if token in MONTH_BRANCH_DAY_BRANCH_TOKENS:
        return {"token":token,"calculator":"MONTH_BRANCH_DAY_BRANCH_V30E9","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    return {"token":token,"calculator":None,"calculator_status":"PENDING_CALCULATOR","normalized_code":None}


def capability_inventory() -> dict:
    tokens = sorted({item.token for item in all_evidence()})
    rows = [token_capability(token) for token in tokens]
    active = [x for x in rows if x["calculator_status"] == "ACTIVE_CALCULABLE"]
    pending = [x for x in rows if x["calculator_status"] == "PENDING_CALCULATOR"]
    return {
        "token_count":len(rows),
        "active_calculable_count":len(active),
        "pending_calculator_count":len(pending),
        "active_tokens":tuple(x["token"] for x in active),
        "pending_tokens":tuple(x["token"] for x in pending),
        "decision_expansion_status":"PARTIAL_ACTIVE",
        "coverage":"12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1_PLUS_DAY_BRANCH_1_PLUS_MONTH_DAY_BRANCH_1",
        "extension_version":"V3_0E9_TIAN_YI",
        "numeric_score":None,
        "numeric_score_status":"LOCKED_OFF",
    }
