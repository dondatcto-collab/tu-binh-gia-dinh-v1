from loi.quyet_dinh.hiep_ky_policy_v25 import (
    DECISION_HIERARCHY,
    NUMERIC_SCORE_STATUS,
    RuleEvidence,
    resolve_conflict,
)


def _assert_no_score(result: dict) -> None:
    assert result["numeric_score"] is None
    assert result["numeric_score_status"] == "LOCKED_OFF"
    assert result["hierarchy"] == "HARD_BLOCK > EVENT > PERSONAL"


def test_rule_evidence_contract_is_traceable_and_inventory_only():
    ev = RuleEvidence(
        rule_id="HK25-KHAI_TRUONG-YI-TIEN_NGUYEN",
        event_code="KHAI_TRUONG",
        token="天願",
        polarity="YI",
        source_id="SRC-HK-QD-V11-WIKISOURCE",
        source_location="卷十一 · 開市",
        evidence_status="VERIFIED",
    )
    assert ev.rule_id
    assert ev.source_id
    assert ev.source_location
    assert ev.decision_status == "INVENTORY_ONLY"
    assert ev.numeric_score is None


def test_gold_1_event_and_personal_favorable_is_favorable():
    r = resolve_conflict(hard_block=False, event_state="FAVORABLE", personal_state="FAVORABLE")
    assert r["state"] == "FAVORABLE"
    assert r["label"] == "Ưu tiên"
    _assert_no_score(r)


def test_gold_2_hard_block_beats_personal_and_event_favorable():
    r = resolve_conflict(hard_block=True, event_state="FAVORABLE", personal_state="FAVORABLE")
    assert r["state"] == "BLOCKED"
    assert r["label"] == "Bị chặn"
    assert r["authority"] == "HARD_BLOCK"
    _assert_no_score(r)


def test_gold_3_event_favorable_personal_caution_only_consider():
    r = resolve_conflict(hard_block=False, event_state="FAVORABLE", personal_state="CAUTION")
    assert r["state"] == "CONSIDER"
    assert r["label"] == "Có thể cân nhắc"
    _assert_no_score(r)


def test_gold_4_broader_favorable_context_cannot_rescue_hard_block():
    # personal_state đại diện lớp cá nhân/bối cảnh thuận; hard_block vẫn thắng tuyệt đối.
    r = resolve_conflict(hard_block=True, event_state="NEUTRAL", personal_state="FAVORABLE")
    assert r["state"] == "BLOCKED"
    assert r["authority"] == "HARD_BLOCK"
    _assert_no_score(r)


def test_gold_5_personal_only_breaks_tie_when_event_has_no_strong_signal():
    favorable = resolve_conflict(hard_block=False, event_state="NEUTRAL", personal_state="FAVORABLE")
    caution = resolve_conflict(hard_block=False, event_state="NEUTRAL", personal_state="CAUTION")
    assert favorable["authority"] == "PERSONAL_TIE_BREAK"
    assert caution["authority"] == "PERSONAL_TIE_BREAK"
    assert favorable["state"] == "CONSIDER"
    assert caution["state"] == "CONSIDER"
    _assert_no_score(favorable)
    _assert_no_score(caution)


def test_unknown_unknown_is_insufficient_not_invented_decision():
    r = resolve_conflict(hard_block=False, event_state="UNKNOWN", personal_state="UNKNOWN")
    assert r["state"] == "INSUFFICIENT"
    assert r["label"] == "Chưa đủ căn cứ"
    _assert_no_score(r)


def test_constants_stay_locked():
    assert DECISION_HIERARCHY == "HARD_BLOCK > EVENT > PERSONAL"
    assert NUMERIC_SCORE_STATUS == "LOCKED_OFF"
