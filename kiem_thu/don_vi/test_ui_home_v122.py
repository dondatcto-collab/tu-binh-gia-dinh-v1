from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_v123_exposes_concrete_evidence_without_recomputing_engine():
    ui = read("public/static/ui-home-v122.js")
    assert "TU_BINH_HOME_UI_VERSION='3.2.3-content-first'" in ui
    assert "TEN_GOD_THEME" in ui
    assert "ten_god_vi" in ui
    assert "theme_group" in ui
    assert "branch_impacts" in ui
    assert "Đang nổi bật:" in ui
    assert "không thuộc nhóm Tài" in ui
    assert "không thuộc nhóm phối hợp/người ngang vai" in ui
    assert "numeric_score" not in ui


def test_home_v123_uses_canonical_v2_payloads_and_keeps_detail_modules():
    ui = read("public/static/ui-home-v122.js")
    for endpoint in ("/api/v2/hom-nay", "/api/v2/thang-nay", "/api/v2/cong-viec", "/api/v2/tai-chinh", "/api/v2/quan-he"):
        assert endpoint in ui
    assert "openWorkDomain('day')" in ui
    assert "openFinanceDomain('day')" in ui
    assert "openRelationshipDomain('day')" in ui
    assert "#home-work-summary-v21,#home-finance-summary-v22,#home-relationship-summary-v23{display:none!important}" in ui
    assert "Cùng một tín hiệu, mỗi lĩnh vực được dùng khác nhau" in ui


def test_home_v123_runtime_source_mirror_and_pwa_cache():
    assert read("public/static/ui-home-v122.js") == read("giao_dien/ui-home-v122.js")
    sw = read("public/service-worker.js")
    assert sw == read("giao_dien/service-worker.js")
    assert "tubinh-ui-v3.2.3-content-first" in sw
    assert "/static/ui-home-v122.js?v=3.2.3" in sw
    bootstrap = read("public/static/ui-bootstrap-v26.js")
    assert bootstrap == read("giao_dien/ui-bootstrap-v26.js")
    assert "/static/ui-home-v122.js?v=3.2.3" in bootstrap
    assert bootstrap.index("ui-event-search-v27.js") < bootstrap.index("ui-home-v122.js")
