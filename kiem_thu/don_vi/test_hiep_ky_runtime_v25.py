from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _base(event_code="KY_HOP_DONG", state="NEUTRAL", mapping="VERIFIED"):
    return {
        "event_code": event_code,
        "event_state": state,
        "mapping_status": mapping,
        "label": "Chưa có tín hiệu theo việc",
        "rank_group": 3,
        "reasons": [],
        "rule_ids": ["HK-GENERAL-0001"],
        "source_id": "SRC-HK-QD-V11-WIKISOURCE",
    }


def _personal(state="DESCRIPTIVE_ONLY"):
    return {"state": state, "rule_ids": [], "source_ids": [], "branch_impacts": [], "theme": {}, "dien_giai": {}, "technical_facts": []}


def test_hard_block_v1_still_wins_everything():
    r = evaluate_event_v25(_base(state="JI"), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="HOI")
    assert r["hard_block"] is True
    assert r["decision_state"] == "BLOCKED"
    assert r["label"] == "Bị chặn"
    assert r["rank_group"] == 9


def test_new_yi_token_can_support_neutral_event_without_score():
    # KY_HOP_DONG có 六合 trong 宜; tháng Dần, ngày Hợi là 六合.
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="HOI")
    assert r["matched_yi_tokens"] == ["六合"]
    assert r["event_signal_v25"] == "FAVORABLE"
    assert r["label"] == "Ưu tiên"
    assert r["score"] is None
    assert r["numeric_score_status"] == "LOCKED_OFF"


def test_new_ji_token_is_caution_not_new_hard_block():
    # KY_HOP_DONG có 月害 trong 忌; tháng Dần, ngày Tị là 月害.
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="TI")
    assert r["matched_ji_tokens"] == ["月害"]
    assert r["event_signal_v25"] == "CAUTION"
    assert r["hard_block"] is False
    assert r["label"] == "Không ưu tiên"
    assert r["decision_authority"] == "EVENT"


def test_personal_cannot_rescue_event_caution():
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="TI")
    assert r["label"] == "Không ưu tiên"
    assert r["rank_group"] == 4


def test_provisional_mapping_cannot_be_promoted_to_priority_by_new_signal():
    r = evaluate_event_v25(_base(event_code="DAM_PHAN", mapping="PROVISIONAL"), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="HOI")
    assert "六合" in r["matched_yi_tokens"]
    assert r["label"] == "Có thể cân nhắc"
    assert r["decision_authority"] == "EVENT_PROVISIONAL"


def test_runtime_is_traceable_and_coverage_is_explicitly_partial():
    r = evaluate_event_v25(_base(), _personal(), chi_thang="DAN", chi_ngay="HOI")
    assert r["matched_evidence"]
    ev = r["matched_evidence"][0]
    assert ev["rule_id"]
    assert ev["source_id"]
    assert ev["source_location"]
    assert ev["decision_status"] == "ACTIVE"
    assert r["coverage"] == COVERAGE == "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"
