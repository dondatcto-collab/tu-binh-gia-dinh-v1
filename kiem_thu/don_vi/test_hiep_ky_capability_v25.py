from loi.quyet_dinh.hiep_ky_capability_v25 import (
    MONTH_BRANCH_DAY_STEM_TOKENS, MONTH_BRANCH_TOKENS, TRUC_TOKEN_TO_CODE,
    capability_inventory, token_capability,
)


def test_exact_12_truc_remain_active_calculable():
    assert set(TRUC_TOKEN_TO_CODE.values()) == {"KIEN","TRU","MAN","BINH","DINH","CHAP","PHA","NGUY","THANH","THU","KHAI","BE"}
    for token, code in TRUC_TOKEN_TO_CODE.items():
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="12_TRUC_EXISTING_V1"; assert row["normalized_code"]==code


def test_v30d_eleven_month_branch_tokens_remain_active():
    assert MONTH_BRANCH_TOKENS==frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})
    for token in MONTH_BRANCH_TOKENS:
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="MONTH_BRANCH_RELATIONS_V25_V30D"


def test_v30e3_opens_exactly_three_day_stem_tokens():
    assert MONTH_BRANCH_DAY_STEM_TOKENS==frozenset({"月徳","月徳合","月恩"})
    for token in MONTH_BRANCH_DAY_STEM_TOKENS:
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"; assert row["normalized_code"]==token


def test_other_named_stars_without_calculator_stay_pending():
    for token in ("天徳","天願","天醫","四相"):
        row=token_capability(token); assert row["calculator_status"]=="PENDING_CALCULATOR"; assert row["calculator"] is None


def test_inventory_claims_only_partial_decision_expansion():
    s=capability_inventory(); assert s["token_count"]==81; assert s["active_calculable_count"]==23; assert s["pending_calculator_count"]==58; assert s["coverage"]=="12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3"; assert s["extension_version"]=="V3_0E3_YUE_EN"; assert s["numeric_score"] is None; assert s["numeric_score_status"]=="LOCKED_OFF"


def test_no_unknown_token_can_be_implicitly_activated():
    assert token_capability("FAKE_STAR_NOT_IN_CLASSICS")["calculator_status"]=="PENDING_CALCULATOR"
