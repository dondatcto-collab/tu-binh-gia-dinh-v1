from loi.quyet_dinh.hiep_ky_capability_v25 import (
    MONTH_BRANCH_DAY_PILLAR_TOKENS, MONTH_BRANCH_DAY_STEM_TOKENS, MONTH_BRANCH_TOKENS, SEASON_DAY_STEM_TOKENS, TRUC_TOKEN_TO_CODE,
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


def test_v30e4_opens_exactly_one_season_day_stem_token():
    assert SEASON_DAY_STEM_TOKENS==frozenset({"四相"})
    row=token_capability("四相"); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="SEASON_DAY_STEM_V30E4"; assert row["normalized_code"]=="四相"


def test_v30e5_opens_exactly_one_month_day_pillar_token():
    assert MONTH_BRANCH_DAY_PILLAR_TOKENS==frozenset({"天願"})
    row=token_capability("天願"); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="MONTH_BRANCH_DAY_PILLAR_V30E5"; assert row["normalized_code"]=="天願"


def test_other_named_stars_without_calculator_stay_pending():
    for token in ("天徳","天醫","天徳合"):
        row=token_capability(token); assert row["calculator_status"]=="PENDING_CALCULATOR"; assert row["calculator"] is None


def test_inventory_claims_only_partial_decision_expansion():
    s=capability_inventory(); assert s["token_count"]==81; assert s["active_calculable_count"]==25; assert s["pending_calculator_count"]==56; assert s["coverage"]=="12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1"; assert s["extension_version"]=="V3_0E5_TIAN_YUAN"; assert s["numeric_score"] is None; assert s["numeric_score_status"]=="LOCKED_OFF"


def test_no_unknown_token_can_be_implicitly_activated():
    assert token_capability("FAKE_STAR_NOT_IN_CLASSICS")["calculator_status"]=="PENDING_CALCULATOR"
