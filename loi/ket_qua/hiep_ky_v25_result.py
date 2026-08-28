"""Result Schema overlay cho V2.5 Hiệp Kỷ mở rộng có kiểm soát.

V2.7 không đổi engine/ranking; chỉ mở rộng contract Event Search để UI có thể
hiển thị top 3 và toàn bộ ngày đã xét từ cùng một nguồn quyết định.
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


def v25_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    implemented = list(out.get("implemented_scopes") or [])
    if "expanded_hiep_ky_event_search" not in implemented:
        implemented.append("expanded_hiep_ky_event_search")
    pending = [x for x in (out.get("pending_scopes") or []) if x != "expanded_hiep_ky_event_search"]
    if "full_classical_hiep_ky" not in pending:
        pending.append("full_classical_hiep_ky")
    out.update({
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "implemented_scopes": implemented,
        "pending_scopes": pending,
        "hiep_ky_v25": {
            "coverage": COVERAGE,
            "capability": capability_inventory(),
            "decision_hierarchy": "HARD_BLOCK > EVENT > PERSONAL",
            "full_classical_claim": False,
        },
        "numeric_score": "LOCKED_OFF",
    })
    principles = list(out.get("principles") or [])
    note = "Hiệp Kỷ V2.5 chỉ kích hoạt rule đã có bộ tính; không coi inventory cổ thư là rule đã tính được."
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
