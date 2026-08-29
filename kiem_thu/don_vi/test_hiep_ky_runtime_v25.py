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


def test_v30a_yue_hai_and_yue_xing_both_survive_as_caution_evidence():
    # KY_HOP_DONG: tháng Dần/ngày Tị đồng thời 月害 + 月刑; không được ghi đè.
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="DAN", chi_ngay="TI")
    assert set(r["matched_ji_tokens"]) == {"月害", "月刑"}
    assert r["event_signal_v25"] == "CAUTION"
    assert r["hard_block"] is False
    assert r["label"] == "Không ưu tiên"
    assert r["decision_authority"] == "EVENT"
    assert len([x for x in r["matched_evidence"] if x["token"] in {"月害", "月刑"}]) == 2


def test_v30a_yue_xing_alone_is_caution_not_hard_block():
    # Tháng Tý, ngày Mão mang 月刑; KY_HOP_DONG không có token ACTIVE khác tại cặp này.
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="TY", chi_ngay="MAO")
    assert r["matched_ji_tokens"] == ["月刑"]
    assert r["event_signal_v25"] == "CAUTION"
    assert r["hard_block"] is False
    assert r["decision_state"] != "BLOCKED"
    ev = r["matched_evidence"][0]
    assert ev["rule_id"].startswith("HK25-KY_HOP_DONG-JI-")
    assert ev["source_id"] == "SRC-HK-QD-V11-WIKISOURCE"
    assert ev["source_location"] == "卷十一 · 立券交易"


def test_personal_cannot_rescue_event_caution():
    r = evaluate_event_v25(_base(), _personal("SUPPORT"), chi_thang="TY", chi_ngay="MAO")
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
    assert r["coverage"] == COVERAGE == "V3_0A_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_6"
    assert r["hiep_ky_extension"] == "V3_0A_YUE_XING"
