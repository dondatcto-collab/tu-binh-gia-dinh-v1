from loi.ket_qua.gio_v29 import HOUR_FUSION_POLICY_VERSION, hour_fusion_gate


def hour_ref():
    return {
        "schema_version": "2.4-alpha.1",
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
        "conclusion": {
            "state": "HARD_BLOCK" if blocked else "FAVORABLE",
            "label": "Bị chặn" if blocked else "Ưu tiên",
        },
        "event_context": {"hard_block": blocked},
        "confidence_state": confidence,
        "rules": ["RULE-EVENT"],
        "sources": ["SRC-EVENT"],
    }


def test_hard_block_day_makes_every_hour_ineligible_without_good_bad_labels():
    out = hour_fusion_gate(hour_ref(), event_code="KY_HOP_DONG", event_day=event_day(blocked=True))
    assert out["hour_fusion_policy_version"] == HOUR_FUSION_POLICY_VERSION == "2.9-alpha.1"
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
