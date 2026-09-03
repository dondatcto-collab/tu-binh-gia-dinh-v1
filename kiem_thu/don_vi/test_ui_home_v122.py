from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_v122_consolidates_three_domains_without_recomputing_engine():
    ui = read("public/static/ui-home-v122.js")
    assert "TU_BINH_HOME_UI_VERSION='3.2.2-home-decision'" in ui
    assert "home-work-summary-v21" in ui
    assert "home-finance-summary-v22" in ui
    assert "home-relationship-summary-v23" in ui
    assert "HÔM NAY THEO TỪNG LĨNH VỰC" in ui
    assert "openWorkDomain('day')" in ui
    assert "openFinanceDomain('day')" in ui
    assert "openRelationshipDomain('day')" in ui
    assert "/api/" not in ui
    assert "numeric_score" not in ui


def test_home_v122_hides_verbose_home_domain_cards_but_keeps_detail_modules():
    ui = read("public/static/ui-home-v122.js")
    assert "#home-work-summary-v21,#home-finance-summary-v22,#home-relationship-summary-v23{display:none!important}" in ui
    assert "Trang chủ chỉ tóm tắt" in ui
    bootstrap = read("public/static/ui-bootstrap-v26.js")
    assert bootstrap.index("ui-event-search-v27.js") < bootstrap.index("ui-home-v122.js") < bootstrap.index("ui-home-v123.js")


def test_home_v122_runtime_source_mirror_and_current_pwa_cache():
    assert read("public/static/ui-home-v122.js") == read("giao_dien/ui-home-v122.js")
    sw = read("public/service-worker.js")
    assert "tubinh-ui-v3.2.3-action-first" in sw
    assert "/static/ui-home-v122.js?v=3.2.2" in sw
    assert "/static/ui-home-v123.js?v=3.2.3" in sw
