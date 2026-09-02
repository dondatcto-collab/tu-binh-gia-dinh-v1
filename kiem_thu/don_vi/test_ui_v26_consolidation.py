from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"
SOURCE_UI = ROOT / "giao_dien"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v26_index_still_uses_one_controlled_bootstrap():
    index = read(PUBLIC / "index.html")
    assert index.count("/static/ui-bootstrap-v26.js") == 1
    assert "/static/ui-work-v21.js" not in index
    assert "/static/ui-finance-v22.js" not in index
    assert "/static/ui-relationship-v23.js" not in index
    assert "/static/ui-hour-v24.js" not in index
    assert "/static/ui-event-search-v27.js" not in index


def test_single_bootstrap_still_owns_core_modules_once():
    bootstrap = read(PUBLIC / "static" / "ui-bootstrap-v26.js")
    for path in (
        "/static/ui-work-v21.js",
        "/static/ui-finance-v22.js",
        "/static/ui-relationship-v23.js",
        "/static/ui-hour-v24.js",
    ):
        assert bootstrap.count(path) == 1
    assert "TU_BINH_UI_READY" in bootstrap
    assert "TU_BINH_PRODUCT_UI_VERSION" in bootstrap


def test_modules_do_not_load_each_other_anymore():
    finance = read(PUBLIC / "static" / "ui-finance-v22.js")
    relationship = read(PUBLIC / "static" / "ui-relationship-v23.js")
    assert "data-v23-relationship" not in finance
    assert "ui-relationship-v23.js" not in finance
    assert "data-v24-hour" not in relationship
    assert "ui-hour-v24.js" not in relationship


def test_user_facing_index_has_no_legacy_v1_badges():
    index = read(PUBLIC / "index.html")
    assert "Tử Bình Gia Đình - V1" not in index
    assert "12 nhóm V1" not in index
    assert "lớp V1" not in index
    assert "giới hạn V1" not in index
    assert "V1 chưa" not in index
    assert "V1 không" not in index


def test_domain_cards_hide_internal_component_versions():
    files = [
        PUBLIC / "static" / "ui-work-v21.js",
        PUBLIC / "static" / "ui-finance-v22.js",
        PUBLIC / "static" / "ui-relationship-v23.js",
        PUBLIC / "static" / "ui-hour-v24.js",
    ]
    text = "\n".join(read(p) for p in files)
    for visible_marker in ("· V2.1", "· V2.2", "· V2.3", "· V2.4"):
        assert visible_marker not in text


def test_pwa_cache_keeps_single_bootstrap_and_current_cache():
    sw = read(PUBLIC / "service-worker.js")
    assert "tubinh-ui-v3.1-ui-v1-1" in sw
    assert "/static/ui-bootstrap-v26.js" in sw


def test_runtime_and_source_ui_copies_stay_identical():
    pairs = [
        (PUBLIC / "index.html", SOURCE_UI / "index.html"),
        (PUBLIC / "service-worker.js", SOURCE_UI / "service-worker.js"),
        (PUBLIC / "static" / "ui-bootstrap-v26.js", SOURCE_UI / "ui-bootstrap-v26.js"),
        (PUBLIC / "static" / "ui-work-v21.js", SOURCE_UI / "ui-work-v21.js"),
        (PUBLIC / "static" / "ui-finance-v22.js", SOURCE_UI / "ui-finance-v22.js"),
        (PUBLIC / "static" / "ui-relationship-v23.js", SOURCE_UI / "ui-relationship-v23.js"),
        (PUBLIC / "static" / "ui-hour-v24.js", SOURCE_UI / "ui-hour-v24.js"),
        (PUBLIC / "static" / "ui-event-search-v27.js", SOURCE_UI / "ui-event-search-v27.js"),
    ]
    for runtime, source in pairs:
        assert read(runtime) == read(source), f"UI mirror lệch: {runtime.name}"
