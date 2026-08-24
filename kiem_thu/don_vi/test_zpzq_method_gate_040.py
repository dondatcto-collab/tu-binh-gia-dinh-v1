from loi.bat_tu.phuong_phap_tu_binh import trang_thai_hien_tai, cho_phep_ket_luan_ca_nhan


def test_cong_phuong_phap_050_mo_sau_sua_selector():
    s=trang_thai_hien_tai()
    assert s.pattern_engine_ready is True
    assert s.use_favor_avoid_ready is True
    assert s.transit_fusion_ready is True
    assert s.personal_decision_ready is True
    assert s.decision_mode=="ZPZQ_PERSONAL"
    assert cho_phep_ket_luan_ca_nhan() is True
