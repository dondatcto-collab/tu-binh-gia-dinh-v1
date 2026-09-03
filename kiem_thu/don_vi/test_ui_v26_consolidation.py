from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"
SOURCE_UI = ROOT / "giao_dien"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v26_index_still_uses_one_controlled_bootstrap():
    index = read(PUBLIC / "index.html")
    assert index.count("/static/ui-bootstrap-v26.js") == 1
    for path in ("ui-work-v21.js", "ui-finance-v22.js", "ui-relationship-v23.js", "ui-hour-v24.js", "ui-event-search-v27.js", "ui-home-v122.js", "ui-home-v123.js"):
        assert f"/static/{path}" not in index


def test_single_bootstrap_owns_all_current_modules_once_and_home_action_loads_last():
    bootstrap = read(PUBLIC / "static" / "ui-bootstrap-v26.js")
    paths = (
        "/static/ui-work-v21.js",
        "/static/ui-finance-v22.js",
        "/static/ui-relationship-v23.js",
        "/static/ui-hour-v24.js",
        "/static/ui-event-search-v27.js",
        "/static/ui-home-v122.js",
        "/static/ui-home-v123.js",
    )
    for path in paths:
        assert bootstrap.count(path) == 1
    assert bootstrap.index("ui-event-search-v27.js") < bootstrap.index("ui-home-v122.js") < bootstrap.index("ui-home-v123.js")
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
    for marker in ("Tử Bình Gia Đình - V1", "12 nhóm V1", "lớp V1", "giới hạn V1", "V1 chưa", "V1 không"):
        assert marker not in index


def test_domain_cards_hide_internal_component_versions():
    files = [PUBLIC / "static" / "ui-work-v21.js", PUBLIC / "static" / "ui-finance-v22.js", PUBLIC / "static" / "ui-relationship-v23.js", PUBLIC / "static" / "ui-hour-v24.js"]
    text = "\n".join(read(p) for p in files)
    for visible_marker in ("· V2.1", "· V2.2", "· V2.3", "· V2.4"):
        assert visible_marker not in text


def test_pwa_cache_keeps_single_bootstrap_and_current_cache():
    sw = read(PUBLIC / "service-worker.js")
    assert "tubinh-ui-v3.2.3-action-first" in sw
    assert "/static/ui-bootstrap-v26.js" in sw
    assert "/static/ui-home-v122.js?v=3.2.2" in sw
    assert "/static/ui-home-v123.js?v=3.2.3" in sw


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
        (PUBLIC / "static" / "ui-home-v122.js", SOURCE_UI / "ui-home-v122.js"),
        (PUBLIC / "static" / "ui-home-v123.js", SOURCE_UI / "ui-home-v123.js"),
    ]
    for runtime, source in pairs:
        assert read(runtime) == read(source), f"UI mirror lệch: {runtime.name}"
