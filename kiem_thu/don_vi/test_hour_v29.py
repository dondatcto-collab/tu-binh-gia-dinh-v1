from pathlib import Path

from loi.ket_qua.confidence_v28 import apply_confidence_v28
from loi.ket_qua.gio_v29 import HOUR_FUSION_POLICY_VERSION, hour_fusion_gate, v29_schema_overlay

ROOT = Path(__file__).resolve().parents[2]


def hour_ref():
    return {
        "schema_version": "2.4-alpha.1",
        "kind": "personal_hour_reference",
        "conclusion": {"state": "DESCRIPTIVE_ONLY"},
        "hours": [
            {
                "chi": "TY",
                "chi_vi": "Tý",
                "time_range": "23:00–01:00",
                "relation": "LUC_HOP",
                "relation_label": "Lục hợp",
                "decision_state": "DESCRIPTIVE_ONLY",
                "is_personal_good_hour": None,
                "is_personal_bad_hour": None,
            },
            {
                "chi": "NGO",
                "chi_vi": "Ngọ",
                "time_range": "11:00–13:00",
                "relation": "LUC_XUNG",
                "relation_label": "Lục xung",
                "decision_state": "DESCRIPTIVE_ONLY",
                "is_personal_good_hour": None,
                "is_personal_bad_hour": None,
            },
            {
                "chi": "THIN",
                "chi_vi": "Thìn",
                "time_range": "07:00–09:00",
                "relation": "NONE",
                "relation_label": "Không có quan hệ trực tiếp",
                "decision_state": "DESCRIPTIVE_ONLY",
                "is_personal_good_hour": None,
                "is_personal_bad_hour": None,
            },
        ],
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }


def event_day(*, blocked=False, confidence="Căn cứ rõ"):
    return {
        "date": "2026-08-28",
        "kind": "event_day",
        "conclusion": {
            "state": "HARD_BLOCK" if blocked else "FAVORABLE",
            "label": "Bị chặn" if blocked else "Ưu tiên",
        },
        "event_context": {"hard_block": blocked},
        "confidence_state": confidence,
        "confidence_basis": ["Evidence ngày đã truy nguồn."],
        "rules": ["RULE-EVENT"],
        "sources": ["SRC-EVENT"],
    }


def test_hard_block_day_makes_every_hour_ineligible_and_cannot_be_rescued():
    out = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=True))
    assert out["hour_fusion_policy_version"] == HOUR_FUSION_POLICY_VERSION == "2.9-beta.1"
    assert out["kind"] == "personal_hour_fusion"
    assert out["conclusion"]["state"] == "BLOCKED_BY_DAY"
    assert out["hour_fusion_ready"] is True
    assert out["personal_hour_decision_ready"] is True
    assert all(x["decision_state"] == "INELIGIBLE_BY_DAY" for x in out["hours"])
    assert all(x["is_personal_good_hour"] is False for x in out["hours"])
    assert out["numeric_score"] is None
    assert "Không xét giờ để cứu ngày" in out["conclusion"]["title"]


def test_passed_day_activates_verified_relation_hour_decision_without_numeric_score():
    out = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=False))
    assert out["conclusion"]["state"] == "HOUR_RULE_DECISION_READY"
    assert out["hour_fusion_ready"] is True
    assert out["personal_hour_decision_ready"] is True
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"

    good, caution, neutral = out["hours"]
    assert good["decision_state"] == "PERSONAL_GOOD_CANDIDATE"
    assert good["decision_label"] == "Có thể ưu tiên"
    assert good["is_personal_good_hour"] is True
    assert good["hour_rule_id"] == "BT-REL-0001"
    assert good["hour_source_id"] == "SRC-TMTH-V02-WIKISOURCE"

    assert caution["decision_state"] == "PERSONAL_CAUTION_HOUR"
    assert caution["decision_label"] == "Nên thận trọng"
    assert caution["is_personal_good_hour"] is False
    assert caution["is_personal_bad_hour"] is False  # caution != hung tuyệt đối
    assert caution["hour_rule_id"] == "BT-REL-0002"

    assert neutral["decision_state"] == "PERSONAL_NEUTRAL_HOUR"
    assert neutral["decision_label"] == "Trung tính"
    assert neutral["hour_rule_id"] is None
    assert neutral["hour_source_id"] is None

    assert set(out["rules"]) == {"BT-REL-0001", "BT-REL-0002"}
    assert out["sources"] == ["SRC-TMTH-V02-WIKISOURCE"]


def test_missing_event_context_keeps_hour_layer_descriptive_only():
    out = hour_fusion_gate(hour_ref())
    assert out["event_day_context_present"] is False
    assert out["hour_fusion_ready"] is False
    assert out["personal_hour_decision_ready"] is False
    assert out["confidence_state"] == "Chưa đủ căn cứ"
    assert out["conclusion"]["label"] == "Thiếu bối cảnh việc"


def test_v29b_confidence_is_medium_for_limited_verified_hour_decision():
    fused = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=False))
    out = apply_confidence_v28(fused, time_certainty="KNOWN")
    assert out["confidence_state"] == "Căn cứ vừa"
    assert any("Rule ID" in x and "Source ID" in x for x in out["confidence_basis"])
    assert out["conclusion"]["state"] == "HOUR_RULE_DECISION_READY"


def test_v28_confidence_preserves_event_evidence_when_hour_is_blocked_by_day():
    fused = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=True, confidence="Căn cứ rõ"))
    out = apply_confidence_v28(fused, time_certainty="UNKNOWN")
    assert out["confidence_state"] == "Căn cứ rõ"
    assert "Evidence ngày đã truy nguồn." in out["confidence_basis"]
    assert out["conclusion"]["state"] == "BLOCKED_BY_DAY"


def test_v29_schema_publishes_verified_hour_decision_but_not_full_classical_claim():
    out = v29_schema_overlay({"implemented_scopes": [], "pending_scopes": ["personal_hour_verified_rule_decision"], "principles": []})
    cap = out["hour_fusion_v29"]
    assert cap["policy_version"] == "2.9-beta.1"
    assert cap["event_day_gate_ready"] is True
    assert cap["verified_hour_rule_decision_ready"] is True
    assert cap["full_classical_hour_auspiciousness_ready"] is False
    assert cap["hard_block_can_be_rescued_by_hour"] is False
    assert cap["numeric_score"] is None
    assert "personal_hour_event_day_gate" in out["implemented_scopes"]
    assert "personal_hour_verified_rule_decision" in out["implemented_scopes"]
    assert "personal_hour_verified_rule_decision" not in out["pending_scopes"]
    assert "personal_hour_full_classical_auspiciousness" in out["pending_scopes"]


def test_v29b_ui_exposes_relative_hour_decision_and_keeps_safety_language():
    pub = (ROOT / "public/static/ui-hour-v24.js").read_text(encoding="utf-8")
    mirror = (ROOT / "giao_dien/ui-hour-v24.js").read_text(encoding="utf-8")
    assert pub == mirror
    assert "TU_BINH_HOUR_UI_VERSION='2.9B'" in pub
    for code in [
        "AN_TANG", "CAU_TAI", "CUOI_HOI", "DAM_PHAN", "DIEU_TRI", "DONG_THO",
        "KHAI_TRUONG", "KY_HOP_DONG", "MUA_TAI_SAN", "NHAM_CHUC", "NHAP_TRACH", "XUAT_HANH",
    ]:
        assert code in pub
    assert "/api/v2/gio-ca-nhan" in pub
    assert "/api/stateless/" not in pub
    assert "numeric_score" not in pub
    assert "PERSONAL_GOOD_CANDIDATE" in pub
    assert "PERSONAL_CAUTION_HOUR" in pub
    assert "Giờ không được cứu một ngày HARD_BLOCK" in pub
    assert "không phải cát/hung tuyệt đối" in pub


def test_v29_api_contract_still_requires_event_search_before_hour_fusion():
    text = (ROOT / "cong/api_v2.py").read_text(encoding="utf-8")
    assert "class HourDecisionRequest" in text
    assert "viec: str | None = None" in text
    assert text.index("event_raw = tim_ngay_v25(event_req)") < text.index("fused = hour_fusion_gate")
    assert "v29_schema_overlay" in text
