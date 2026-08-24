from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v24_hour_endpoint_is_registered_without_replacing_v1():
    text = (ROOT / "cong/api_v2.py").read_text(encoding="utf-8")
    assert '@router.post("/gio-ca-nhan")' in text
    assert "hour_reference_result" in text
    assert "register_v2" in text


def test_v24_does_not_reintroduce_numeric_scoring():
    text = (ROOT / "loi/ket_qua/gio_v24.py").read_text(encoding="utf-8")
    assert '"numeric_score": None' in text
    assert '"numeric_score_status": "LOCKED_OFF"' in text
