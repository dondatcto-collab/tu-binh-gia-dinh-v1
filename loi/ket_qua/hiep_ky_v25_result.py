"""Result Schema overlay cho Hiệp Kỷ mở rộng có kiểm soát.

Giữ schema và trường coverage V2.5 để tương thích. V3.0A công bố 月刑;
V3.0B công bố 劫煞, 災煞, 月煞; V3.0C mở thêm 月厭 theo bảng 12 tháng.
Không đổi thứ bậc, không tạo HARD_BLOCK mới và không dùng numeric score.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from loi.ket_qua.v2 import event_item, event_search
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE

SCHEMA_VERSION = "2.5-alpha.1"
STATUS = "V2_5_HIEP_KY_PARTIAL_ACTIVE"
EVENT_SEARCH_CONTRACT = "V2_7_COMPLETE_RESULTS"
LEGACY_V25_COVERAGE = "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"


def v25_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    implemented = list(out.get("implemented_scopes") or [])
    for scope in (
        "expanded_hiep_ky_event_search",
        "hiep_ky_v30a_yue_xing",
        "hiep_ky_v30b_sat_trio",
        "hiep_ky_v30c_yue_yan",
    ):
        if scope not in implemented:
            implemented.append(scope)
    pending = [x for x in (out.get("pending_scopes") or []) if x != "expanded_hiep_ky_event_search"]
    if "full_classical_hiep_ky" not in pending:
        pending.append("full_classical_hiep_ky")
    cap = capability_inventory()
    out.update({
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "implemented_scopes": implemented,
        "pending_scopes": pending,
        "hiep_ky_v25": {
            "coverage": LEGACY_V25_COVERAGE,
            "effective_coverage": COVERAGE,
            "capability": cap,
            "decision_hierarchy": "HARD_BLOCK > EVENT > PERSONAL",
            "full_classical_claim": False,
        },
        "hiep_ky_v30a": {
            "extension_version": "V3_0A_YUE_XING",
            "status": "PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",
            "activated_token": "月刑",
            "activated_token_vi": "Nguyệt Hình",
            "calculator": "MONTH_BRANCH_RELATIONS_V25_V30C",
            "source_scope": "欽定協紀辨方書 卷20–31 · 月表一至十二",
            "coverage": COVERAGE,
            "decision_effect": "CAUTION_ONLY",
            "creates_hard_block": False,
            "full_classical_claim": False,
            "numeric_score": None,
            "numeric_score_status": "LOCKED_OFF",
        },
        "hiep_ky_v30b": {
            "extension_version": "V3_0B_SAT_TRIO",
            "status": "PARTIAL_ACTIVE_THREE_ADDITIONAL_RULES",
            "activated_tokens": ["劫煞", "災煞", "月煞"],
            "activated_tokens_vi": ["Kiếp Sát", "Tai Sát", "Nguyệt Sát"],
            "calculator": "MONTH_BRANCH_RELATIONS_V25_V30C",
            "source_scope": "欽定協紀辨方書 卷20–31 · 月表一至十二",
            "coverage": COVERAGE,
            "decision_effect": "CAUTION_ONLY",
            "creates_hard_block": False,
            "full_classical_claim": False,
            "numeric_score": None,
            "numeric_score_status": "LOCKED_OFF",
        },
        "hiep_ky_v30c": {
            "extension_version": "V3_0C_YUE_YAN",
            "status": "PARTIAL_ACTIVE_ONE_ADDITIONAL_RULE",
            "activated_token": "月厭",
            "activated_token_vi": "Nguyệt Yếm",
            "calculator": "MONTH_BRANCH_RELATIONS_V25_V30C",
            "source_scope": "欽定協紀辨方書 卷20–31 · 月表一至十二",
            "coverage": COVERAGE,
            "decision_effect": "CAUTION_ONLY",
            "creates_hard_block": False,
            "full_classical_claim": False,
            "numeric_score": None,
            "numeric_score_status": "LOCKED_OFF",
        },
        "numeric_score": "LOCKED_OFF",
    })
    principles = list(out.get("principles") or [])
    notes = (
        "Hiệp Kỷ chỉ kích hoạt rule đã có bộ tính; không coi inventory cổ thư là rule đã tính được.",
        "V3.0A mở Nguyệt Hình (月刑) từ bảng 12 tháng; tín hiệu này tạo thận trọng, không tự tạo HARD_BLOCK.",
        "V3.0B mở Kiếp Sát, Tai Sát, Nguyệt Sát (劫煞、災煞、月煞) từ bảng 12 tháng; cả ba chỉ tạo thận trọng, không tự tạo HARD_BLOCK và không cộng điểm.",
        "V3.0C mở Nguyệt Yếm (月厭) từ bảng 12 tháng; chỉ tạo thận trọng, không tự tạo HARD_BLOCK và không cộng điểm.",
    )
    for note in notes:
        if note not in principles:
            principles.append(note)
    out["principles"] = principles
    return out


def _enrich_item(item: dict[str, Any], src: dict[str, Any]) -> dict[str, Any]:
    item["schema_version"] = SCHEMA_VERSION
    item["rules"] = list(src.get("rule_ids") or [])
    item["sources"] = list(src.get("source_ids") or [])
    technical = dict(item.get("technical") or {})
    technical.update({
        "coverage": src.get("coverage"),
        "hiep_ky_extension": src.get("hiep_ky_extension"),
        "decision_authority": src.get("decision_authority"),
        "event_state_v1": src.get("event_state_v1"),
        "event_signal_v25": src.get("event_signal_v25"),
        "active_hiep_ky_tokens": src.get("active_hiep_ky_tokens") or [],
        "matched_yi_tokens": src.get("matched_yi_tokens") or [],
        "matched_ji_tokens": src.get("matched_ji_tokens") or [],
        "matched_evidence": src.get("matched_evidence") or [],
    })
    item["technical"] = technical
    item["numeric_score"] = None
    item["numeric_score_status"] = "LOCKED_OFF"
    return item


def event_search_v25(raw: dict[str, Any]) -> dict[str, Any]:
    out = event_search(raw)
    out["schema_version"] = SCHEMA_VERSION
    out["status"] = STATUS
    out["ranking_mode"] = "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL"
    out["hiep_ky_coverage"] = COVERAGE
    out["hiep_ky_extension"] = "V3_0C_YUE_YAN"
    out["event_search_contract"] = EVENT_SEARCH_CONTRACT

    top_sources = list(raw.get("top") or [])
    for idx, item in enumerate(out.get("results") or []):
        if idx >= len(top_sources):
            break
        _enrich_item(item, top_sources[idx])

    event_code = raw.get("viec") or ""
    all_sources = list(raw.get("cac_ngay") or [])
    all_results = [_enrich_item(event_item(src, event_code=event_code), src) for src in all_sources]
    out["all_results"] = all_results
    out["result_count"] = len(all_results)
    out["top_result_count"] = len(out.get("results") or [])
    out["group_counts"] = dict(Counter((x.get("conclusion") or {}).get("label") or "Chưa đủ căn cứ" for x in all_results))
    out["numeric_score"] = None
    out["numeric_score_status"] = "LOCKED_OFF"
    return out
