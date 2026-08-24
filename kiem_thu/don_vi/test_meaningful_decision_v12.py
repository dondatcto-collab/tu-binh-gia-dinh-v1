from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tt(day_can="MAU", day_branch="DAN"):
    return {
        "nam": TruVi("MAU", "THIN"),
        "thang": TruVi("QUY", "HOI"),
        "ngay": TruVi(day_can, day_branch),
        "gio": TruVi("BINH", "THIN"),
    }


def test_moi_ket_luan_co_3_yeu_to_va_hanh_dong_cu_the(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[{"label":"Năm","tru":"Bính Ngọ","ten_god_vi":"Thiên Ấn"}])
    d=r["dien_giai"]
    assert d["interpretation_status"] == "PRODUCT_INTERPRETATION_V1_2"
    assert len(d["yeu_to_chinh"]) == 3
    assert len(d["nen_cu_the"]) >= 2
    assert len(d["tranh_cu_the"]) >= 1
    assert d["cong_viec"] != d["tai_chinh"] != d["quan_he"]


def test_10_nhat_chu_khong_duoc_cung_mot_thap_than_cho_binh(db_da_nap):
    day_masters=["GIAP","AT","BINH","DINH","MAU","KY","CANH","TAN","NHAM","QUY"]
    gods=[]
    works=[]
    for dm in day_masters:
        r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(dm),nhat_chu=dm,can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
        gods.append(r["theme"]["ten_god_vi"])
        works.append(r["dien_giai"]["cong_viec"])
    assert len(set(gods)) >= 5
    assert len(set(works)) >= 5


def test_cung_nguoi_hai_can_ngay_khac_phai_cho_hanh_dong_khac(db_da_nap):
    a=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="NGO",scope="day",context=[])
    b=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="CANH",chi_hien_tai="THAN",scope="day",context=[])
    assert a["theme"]["theme_group"] != b["theme"]["theme_group"]
    assert a["dien_giai"]["nen_cu_the"] != b["dien_giai"]["nen_cu_the"]


def test_tai_chinh_luon_hien_ke_ca_khi_khong_co_tin_hieu_tai_loc(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tt(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
    assert r["dien_giai"]["tai_chinh"]
    assert "tài lộc" in r["dien_giai"]["tai_chinh"].lower() or "tài chính" in r["dien_giai"]["tai_chinh"].lower()
