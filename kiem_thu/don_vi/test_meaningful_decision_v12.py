"""Meaningful decision 0.5.0."""
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tt(day="DAN"):
    return {"nam":TruVi("MAU","THIN"),"thang":TruVi("QUY","HOI"),"ngay":TruVi("MAU",day),"gio":TruVi("BINH","THIN")}


def test_ket_luan_ca_nhan_chi_mo_khi_cach_cuc_ready(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="CANH",chi_hien_tai="THAN",scope="day",context=[])
    if r["natal_pattern"]["status"]=="READY": assert r["state"] in {"SUPPORT","CAUTION","NEUTRAL"}
    else: assert r["state"]=="DESCRIPTIVE_ONLY"


def test_10_nhat_chu_khong_dung_mot_thap_than_lam_cat_hung(db_da_nap):
    for can in ("GIAP","AT","BINH","DINH","MAU","KY","CANH","TAN","NHAM","QUY"):
        r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu=can,can_hien_tai="CANH",chi_hien_tai="THAN",scope="day",context=[])
        assert r["state"] in {"SUPPORT","CAUTION","NEUTRAL","DESCRIPTIVE_ONLY"}
        assert "score" not in r


def test_tai_chinh_khong_goi_tai_loc_chac_chan(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="CANH",chi_hien_tai="THAN",scope="day",context=[])
    text=r["dien_giai"]["tai_chinh"].lower(); assert "tài lộc chắc" not in text and "chắc chắn" not in text
