from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_relationship_ui_mirrors_are_identical():
    assert read("public/static/ui-relationship-v23.js") == read("giao_dien/ui-relationship-v23.js")


def test_relationship_ui_reads_only_canonical_v2_endpoint():
    text = read("public/static/ui-relationship-v23.js")
    assert "/api/v2/quan-he" in text
    assert "/api/stateless/" not in text
    assert "openRelationshipDomain" in text
    assert "Vì sao app kết luận về quan hệ?" in text
    assert "hôn nhân" in text


def test_relationship_ui_is_owned_by_v26_bootstrap():
    finance = read("public/static/ui-finance-v22.js")
    bootstrap = read("public/static/ui-bootstrap-v26.js")
    assert "ui-relationship-v23.js" not in finance
    assert "/static/ui-relationship-v23.js" in bootstrap
    assert bootstrap.index("ui-finance-v22.js") < bootstrap.index("ui-relationship-v23.js")


def test_relationship_api_route_is_present_and_uses_domain_adapter():
    text = read("cong/api_v2.py")
    assert '@router.post("/quan-he")' in text
    assert "danh_gia_quan_he" in text
    assert "relationship_result" in text
