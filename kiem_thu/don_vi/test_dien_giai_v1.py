"""Quan hệ Chi được phép giải thích cấu trúc, không được biến thành cát/hung."""
from loi.quyet_dinh.v1 import danh_gia_giai_doan


def test_luc_xung_chi_ghi_nhan_cau_truc():
    d = danh_gia_giai_doan('DAN', 'THAN', 'month')
    g = d['dien_giai']
    assert d['state'] == 'DESCRIPTIVE_ONLY'
    assert d['label'] == 'Chỉ ghi nhận cấu trúc'
    assert d['relation']['nhan'] == 'Lục xung'
    assert d['relation']['muc'] == 'STRUCTURAL_ONLY'
    assert d['recommended'] == [] and d['caution'] == []
    assert g['interpretation_status'] == 'ZPZQ_DESCRIPTIVE_ONLY_0_4'
    assert g['evidence_scope'] == 'BRANCH_RELATION_NOT_DECISION'


def test_luc_hop_khong_bi_goi_la_thuan():
    d = danh_gia_giai_doan('DAN', 'HOI', 'day')
    assert d['relation']['nhan'] == 'Lục hợp'
    assert d['state'] == 'DESCRIPTIVE_ONLY'
    assert 'thuận' not in d['label'].lower()
    assert not d['recommended']


def test_khong_co_quan_he_khong_bi_goi_la_trung_tinh_hay_tot():
    d = danh_gia_giai_doan('DAN', 'TY', 'day')
    g = d['dien_giai']
    assert d['state'] == 'DESCRIPTIVE_ONLY'
    assert 'chưa có quan hệ' in g['headline'].lower()
    assert g['focus'] == []
    assert 'không có nghĩa' not in d['label'].lower()  # label chỉ mô tả, không phán
