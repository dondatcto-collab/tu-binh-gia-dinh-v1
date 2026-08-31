from loi.quyet_dinh.hiep_ky_capability_v25 import (
    DAY_BRANCH_TOKENS, MONTH_BRANCH_DAY_BRANCH_TOKENS, MONTH_BRANCH_DAY_PILLAR_TOKENS, MONTH_BRANCH_DAY_STEM_TOKENS, MONTH_BRANCH_TOKENS,
    PAIRED_MONTH_DAY_BRANCH_TOKENS, QUARTERED_MONTH_DAY_BRANCH_TOKENS, SEASON_DAY_BRANCH_TOKENS, SEASON_DAY_PILLAR_TOKENS, SEASON_DAY_STEM_TOKENS,
    SEASON_GUAN_RI_TOKENS, SEASON_WANG_RI_TOKENS, TRUC_TOKEN_TO_CODE, capability_inventory, token_capability,
)

def test_exact_12_truc_remain_active_calculable():
    assert set(TRUC_TOKEN_TO_CODE.values())=={"KIEN","TRU","MAN","BINH","DINH","CHAP","PHA","NGUY","THANH","THU","KHAI","BE"}
    for token,code in TRUC_TOKEN_TO_CODE.items():
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="12_TRUC_EXISTING_V1"; assert row["normalized_code"]==code

def test_v30d_eleven_month_branch_tokens_remain_active():
    assert MONTH_BRANCH_TOKENS==frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"})
    for token in MONTH_BRANCH_TOKENS:
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]=="MONTH_BRANCH_RELATIONS_V25_V30D"

def test_typed_calculator_groups_are_exact():
    assert MONTH_BRANCH_DAY_STEM_TOKENS==frozenset({"月徳","月徳合","月恩"}); assert SEASON_DAY_STEM_TOKENS==frozenset({"四相"}); assert MONTH_BRANCH_DAY_PILLAR_TOKENS==frozenset({"天願"}); assert SEASON_DAY_PILLAR_TOKENS==frozenset({"天赦"}); assert SEASON_DAY_BRANCH_TOKENS==frozenset({"天喜"}); assert DAY_BRANCH_TOKENS==frozenset({"五合"}); assert MONTH_BRANCH_DAY_BRANCH_TOKENS==frozenset({"天醫"}); assert PAIRED_MONTH_DAY_BRANCH_TOKENS==frozenset({"解神"}); assert QUARTERED_MONTH_DAY_BRANCH_TOKENS==frozenset({"五富"}); assert SEASON_WANG_RI_TOKENS==frozenset({"王日"}); assert SEASON_GUAN_RI_TOKENS==frozenset({"官日"})

def test_known_calculators_remain_bound_to_their_tokens():
    expected={"月徳":"MONTH_BRANCH_DAY_STEM_V30E3","月徳合":"MONTH_BRANCH_DAY_STEM_V30E3","月恩":"MONTH_BRANCH_DAY_STEM_V30E3","四相":"SEASON_DAY_STEM_V30E4","天願":"MONTH_BRANCH_DAY_PILLAR_V30E5","天赦":"SEASON_DAY_PILLAR_V30E6","天喜":"SEASON_DAY_BRANCH_V30E7","五合":"DAY_BRANCH_V30E8","天醫":"MONTH_BRANCH_DAY_BRANCH_V30E9","解神":"MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN","五富":"MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU","王日":"SEASON_DAY_BRANCH_V30E12_WANG_RI","官日":"SEASON_DAY_BRANCH_V30E13_GUAN_RI"}
    for token,calculator in expected.items():
        row=token_capability(token); assert row["calculator_status"]=="ACTIVE_CALCULABLE"; assert row["calculator"]==calculator; assert row["normalized_code"]==token

def test_other_named_stars_without_calculator_stay_pending():
    for token in ("天徳","天徳合"):
        row=token_capability(token); assert row["calculator_status"]=="PENDING_CALCULATOR"; assert row["calculator"] is None

def test_current_global_capability_is_checked_only_here():
    s=capability_inventory(); assert s["token_count"]==81; assert s["active_calculable_count"]==33; assert s["pending_calculator_count"]==48; assert s["extension_version"]=="V3_0E13_GUAN_RI"; assert s["numeric_score"] is None; assert s["numeric_score_status"]=="LOCKED_OFF"

def test_no_unknown_token_can_be_implicitly_activated():
    assert token_capability("FAKE_STAR_NOT_IN_CLASSICS")["calculator_status"]=="PENDING_CALCULATOR"
