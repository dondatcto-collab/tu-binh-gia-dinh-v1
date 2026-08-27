from loi.ket_qua.hiep_ky_v25_result import (
    SCHEMA_VERSION,
    STATUS,
    event_search_v25,
    v25_schema_overlay,
)


def test_schema_overlay_declares_partial_not_full_classical_coverage():
    out = v25_schema_overlay({"implemented_scopes": ["event_search"], "pending_scopes": [], "principles": []})
    assert out["schema_version"] == SCHEMA_VERSION == "2.5-alpha.1"
    assert out["status"] == STATUS == "V2_5_HIEP_KY_PARTIAL_ACTIVE"
    assert "expanded_hiep_ky_event_search" in out["implemented_scopes"]
    assert "full_classical_hiep_ky" in out["pending_scopes"]
    assert out["hiep_ky_v25"]["full_classical_claim"] is False
    assert out["numeric_score"] == "LOCKED_OFF"


def test_event_search_result_keeps_rules_sources_and_no_score():
    raw = {
        "viec": "KY_HOP_DONG",
        "so_ngay_da_quet": 1,
        "xep_hang_status": "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL",
        "top": [{
            "ngay": "2026-09-01",
            "label": "Ưu tiên",
            "decision_state": "FAVORABLE",
            "hard_block": False,
            "rank_group": 1,
            "event_state": "YI",
            "personal_v1_1": {},
            "reasons": ["reason"],
            "mapping_status": "VERIFIED",
            "coverage": "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5",
            "rule_ids": ["HK25-X"],
            "source_ids": ["SRC-HK-QD-V11-WIKISOURCE"],
            "matched_evidence": [{"rule_id": "HK25-X", "source_id": "SRC-HK-QD-V11-WIKISOURCE"}],
            "active_hiep_ky_tokens": ["六合"],
            "matched_yi_tokens": ["六合"],
            "matched_ji_tokens": [],
            "decision_authority": "EVENT",
            "event_state_v1": "NEUTRAL",
            "event_signal_v25": "FAVORABLE",
        }],
    }
    out = event_search_v25(raw)
    item = out["results"][0]
    assert out["schema_version"] == "2.5-alpha.1"
    assert out["numeric_score"] is None
    assert item["rules"] == ["HK25-X"]
    assert item["sources"] == ["SRC-HK-QD-V11-WIKISOURCE"]
    assert item["technical"]["matched_yi_tokens"] == ["六合"]
    assert item["numeric_score"] is None
    assert item["numeric_score_status"] == "LOCKED_OFF"
