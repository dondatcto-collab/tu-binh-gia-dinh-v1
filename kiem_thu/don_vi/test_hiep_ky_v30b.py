from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _neutral_personal(state="NEUTRAL"):
    return {"state": state, "rule_ids": [], "source_ids": []}


def test_v30b_tokens_remain_active_after_v30c():
    cap = capability_inventory()
    assert cap["token_count"] == 81
    assert cap["active_calculable_count"] == 19
    assert cap["pending_calculator_count"] == 62
    assert {"劫煞", "災煞", "月煞"}.issubset(set(cap["active_tokens"]))
    assert cap["coverage"] == "12_TRUC_PLUS_MONTH_BRANCH_10"
    assert cap["extension_version"] == "V3_0C_YUE_YAN"
    assert cap["numeric_score"] is None


def test_v30b_favorable_relation_cannot_override_jie_sha_caution():
    base = {
        "event_code": "KY_HOP_DONG",
        "event_state": "NEUTRAL",
        "mapping_status": "VERIFIED",
        "rule_ids": [],
        "reasons": [],
    }
    out = evaluate_event_v25(base, _neutral_personal("SUPPORT"), chi_thang="DAN", chi_ngay="HOI")
    assert "六合" in out["active_hiep_ky_tokens"]
    assert "劫煞" in out["active_hiep_ky_tokens"]
    assert "六合" in out["matched_yi_tokens"]
    assert "劫煞" in out["matched_ji_tokens"]
    assert out["event_signal_v25"] == "CAUTION"
    assert out["event_state"] == "CAUTION"
    assert out["label"] == "Không ưu tiên"
    assert out["hard_block"] is False
    assert out["numeric_score"] is None


def test_v30b_existing_hard_block_still_wins():
    base = {
        "event_code": "KY_HOP_DONG",
        "event_state": "JI",
        "mapping_status": "VERIFIED",
        "rule_ids": [],
        "reasons": [],
    }
    out = evaluate_event_v25(base, _neutral_personal("SUPPORT"), chi_thang="DAN", chi_ngay="HOI")
    assert out["hard_block"] is True
    assert out["decision_state"] == "BLOCKED"
    assert out["event_state"] == "JI"
    assert out["numeric_score"] is None


def test_v30b_schema_remains_explicit_after_v30c():
    s = v25_schema_overlay({"implemented_scopes": [], "pending_scopes": [], "principles": []})
    assert s["hiep_ky_v25"]["coverage"] == "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"
    assert s["hiep_ky_v25"]["effective_coverage"] == COVERAGE
    assert s["hiep_ky_v30a"]["extension_version"] == "V3_0A_YUE_XING"
    v = s["hiep_ky_v30b"]
    assert v["extension_version"] == "V3_0B_SAT_TRIO"
    assert v["activated_tokens"] == ["劫煞", "災煞", "月煞"]
    assert v["decision_effect"] == "CAUTION_ONLY"
    assert v["creates_hard_block"] is False
    assert v["full_classical_claim"] is False
    assert v["numeric_score"] is None
    assert "hiep_ky_v30b_sat_trio" in s["implemented_scopes"]
