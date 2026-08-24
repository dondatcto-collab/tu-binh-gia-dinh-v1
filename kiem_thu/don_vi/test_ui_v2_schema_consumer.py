from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ui_reads_all_core_v2_endpoints_directly():
    text = read("public/static/ui-language-051.js")
    for endpoint in ("/api/v2/hom-nay", "/api/v2/thang-nay", "/api/v2/dai-van", "/api/v2/tim-ngay"):
        assert endpoint in text


def test_v2_ui_reads_canonical_result_fields():
    text = read("public/static/ui-language-051.js")
    for field in ("conclusion", "plain_explanation", "recommended_actions", "cautions", "confidence_state", "schema_version", "event_context", "technical"):
        assert field in text


def test_v2_ui_does_not_loop_back_to_v1_core_routes():
    text = read("public/static/ui-language-051.js")
    for route in ("/api/stateless/hom-nay", "/api/stateless/thang-nay", "/api/stateless/toi-dang-o-dau", "/api/stateless/tim-ngay"):
        assert route not in text


def test_v2_ui_keeps_technical_content_progressively_disclosed():
    text = read("public/static/ui-language-051.js")
    assert "Xem phương pháp Tử Bình & dữ liệu kỹ thuật" in text
    assert "Xem nguồn & quy tắc" in text
    assert "Phạm vi kết luận" in text
    assert "Schema ${esc(r?.schema_version||V2_SCHEMA)}" in text


def test_decade_ui_is_context_not_domain_prediction():
    text = read("public/static/ui-language-051.js")
    assert "Đại vận là bối cảnh dài hạn, không phải phán quyết cho cả 10 năm" in text
    assert "GIAI ĐOẠN 10 NĂM HIỆN TẠI" in text


def test_v2_ui_mirrors_are_identical():
    assert read("public/static/ui-language-051.js") == read("giao_dien/ui-language-051.js")
