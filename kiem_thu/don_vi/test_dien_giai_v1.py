from loi.quyet_dinh.v1 import danh_gia_giai_doan


def test_luc_xung_van_chi_la_evidence_o_lop_quan_he_don():
    r=danh_gia_giai_doan("DAN","THAN","day")
    assert r["state"]=="DESCRIPTIVE_ONLY"
    assert r["relation"]["muc"]=="STRUCTURAL_ONLY"
    assert r["dien_giai"]["interpretation_status"]=="ZPZQ_DESCRIPTIVE_ONLY_0_5"


def test_khong_quan_he_truc_tiep_khong_bia_cat_hung():
    r=danh_gia_giai_doan("DAN","MAO","day")
    assert r["recommended"]==[] and r["caution"]==[]
