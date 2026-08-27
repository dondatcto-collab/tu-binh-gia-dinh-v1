from loi.quyet_dinh.hiep_ky_evidence_v25 import all_evidence, evidence_for_event, evidence_status
from loi.quyet_dinh.hiep_ky_v25 import HK_V25_EVENT_RULES


def test_all_12_events_have_traceable_evidence():
    assert len(HK_V25_EVENT_RULES) == 12
    for code, rule in HK_V25_EVENT_RULES.items():
        items = evidence_for_event(code)
        assert len(items) == len(rule.yi_tokens) + len(rule.ji_tokens)
        assert items
        for item in items:
            assert item.rule_id.startswith(f"HK25-{code}-")
            assert item.source_id == rule.source_id
            assert item.source_location == rule.source_location
            assert item.decision_status == "INVENTORY_ONLY"
            assert item.numeric_score is None
            assert item.evidence_status in {"VERIFIED", "PROVISIONAL"}


def test_rule_ids_are_unique_and_stable_shape():
    items = all_evidence()
    ids = [x.rule_id for x in items]
    assert len(ids) == len(set(ids))
    assert all(x.startswith("HK25-") for x in ids)


def test_provisional_modern_mappings_stay_provisional():
    for code in ("MUA_TAI_SAN", "DAM_PHAN"):
        items = evidence_for_event(code)
        assert items
        assert {x.evidence_status for x in items} == {"PROVISIONAL"}


def test_verified_events_do_not_get_downgraded_or_upgraded_implicitly():
    for code, rule in HK_V25_EVENT_RULES.items():
        if rule.mapping_status == "VERIFIED":
            assert {x.evidence_status for x in evidence_for_event(code)} == {"VERIFIED"}


def test_evidence_status_is_inventory_only_and_score_off():
    status = evidence_status()
    assert status["event_count"] == 12
    assert status["evidence_count"] > 12
    assert status["evidence_count"] == status["rule_id_count"]
    assert status["decision_status"] == "INVENTORY_ONLY"
    assert status["numeric_score"] is None
    assert status["numeric_score_status"] == "LOCKED_OFF"
