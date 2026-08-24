from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def test_seed_rule_db_ton_tai_va_khong_bi_gitignore_chan():
    seed = ROOT / 'du_lieu' / 'kho' / 'xemngay-rules-seed.sqlite3'
    assert seed.exists() and seed.stat().st_size > 100_000
    gi = (ROOT / '.gitignore').read_text(encoding='utf-8')
    assert '!du_lieu/kho/xemngay-rules-seed.sqlite3' in gi


def test_api_co_fallback_neu_seed_thieu():
    api = (ROOT / 'cong' / 'api.py').read_text(encoding='utf-8')
    assert 'chay_migration(c)' in api and 'nap_mam(c)' in api


def test_gio_04_chi_duoc_trinh_bay_la_cau_truc():
    api = (ROOT / 'cong' / 'api.py').read_text(encoding='utf-8')
    ui = (ROOT / 'public' / 'static' / 'app.js').read_text(encoding='utf-8')
    assert 'STRUCTURAL_ONLY_PERSONAL_USE_PENDING' in api
    assert 'QUAN HỆ CHI GIỜ VỚI HỒ SƠ' in ui
    assert 'chưa gọi giờ tốt/xấu' in ui
    assert 'GIỜ PHÙ HỢP TRONG NGÀY' not in ui


def test_phien_ban_pwa_dong_bo_040():
    assert 'version = "0.4.0"' in (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    assert '0.4.0' in (ROOT / 'public' / 'service-worker.js').read_text(encoding='utf-8')
    assert "APP_VERSION='0.4.0'" in (ROOT / 'public' / 'static' / 'app.js').read_text(encoding='utf-8')
    assert '0.4.0' in (ROOT / 'public' / 'index.html').read_text(encoding='utf-8')


def test_ui_public_va_source_dong_bo():
    assert (ROOT / 'public' / 'static' / 'app.js').read_bytes() == (ROOT / 'giao_dien' / 'app.js').read_bytes()
    assert (ROOT / 'public' / 'static' / 'app.css').read_bytes() == (ROOT / 'giao_dien' / 'app.css').read_bytes()
