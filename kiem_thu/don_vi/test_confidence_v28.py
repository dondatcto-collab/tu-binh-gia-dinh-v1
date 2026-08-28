from loi.ket_qua.confidence_v28 import (
    CLEAR,
    MEDIUM,
    INSUFFICIENT,
    CONFIDENCE_MODEL_VERSION,
    apply_confidence_v28,
)


def event(*, mapping="VERIFIED", authority="EVENT", hard_block=False, rules=True, sources=True):
    return {
        "kind": "event_day",
        "conclusion": {"label": "Bị chặn" if hard_block else "Ưu tiên", "state": "HARD_BLOCK" if hard_block else "FAVORABLE"},
        "confidence_state": "Căn cứ rõ",
        "event_context": {"hard_block": hard_block},
        "rules": ["HK-V25-TEST"] if rules else [],
        "sources": ["SRC-HK-QD-V11-WIKISOURCE"] if sources else [],
        "evidence": ["evidence"],
        "technical": {
            "mapping_status": mapping,
            "decision_authority": authority,
            "matched_yi_tokens": ["六合"],
            "matched_ji_tokens": [],
        },
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }


def test_verified_event_with_traceability_can_be_clear():
    out = apply_confidence_v28(event(), time_certainty="KNOWN")
    assert out["confidence_state"] == CLEAR
    assert out["confidence_model_version"] == CONFIDENCE_MODEL_VERSION
    assert out["numeric_score"] is None
    assert out["conclusion"]["label"] == "Ưu tiên"


def test_provisional_mapping_is_capped_at_medium_even_when_label_is_favorable():
    out = apply_confidence_v28(event(mapping="PROVISIONAL"), time_certainty="KNOWN")
    assert out["confidence_state"] == MEDIUM
    assert any("PROVISIONAL" in x for x in out["confidence_basis"])


def test_event_without_rule_or_source_is_insufficient_not_clear():
    out = apply_confidence_v28(event(rules=False), time_certainty="KNOWN")
    assert out["confidence_state"] == INSUFFICIENT
    out2 = apply_confidence_v28(event(sources=False), time_certainty="KNOWN")
    assert out2["confidence_state"] == INSUFFICIENT


def test_uncertain_birth_time_only_caps_when_personal_layer_is_authority():
    personal = apply_confidence_v28(event(authority="PERSONAL"), time_certainty="APPROXIMATE")
    assert personal["confidence_state"] == MEDIUM
    event_authority = apply_confidence_v28(event(authority="EVENT"), time_certainty="APPROXIMATE")
    assert event_authority["confidence_state"] == CLEAR


def test_verified_hard_block_remains_clear_even_when_birth_time_is_uncertain():
    out = apply_confidence_v28(event(hard_block=True), time_certainty="UNKNOWN")
    assert out["confidence_state"] == CLEAR
    assert out["conclusion"]["state"] == "HARD_BLOCK"
    assert any("HARD_BLOCK" in x for x in out["confidence_basis"])


def test_domain_needs_rule_source_and_birth_certainty_for_clear():
    domain = {
        "kind": "domain_period", "conclusion": {"label": "Cân nhắc"},
        "rules": ["D-R1"], "sources": ["D-S1"], "evidence": ["e1"],
        "technical": {}, "numeric_score": None,
    }
    assert apply_confidence_v28(domain, time_certainty="KNOWN")["confidence_state"] == CLEAR
    assert apply_confidence_v28(domain, time_certainty="UNKNOWN")["confidence_state"] == MEDIUM
    domain["sources"] = []
    assert apply_confidence_v28(domain, time_certainty="KNOWN")["confidence_state"] == INSUFFICIENT


def test_hour_reference_is_always_insufficient_for_personal_good_bad_claim():
    hour = {"kind": "personal_hour_reference", "confidence_state": "Căn cứ rõ", "numeric_score": None}
    out = apply_confidence_v28(hour, time_certainty="KNOWN")
    assert out["confidence_state"] == INSUFFICIENT
    assert "personal-hour" in out["confidence_basis"][0]


def test_event_search_applies_model_to_top_and_all_without_reordering():
    a, b = event(), event(mapping="PROVISIONAL")
    a["date"], b["date"] = "2026-09-01", "2026-09-02"
    search = {"kind": "event_search", "results": [a], "all_results": [a, b], "numeric_score": None}
    out = apply_confidence_v28(search, time_certainty="KNOWN")
    assert [x["date"] for x in out["all_results"]] == ["2026-09-01", "2026-09-02"]
    assert out["results"][0]["confidence_state"] == CLEAR
    assert out["all_results"][1]["confidence_state"] == MEDIUM
    assert out["confidence_model_version"] == CONFIDENCE_MODEL_VERSION
