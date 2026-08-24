from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_vercel_entrypoint_registers_v2_without_replacing_v1():
    text = read("api/index.py")
    assert "from cong.api import app" in text
    assert "from cong.api_v2 import register_v2" in text
    assert "register_v2(app)" in text


def test_v2_routes_cover_core_user_flows():
    text = read("cong/api_v2.py")
    for route in ("/schema-status", "/hom-nay", "/thang-nay", "/dai-van", "/tim-ngay"):
        assert route in text
    assert "raw = hom_nay(v)" in text
    assert "raw = thang_nay(v)" in text
    assert "raw = toi_dang_o_dau(v)" in text
    assert "raw = tim_ngay(v)" in text


def test_v2_adapter_is_not_a_second_decision_engine():
    text = read("loi/ket_qua/v2.py")
    assert "không đổi engine" in text.lower()
    assert "NUMERIC_SCORE_STATUS = \"LOCKED_OFF\"" in text
    assert "DESCRIPTIVE_ONLY" in text
