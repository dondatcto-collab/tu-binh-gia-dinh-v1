from loi.quyet_dinh.hiep_ky_v25 import (
    HK_V25_COVERAGE,
    HK_V25_DECISION_HIERARCHY,
    HK_V25_EVENT_RULES,
    HK_V25_NUMERIC_SCORE_STATUS,
    inventory_status,
)

EXPECTED_EVENTS = {
    "AN_TANG",
    "CAU_TAI",
    "CUOI_HOI",
    "DAM_PHAN",
    "DIEU_TRI",
    "DONG_THO",
    "KHAI_TRUONG",
    "KY_HOP_DONG",
    "MUA_TAI_SAN",
    "NHAM_CHUC",
    "NHAP_TRACH",
    "XUAT_HANH",
}


def test_v25_inventory_covers_exact_12_events():
    assert set(HK_V25_EVENT_RULES) == EXPECTED_EVENTS
    assert HK_V25_COVERAGE == "SOURCE_INVENTORY_12_12_DECISION_ACTIVE_12_TRUC_ONLY"


def test_v25_inventory_is_not_decision_active_yet():
    for rule in HK_V25_EVENT_RULES.values():
        assert rule.decision_status == "INVENTORY_ONLY"
        assert rule.numeric_score is None
        assert rule.source_id == "SRC-HK-QD-V11-WIKISOURCE"
        assert rule.yi_tokens or rule.ji_tokens


def test_v25_keeps_no_score_and_conflict_hierarchy_locked():
    status = inventory_status()
    assert status["event_count"] == 12
    assert status["verified_mapping_count"] == 10
    assert status["provisional_mapping_count"] == 2
    assert status["numeric_score"] is None
    assert status["numeric_score_status"] == HK_V25_NUMERIC_SCORE_STATUS == "LOCKED_OFF"
    assert status["hierarchy"] == HK_V25_DECISION_HIERARCHY == "HARD_BLOCK > EVENT > PERSONAL"


def test_v25_provisional_mappings_are_only_modern_semantic_bridges():
    provisional = {k for k, v in HK_V25_EVENT_RULES.items() if v.mapping_status == "PROVISIONAL"}
    assert provisional == {"MUA_TAI_SAN", "DAM_PHAN"}
