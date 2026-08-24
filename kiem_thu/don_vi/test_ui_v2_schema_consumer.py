from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ui_reads_v2_period_and_event_endpoints_directly():
    text = read("public/static/ui-language-051.js")
    for endpoint in ("/api/v2/hom-nay", "/api/v2/thang-nay", "/api/v2/tim-ngay"):
        assert endpoint in text


def test_v2_ui_reads_canonical_result_fields():
    text = read("public/static/ui-language-051.js")
    for field in (
        "conclusion",
        "plain_explanation",
        "recommended_actions",
        "cautions",
        "confidence_state",
        "schema_version",
        "event_context",
        "technical",
    ):
        assert field in text


def test_v2_ui_does_not_call_v1_period_or_event_search_routes():
    text = read("public/static/ui-language-051.js")
    assert "/api/stateless/hom-nay" not in text
    assert "/api/stateless/thang-nay" not in text
    assert "/api/stateless/tim-ngay" not in text


def test_v2_ui_keeps_technical_content_progressively_disclosed():
    text = read("public/static/ui-language-051.js")
    assert "Xem phương pháp Tử Bình & dữ liệu kỹ thuật" in text
    assert "Xem nguồn & quy tắc" in text
    assert "Phạm vi kết luận" in text
    assert "Schema ${esc(r?.schema_version||V2_SCHEMA)}" in text


def test_v2_ui_mirrors_are_identical():
    assert read("public/static/ui-language-051.js") == read("giao_dien/ui-language-051.js")
