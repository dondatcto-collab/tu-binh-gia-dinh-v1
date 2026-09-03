from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_v123_is_action_first_and_uses_domain_payloads():
    ui = read("public/static/ui-home-v123.js")
    assert "TU_BINH_HOME_ACTION_UI_VERSION='3.2.3-action-first'" in ui
    assert "HÔM NAY NÊN LÀM GÌ?" in ui
    assert "recommended_actions" in ui
    assert "cautions" in ui
    assert "Nên:" in ui
    assert "Cần lưu ý:" in ui
    assert "Chưa có khuyến nghị riêng cho hôm nay." in ui
    assert "Tìm ngày cho một việc" in ui
    assert "numeric_score" not in ui


def test_home_v123_reads_only_existing_canonical_domain_endpoints():
    ui = read("public/static/ui-home-v123.js")
    for endpoint in ("/api/v2/cong-viec", "/api/v2/tai-chinh", "/api/v2/quan-he"):
        assert endpoint in ui
    assert "/api/v2/tim-ngay" not in ui


def test_home_v123_is_loaded_after_v122_and_is_precached():
    bootstrap = read("public/static/ui-bootstrap-v26.js")
    assert bootstrap.index("ui-home-v122.js") < bootstrap.index("ui-home-v123.js")
    sw = read("public/service-worker.js")
    assert "tubinh-ui-v3.2.3-action-first" in sw
    assert "/static/ui-home-v123.js?v=3.2.3" in sw
    assert read("public/static/ui-home-v123.js") == read("giao_dien/ui-home-v123.js")
