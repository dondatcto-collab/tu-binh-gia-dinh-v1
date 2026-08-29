from loi.quyet_dinh.hiep_ky_month_v25 import (
    YUE_XING_BY_MONTH_BRANCH,
    active_month_tokens,
    calculator_status,
    tam_hop_partners,
    yue_xing_branch,
)


def test_tam_hop_partners_follow_month_branch_group():
    assert tam_hop_partners("DAN") == frozenset({"NGO", "TUAT"})
    assert tam_hop_partners("MAO") == frozenset({"HOI", "MUI"})
    assert tam_hop_partners("TY") == frozenset({"THAN", "THIN"})
    assert tam_hop_partners("DAU") == frozenset({"TI", "SUU"})


def test_month_build_and_break_are_exact():
    assert active_month_tokens("DAN", "DAN") == ("月建",)
    assert active_month_tokens("DAN", "THAN") == ("月破",)


def test_sanhe_liuhe_yuehai_are_not_confused():
    assert active_month_tokens("DAN", "NGO") == ("三合",)
    assert active_month_tokens("DAN", "HOI") == ("六合",)
    # V3.0A: tháng Dần ngày Tị vừa 月害 vừa 月刑; phải giữ cả hai evidence.
    assert active_month_tokens("DAN", "TI") == ("月害", "月刑")


def test_v30a_yue_xing_locks_all_twelve_month_tables():
    expected = {
        "DAN": "TI",
        "MAO": "TY",
        "THIN": "THIN",
        "TI": "THAN",
        "NGO": "NGO",
        "MUI": "SUU",
        "THAN": "DAN",
        "DAU": "DAU",
        "TUAT": "MUI",
        "HOI": "HOI",
        "TY": "MAO",
        "SUU": "TUAT",
    }
    assert YUE_XING_BY_MONTH_BRANCH == expected
    for month_branch, day_branch in expected.items():
        assert yue_xing_branch(month_branch) == day_branch
        assert "月刑" in active_month_tokens(month_branch, day_branch)


def test_v30a_self_punishment_months_do_not_overwrite_month_build():
    # 辰/午/酉/亥: 月刑 trùng chính Chi tháng; cả 月建 và 月刑 phải cùng tồn tại.
    for branch in ("THIN", "NGO", "DAU", "HOI"):
        tokens = active_month_tokens(branch, branch)
        assert "月建" in tokens
        assert "月刑" in tokens


def test_calculator_scope_is_explicit_and_no_score():
    s = calculator_status()
    assert set(s["active_tokens"]) == {"月建", "月破", "三合", "六合", "月害", "月刑"}
    assert s["extension_version"] == "V3_0A_YUE_XING"
    assert s["numeric_score"] is None
    assert s["numeric_score_status"] == "LOCKED_OFF"


def test_invalid_branch_fails_closed():
    try:
        active_month_tokens("INVALID", "TY")
    except ValueError as exc:
        assert "CHI_KHONG_HOP_LE" in str(exc)
    else:
        raise AssertionError("invalid branch must not be silently accepted")
