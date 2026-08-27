from loi.quyet_dinh.hiep_ky_capability_v25 import (
    TRUC_TOKEN_TO_CODE,
    capability_inventory,
    token_capability,
)


def test_exact_12_truc_are_the_only_active_calculable_tokens_now():
    assert set(TRUC_TOKEN_TO_CODE.values()) == {
        "KIEN", "TRU", "MAN", "BINH", "DINH", "CHAP",
        "PHA", "NGUY", "THANH", "THU", "KHAI", "BE",
    }
    for token, code in TRUC_TOKEN_TO_CODE.items():
        row = token_capability(token)
        assert row["calculator_status"] == "ACTIVE_CALCULABLE"
        assert row["calculator"] == "12_TRUC_EXISTING_V1"
        assert row["normalized_code"] == code


def test_named_classical_star_without_calculator_stays_pending():
    for token in ("天徳", "月徳", "天願", "三合", "六合", "月破", "劫煞"):
        row = token_capability(token)
        assert row["calculator_status"] == "PENDING_CALCULATOR"
        assert row["calculator"] is None
        assert row["normalized_code"] is None


def test_inventory_does_not_claim_decision_expansion_yet():
    status = capability_inventory()
    assert status["active_calculable_count"] > 0
    assert status["pending_calculator_count"] > 0
    assert status["decision_expansion_status"] == "NOT_YET_ACTIVE"
    assert status["numeric_score"] is None
    assert status["numeric_score_status"] == "LOCKED_OFF"


def test_no_unknown_token_can_be_implicitly_activated():
    row = token_capability("FAKE_STAR_NOT_IN_CLASSICS")
    assert row["calculator_status"] == "PENDING_CALCULATOR"
