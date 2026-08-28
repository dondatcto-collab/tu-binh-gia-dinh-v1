from loi.gio.quyet_dinh_v29c import (
    HOUR_SCIENCE_POLICY_VERSION,
    enrich_hour_fusion_v29c,
    v29c_schema_overlay,
)


def _fused(hours):
    return {
        "kind": "personal_hour_fusion",
        "conclusion": {"state": "HOUR_RULE_DECISION_READY", "label": "Đã phân loại"},
        "hours": hours,
        "rules": [],
        "sources": [],
        "evidence": [],
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }


def _personal(chi, state, *, boundary="VERIFIED_NON_LATE_ZI", can="BINH"):
    return {
        "chi": chi,
        "hour_can": can,
        "hour_can_vi": "Bính" if can else None,
        "day_can": "GIAP",
        "day_can_vi": "Giáp",
        "day_chi": "DAN",
        "day_chi_vi": "Dần",
        "personal_transit_state": state,
        "personal_transit_label": {"SUPPORT": "Thuận nền mệnh", "CAUTION": "Cần thận trọng", "NEUTRAL": "Trung tính", "DESCRIPTIVE_ONLY": "Can giờ Tý còn tranh luận"}[state],
        "stem_effect": "FAVORABLE" if state == "SUPPORT" else "UNFAVORABLE" if state == "CAUTION" else "NEUTRAL",
        "branch_effect": "NEUTRAL",
        "personal_rule_ids": ["BT-DY-0401", "TRANSIT-001"] if state != "DESCRIPTIVE_ONLY" else [],
        "personal_source_ids": ["SRC-UHTB-CHEP", "SRC-ZPZQ-NLC-SCAN"],
        "hour_stem_method_id": "NGU_THU_DON",
        "hour_stem_rule_id": None,
        "hour_stem_source_id": "SRC-UHTB-CHEP",
        "hour_stem_boundary_status": boundary,
        "hour_stem_conflict_id": "TIME-0007" if boundary == "CONFLICTED_LATE_ZI" else None,
        "hour_stem_note": "test",
    }


def test_double_support_becomes_stronger_priority_without_score():
    hours = [{
        "chi": "SUU", "decision_state": "PERSONAL_GOOD_CANDIDATE", "decision_label": "Có thể ưu tiên",
        "is_personal_good_hour": True, "is_personal_bad_hour": False,
    }]
    out = enrich_hour_fusion_v29c(_fused(hours), personal_hours=[_personal("SUU", "SUPPORT")])
    h = out["hours"][0]
    assert out["hour_science_policy_version"] == HOUR_SCIENCE_POLICY_VERSION == "2.9C-alpha.1"
    assert h["decision_state"] == "PERSONAL_GOOD_CANDIDATE"
    assert h["decision_label"] == "Ưu tiên hơn"
    assert h["fusion_alignment"] == "DOUBLE_SUPPORT"
    assert h["hour_can"] == "BINH"
    assert "BT-DY-0401" in out["rules"]
    assert "SRC-UHTB-CHEP" in out["sources"]
    assert out["numeric_score"] is None


def test_personal_support_can_promote_relation_neutral_hour():
    hours = [{
        "chi": "MAO", "decision_state": "PERSONAL_NEUTRAL_HOUR", "decision_label": "Trung tính",
        "is_personal_good_hour": False, "is_personal_bad_hour": False,
    }]
    out = enrich_hour_fusion_v29c(_fused(hours), personal_hours=[_personal("MAO", "SUPPORT")])
    h = out["hours"][0]
    assert h["decision_state"] == "PERSONAL_GOOD_CANDIDATE"
    assert h["fusion_alignment"] == "PERSONAL_SUPPORT_ONLY"


def test_caution_wins_when_relation_and_personal_evidence_disagree():
    hours = [{
        "chi": "NGO", "decision_state": "PERSONAL_GOOD_CANDIDATE", "decision_label": "Có thể ưu tiên",
        "is_personal_good_hour": True, "is_personal_bad_hour": False,
    }]
    out = enrich_hour_fusion_v29c(_fused(hours), personal_hours=[_personal("NGO", "CAUTION")])
    h = out["hours"][0]
    assert h["decision_state"] == "PERSONAL_CAUTION_HOUR"
    assert h["decision_label"] == "Nên thận trọng"
    assert h["fusion_alignment"] == "MIXED_CAUTION"
    assert h["is_personal_bad_hour"] is False


def test_late_zi_conflict_never_uses_hour_stem_to_strengthen_decision():
    hours = [{
        "chi": "TY", "decision_state": "PERSONAL_GOOD_CANDIDATE", "decision_label": "Có thể ưu tiên",
        "is_personal_good_hour": True, "is_personal_bad_hour": False, "decision_basis": "Lục hợp.",
    }]
    p = _personal("TY", "DESCRIPTIVE_ONLY", boundary="CONFLICTED_LATE_ZI", can=None)
    out = enrich_hour_fusion_v29c(_fused(hours), personal_hours=[p])
    h = out["hours"][0]
    assert h["decision_label"] == "Có thể ưu tiên"
    assert h["fusion_alignment"] == "LATE_ZI_GUARDED_RELATION_ONLY"
    assert h["hour_can"] is None
    assert h["hour_stem_conflict_id"] == "TIME-0007"
    assert out["late_zi_guarded_hours"] == 1


def test_hard_block_short_circuits_hour_science():
    blocked = {
        "kind": "personal_hour_fusion",
        "conclusion": {"state": "BLOCKED_BY_DAY"},
        "hours": [{"chi": "SUU", "decision_state": "INELIGIBLE_BY_DAY"}],
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
    out = enrich_hour_fusion_v29c(blocked, personal_hours=[_personal("SUU", "SUPPORT")])
    assert out["hours"][0]["decision_state"] == "INELIGIBLE_BY_DAY"
    assert out["numeric_score"] is None


def test_schema_announces_v29c_but_keeps_full_classical_hour_pending():
    out = v29c_schema_overlay({"implemented_scopes": [], "principles": []})
    cap = out["hour_science_v29c"]
    assert cap["stem_branch_xiji_fusion_ready"] is True
    assert cap["late_zi_conflict_guard"] is True
    assert cap["full_classical_hour_auspiciousness_ready"] is False
    assert cap["numeric_score"] is None
    assert "personal_hour_stem_branch_xiji_fusion" in out["implemented_scopes"]
