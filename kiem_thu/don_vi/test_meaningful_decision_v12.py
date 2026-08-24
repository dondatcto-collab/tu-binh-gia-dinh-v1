"""Hồi quy 0.4: giữ dữ liệu cá nhân hóa, bỏ hiệu lực quyết định sai của 0.3.x."""
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tt(day_can="MAU", day_branch="DAN"):
    return {
        "nam": TruVi("MAU", "THIN"),
        "thang": TruVi("QUY", "HOI"),
        "ngay": TruVi(day_can, day_branch),
        "gio": TruVi("BINH", "THIN"),
    }


def test_ket_luan_04_chi_mo_ta_khong_phat_sinh_hanh_dong(db_da_nap):
    r = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tt(), nhat_chu="MAU",
        can_hien_tai="BINH", chi_hien_tai="THAN", scope="month",
        context=[{"label":"Năm","tru":"Bính Ngọ","ten_god_vi":"Thiên Ấn"}],
    )
    d = r["dien_giai"]
    assert r["state"] == "DESCRIPTIVE_ONLY"
    assert d["interpretation_status"] == "ZPZQ_DESCRIPTIVE_ONLY_0_4"
    assert d["nen_cu_the"] == []
    assert d["tranh_cu_the"] == []
    assert r["recommended"] == [] and r["caution"] == []


def test_10_nhat_chu_van_tinh_dung_thap_than_nhung_khong_bien_thanh_cat_hung(db_da_nap):
    day_masters=["GIAP","AT","BINH","DINH","MAU","KY","CANH","TAN","NHAM","QUY"]
    gods=[]
    for dm in day_masters:
        r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(dm),nhat_chu=dm,can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
        gods.append(r["theme"]["ten_god_vi"])
        assert r["state"] == "DESCRIPTIVE_ONLY"
        assert not r["dien_giai"]["nen_cu_the"]
    assert len(set(gods)) >= 5


def test_tai_chinh_hien_trung_thuc_khong_goi_tai_loc(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
    text=r["dien_giai"]["tai_chinh"].lower()
    assert "chưa" in text
    assert "thuận tài" not in text and "tài lộc tốt" not in text
