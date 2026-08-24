from loi.ket_qua.v2 import finance_result, schema_status
from loi.linh_vuc.tai_chinh import FINANCE_POLICY_RULE, danh_gia_tai_chinh


def raw(theme_group="WEALTH", state="SUPPORT", natal_status="READY"):
    return {"chuyen_sau": {"ngay": {"danh_gia": {"state": state, "theme": {"theme_group": theme_group, "theme": "Tài chính, tài sản và quản lý nguồn lực", "ten_god": "CHINH_TAI", "ten_god_vi": "Chính Tài", "rule_id": "TT-001", "source_id": "SRC-TT", "verification_status": "VERIFIED"}, "natal_pattern": {"status": natal_status, "pattern": "ZHENG_GUAN"}, "branch_impacts": [], "rule_ids": ["BT-DY-0401"], "source_ids": ["SRC-ZPZQ"]}}}}


def test_finance_support_requires_wealth_theme_and_ready_personal_layer():
    d = danh_gia_tai_chinh(raw(), scope="day")
    assert d["state"] == "SUPPORT"
    assert d["domain"] == "finance"
    assert "quản lý" in d["title"].lower()
    assert FINANCE_POLICY_RULE in d["rule_ids"]


def test_non_wealth_theme_must_not_be_relabelled_as_finance():
    d = danh_gia_tai_chinh(raw(theme_group="AUTHORITY"), scope="day")
    assert d["state"] == "INSUFFICIENT"


def test_descriptive_or_unready_pattern_must_not_create_finance_advice():
    assert danh_gia_tai_chinh(raw(state="DESCRIPTIVE_ONLY"), scope="day")["state"] == "INSUFFICIENT"
    assert danh_gia_tai_chinh(raw(natal_status="AMBIGUOUS"), scope="day")["state"] == "INSUFFICIENT"


def test_finance_caution_is_not_loss_prediction():
    d = danh_gia_tai_chinh(raw(state="CAUTION"), scope="day")
    assert d["state"] == "CAUTION"
    text = (d["plain_explanation"] + " " + " ".join(d["cautions"])).lower()
    assert "không có nghĩa chắc chắn mất tiền" in text


def test_finance_result_has_no_numeric_score():
    out = finance_result(danh_gia_tai_chinh(raw(), scope="day"))
    assert out["domain"] == "finance"
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"
    assert out["personal_context"]["finance_ruleset_version"] == "V2.2-FINANCE.1"


def test_finance_remains_implemented_when_relationship_opens():
    s = schema_status()
    assert "finance_domain_day" in s["implemented_scopes"]
    assert "finance_domain_month" in s["implemented_scopes"]
