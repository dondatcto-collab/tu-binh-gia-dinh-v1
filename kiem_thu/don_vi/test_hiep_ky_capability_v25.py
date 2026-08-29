from loi.quyet_dinh.hiep_ky_capability_v25 import (
    MONTH_BRANCH_TOKENS,
    TRUC_TOKEN_TO_CODE,
    capability_inventory,
    token_capability,
)


def test_exact_12_truc_remain_active_calculable():
    assert set(TRUC_TOKEN_TO_CODE.values()) == {
        "KIEN", "TRU", "MAN", "BINH", "DINH", "CHAP",
        "PHA", "NGUY", "THANH", "THU", "KHAI", "BE",
    }
    for token, code in TRUC_TOKEN_TO_CODE.items():
        row = token_capability(token)
        assert row["calculator_status"] == "ACTIVE_CALCULABLE"
        assert row["calculator"] == "12_TRUC_EXISTING_V1"
        assert row["normalized_code"] == code


def test_v30c_exact_ten_month_branch_tokens_are_active():
    assert MONTH_BRANCH_TOKENS == frozenset({"月建", "月破", "三合", "六合", "月害", "月刑", "劫煞", "災煞", "月煞", "月厭"})
    for token in MONTH_BRANCH_TOKENS:
        row = token_capability(token)
        assert row["calculator_status"] == "ACTIVE_CALCULABLE"
        assert row["calculator"] == "MONTH_BRANCH_RELATIONS_V25_V30C"
        assert row["normalized_code"] == token


def test_named_star_without_calculator_stays_pending():
    for token in ("天徳", "月徳", "天願", "天醫", "大時", "天吏"):
        row = token_capability(token)
        assert row["calculator_status"] == "PENDING_CALCULATOR"
        assert row["calculator"] is None
        assert row["normalized_code"] is None


def test_inventory_claims_only_partial_decision_expansion():
    status = capability_inventory()
    assert status["active_calculable_count"] == 19
    assert status["pending_calculator_count"] == 62
    assert status["decision_expansion_status"] == "PARTIAL_ACTIVE"
    assert status["coverage"] == "12_TRUC_PLUS_MONTH_BRANCH_10"
    assert status["extension_version"] == "V3_0C_YUE_YAN"
    assert status["numeric_score"] is None
    assert status["numeric_score_status"] == "LOCKED_OFF"


def test_no_unknown_token_can_be_implicitly_activated():
    row = token_capability("FAKE_STAR_NOT_IN_CLASSICS")
    assert row["calculator_status"] == "PENDING_CALCULATOR"
