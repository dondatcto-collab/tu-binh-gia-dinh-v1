from loi.quyet_dinh.hiep_ky_month_v25 import (
    JIE_SHA_BY_MONTH_BRANCH,SHI_DE_BY_MONTH_BRANCH,YUE_SHA_BY_MONTH_BRANCH,YUE_XING_BY_MONTH_BRANCH,YUE_YAN_BY_MONTH_BRANCH,ZAI_SHA_BY_MONTH_BRANCH,
    active_month_tokens,calculator_status,jie_sha_branch,shi_de_branch,tam_hop_partners,yue_sha_branch,yue_xing_branch,yue_yan_branch,zai_sha_branch,
)


def test_tam_hop_partners_follow_month_branch_group():
    assert tam_hop_partners("DAN")==frozenset({"NGO","TUAT"}); assert tam_hop_partners("MAO")==frozenset({"HOI","MUI"}); assert tam_hop_partners("TY")==frozenset({"THAN","THIN"}); assert tam_hop_partners("DAU")==frozenset({"TI","SUU"})


def test_month_build_and_break_are_exact():
    assert active_month_tokens("DAN","DAN")== ("月建",); assert active_month_tokens("DAN","THAN")== ("月破",)


def test_relations_and_overlaps_are_retained():
    assert active_month_tokens("DAN","NGO")== ("三合","時徳")
    assert active_month_tokens("DAN","HOI")== ("六合","劫煞")
    assert active_month_tokens("DAN","TI")== ("月害","月刑")


def test_v30a_yue_xing_locks_all_twelve_month_tables():
    expected={"DAN":"TI","MAO":"TY","THIN":"THIN","TI":"THAN","NGO":"NGO","MUI":"SUU","THAN":"DAN","DAU":"DAU","TUAT":"MUI","HOI":"HOI","TY":"MAO","SUU":"TUAT"}; assert YUE_XING_BY_MONTH_BRANCH==expected
    for m,d in expected.items(): assert yue_xing_branch(m)==d; assert "月刑" in active_month_tokens(m,d)


def test_v30b_sat_trio_locks_all_twelve_month_tables():
    ej={"DAN":"HOI","MAO":"THAN","THIN":"TI","TI":"DAN","NGO":"HOI","MUI":"THAN","THAN":"TI","DAU":"DAN","TUAT":"HOI","HOI":"THAN","TY":"TI","SUU":"DAN"}
    ez={"DAN":"TY","MAO":"DAU","THIN":"NGO","TI":"MAO","NGO":"TY","MUI":"DAU","THAN":"NGO","DAU":"MAO","TUAT":"TY","HOI":"DAU","TY":"NGO","SUU":"MAO"}
    ey={"DAN":"SUU","MAO":"TUAT","THIN":"MUI","TI":"THIN","NGO":"SUU","MUI":"TUAT","THAN":"MUI","DAU":"THIN","TUAT":"SUU","HOI":"TUAT","TY":"MUI","SUU":"THIN"}
    assert JIE_SHA_BY_MONTH_BRANCH==ej; assert ZAI_SHA_BY_MONTH_BRANCH==ez; assert YUE_SHA_BY_MONTH_BRANCH==ey
    for m in ej: assert jie_sha_branch(m)==ej[m]; assert zai_sha_branch(m)==ez[m]; assert yue_sha_branch(m)==ey[m]


def test_v30c_yue_yan_locks_all_twelve_month_tables():
    expected={"DAN":"TUAT","MAO":"DAU","THIN":"THAN","TI":"MUI","NGO":"NGO","MUI":"TI","THAN":"THIN","DAU":"MAO","TUAT":"DAN","HOI":"SUU","TY":"TY","SUU":"HOI"}; assert YUE_YAN_BY_MONTH_BRANCH==expected
    for m,d in expected.items(): assert yue_yan_branch(m)==d; assert "月厭" in active_month_tokens(m,d)


def test_v30d_shi_de_locks_four_seasons_across_twelve_month_branches():
    expected={"DAN":"NGO","MAO":"NGO","THIN":"NGO","TI":"THIN","NGO":"THIN","MUI":"THIN","THAN":"TY","DAU":"TY","TUAT":"TY","HOI":"DAN","TY":"DAN","SUU":"DAN"}
    assert SHI_DE_BY_MONTH_BRANCH==expected
    for m,d in expected.items(): assert shi_de_branch(m)==d; assert "時徳" in active_month_tokens(m,d)


def test_v30d_conflict_overlap_is_retained():
    tokens=active_month_tokens("THIN","NGO"); assert "時徳" in tokens; assert "災煞" in tokens


def test_v30c_overlapping_tokens_are_all_retained():
    tokens=active_month_tokens("NGO","NGO"); assert {"月建","月刑","月厭"}.issubset(set(tokens))


def test_calculator_scope_is_explicit_and_no_score():
    s=calculator_status(); assert set(s["active_tokens"])=={"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳"}; assert s["extension_version"]=="V3_0D_SHI_DE"; assert s["calculator"]=="MONTH_BRANCH_RELATIONS_V25_V30D"; assert s["numeric_score"] is None


def test_invalid_branch_fails_closed():
    try: active_month_tokens("INVALID","TY")
    except ValueError as exc: assert "CHI_KHONG_HOP_LE" in str(exc)
    else: raise AssertionError("invalid branch must not be silently accepted")
