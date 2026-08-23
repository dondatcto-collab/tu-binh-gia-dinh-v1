from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def test_calendar_va_tim_ngay_dung_lop_ca_nhan_v11():
    api = (ROOT / 'cong' / 'api.py').read_text(encoding='utf-8')
    assert api.count('phan_tich_ca_nhan(') >= 2
    assert api.count('bo_sung_event_ca_nhan(') >= 2
    assert 'ORDINAL_V1_1_PERSONAL' in api


def test_hop_luu_co_day_du_dai_van_nam_thang_ngay():
    src = (ROOT / 'loi' / 'hop_luu' / 'hop_luu.py').read_text(encoding='utf-8')
    assert 'qd_dai_van = phan_tich_ca_nhan' in src
    assert 'qd_nam = phan_tich_ca_nhan' in src
    assert 'qd_thang = phan_tich_ca_nhan' in src
    assert 'qd_ngay = phan_tich_ca_nhan' in src


def test_quyet_dinh_da_khoa_ton_tai():
    p = ROOT / 'tai_lieu' / 'QUYET-DINH-DA-KHOA-0.3.0.md'
    text = p.read_text(encoding='utf-8')
    assert 'Giao diện — LOCKED' in text
    assert 'Không bịa điểm 0–10' in text
    assert 'Personal Bazi Decision Engine V1.1 — ACTIVE' in text
