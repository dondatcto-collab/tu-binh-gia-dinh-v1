from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_finance_ui_uses_only_v2_finance_endpoint():
    text = read("public/static/ui-finance-v22.js")
    assert "/api/v2/tai-chinh" in text
    assert "/api/stateless/" not in text
    assert "numeric_score" not in text
    assert "có tiền" in text.lower()
    assert "tăng thu nhập" in text.lower()


def test_finance_ui_mirrors_are_identical():
    assert read("public/static/ui-finance-v22.js") == read("giao_dien/ui-finance-v22.js")


def test_bootstrap_loads_finance_after_work_layer():
    pub = read("public/static/ui-bootstrap-v26.js")
    mirror = read("giao_dien/ui-bootstrap-v26.js")
    assert pub == mirror
    assert pub.index("ui-work-v21.js") < pub.index("ui-finance-v22.js")
    assert "/static/ui-finance-v22.js" in pub


def test_v2_api_has_finance_route_without_removing_work():
    text = read("cong/api_v2.py")
    assert '@router.post("/cong-viec")' in text
    assert '@router.post("/tai-chinh")' in text
    assert "danh_gia_tai_chinh" in text
    assert "finance_result" in text
