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
    assert "hiep_ky_v30a_yue_xing" in out["implemented_scopes"]
    assert "hiep_ky_v30b_sat_trio" in out["implemented_scopes"]
    assert "full_classical_hiep_ky" in out["pending_scopes"]
    assert out["hiep_ky_v25"]["full_classical_claim"] is False
    v30a = out["hiep_ky_v30a"]
    assert v30a["extension_version"] == "V3_0A_YUE_XING"
    assert v30a["activated_token"] == "月刑"
    assert v30a["decision_effect"] == "CAUTION_ONLY"
    assert v30a["creates_hard_block"] is False
    v30b = out["hiep_ky_v30b"]
    assert v30b["extension_version"] == "V3_0B_SAT_TRIO"
    assert v30b["activated_tokens"] == ["劫煞", "災煞", "月煞"]
    assert v30b["decision_effect"] == "CAUTION_ONLY"
    assert v30b["creates_hard_block"] is False
    assert v30b["full_classical_claim"] is False
    assert v30b["numeric_score"] is None
    assert out["numeric_score"] == "LOCKED_OFF"


def test_event_search_result_keeps_rules_sources_and_no_score():
    raw = {
        "viec": "KY_HOP_DONG",
        "so_ngay_da_quet": 1,
        "xep_hang_status": "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL",
        "top": [{
            "ngay": "2026-09-01",
            "label": "Không ưu tiên",
            "decision_state": "CAUTION",
            "hard_block": False,
            "rank_group": 4,
            "event_state": "CAUTION",
            "personal_v1_1": {},
            "reasons": ["reason"],
            "mapping_status": "VERIFIED",
            "coverage": "V3_0B_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_9",
            "hiep_ky_extension": "V3_0B_SAT_TRIO",
            "rule_ids": ["HK25-X"],
            "source_ids": ["SRC-HK-QD-V11-WIKISOURCE"],
            "matched_evidence": [{"rule_id": "HK25-X", "source_id": "SRC-HK-QD-V11-WIKISOURCE"}],
            "active_hiep_ky_tokens": ["劫煞"],
            "matched_yi_tokens": [],
            "matched_ji_tokens": ["劫煞"],
            "decision_authority": "EVENT",
            "event_state_v1": "NEUTRAL",
            "event_signal_v25": "CAUTION",
        }],
    }
    out = event_search_v25(raw)
    item = out["results"][0]
    assert out["schema_version"] == "2.5-alpha.1"
    assert out["hiep_ky_extension"] == "V3_0B_SAT_TRIO"
    assert out["numeric_score"] is None
    assert item["rules"] == ["HK25-X"]
    assert item["sources"] == ["SRC-HK-QD-V11-WIKISOURCE"]
    assert item["technical"]["matched_ji_tokens"] == ["劫煞"]
    assert item["technical"]["hiep_ky_extension"] == "V3_0B_SAT_TRIO"
    assert item["numeric_score"] is None
    assert item["numeric_score_status"] == "LOCKED_OFF"
