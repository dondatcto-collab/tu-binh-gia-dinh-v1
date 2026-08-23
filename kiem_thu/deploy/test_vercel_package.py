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
