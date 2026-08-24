"""Đầu-cuối 0.5.0 cho người không biết Tử Bình."""
from __future__ import annotations
import json
from datetime import date
import pytest

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so import ho_so
from loi.ho_so.ho_so import HoSoError
from loi.hop_luu.hop_luu import hop_luu
from loi.van import dong_thoi_gian as dtg

THUAT_NGU_CAM=("Tàng Can","Thập Thần","Nguyệt lệnh","Dụng thần","Thần sát","tang_can","thap_than","nguyet_lenh")
NGUOI_MOI=dict(full_name="Bà Nội",gender="NU",birth_year=1952,birth_month=11,birth_day=3,birth_hour=4,birth_minute=45,birth_place_text="Vĩnh Long",timezone_name="Asia/Ho_Chi_Minh")

@pytest.fixture
def nguoi(db_da_nap):
    hs=ho_so.tao(db_da_nap,**NGUOI_MOI)
    yield db_da_nap,hs
    try: ho_so.xoa(db_da_nap,hs.profile_id)
    except HoSoError: pass


def test_tao_sua_xoa_ho_so(db_da_nap):
    hs=ho_so.tao(db_da_nap,**NGUOI_MOI); assert hs.profile_id.startswith("P-")
    hs2=ho_so.sua(db_da_nap,hs.profile_id,full_name="Bà Nội Hai"); assert hs2.full_name=="Bà Nội Hai" and hs2.birth_year==1952
    ho_so.xoa(db_da_nap,hs.profile_id)
    with pytest.raises(HoSoError): ho_so.lay(db_da_nap,hs.profile_id)


def test_nhap_sai_bao_tieng_viet(db_da_nap):
    with pytest.raises(HoSoError) as e: ho_so.tao(db_da_nap,**{**NGUOI_MOI,"birth_month":13})
    assert "Ngày giờ sinh không hợp lệ" in str(e.value)


def test_xem_thang_va_hom_nay(nguoi):
    c,hs=nguoi; kq=hop_luu(c,hs,ngay=date(2026,9,15)); t1=tang_1(kq)
    assert kq.day_state["solar_date"]=="2026-09-15" and t1["tieu_de"] and any("Bốn trụ" in x for x in t1["he_thong_biet_gi"])


def test_chon_viec_da_co_lop_hiep_ky_v1(nguoi):
    c,hs=nguoi; kq=hop_luu(c,hs,ngay=date(2026,9,15),event_code="CUOI_HOI")
    assert kq.event_state["event_code"]=="CUOI_HOI"
    assert kq.event_state["support_level"]=="ACTIVE_BASIC"
    assert kq.event_state["score"] is None
    assert kq.event_state["decision_state"] in {"PRIORITY","CONSIDER","NOT_PREFERRED","HARD_BLOCK","EVENT_ONLY"}


def test_ba_ngay_khong_co_diem_gia(nguoi):
    c,hs=nguoi
    for d in (date(2026,9,1),date(2026,9,2),date(2026,9,3)):
        kq=hop_luu(c,hs,ngay=d,event_code="KHAI_TRUONG")
        assert kq.score is None and kq.scoring_status=="ORDINAL_V1_1_PERSONAL"
        assert kq.label in {"Ưu tiên","Có thể cân nhắc","Không ưu tiên","Bị chặn","Phù hợp theo Hiệp Kỷ","Chưa có tín hiệu theo việc"}


def test_gio_van_chua_duoc_phat_trien_thanh_cat_hung(nguoi):
    c,hs=nguoi; kq=hop_luu(c,hs,ngay=date(2026,9,15),gio_chi="NGO")
    assert kq.hour_state["chi_gio"]=="NGO" and kq.hour_state["danh_gia"]["status"]=="UNKNOWN"


def test_tang_1_khong_ep_hoc_thuat_ngu(nguoi):
    c,hs=nguoi
    for d in (None,date(2026,1,1),date(2026,6,30)):
        van=json.dumps(tang_1(hop_luu(c,hs,ngay=d)),ensure_ascii=False)
        for tu in THUAT_NGU_CAM: assert tu not in van, f"{d}: lộ thuật ngữ {tu!r}"


def test_tang_1_noi_ro_gioi_han(nguoi):
    c,hs=nguoi; t1=tang_1(hop_luu(c,hs))
    assert t1["canh_bao_trung_thuc"] and t1["he_thong_chua_biet_gi"]


def test_chuyen_sau_co_day_du_tang(nguoi):
    c,hs=nguoi; t2=tang_2(hop_luu(c,hs,ngay=date(2026,9,15)))
    assert set(t2)>={"menh","dai_van","nam","thang","ngay","gio","hiep_ky","than_sat","hop_luu","rule_trace","source_trace"}
    assert t2["rule_trace"]


def test_cach_cuc_da_duoc_noi_vao_hop_luu(nguoi):
    c,hs=nguoi; kq=hop_luu(c,hs,ngay=date(2026,9,15))
    assert kq.base_state["cach_cuc"]["status"] in {"READY","AMBIGUOUS"}
    if kq.base_state["cach_cuc"]["status"]=="READY": assert kq.base_state["dung_hy_ky"]["status"]=="READY"
    assert {u.ma for u in kq.uncertainties}=={"THAN_SAT","CHAM_DIEM"}


def test_truy_nguoc_quy_tac(nguoi):
    c,hs=nguoi; chain=truy_nguoc_day_du(c,hop_luu(c,hs,ngay=date(2026,9,15)))
    assert len(chain)>=10
    for m in chain:
        assert m["rule_id"] and m["rule_version"] and m["verification_status"] in {"VERIFIED","PROVISIONAL","CONFLICTED","REJECTED"}
        assert m["source_id"]


def test_khong_bia_yeu_to_duong_am_tu_quan_he_don_le(nguoi):
    c,hs=nguoi; kq=hop_luu(c,hs,ngay=date(2026,9,15))
    assert kq.positive_factors==[] and kq.negative_factors==[]


def test_dong_thoi_gian_du_bon_tang(nguoi):
    c,hs=nguoi; d=dtg.dung(c,hs).to_dict(); assert set(d["tu_tru"])=={"nam","thang","ngay","gio"}
    assert d["nam_hien_tai"]["vi"] and d["thang_hien_tai"]["vi"]


def test_nhieu_nguoi_ra_la_so_khac(db_da_nap):
    a=ho_so.tao(db_da_nap,**NGUOI_MOI); b=ho_so.tao(db_da_nap,**{**NGUOI_MOI,"full_name":"Ông Nội","gender":"NAM","birth_year":1949})
    da=dtg.dung(db_da_nap,a).to_dict(); dbb=dtg.dung(db_da_nap,b).to_dict(); assert da["tu_tru"]["nam"]["vi"]!=dbb["tu_tru"]["nam"]["vi"]
