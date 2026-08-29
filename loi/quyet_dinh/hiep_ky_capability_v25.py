"""Capability gate cho token Hiệp Kỷ.

Có tên trong cổ thư != đã có bộ tính. V3.0D mở thêm 時徳 sau khi khóa
quy tắc bốn mùa từ 卷五. Các token khác vẫn PENDING_CALCULATOR.
"""
from __future__ import annotations

from loi.quyet_dinh.hiep_ky_evidence_v25 import all_evidence

TRUC_TOKEN_TO_CODE = {
    "建日":"KIEN","除日":"TRU","滿日":"MAN","平日":"BINH","定日":"DINH","執日":"CHAP",
    "破日":"PHA","危日":"NGUY","成日":"THANH","收日":"THU","開日":"KHAI","閉日":"BE",
}
MONTH_BRANCH_TOKENS = frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})


def token_capability(token: str) -> dict:
    if token in TRUC_TOKEN_TO_CODE:
        return {"token":token,"calculator":"12_TRUC_EXISTING_V1","calculator_status":"ACTIVE_CALCULABLE","normalized_code":TRUC_TOKEN_TO_CODE[token]}
    if token in MONTH_BRANCH_TOKENS:
        return {"token":token,"calculator":"MONTH_BRANCH_RELATIONS_V25_V30D","calculator_status":"ACTIVE_CALCULABLE","normalized_code":token}
    return {"token":token,"calculator":None,"calculator_status":"PENDING_CALCULATOR","normalized_code":None}


def capability_inventory() -> dict:
    tokens = sorted({item.token for item in all_evidence()})
    rows = [token_capability(token) for token in tokens]
    active = [x for x in rows if x["calculator_status"] == "ACTIVE_CALCULABLE"]
    pending = [x for x in rows if x["calculator_status"] == "PENDING_CALCULATOR"]
    return {
        "token_count":len(rows),"active_calculable_count":len(active),"pending_calculator_count":len(pending),
        "active_tokens":tuple(x["token"] for x in active),"pending_tokens":tuple(x["token"] for x in pending),
        "decision_expansion_status":"PARTIAL_ACTIVE","coverage":"12_TRUC_PLUS_MONTH_BRANCH_11",
        "extension_version":"V3_0D_SHI_DE","numeric_score":None,"numeric_score_status":"LOCKED_OFF",
    }
