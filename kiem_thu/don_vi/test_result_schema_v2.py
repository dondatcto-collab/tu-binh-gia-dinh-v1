from loi.ket_qua.v2 import (
    NUMERIC_SCORE_STATUS,
    SCHEMA_VERSION,
    decade_result,
    event_item,
    event_search,
    personal_result,
    schema_status,
)


def test_schema_status_locks_core_flow_principles():
    s = schema_status()
    assert s["schema_version"] == SCHEMA_VERSION == "2.0-alpha.2"
    assert s["numeric_score"] == NUMERIC_SCORE_STATUS == "LOCKED_OFF"
    assert s["status"] == "ALPHA_CORE_FLOWS"
    for scope in ("day", "month", "decade", "event_search"):
        assert scope in s["implemented_scopes"]
    assert "finance_domain" in s["pending_scopes"]
    assert "UI không tự suy quyết định từ dữ liệu kỹ thuật" in s["principles"]


def test_personal_day_plain_language_does_not_fake_domains():
    raw = {"don_gian": {"tom_tat": "Thuận nền mệnh"}, "chuyen_sau": {"foo": "bar"}}
    out = personal_result(raw, scope="day")
    assert out["conclusion"]["label"] == "Khá thuận"
    assert "Hôm nay" in out["conclusion"]["title"]
    assert "tiền bạc" in out["plain_explanation"].lower()
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"
    assert out["confidence_state"] == "Căn cứ vừa"
    assert out["technical"] == {"foo": "bar"}


def test_personal_caution_is_not_rendered_as_bad_absolute_day():
    out = personal_result({"don_gian": {"tom_tat": "Cần thận trọng"}}, scope="day")
    assert out["conclusion"]["label"] == "Nên thận trọng"
    assert "quyết định quan trọng" in out["conclusion"]["title"]
    assert "Việc thường ngày" in out["plain_explanation"]


def test_decade_is_descriptive_context_not_fake_domain_prediction():
    raw = {"dai_van": {"tru": "Canh Tý", "nam_thu_may": 5, "nam_bat_dau": 2022, "nam_ket_thuc": 2031}}
    out = decade_result(raw)
    assert out["scope"] == "decade"
    assert out["conclusion"]["state"] == "DESCRIPTIVE_ONLY"
    assert "giai đoạn giữa" in out["conclusion"]["title"].lower()
    assert "tiền bạc" in out["plain_explanation"].lower()
    assert out["numeric_score"] is None
    assert out["personal_context"]["decade_pillar"] == "Canh Tý"


def test_hard_block_always_wins_in_v2_event_item():
    item = {"ngay": "2026-09-12", "label": "Ưu tiên", "decision_state": "PRIORITY", "hard_block": True, "rank_group": 1, "event_state": "JI", "score": 999}
    out = event_item(item, event_code="KY_HOP_DONG")
    assert out["conclusion"]["label"] == "Bị chặn"
    assert out["event_context"]["hard_block"] is True
    assert out["confidence_state"] == "Căn cứ rõ"
    assert out["numeric_score"] is None


def test_event_search_keeps_ordinal_ranking_and_no_score():
    raw = {"viec": "KY_HOP_DONG", "so_ngay_da_quet": 3, "xep_hang_status": "ORDINAL_V1_1_PERSONAL", "top": [
        {"ngay": "2026-09-01", "label": "Ưu tiên", "decision_state": "PRIORITY", "hard_block": False, "rank_group": 1},
        {"ngay": "2026-09-02", "label": "Có thể cân nhắc", "decision_state": "CONSIDER", "hard_block": False, "rank_group": 2},
    ]}
    out = event_search(raw)
    assert out["ranking_mode"] == "ORDINAL_HARD_BLOCK_EVENT_PERSONAL"
    assert out["numeric_score"] is None
    assert [x["conclusion"]["label"] for x in out["results"]] == ["Ưu tiên", "Có thể cân nhắc"]


def test_required_v2_result_fields_are_stable():
    out = personal_result({"don_gian": {"tom_tat": "Trung tính"}}, scope="month")
    required = {"schema_version", "kind", "scope", "domain", "conclusion", "plain_explanation", "recommended_actions", "cautions", "confidence_state", "event_context", "personal_context", "evidence", "rules", "sources", "technical", "numeric_score", "numeric_score_status"}
    assert required.issubset(out)
