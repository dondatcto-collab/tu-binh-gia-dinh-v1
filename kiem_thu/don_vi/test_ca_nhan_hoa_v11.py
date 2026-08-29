"""Kiểm thử cá nhân hóa 0.5.0: Cách cục đã mở, quan hệ Chi không tự quyết."""
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan, bo_sung_event_ca_nhan
from loi.van.dong_thoi_gian import TruVi


def _tu_tru_user(day_branch="DAN"):
    return {"nam":TruVi("MAU","THIN"),"thang":TruVi("QUY","HOI"),"ngay":TruVi("MAU",day_branch),"gio":TruVi("BINH","THIN")}


def test_doc_du_bon_tru_va_co_natal_pattern(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tu_tru_user(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
    assert r["theme"]["ten_god_vi"]=="Thiên Ấn"
    assert r["natal_pattern"]["status"] in {"READY","AMBIGUOUS"}
    rel={(x["position"],x["relation"]) for x in r["branch_impacts"]}; assert ("ngay","LUC_XUNG") in rel and ("thang","LUC_HAI") in rel


def test_current_stem_branch_are_machine_readable_contract(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tu_tru_user(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="day",context=[])
    assert r["current_stem"]=="BINH"
    assert r["current_branch"]=="THAN"
    assert r["current_stem"] in {"GIAP","AT","BINH","DINH","MAU","KY","CANH","TAN","NHAM","QUY"}


def test_nguoi_khac_co_evidence_khac(db_da_nap):
    a=phan_tich_ca_nhan(db_da_nap,tu_tru=_tu_tru_user("DAN"),nhat_chu="MAU",can_hien_tai="KY",chi_hien_tai="TI",scope="day",context=[])
    b=phan_tich_ca_nhan(db_da_nap,tu_tru=_tu_tru_user("MAO"),nhat_chu="MAU",can_hien_tai="KY",chi_hien_tai="TI",scope="day",context=[])
    assert a["branch_impacts"]!=b["branch_impacts"]
    assert a["state"] in {"SUPPORT","CAUTION","NEUTRAL","DESCRIPTIVE_ONLY"}


def test_khong_bia_diem_so(db_da_nap):
    r=phan_tich_ca_nhan(db_da_nap,tu_tru=_tu_tru_user(),nhat_chu="MAU",can_hien_tai="BINH",chi_hien_tai="THAN",scope="month",context=[])
    assert "8.6" not in str(r) and "7.8" not in str(r)


def test_event_yi_ca_nhan_thuan_duoc_uu_tien():
    base={"event_state":"YI","mapping_status":"VERIFIED","rank_group":1,"label":"Phù hợp theo Hiệp Kỷ","reasons":[],"rule_ids":[]}
    personal={"state":"SUPPORT","current_stem":"BINH","current_branch":"THAN","branch_impacts":[],"theme":{},"rule_ids":[],"dien_giai":{},"technical_facts":[],"methodology":{"decision_mode":"ZPZQ_PERSONAL"}}
    r=bo_sung_event_ca_nhan(base,personal); assert r["decision_state"]=="PRIORITY" and r["score"] is None
    assert r["personal_v1_1"]["current_stem"]=="BINH"


def test_event_ji_khong_duoc_ca_nhan_cuu():
    base={"event_state":"JI","mapping_status":"VERIFIED","rank_group":5,"label":"Không ưu tiên theo việc","reasons":[],"rule_ids":[]}
    personal={"state":"SUPPORT","current_stem":"BINH","current_branch":"THAN","branch_impacts":[],"theme":{},"rule_ids":[],"dien_giai":{},"technical_facts":[],"methodology":{"decision_mode":"ZPZQ_PERSONAL"}}
    r=bo_sung_event_ca_nhan(base,personal); assert r["hard_block"] is True and r["rank_group"]==9 and r["label"]=="Bị chặn"
