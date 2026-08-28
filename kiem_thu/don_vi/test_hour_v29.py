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
                "chi": "Tý",
                "relation": "LUC_HOP",
                "decision_state": "DESCRIPTIVE_ONLY",
                "is_personal_good_hour": None,
                "is_personal_bad_hour": None,
            },
            {
                "chi": "Ngọ",
                "relation": "XUNG",
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


def test_hard_block_day_makes_every_hour_ineligible_without_good_bad_labels():
    out = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=True))
    assert out["hour_fusion_policy_version"] == HOUR_FUSION_POLICY_VERSION == "2.9-alpha.1"
    assert out["kind"] == "personal_hour_fusion"
    assert out["conclusion"]["state"] == "BLOCKED_BY_DAY"
    assert out["hour_fusion_ready"] is True
    assert out["personal_hour_decision_ready"] is False
    assert all(x["decision_state"] == "INELIGIBLE_BY_DAY" for x in out["hours"])
    assert all(x["is_personal_good_hour"] is None for x in out["hours"])
    assert all(x["is_personal_bad_hour"] is None for x in out["hours"])
    assert out["numeric_score"] is None


def test_favorable_day_does_not_auto_create_good_hour_from_branch_relation():
    out = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=False))
    assert out["conclusion"]["state"] == "DESCRIPTIVE_ONLY"
    assert out["hour_fusion_ready"] is True
    assert out["personal_hour_decision_ready"] is False
    assert {x["relation"] for x in out["hours"]} == {"LUC_HOP", "XUNG"}
    assert all(x["decision_state"] == "DESCRIPTIVE_ONLY" for x in out["hours"])
    assert all(x["is_personal_good_hour"] is None for x in out["hours"])
    assert all(x["is_personal_bad_hour"] is None for x in out["hours"])


def test_missing_event_context_keeps_hour_layer_descriptive_only():
    out = hour_fusion_gate(hour_ref())
    assert out["event_day_context_present"] is False
    assert out["hour_fusion_ready"] is False
    assert out["personal_hour_decision_ready"] is False
    assert out["confidence_state"] == "Chưa đủ căn cứ"
    assert out["conclusion"]["label"] == "Thiếu bối cảnh việc"


def test_hour_relation_can_never_rescue_hard_block_day():
    ref = hour_ref()
    ref["hours"][0]["relation"] = "TAM_HOP"
    out = hour_fusion_gate(ref, event_code="CUOI_HOI", event_day=event_day(blocked=True))
    assert out["hours"][0]["decision_state"] == "INELIGIBLE_BY_DAY"
    assert out["hours"][0]["is_personal_good_hour"] is None
    assert "Không xét giờ để cứu ngày" in out["conclusion"]["title"]


def test_v29_schema_publishes_gate_ready_but_verified_hour_decision_pending():
    out = v29_schema_overlay({"implemented_scopes": [], "pending_scopes": [], "principles": []})
    cap = out["hour_fusion_v29"]
    assert cap["policy_version"] == "2.9-alpha.1"
    assert cap["event_day_gate_ready"] is True
    assert cap["verified_hour_rule_decision_ready"] is False
    assert cap["hard_block_can_be_rescued_by_hour"] is False
    assert cap["numeric_score"] is None
    assert "personal_hour_event_day_gate" in out["implemented_scopes"]
    assert "personal_hour_verified_rule_decision" in out["pending_scopes"]


def test_v28_confidence_preserves_event_evidence_when_hour_is_blocked_by_day():
    fused = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=True, confidence="Căn cứ rõ"))
    out = apply_confidence_v28(fused, time_certainty="UNKNOWN")
    assert out["confidence_state"] == "Căn cứ rõ"
    assert "Evidence ngày đã truy nguồn." in out["confidence_basis"]
    assert out["conclusion"]["state"] == "BLOCKED_BY_DAY"


def test_v29_ui_selects_exact_v1_events_and_never_calls_stateless_or_numeric_score():
    pub = (ROOT / "public/static/ui-hour-v24.js").read_text(encoding="utf-8")
    mirror = (ROOT / "giao_dien/ui-hour-v24.js").read_text(encoding="utf-8")
    assert pub == mirror
    assert "TU_BINH_HOUR_UI_VERSION='2.9A'" in pub
    assert pub.count("['") >= 13  # placeholder + exact 12 event entries
    for code in [
        "AN_TANG", "CAU_TAI", "CUOI_HOI", "DAM_PHAN", "DIEU_TRI", "DONG_THO",
        "KHAI_TRUONG", "KY_HOP_DONG", "MUA_TAI_SAN", "NHAM_CHUC", "NHAP_TRACH", "XUAT_HANH",
    ]:
        assert code in pub
    assert "/api/v2/gio-ca-nhan" in pub
    assert "/api/stateless/" not in pub
    assert "numeric_score" not in pub
    assert "Giờ không được cứu một ngày HARD_BLOCK" in pub
    assert "rule giờ có nguồn và trạng thái VERIFIED" in pub


def test_v29_api_contract_requires_event_search_before_hour_gate_when_event_selected():
    text = (ROOT / "cong/api_v2.py").read_text(encoding="utf-8")
    assert "class HourDecisionRequest" in text
    assert "viec: str | None = None" in text
    assert text.index("event_raw = tim_ngay_v25(event_req)") < text.index("fused = hour_fusion_gate")
    assert "v29_schema_overlay" in text
