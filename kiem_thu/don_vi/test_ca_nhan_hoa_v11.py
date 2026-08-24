"""Kiểm tra dữ liệu cấu trúc cá nhân vẫn đúng sau cổng phương pháp 0.4."""
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan, bo_sung_event_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tu_tru_user(day_branch="DAN"):
    return {
        "nam": TruVi("MAU", "THIN"),
        "thang": TruVi("QUY", "HOI"),
        "ngay": TruVi("MAU", day_branch),
        "gio": TruVi("BINH", "THIN"),
    }


def test_thang_binh_than_van_doc_du_bon_tru_nhung_chi_la_cau_truc(db_da_nap):
    r = phan_tich_ca_nhan(db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU", can_hien_tai="BINH", chi_hien_tai="THAN", scope="month", context=[])
    assert r["theme"]["ten_god_vi"] == "Thiên Ấn"
    rel = {(x["position"], x["relation"]) for x in r["branch_impacts"]}
    assert ("ngay", "LUC_XUNG") in rel
    assert ("thang", "LUC_HAI") in rel
    assert all(x["decision_effect"] == "UNDETERMINED" for x in r["branch_impacts"])


def test_cung_ngay_nguoi_khac_van_co_evidence_khac_nhung_khong_ep_cat_hung(db_da_nap):
    a = phan_tich_ca_nhan(db_da_nap, tu_tru=_tu_tru_user("DAN"), nhat_chu="MAU", can_hien_tai="KY", chi_hien_tai="TI", scope="day", context=[])
    b = phan_tich_ca_nhan(db_da_nap, tu_tru=_tu_tru_user("MAO"), nhat_chu="MAU", can_hien_tai="KY", chi_hien_tai="TI", scope="day", context=[])
    assert a["branch_impacts"] != b["branch_impacts"]
    assert a["state"] == b["state"] == "DESCRIPTIVE_ONLY"


def test_khong_bia_dung_hy_ky_hoac_diem_so(db_da_nap):
    r = phan_tich_ca_nhan(db_da_nap, tu_tru=_tu_tru_user(), nhat_chu="MAU", can_hien_tai="BINH", chi_hien_tai="THAN", scope="month", context=[])
    text = str(r).lower()
    assert "8.6" not in text and "7.8" not in text
    assert "dụng thần là" not in text and "hỷ thần là" not in text


def test_event_yi_khong_bi_ha_chi_vi_xung_hop_ca_nhan_khi_hy_ky_chua_san_sang():
    base = {"event_state":"YI","mapping_status":"VERIFIED","rank_group":1,"label":"Phù hợp theo Hiệp Kỷ","reasons":[],"rule_ids":[]}
    personal = {"branch_impacts":[{"level":"CAUTION"}],"theme":{"theme":"Học hỏi","ten_god_vi":"Thiên Ấn"},"rule_ids":["BT-X"],"dien_giai":{},"technical_facts":[],"methodology":{"decision_mode":"DESCRIPTIVE_ONLY"}}
    r = bo_sung_event_ca_nhan(base, personal)
    assert r["rank_group"] == 1
    assert r["label"] == "Phù hợp theo Hiệp Kỷ"
    assert r["personal_rank_adjustment"] == 0


def test_event_ji_khong_duoc_ca_nhan_cuu():
    base = {"event_state":"JI","mapping_status":"VERIFIED","rank_group":5,"label":"Không ưu tiên theo việc","reasons":[],"rule_ids":[]}
    personal = {"branch_impacts":[{"level":"POSITIVE"}],"theme":{"theme":"Tài chính","ten_god_vi":"Chính Tài"},"rule_ids":[],"dien_giai":{},"technical_facts":[],"methodology":{"decision_mode":"DESCRIPTIVE_ONLY"}}
    r = bo_sung_event_ca_nhan(base, personal)
    assert r["rank_group"] == 5
    assert r["label"] == "Không ưu tiên theo việc"
