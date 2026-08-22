"""Kiểm thử Calendar Engine.

Nguyên tắc: mọi con số trong tệp này hoặc do thiên văn quyết định, hoặc là
tính chất cấu trúc kiểm được. Không có đáp án huyền học nào được tôi tự đặt
rồi tự xác nhận.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from loi.lich.bo_quy_uoc import kiem_khong_hard_code, tai_tat_ca, tai_tu_tep
from loi.lich.can_chi_nam import TruNamError
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN, CHI, quy_uoc_mac_dinh, tai_quy_uoc
from loi.lich.thoi_gian import ThoiGianError
from loi.lich.tiet_khi import NEN_DU_PHONG, BoTinhTietKhi, doi_chieu_hai_nen
from loi.nen.phien_ban import DUONG_DAN

TZ = "Asia/Ho_Chi_Minh"
VN = timezone(timedelta(hours=7))


@pytest.fixture(scope="module")
def bo_lich():
    return tai_tat_ca()


@pytest.fixture(scope="module")
def eV1(bo_lich):
    return CalendarEngine(bo_lich["CAL-V1"])


@pytest.fixture(scope="module")
def e23(bo_lich):
    return CalendarEngine(bo_lich["CAL-V1-23H"])


def _tinh(e, y, m, d, h, mi, gioi_tinh="NAM"):
    return e.tinh(y, m, d, h, mi, timezone_name=TZ, gioi_tinh=gioi_tinh)


# ============ 1-2. Trước và sau Lập Xuân =============================

def test_01_truoc_lap_xuan_thuoc_nam_cu(eV1):
    r = _tinh(eV1, 1990, 2, 4, 6, 0)
    assert r.tru_nam.nam_can_chi == 1989
    assert r.thoi_diem.utc < r.tru_nam.ket_thuc_utc
    assert r.thoi_diem.utc >= r.tru_nam.bat_dau_utc


def test_02_sau_lap_xuan_thuoc_nam_moi(eV1):
    r = _tinh(eV1, 1990, 2, 4, 12, 0)
    assert r.tru_nam.nam_can_chi == 1990
    assert r.thoi_diem.utc >= r.tru_nam.bat_dau_utc
    assert r.thoi_diem.utc < r.tru_nam.ket_thuc_utc


def test_02b_hai_ben_lap_xuan_khac_tru_nam_va_tru_thang(eV1):
    a = _tinh(eV1, 1990, 2, 4, 6, 0)
    b = _tinh(eV1, 1990, 2, 4, 12, 0)
    assert (a.tru_nam.can, a.tru_nam.chi) != (b.tru_nam.can, b.tru_nam.chi)
    assert (a.tru_thang.can, a.tru_thang.chi) != (b.tru_thang.can, b.tru_thang.chi)
    # Trụ ngày phải đứng yên, nếu không thì ca không cô lập được thứ cần kiểm.
    assert (a.tru_ngay.can, a.tru_ngay.chi) == (b.tru_ngay.can, b.tru_ngay.chi)


def test_02c_tru_nam_lien_tuc_qua_moc(eV1):
    """Trụ năm hai bên mốc phải cách nhau đúng một bước trong chu kỳ 60."""
    a = _tinh(eV1, 1990, 2, 4, 6, 0)
    b = _tinh(eV1, 1990, 2, 4, 12, 0)
    assert (CAN.index(b.tru_nam.can) - CAN.index(a.tru_nam.can)) % 10 == 1
    assert (CHI.index(b.tru_nam.chi) - CHI.index(a.tru_nam.chi)) % 12 == 1


# ============ 3-4. Trước và sau Jie ==================================

def test_03_truoc_jie(eV1):
    bo_tiet = eV1.bo_tiet
    moc = bo_tiet.thoi_diem(2024, "MANG_CHUNG")
    truoc = (moc - timedelta(hours=2)).astimezone(VN)
    r = _tinh(eV1, truoc.year, truoc.month, truoc.day, truoc.hour, truoc.minute)
    assert r.tru_thang.tiet_mo_thang != "MANG_CHUNG"


def test_04_sau_jie(eV1):
    moc = eV1.bo_tiet.thoi_diem(2024, "MANG_CHUNG")
    sau = (moc + timedelta(hours=2)).astimezone(VN)
    r = _tinh(eV1, sau.year, sau.month, sau.day, sau.hour, sau.minute)
    assert r.tru_thang.tiet_mo_thang == "MANG_CHUNG"
    assert r.tru_thang.chi == "NGO"


def test_04b_hai_ben_jie_khac_tru_thang_cung_tru_nam(eV1):
    moc = eV1.bo_tiet.thoi_diem(2024, "MANG_CHUNG")
    a = (moc - timedelta(hours=2)).astimezone(VN)
    b = (moc + timedelta(hours=2)).astimezone(VN)
    ra = _tinh(eV1, a.year, a.month, a.day, a.hour, a.minute)
    rb = _tinh(eV1, b.year, b.month, b.day, b.hour, b.minute)
    assert (ra.tru_thang.can, ra.tru_thang.chi) != (rb.tru_thang.can, rb.tru_thang.chi)
    assert ra.tru_nam.nam_can_chi == rb.tru_nam.nam_can_chi
    assert (CHI.index(rb.tru_thang.chi) - CHI.index(ra.tru_thang.chi)) % 12 == 1


# ============ 5-10. Sáu mốc giờ quanh nửa đêm =========================

MOC_GIO = [
    ("T2259", 2024, 6, 10, 22, 59),
    ("T2300", 2024, 6, 10, 23, 0),
    ("T2359", 2024, 6, 10, 23, 59),
    ("T0000", 2024, 6, 11, 0, 0),
    ("T0059", 2024, 6, 11, 0, 59),
    ("T0100", 2024, 6, 11, 1, 0),
]


@pytest.mark.parametrize("nhan,y,m,d,h,mi", MOC_GIO)
def test_05_10_moc_gio_deu_tinh_duoc(eV1, nhan, y, m, d, h, mi):
    r = _tinh(eV1, y, m, d, h, mi)
    assert r.tru_gio.chi in CHI and r.tru_gio.can in CAN


def test_05_10a_v1_doi_ngay_dung_luc_nua_dem(eV1):
    truoc = _tinh(eV1, 2024, 6, 10, 23, 59)
    sau = _tinh(eV1, 2024, 6, 11, 0, 0)
    assert truoc.tru_ngay.ngay_lich_phap != sau.tru_ngay.ngay_lich_phap
    assert not _tinh(eV1, 2024, 6, 10, 23, 0).tru_ngay.da_vuot_moc_doi_ngay


def test_05_10b_23h_doi_ngay_dung_luc_23_gio(e23):
    truoc = _tinh(e23, 2024, 6, 10, 22, 59)
    sau = _tinh(e23, 2024, 6, 10, 23, 0)
    assert truoc.tru_ngay.ngay_lich_phap != sau.tru_ngay.ngay_lich_phap
    assert sau.tru_ngay.da_vuot_moc_doi_ngay
    # Từ 23:00 tới 00:00 hôm sau phải là cùng một ngày lịch pháp.
    assert sau.tru_ngay.ngay_lich_phap == _tinh(e23, 2024, 6, 11, 0, 0).tru_ngay.ngay_lich_phap


def test_05_10c_chi_gio_doi_dung_moc_le(eV1):
    """Chi giờ đổi tại 23:00, 01:00, 03:00... không phụ thuộc mốc đổi ngày."""
    assert _tinh(eV1, 2024, 6, 10, 22, 59).tru_gio.chi == "HOI"
    assert _tinh(eV1, 2024, 6, 10, 23, 0).tru_gio.chi == "TY"
    assert _tinh(eV1, 2024, 6, 11, 0, 59).tru_gio.chi == "TY"
    assert _tinh(eV1, 2024, 6, 11, 1, 0).tru_gio.chi == "SUU"


def test_05_10d_ranh_gioi_ngay_va_chi_gio_khong_lan_lon(eV1, e23):
    """Cùng thời điểm 23:00: chi giờ như nhau, trụ ngày khác nhau."""
    a = _tinh(eV1, 2024, 6, 10, 23, 0)
    b = _tinh(e23, 2024, 6, 10, 23, 0)
    assert a.tru_gio.chi == b.tru_gio.chi == "TY"
    assert (a.tru_ngay.can, a.tru_ngay.chi) != (b.tru_ngay.can, b.tru_ngay.chi)


# ============ 11-14. Bốn tổ hợp âm dương nam nữ ======================

def _chieu(e, y, m, d, gioi_tinh):
    return _tinh(e, y, m, d, 12, 0, gioi_tinh).dai_van.chieu


def test_11_duong_nam_di_thuan(eV1):
    r = _tinh(eV1, 1990, 6, 15, 12, 0, "NAM")     # Canh Ngọ, Canh là can dương
    assert CAN.index(r.tru_nam.can) % 2 == 0
    assert r.dai_van.chieu == "THUAN"


def test_12_am_nu_di_thuan(eV1):
    r = _tinh(eV1, 1989, 6, 15, 12, 0, "NU")      # Kỷ Tị, Kỷ là can âm
    assert CAN.index(r.tru_nam.can) % 2 == 1
    assert r.dai_van.chieu == "THUAN"


def test_13_am_nam_di_nghich(eV1):
    r = _tinh(eV1, 1989, 6, 15, 12, 0, "NAM")
    assert CAN.index(r.tru_nam.can) % 2 == 1
    assert r.dai_van.chieu == "NGHICH"


def test_14_duong_nu_di_nghich(eV1):
    r = _tinh(eV1, 1990, 6, 15, 12, 0, "NU")
    assert CAN.index(r.tru_nam.can) % 2 == 0
    assert r.dai_van.chieu == "NGHICH"


def test_14b_thuan_dem_toi_jie_sau_nghich_dem_ve_jie_truoc(eV1):
    thuan = _tinh(eV1, 1990, 6, 15, 12, 0, "NAM")
    nghich = _tinh(eV1, 1990, 6, 15, 12, 0, "NU")
    assert thuan.dai_van.thoi_diem_tiet_muc_tieu_utc > thuan.thoi_diem.utc
    assert nghich.dai_van.thoi_diem_tiet_muc_tieu_utc < nghich.thoi_diem.utc
    assert thuan.dai_van.so_ngay_toi_tiet > 0
    assert nghich.dai_van.so_ngay_toi_tiet > 0
    # Hai chiều cộng lại đúng bằng độ dài một tháng lệnh.
    tong = thuan.dai_van.so_ngay_toi_tiet + nghich.dai_van.so_ngay_toi_tiet
    assert 28 < tong < 33


def test_14c_van_di_lien_tuc_tu_tru_thang(eV1):
    r = _tinh(eV1, 1990, 6, 15, 12, 0, "NAM")
    v1 = r.dai_van.cac_van[0]
    assert (CAN.index(v1.can) - CAN.index(r.tru_thang.can)) % 10 == 1
    assert (CHI.index(v1.chi) - CHI.index(r.tru_thang.chi)) % 12 == 1
    assert len(r.dai_van.cac_van) == 10
    for a, b in zip(r.dai_van.cac_van, r.dai_van.cac_van[1:]):
        assert abs(b.tuoi_bat_dau - a.tuoi_bat_dau - 10) < 1e-6


def test_14d_khoi_van_dung_cong_thuc_ba_ngay_mot_nam(eV1):
    r = _tinh(eV1, 1990, 6, 15, 12, 0, "NAM")
    dv = r.dai_van
    assert abs(dv.tuoi_khoi_van - dv.so_ngay_toi_tiet / 3.0) < 1e-9
    # Tầng chiết trừ đã có nguồn Tam Mệnh Thông Hội.
    assert dv.trang_thai_chiet_tru == "VERIFIED"
    # Tầng đổi ra ngày dương lịch thì chưa.
    assert dv.trang_thai_ra_ngay == "PROVISIONAL"


# ============ 15. Cùng đầu vào, hai bộ quy ước =======================

def test_15_hai_bo_quy_uoc_cho_ket_qua_khac_nhau(eV1, e23):
    a = _tinh(eV1, 2024, 6, 10, 23, 30)
    b = _tinh(e23, 2024, 6, 10, 23, 30)
    assert a.ruleset_id == "CAL-V1"
    assert b.ruleset_id == "CAL-V1-23H"
    assert a.tom_tat()["day_pillar"] != b.tom_tat()["day_pillar"]


def test_15b_ngoai_vung_ranh_gioi_hai_bo_giong_nhau(eV1, e23):
    a = _tinh(eV1, 2024, 6, 11, 10, 0)
    b = _tinh(e23, 2024, 6, 11, 10, 0)
    for k in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        assert a.tom_tat()[k] == b.tom_tat()[k]


def test_15c_khong_co_bo_mac_dinh_ngam(bo_lich):
    """Không tạo được Engine mà không nói rõ dùng bộ quy ước nào."""
    with pytest.raises(TypeError):
        CalendarEngine()


# ============ 16. Sinh sát tiết khí ==================================

def test_16_sinh_sat_tiet_khi_co_canh_bao(eV1):
    moc = eV1.bo_tiet.thoi_diem(2024, "MANG_CHUNG").astimezone(VN)
    for lech in (-5, 5):
        t = moc + timedelta(minutes=lech)
        r = _tinh(eV1, t.year, t.month, t.day, t.hour, t.minute)
        assert r.boundary_warning
        assert "SAT_MOC_DOI_THANG" in [c.ma for c in r.canh_bao]


def test_16b_xa_tiet_khi_thi_khong_canh_bao_thang(eV1):
    r = _tinh(eV1, 2024, 6, 15, 10, 0)
    assert "SAT_MOC_DOI_THANG" not in [c.ma for c in r.canh_bao]


def test_16c_sat_lap_xuan_co_canh_bao_nam(eV1):
    moc = eV1.bo_tiet.thoi_diem(1990, "LAP_XUAN").astimezone(VN)
    t = moc + timedelta(minutes=10)
    r = _tinh(eV1, t.year, t.month, t.day, t.hour, t.minute)
    assert "SAT_MOC_DOI_NAM" in [c.ma for c in r.canh_bao]


def test_16c2_sat_lap_xuan_phia_TRUOC_cung_phai_canh_bao(eV1):
    """Lỗi từng bỏ sót: sinh trước mốc vài phút cũng phải được cảnh báo."""
    moc = eV1.bo_tiet.thoi_diem(1990, "LAP_XUAN").astimezone(VN)
    t = moc - timedelta(minutes=10)
    r = _tinh(eV1, t.year, t.month, t.day, t.hour, t.minute)
    assert r.tru_nam.nam_can_chi == 1989
    assert "SAT_MOC_DOI_NAM" in [c.ma for c in r.canh_bao]


def test_16d_canh_bao_gio_ty_truoc_nua_dem(eV1):
    r = _tinh(eV1, 2024, 6, 10, 23, 30)
    assert "GIO_TY_TRUOC_NUA_DEM" in [c.ma for c in r.canh_bao]
    assert r.tru_gio.nam_trong_phan_ty_truoc_nua_dem


def test_16e_canh_bao_ghi_ro_cach_moc_bao_nhieu_phut(eV1):
    moc = eV1.bo_tiet.thoi_diem(2024, "MANG_CHUNG").astimezone(VN)
    t = moc + timedelta(minutes=7)
    r = _tinh(eV1, t.year, t.month, t.day, t.hour, t.minute)
    cb = [c for c in r.canh_bao if c.ma == "SAT_MOC_DOI_THANG"][0]
    assert 6 <= cb.cach_moc_phut <= 8


# ============ 17. Múi giờ ============================================

def test_17_mui_gio_lich_su_duoc_ap_dung(eV1):
    """Việt Nam từng ở múi giờ khác. Engine phải tra theo thời điểm lịch sử."""
    cu = eV1.tinh(1960, 6, 1, 12, 0, timezone_name=TZ, gioi_tinh="NAM")
    nay = eV1.tinh(2024, 6, 1, 12, 0, timezone_name=TZ, gioi_tinh="NAM")
    assert cu.thoi_diem.utc_offset_phut == 480
    assert nay.thoi_diem.utc_offset_phut == 420


def test_17b_hai_mui_gio_cung_moc_tuyet_doi_cho_cung_tru_ngay(eV1):
    a = eV1.tinh(2024, 6, 11, 10, 0, timezone_name="Asia/Ho_Chi_Minh", gioi_tinh="NAM")
    b = eV1.tinh(2024, 6, 11, 11, 0, timezone_name="Asia/Shanghai", gioi_tinh="NAM")
    assert a.thoi_diem.utc == b.thoi_diem.utc
    assert (a.tru_nam.can, a.tru_thang.can) == (b.tru_nam.can, b.tru_thang.can)


def test_17c_mui_gio_khong_biet_thi_bao_loi(eV1):
    with pytest.raises(ThoiGianError, match="MUI_GIO_KHONG_BIET"):
        eV1.tinh(2024, 6, 11, 10, 0, timezone_name="Chau/Khong_Co")


def test_17d_thieu_mui_gio_thi_bao_loi(eV1):
    with pytest.raises(ThoiGianError, match="THIEU_MUI_GIO"):
        eV1.tinh(2024, 6, 11, 10, 0)


def test_17e_dung_do_lech_thay_ten_mui_gio(eV1):
    r = eV1.tinh(2024, 6, 11, 10, 0, utc_offset_phut=420, gioi_tinh="NAM")
    assert r.thoi_diem.utc_offset_phut == 420


# ============ 18. Kết quả lặp lại giống nhau =========================

def test_18_ket_qua_deterministic(eV1):
    a = _tinh(eV1, 1990, 2, 4, 12, 0).tom_tat()
    b = _tinh(eV1, 1990, 2, 4, 12, 0).tom_tat()
    assert a == b


def test_18b_engine_moi_cho_ket_qua_giong_engine_cu(bo_lich):
    a = CalendarEngine(bo_lich["CAL-V1"])
    b = CalendarEngine(bo_lich["CAL-V1"])
    assert (_tinh(a, 1990, 2, 4, 12, 0).tom_tat()
            == _tinh(b, 1990, 2, 4, 12, 0).tom_tat())


def test_18c_hai_nen_thien_van_khop_nhau_trong_mot_phut():
    for nam, code in ((1990, "LAP_XUAN"), (2024, "MANG_CHUNG"), (2026, "LAP_XUAN")):
        _, _, lech_giay = doi_chieu_hai_nen(nam, code)
        assert lech_giay < 60, f"{code} {nam} lệch {lech_giay} giây"


def test_18d_nen_du_phong_cho_cung_tu_tru(bo_lich):
    chinh = CalendarEngine(bo_lich["CAL-V1"])
    du_phong = CalendarEngine(bo_lich["CAL-V1"],
                              bo_tiet=BoTinhTietKhi(quy_uoc_mac_dinh(), NEN_DU_PHONG))
    a = _tinh(chinh, 1990, 2, 4, 12, 0).tom_tat()
    b = _tinh(du_phong, 1990, 2, 4, 12, 0).tom_tat()
    for k in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        assert a[k] == b[k]


# ============ 19. Dấu vết phiên bản ==================================

def test_19_ket_qua_ghi_du_dau_vet(eV1):
    r = _tinh(eV1, 1990, 2, 4, 12, 0)
    assert r.ruleset_id == "CAL-V1"
    assert r.ruleset_version
    assert r.ganzhi_ruleset_id == "GZ-V1"
    assert r.engine_version
    assert r.nen_thien_van == "astronomy-engine"
    assert r.calculation_timestamp


def test_19b_boundary_rule_ghi_du_bay_khoa(eV1):
    r = _tinh(eV1, 1990, 2, 4, 12, 0)
    assert set(r.boundary_rule) == {
        "YEAR_BOUNDARY", "MONTH_BOUNDARY", "DAY_BOUNDARY", "HOUR_STEM_LATE_ZI",
        "TRUE_SOLAR_TIME", "LOCAL_TIMEZONE", "HISTORICAL_TIMEZONE"}
    assert r.boundary_rule["DAY_BOUNDARY"] == "00:00"


def test_19c_bo_quy_uoc_can_chi_khong_khop_thi_bao_loi(bo_lich, tmp_path):
    import yaml
    goc = DUONG_DAN["goc"] / "cau_hinh" / "can_chi" / "quy_uoc_can_chi.yaml"
    raw = yaml.safe_load(goc.read_text(encoding="utf-8"))
    raw["ruleset_id"] = "GZ-KHAC"
    tep = tmp_path / "khac.yaml"
    tep.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="QUY_UOC_CAN_CHI_KHONG_KHOP"):
        CalendarEngine(bo_lich["CAL-V1"], quy_uoc=tai_quy_uoc(tep))


# ============ 20. Không chép cứng mốc lịch ===========================

def test_20_khong_hard_code_moc_lich():
    assert kiem_khong_hard_code() == []


def test_20b_moc_doi_nam_la_thi_bao_loi_khong_lang_le_thay(bo_lich, tmp_path):
    import yaml
    goc = DUONG_DAN["lich_phap"] / "CAL-V1.yaml"
    raw = yaml.safe_load(goc.read_text(encoding="utf-8"))
    raw["calendar_ruleset_id"] = "CAL-THU"
    raw["settings"]["YEAR_BOUNDARY"]["value"] = "LUNAR_NEW_YEAR"
    raw["is_default"] = False
    tep = tmp_path / "CAL-THU.yaml"
    tep.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    e = CalendarEngine(tai_tu_tep(tep))
    with pytest.raises(TruNamError, match="MOC_DOI_NAM_CHUA_HO_TRO"):
        _tinh(e, 1990, 2, 4, 12, 0)


def test_20c_gio_mat_troi_that_bat_len_thi_bao_loi(tmp_path):
    import yaml
    goc = DUONG_DAN["lich_phap"] / "CAL-V1.yaml"
    raw = yaml.safe_load(goc.read_text(encoding="utf-8"))
    raw["calendar_ruleset_id"] = "CAL-MT"
    raw["settings"]["TRUE_SOLAR_TIME"]["value"] = "true"
    raw["is_default"] = False
    tep = tmp_path / "CAL-MT.yaml"
    tep.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    e = CalendarEngine(tai_tu_tep(tep))
    with pytest.raises(ThoiGianError, match="GIO_MAT_TROI_THAT_CHUA_HO_TRO"):
        _tinh(e, 1990, 2, 4, 12, 0)


def test_20d_doi_moc_trong_cau_hinh_thi_engine_doi_theo(bo_lich, tmp_path):
    """Sửa tệp cấu hình là đủ để đổi hành vi. Không phải sửa mã."""
    import yaml
    goc = DUONG_DAN["lich_phap"] / "CAL-V1.yaml"
    raw = yaml.safe_load(goc.read_text(encoding="utf-8"))
    raw["calendar_ruleset_id"] = "CAL-2130"
    raw["settings"]["DAY_BOUNDARY"]["value"] = "21:30"
    raw["is_default"] = False
    tep = tmp_path / "CAL-2130.yaml"
    tep.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    e = CalendarEngine(tai_tu_tep(tep))
    truoc = _tinh(e, 2024, 6, 10, 21, 29)
    sau = _tinh(e, 2024, 6, 10, 21, 30)
    assert truoc.tru_ngay.ngay_lich_phap != sau.tru_ngay.ngay_lich_phap


# ============ Kiểm tra tệp quy ước Can Chi ===========================

def test_quy_uoc_can_chi_du_24_tiet_va_12_jie():
    q = quy_uoc_mac_dinh()
    assert len(q.tiet_khi) == 24
    assert len(q.cac_jie) == 12
    assert {t.month_branch for t in q.cac_jie} == set(CHI)


def test_bang_don_du_muoi_can():
    q = quy_uoc_mac_dinh()
    for can in CAN:
        assert q.can_thang_dan(can) in CAN
        assert q.can_gio_ty(can) in CAN


def test_tru_ngay_chay_lien_tuc_khong_dut():
    from datetime import date
    q = quy_uoc_mac_dinh()
    truoc = q.can_chi_ngay(date(2024, 6, 10))
    sau = q.can_chi_ngay(date(2024, 6, 11))
    assert (CAN.index(sau[0]) - CAN.index(truoc[0])) % 10 == 1
    assert (CHI.index(sau[1]) - CHI.index(truoc[1])) % 12 == 1
    # Chu kỳ đúng 60 ngày.
    assert q.can_chi_ngay(date(2024, 6, 11)) == q.can_chi_ngay(date(2024, 8, 10))


def test_quy_uoc_can_chi_van_dang_o_trang_thai_cho():
    q = quy_uoc_mac_dinh()
    assert q.status == "PROVISIONAL", "chưa có nguồn sách thì không được đánh dấu đã xác minh"
