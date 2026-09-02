from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_coverage_gate_v30e10 import event_coverage_rows, v1_engine_readiness
from loi.quyet_dinh.hiep_ky_policy_v25 import resolve_conflict
from loi.quyet_dinh.hiep_ky_v25 import HK_V25_EVENT_RULES


def test_audit_snapshot_is_exactly_43_active_and_score_off():
    cap=capability_inventory()
    assert cap["token_count"]==81
    assert cap["active_calculable_count"]==43
    assert cap["pending_calculator_count"]==38
    assert cap["extension_version"]=="V3_0E23_DA_HAO"
    assert cap["numeric_score"] is None
    assert cap["numeric_score_status"]=="LOCKED_OFF"


def test_audit_coverage_gate_passes_for_all_verified_events():
    readiness=v1_engine_readiness()
    assert readiness["verified_event_count"]==10
    assert readiness["rule_target_gate"] is True
    assert readiness["verified_balance_gate"] is True
    assert readiness["verified_balance_failed_events"]==()
    assert readiness["v1_engine_ready"] is True
    assert readiness["numeric_score"] is None
    for row in event_coverage_rows():
        if row["mapping_status"]=="VERIFIED":
            assert row["active_yi_count"]>=2
            assert row["active_ji_count"]>=2
            assert row["verified_balance_gate"] is True


def test_audit_no_same_event_token_is_both_yi_and_ji():
    for code,rule in HK_V25_EVENT_RULES.items():
        assert not (set(rule.yi_tokens) & set(rule.ji_tokens)), code


def test_audit_pending_source_conflicts_are_not_silently_activated():
    for token in ("守日","天徳","天徳合"):
        row=token_capability(token)
        assert row["calculator_status"]=="PENDING_CALCULATOR"
        assert row["calculator"] is None


def test_audit_hard_block_always_beats_event_and_personal():
    for event_state in ("HARD_BLOCK","FAVORABLE","CAUTION","NEUTRAL","UNKNOWN"):
        for personal_state in ("FAVORABLE","CAUTION","NEUTRAL","UNKNOWN","HARD_BLOCK"):
            out=resolve_conflict(hard_block=True,event_state=event_state,personal_state=personal_state)
            assert out["state"]=="BLOCKED"
            assert out["authority"]=="HARD_BLOCK"
            assert out["numeric_score"] is None


def test_audit_event_caution_cannot_be_rescued_by_personal_support():
    out=resolve_conflict(hard_block=False,event_state="CAUTION",personal_state="FAVORABLE")
    assert out["state"]=="CONSIDER"
    assert out["label"]=="Không ưu tiên"
    assert out["authority"]=="EVENT"


def test_audit_schema_is_truthful_for_final_rule_snapshot():
    out=v25_schema_overlay({})
    cap=out["hiep_ky_v25"]["capability"]
    assert cap["active_calculable_count"]==43
    assert cap["pending_calculator_count"]==38
    assert out["hiep_ky_v1_engine_readiness"]["v1_engine_ready"] is True
    assert out["hiep_ky_v30e22"]["activated_token"]=="除神"
    assert out["hiep_ky_v30e23"]["activated_token"]=="大耗"
    assert out["hiep_ky_v30e23"]["decision_effect"]=="CAUTION_ONLY"
    assert out["hiep_ky_v30e23"]["creates_hard_block"] is False
    assert out["numeric_score"]=="LOCKED_OFF"
