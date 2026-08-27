from loi.quyet_dinh.hiep_ky_month_v25 import (
    active_month_tokens,
    calculator_status,
    tam_hop_partners,
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
    assert active_month_tokens("DAN", "TI") == ("月害",)


def test_calculator_scope_is_explicit_and_no_score():
    s = calculator_status()
    assert set(s["active_tokens"]) == {"月建", "月破", "三合", "六合", "月害"}
    assert s["numeric_score"] is None
    assert s["numeric_score_status"] == "LOCKED_OFF"


def test_invalid_branch_fails_closed():
    try:
        active_month_tokens("INVALID", "TY")
    except ValueError as exc:
        assert "CHI_KHONG_HOP_LE" in str(exc)
    else:
        raise AssertionError("invalid branch must not be silently accepted")
