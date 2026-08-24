from pathlib import Path

from loi.ket_qua.v2 import relationship_result, schema_status
from loi.linh_vuc.quan_he import RELATIONSHIP_POLICY_RULE, danh_gia_quan_he

ROOT = Path(__file__).resolve().parents[2]


def raw(theme_group="PEER", state="SUPPORT", natal_status="READY", impacts=None):
    return {"chuyen_sau": {"ngay": {"danh_gia": {"state": state, "theme": {"theme_group": theme_group, "theme": "Phối hợp và người ngang vai", "ten_god": "BI_KIEN", "ten_god_vi": "Tỷ Kiên", "rule_id": "TT-PEER", "source_id": "SRC-TT", "verification_status": "VERIFIED"}, "natal_pattern": {"status": natal_status, "pattern": "ZHENG_GUAN"}, "branch_impacts": impacts or [], "rule_ids": ["BT-DY-0401"], "source_ids": ["SRC-ZPZQ"]}}}}


def test_relationship_support_requires_peer_theme_and_ready_personal_layer():
    d = danh_gia_quan_he(raw(), scope="day")
    assert d["state"] == "SUPPORT"
    assert d["domain"] == "relationship"
    assert RELATIONSHIP_POLICY_RULE in d["rule_ids"]
    assert d["technical"]["relationship_scope"] == "SOCIAL_COLLABORATION_ONLY"


def test_non_peer_theme_must_not_be_relabelled_as_relationship():
    for group in ("WEALTH", "AUTHORITY", "RESOURCE", "OUTPUT"):
        d = danh_gia_quan_he(raw(theme_group=group), scope="day")
        assert d["state"] == "INSUFFICIENT"
        assert d["confidence_state"] == "Chưa đủ căn cứ"


def test_descriptive_or_unready_pattern_must_not_create_relationship_advice():
    assert danh_gia_quan_he(raw(state="DESCRIPTIVE_ONLY"), scope="day")["state"] == "INSUFFICIENT"
    assert danh_gia_quan_he(raw(natal_status="AMBIGUOUS"), scope="day")["state"] == "INSUFFICIENT"


def test_branch_relation_is_evidence_only_not_romance_prediction():
    d = danh_gia_quan_he(raw(impacts=[{"level": "CAUTION", "type": "XUNG"}]), scope="day")
    assert d["state"] == "SUPPORT"
    text = (d["plain_explanation"] + " " + " ".join(d["cautions"])).lower()
    assert "hôn nhân" in text
    assert any(x["type"] == "BRANCH_RELATIONS" for x in d["evidence"])


def test_relationship_caution_is_not_conflict_or_breakup_prediction():
    d = danh_gia_quan_he(raw(state="CAUTION"), scope="day")
    assert d["state"] == "CAUTION"
    text = (d["plain_explanation"] + " " + " ".join(d["cautions"])).lower()
    assert "không có nghĩa chắc chắn xảy ra mâu thuẫn" in text
    assert "chia tay" in text


def test_relationship_result_has_no_numeric_score():
    out = relationship_result(danh_gia_quan_he(raw(), scope="day"))
    assert out["domain"] == "relationship"
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"
    assert out["personal_context"]["relationship_ruleset_version"] == "V2.3-RELATIONSHIP.1"


def test_schema_status_opens_relationship_and_leaves_hour_pending():
    s = schema_status()
    assert s["schema_version"] == "2.3-alpha.1"
    assert s["status"] == "V2_3_RELATIONSHIP_ALPHA"
    assert "relationship_domain_day" in s["implemented_scopes"]
    assert "relationship_domain_month" in s["implemented_scopes"]
    assert s["pending_scopes"] == ["personal_hour"]


def test_relationship_ui_mirrors_and_only_calls_v2_route():
    a = (ROOT / "public/static/ui-relationship-v23.js").read_text(encoding="utf-8")
    b = (ROOT / "giao_dien/ui-relationship-v23.js").read_text(encoding="utf-8")
    assert a == b
    assert "/api/v2/quan-he" in a
    assert "/api/stateless/" not in a
