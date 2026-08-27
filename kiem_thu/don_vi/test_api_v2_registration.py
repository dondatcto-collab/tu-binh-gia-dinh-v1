from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_vercel_entrypoint_registers_v2_without_replacing_v1():
    text = read("api/index.py")
    assert "from cong.api import app" in text
    assert "from cong.api_v2 import register_v2" in text
    assert "register_v2(app)" in text


def test_v2_routes_cover_core_user_flows_and_work_domain():
    text = read("cong/api_v2.py")
    for route in ("/schema-status", "/hom-nay", "/thang-nay", "/dai-van", "/cong-viec", "/tim-ngay"):
        assert route in text
    assert "raw = hom_nay(v)" in text
    assert "raw = thang_nay(v)" in text
    assert "raw = toi_dang_o_dau(v)" in text
    assert "raw = tim_ngay_v25(v)" in text
    assert "event_search_v25" in text
    assert "v25_schema_overlay" in text
    assert "danh_gia_cong_viec" in text
    assert "work_result" in text


def test_work_domain_api_only_accepts_day_or_month():
    text = read("cong/api_v2.py")
    assert 'v.scope == "day"' in text
    assert 'v.scope == "month"' in text
    assert "hiện chỉ hỗ trợ scope day hoặc month" in text


def test_v2_adapter_is_not_a_second_general_decision_engine():
    text = read("loi/ket_qua/v2.py")
    assert "không đổi engine" in text.lower()
    assert "NUMERIC_SCORE_STATUS = \"LOCKED_OFF\"" in text
    assert "DESCRIPTIVE_ONLY" in text


def test_v25_pipeline_is_isolated_from_v1_endpoint():
    text = read("cong/tim_ngay_v25.py")
    assert "evaluate_event_v25" in text
    assert "danh_gia_event" in text
    assert "V25_RANKING_MODE" in text
    api_v1 = read("cong/api.py")
    assert "tim_ngay_v25" not in api_v1
