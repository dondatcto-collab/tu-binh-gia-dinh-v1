"""Kiểm thử đầu-cuối: người dùng KHÔNG biết Tử Bình.

Luật của mục XXI: nếu người đó buộc phải hiểu Tàng Can, Thập Thần,
Nguyệt lệnh, Dụng thần hay Thần sát mới biết bấm gì hoặc hiểu kết quả,
thì trải nghiệm V1 coi như TRƯỢT.

Test này đi đúng mười ba bước của mục XX.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pytest

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so import ho_so
from loi.ho_so.ho_so import HoSoError
from loi.hop_luu.hop_luu import NOT_CALIBRATED, UNKNOWN, hop_luu
from loi.van import dong_thoi_gian as dtg

# Thuật ngữ mà người không biết Tử Bình KHÔNG được buộc phải hiểu.
THUAT_NGU_CAM = ("Tàng Can", "Thập Thần", "Nguyệt lệnh", "Dụng thần",
                 "Thần sát", "tang_can", "thap_than", "nguyet_lenh")

NGUOI_MOI = dict(
    full_name="Bà Nội", gender="NU",
    birth_year=1952, birth_month=11, birth_day=3,
    birth_hour=4, birth_minute=45,
    birth_place_text="Vĩnh Long", timezone_name="Asia/Ho_Chi_Minh",
)


@pytest.fixture
def nguoi(db_da_nap):
    hs = ho_so.tao(db_da_nap, **NGUOI_MOI)
    yield db_da_nap, hs
    try:
        ho_so.xoa(db_da_nap, hs.profile_id)
    except HoSoError:
        pass


# ============ Mười ba bước của mục XX ================================

def test_buoc_1_tao_ho_so(db_da_nap):
    hs = ho_so.tao(db_da_nap, **NGUOI_MOI)
    assert hs.profile_id.startswith("P-")
    assert hs.full_name == "Bà Nội"


def test_buoc_1b_nhap_sai_thi_bao_bang_tieng_viet_de_hieu(db_da_nap):
    with pytest.raises(HoSoError) as e:
        ho_so.tao(db_da_nap, **{**NGUOI_MOI, "birth_month": 13})
    assert "Ngày giờ sinh không hợp lệ" in str(e.value)
    with pytest.raises(HoSoError) as e:
        ho_so.tao(db_da_nap, **{**NGUOI_MOI, "full_name": "  "})
    assert "Chưa nhập tên" in str(e.value)


def test_buoc_2_chon_ho_so(nguoi):
    conn, hs = nguoi
    ds = ho_so.danh_sach(conn)
    assert hs.profile_id in [x.profile_id for x in ds]


def test_buoc_3_xem_thang_nay(nguoi):
    conn, hs = nguoi
    t1 = tang_1(hop_luu(conn, hs))
    assert t1["tieu_de"]
    assert t1["he_thong_biet_gi"], "phải nói được ít nhất bốn trụ"
    assert any("Bốn trụ" in x for x in t1["he_thong_biet_gi"])


def test_buoc_4_hieu_nen_hay_han_che(nguoi):
    """Chưa có căn cứ thì ba danh sách phải RỖNG, không được bịa."""
    conn, hs = nguoi
    t1 = tang_1(hop_luu(conn, hs))
    assert t1["nen_lam"] == []
    assert t1["can_nhac"] == []
    assert t1["khong_uu_tien"] == []
    assert t1["he_thong_chua_biet_gi"], "phải nói rõ chưa biết gì"


def test_buoc_5_xem_hom_nay(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15))
    assert kq.day_state["tru_ngay"]
    assert kq.day_state["solar_date"] == "2026-09-15"


def test_buoc_6_7_chon_viec_va_khoang_ngay(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15), event_code="CUOI_HOI")
    assert kq.event_state["event_code"] == "CUOI_HOI"
    assert kq.event_state["support_level"] == "NO_RULE_AVAILABLE"
    assert kq.event_state["status"] == UNKNOWN


def test_buoc_8_9_danh_sach_ngay_khong_duoc_xep_hang_gia(nguoi):
    """Chưa có căn cứ thì KHÔNG xếp hạng. Xếp hạng sai tệ hơn không xếp."""
    conn, hs = nguoi
    for d in (date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)):
        kq = hop_luu(conn, hs, ngay=d, event_code="KHAI_TRUONG")
        assert kq.score is None, "không được tạo điểm giả"
        assert kq.label == UNKNOWN
        assert kq.scoring_status == NOT_CALIBRATED


def test_buoc_10_11_xem_gio(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15), gio_chi="NGO")
    assert kq.hour_state["chi_gio"] == "NGO"
    assert kq.hour_state["danh_gia"]["status"] == UNKNOWN
    assert "bối cảnh ngày" in kq.hour_state["ghi_chu"]


def test_buoc_12_doc_ly_do_don_gian(nguoi):
    conn, hs = nguoi
    t1 = tang_1(hop_luu(conn, hs, ngay=date(2026, 9, 15)))
    van = json.dumps(t1, ensure_ascii=False)
    for tu in THUAT_NGU_CAM:
        assert tu not in van, (
            f"Tầng đơn giản buộc người dùng phải hiểu {tu!r}. UX V1 = FAIL.")


def test_buoc_13_mo_chuyen_sau_neu_muon(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15))
    t2 = tang_2(kq)
    assert set(t2) >= {"menh", "dai_van", "nam", "thang", "ngay", "gio",
                       "hiep_ky", "than_sat", "hop_luu", "rule_trace", "source_trace"}
    assert t2["rule_trace"], "chuyên sâu phải truy được về quy tắc"


# ============ Mục XXI: người không biết Tử Bình =====================

def test_toan_bo_tang_1_khong_ep_hoc_thuat_ngu(nguoi):
    conn, hs = nguoi
    for d in (None, date(2026, 1, 1), date(2026, 6, 30)):
        t1 = tang_1(hop_luu(conn, hs, ngay=d))
        van = json.dumps(t1, ensure_ascii=False)
        for tu in THUAT_NGU_CAM:
            assert tu not in van, f"{d}: lộ thuật ngữ {tu!r}"


def test_tang_1_noi_ro_khi_chua_biet(nguoi):
    """Không được lấp chỗ chưa biết bằng câu chữ mơ hồ nghe như kết luận."""
    conn, hs = nguoi
    t1 = tang_1(hop_luu(conn, hs))
    assert "CHƯA" in t1["tieu_de"] or t1["nen_lam"]
    assert t1["canh_bao_trung_thuc"]
    assert "chưa tra được" in t1["canh_bao_trung_thuc"]


# ============ Mục XVII: truy ngược ==================================

def test_moi_quy_tac_truy_duoc_ve_nguon_va_trang_thai(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15))
    chuoi = truy_nguoc_day_du(conn, kq)
    assert len(chuoi) >= 10
    for m in chuoi:
        assert m["rule_id"] and m["rule_version"]
        assert m["verification_status"] in (
            "VERIFIED", "PROVISIONAL", "CONFLICTED", "REJECTED")
        assert m["source_id"], f"{m['rule_id']} không truy được về nguồn"


def test_khong_quy_tac_nao_trong_ket_qua_tua_vao_cho_trong(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15))
    for m in truy_nguoc_day_du(conn, kq):
        if m["verification_status"] == "VERIFIED":
            assert m["source_id"] != "SRC-CHUA-CO-NGUON", m["rule_id"]


# ============ Mục VI và X: không kết luận giả =======================

def test_khong_o_nao_tu_dien_bua(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15), event_code="DONG_THO")
    d = kq.to_dict()
    for o in ("vuong_suy", "cach_cuc", "dung_hy_ky"):
        assert d["base_state"][o]["status"] == UNKNOWN
        assert d["base_state"][o]["ly_do"]
        assert d["base_state"][o]["can_gi_de_go"]


def test_moi_dieu_chua_biet_deu_noi_cach_go(nguoi):
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15), event_code="DONG_THO")
    assert len(kq.uncertainties) == 7
    for u in kq.uncertainties:
        assert u.ly_do.strip() and u.can_gi_de_go.strip()


def test_khong_yeu_to_nao_duoc_goi_la_thuan_hay_nghich(nguoi):
    """Chưa biết Dụng Hỷ Kỵ thì không được xếp yếu tố vào thuận hay nghịch."""
    conn, hs = nguoi
    kq = hop_luu(conn, hs, ngay=date(2026, 9, 15))
    assert kq.positive_factors == []
    assert kq.negative_factors == []


# ============ Dòng thời gian =========================================

def test_dong_thoi_gian_du_bon_tang(nguoi):
    conn, hs = nguoi
    d = dtg.dung(conn, hs).to_dict()
    assert set(d["tu_tru"]) == {"nam", "thang", "ngay", "gio"}
    assert d["nam_hien_tai"]["vi"] and d["thang_hien_tai"]["vi"]
    if d["dai_van"]:
        assert 1 <= d["dai_van"]["nam_thu_may"] <= 10
        assert d["dai_van"]["canh_bao"], "phải cảnh báo mốc chuyển vận chưa chắc"


def test_dai_van_canh_bao_moc_chuyen_chua_co_nguon(nguoi):
    conn, hs = nguoi
    d = dtg.dung(conn, hs).to_dict()
    if d["dai_van"]:
        assert any("TIME-0006C" in c for c in d["dai_van"]["canh_bao"])


# ============ Sửa và xóa hồ sơ ======================================

def test_sua_va_xoa_ho_so(db_da_nap):
    hs = ho_so.tao(db_da_nap, **NGUOI_MOI)
    hs2 = ho_so.sua(db_da_nap, hs.profile_id, full_name="Bà Nội Hai")
    assert hs2.full_name == "Bà Nội Hai"
    assert hs2.birth_year == NGUOI_MOI["birth_year"], "sửa tên không được đổi ngày sinh"
    ho_so.xoa(db_da_nap, hs.profile_id)
    with pytest.raises(HoSoError):
        ho_so.lay(db_da_nap, hs.profile_id)


def test_nhieu_nguoi_trong_mot_nha(db_da_nap):
    a = ho_so.tao(db_da_nap, **NGUOI_MOI)
    b = ho_so.tao(db_da_nap, **{**NGUOI_MOI, "full_name": "Ông Nội",
                                "gender": "NAM", "birth_year": 1949})
    ds = ho_so.danh_sach(db_da_nap)
    assert len(ds) == 2
    # Hai người khác nhau phải cho hai lá số khác nhau.
    da = dtg.dung(db_da_nap, a).to_dict()
    dbb = dtg.dung(db_da_nap, b).to_dict()
    assert da["tu_tru"]["nam"]["vi"] != dbb["tu_tru"]["nam"]["vi"]
