from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tu_tru_user(day_branch="DAN"):
    return {
        "nam": TruVi("MAU", "THIN"),
        "thang": TruVi("QUY", "HOI"),
        "ngay": TruVi("MAU", day_branch),
        "gio": TruVi("BINH", "THIN"),
    }


def test_thang_binh_than_khong_con_chi_nhin_mot_tru(db_da_nap):
    r = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU",
        can_hien_tai="BINH", chi_hien_tai="THAN", scope="month", context=[])
    assert r["theme"]["ten_god_vi"] == "Thiên Ấn"
    rel = {(x["position"], x["relation"]) for x in r["branch_impacts"]}
    assert ("ngay", "LUC_XUNG") in rel       # Dần – Thân
    assert ("thang", "LUC_HAI") in rel       # Hợi – Thân
    assert len(r["branch_impacts"]) >= 2


def test_ngay_ky_ti_co_chu_de_va_nhieu_tuong_tac(db_da_nap):
    r = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU",
        can_hien_tai="KY", chi_hien_tai="TI", scope="day", context=[])
    assert r["theme"]["ten_god_vi"] == "Kiếp Tài"
    rel = {(x["position"], x["relation"]) for x in r["branch_impacts"]}
    assert ("thang", "LUC_XUNG") in rel       # Hợi – Tị
    assert any(pos == "ngay" for pos, _ in rel) # Dần – Tị có quan hệ trực tiếp
    assert "Công việc" not in r["dien_giai"]["cong_viec"]  # nội dung, không heading lặp


def test_cung_ngay_nhung_nguoi_khac_phai_ra_khac(db_da_nap):
    a = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user("DAN"), nhat_chu="MAU",
        can_hien_tai="KY", chi_hien_tai="TI", scope="day", context=[])
    b = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user("MAO"), nhat_chu="MAU",
        can_hien_tai="KY", chi_hien_tai="TI", scope="day", context=[])
    assert a["branch_impacts"] != b["branch_impacts"]
    assert a["dien_giai"]["technical_trigger"] != b["dien_giai"]["technical_trigger"]


def test_bon_linh_vuc_co_noi_dung_rieng(db_da_nap):
    r = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU",
        can_hien_tai="BINH", chi_hien_tai="THAN", scope="month", context=[])
    d = r["dien_giai"]
    vals = [d["cong_viec"], d["tai_chinh"], d["quan_he"], d["viec_lon"]]
    assert all(vals)
    assert len(set(vals)) == 4
    assert d["interpretation_status"] == "PRODUCT_INTERPRETATION_V1_2"


def test_khong_bia_dung_hy_ky_hoac_diem_so(db_da_nap):
    r = phan_tich_ca_nhan(
        db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU",
        can_hien_tai="BINH", chi_hien_tai="THAN", scope="month", context=[])
    text = str(r).lower()
    assert "8.6" not in text and "7.8" not in text
    assert "dụng thần là" not in text
    assert "hỷ thần là" not in text

from loi.quyet_dinh.ca_nhan import bo_sung_event_ca_nhan


def test_event_yi_bi_ha_neu_va_cham_ca_nhan():
    base = {"event_state":"YI","mapping_status":"VERIFIED","rank_group":1,"label":"Phù hợp","reasons":[],"rule_ids":[]}
    personal = {"branch_impacts":[{"level":"CAUTION"}],"theme":{"theme":"Học hỏi"},"rule_ids":["BT-X"],"dien_giai":{},"technical_facts":[]}
    r = bo_sung_event_ca_nhan(base, personal)
    assert r["rank_group"] == 2
    assert "cân nhắc cá nhân" in r["label"].lower()


def test_event_ji_khong_duoc_ca_nhan_cuu():
    base = {"event_state":"JI","mapping_status":"VERIFIED","rank_group":5,"label":"Không ưu tiên","reasons":[],"rule_ids":[]}
    personal = {"branch_impacts":[{"level":"POSITIVE"}],"theme":{"theme":"Tài chính"},"rule_ids":[],"dien_giai":{},"technical_facts":[]}
    r = bo_sung_event_ca_nhan(base, personal)
    assert r["rank_group"] == 5
    assert r["label"] == "Không ưu tiên"
