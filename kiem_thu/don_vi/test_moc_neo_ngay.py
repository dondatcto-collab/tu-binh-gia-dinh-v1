"""Kiểm thử mốc neo Can Chi ngày.

Tách rõ hai việc, đúng như yêu cầu:

  TIME-0005A  chu kỳ 60 chạy liên tục, không đứt
  TIME-0005B  một ngày cụ thể ứng với Can Chi nào

Hai việc này KHÔNG dùng chung bằng chứng. Tính tuần hoàn không chứng minh
được mốc neo, và mốc neo không chứng minh được tính tuần hoàn.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from loi.lich.quy_uoc_can_chi import (
    CAN,
    CHI,
    jdn_tu_ngay_duong,
    jdn_tu_ngay_julius,
    quy_uoc_mac_dinh,
)

# --- Sáu mốc đối chiếu, mỗi mốc một nguồn khác nhau ------------------
# (tên, số ngày Julius, Can, Chi, nguồn)
MOC_DOI_CHIEU = [
    ("720 TCN-02-22 lịch Julius", jdn_tu_ngay_julius(-719, 2, 22), "KY", "TI",
     "Xuân Thu chép, thiên văn xác nhận nhật thực"),
    ("1781-03-13", 2371629, "NHAM", "TUAT", "ytliu0, ví dụ tính trong bài"),
    ("2019-01-27", 2458511, "GIAP", "TY", "ytliu0, mốc neo riêng của họ"),
    ("2024-06-10", jdn_tu_ngay_duong(date(2024, 6, 10)), "AT", "TI",
     "sxtwl và lunar-python"),
    ("2024-06-11", jdn_tu_ngay_duong(date(2024, 6, 11)), "BINH", "NGO",
     "mốc neo cũ, nay thành mốc đối chiếu"),
    ("1990-02-04", jdn_tu_ngay_duong(date(1990, 2, 4)), "CANH", "TY",
     "ca vàng CAL-0001 đã được duyệt"),
]


@pytest.fixture(scope="module")
def q():
    return quy_uoc_mac_dinh()


# ============ TIME-0005B: mốc neo ===================================

def test_moc_neo_la_ngay_nhat_thuc_xuan_thu(q):
    assert q.moc_ngay_jdn == 1458496
    assert q.can_chi_theo_jdn(q.moc_ngay_jdn) == ("KY", "TI")
    # Số ngày Julius phải đúng ngày 22 tháng 2 năm 720 trước Công nguyên.
    assert q.moc_ngay_jdn == jdn_tu_ngay_julius(-719, 2, 22)


@pytest.mark.parametrize("ten,jdn,can,chi,nguon", MOC_DOI_CHIEU,
                         ids=[m[0] for m in MOC_DOI_CHIEU])
def test_khop_sau_moc_doi_chieu(q, ten, jdn, can, chi, nguon):
    assert q.can_chi_theo_jdn(jdn) == (can, chi), f"{ten} — nguồn: {nguon}"


# Mỗi mốc đối chiếu thuộc nhóm bằng chứng nào. Đây là chỗ tôi từng đếm SAI:
# lượt trước tôi báo "sáu nguồn khớp" như thể là sáu bằng chứng độc lập.
# Thực ra sáu mốc chỉ nằm trong bốn nhóm.
NHOM_CUA_MOC = {
    "720 TCN-02-22 lịch Julius": "CLASSICAL_TEXT+ASTRONOMICAL_EPHEMERIS",
    "1781-03-13": "ACADEMIC_CALENDAR_RESEARCH",
    "2019-01-27": "ACADEMIC_CALENDAR_RESEARCH",
    "2024-06-10": "MODERN_CALENDAR_IMPLEMENTATION",
    "2024-06-11": "MODERN_CALENDAR_IMPLEMENTATION",
    "1990-02-04": "GOLDEN_CASE",
}


def test_sau_moc_chi_thuoc_bon_nhom_bang_chung():
    """Đếm TÊN NGUỒN không phải đếm BẰNG CHỨNG ĐỘC LẬP."""
    assert len(MOC_DOI_CHIEU) == 6, "sáu mốc đối chiếu"
    nhom = set()
    for n in NHOM_CUA_MOC.values():
        nhom.update(n.split("+"))
    assert len(nhom) == 5, f"năm nhóm khác nhau, đang có {sorted(nhom)}"
    # Hai mốc ytliu0 gộp làm một, hai mốc thư viện hiện đại gộp làm một.
    assert NHOM_CUA_MOC["1781-03-13"] == NHOM_CUA_MOC["2019-01-27"]
    assert NHOM_CUA_MOC["2024-06-10"] == NHOM_CUA_MOC["2024-06-11"]


# Nhóm độc lập mong đợi cho từng quy tắc. Chốt CHÍNH XÁC tập nhóm,
# không chỉ chốt số lượng — vì gộp nhầm nhóm vẫn giữ nguyên số lượng.
NHOM_MONG_DOI = {
    "TIME-0005B": {"CLASSICAL_TEXT", "ASTRONOMICAL_EPHEMERIS",
                   "ACADEMIC_CALENDAR_RESEARCH", "MODERN_CALENDAR_IMPLEMENTATION"},
    "TIME-0005A": {"CLASSICAL_TEXT", "ACADEMIC_CALENDAR_RESEARCH",
                   "MODERN_CALENDAR_IMPLEMENTATION"},
    "TIME-0003": {"CLASSICAL_TEXT", "MODERN_CALENDAR_IMPLEMENTATION"},
    "TIME-0004": {"CLASSICAL_TEXT", "MODERN_CALENDAR_IMPLEMENTATION"},
    "TIME-0006B": {"CLASSICAL_TEXT"},
    "TIME-0006C": set(),
}

NHOM_CUA_NGUON = {
    "SRC-XUANTHU-NHATTHUC": "CLASSICAL_TEXT",
    "SRC-UHTB-CHEP": "CLASSICAL_TEXT",
    "SRC-TMTH-CHEP": "CLASSICAL_TEXT",
    "SRC-VSOP87-AE": "ASTRONOMICAL_EPHEMERIS",
    "SRC-MEEUS": "ASTRONOMICAL_EPHEMERIS",
    "SRC-THIENVAN-NHATTHUC": "ASTRONOMICAL_EPHEMERIS",
    "SRC-NASA-5MCSE": "ASTRONOMICAL_EPHEMERIS",
    "SRC-YTLIU-LICHPHAP": "ACADEMIC_CALENDAR_RESEARCH",
    "SRC-DOI-CHIEU-HD": "MODERN_CALENDAR_IMPLEMENTATION",
    "SRC-CHUA-CO-NGUON": "NONE",
}


@pytest.mark.parametrize("sid,nhom", sorted(NHOM_CUA_NGUON.items()))
def test_tung_nguon_dung_nhom_doc_lap(db_da_nap, sid, nhom):
    """Chốt từng nguồn. Gộp nhầm một nguồn sang nhóm khác là bị bắt ngay."""
    r = db_da_nap.execute(
        "SELECT independence_group FROM sources WHERE source_id = ?", (sid,)).fetchone()
    assert r is not None, f"thiếu nguồn {sid}"
    assert r["independence_group"] == nhom


@pytest.mark.parametrize("rule_id,nhom", sorted(NHOM_MONG_DOI.items()))
def test_tung_quy_tac_tua_vao_dung_bo_nhom(db_da_nap, rule_id, nhom):
    from loi.lich.do_phu import dem_bang_chung
    d = dem_bang_chung(db_da_nap, rule_id)
    assert set(d["groups"]) == nhom, d


def test_moc_neo_tua_vao_bon_nhom_doc_lap(db_da_nap):
    from loi.lich.do_phu import dem_bang_chung
    d = dem_bang_chung(db_da_nap, "TIME-0005B")
    assert d["SOURCE_COUNT"] == 4
    assert d["INDEPENDENT_EVIDENCE_GROUP_COUNT"] == 4, d
    assert "CLASSICAL_TEXT" in d["groups"]
    assert "ASTRONOMICAL_EPHEMERIS" in d["groups"]


def test_so_nguon_khac_so_nhom_o_it_nhat_mot_quy_tac(db_da_nap):
    """Chứng minh bằng mã rằng hai con số này KHÁC nhau."""
    from loi.lich.do_phu import dem_bang_chung
    khac = [r for r in NHOM_MONG_DOI
            if (d := dem_bang_chung(db_da_nap, r))["SOURCE_COUNT"]
            != d["INDEPENDENT_EVIDENCE_GROUP_COUNT"]]
    assert khac, "nếu hai số luôn bằng nhau thì trường nhóm độc lập vô dụng"


def test_nguon_nasa_cung_nhom_voi_phep_tinh_cua_minh(db_da_nap):
    """NASA và astronomy-engine cùng dùng VSOP87 nên KHÔNG độc lập với nhau."""
    rows = db_da_nap.execute(
        "SELECT source_id, independence_group FROM sources "
        "WHERE source_id IN ('SRC-NASA-5MCSE','SRC-THIENVAN-NHATTHUC','SRC-VSOP87-AE')"
    ).fetchall()
    assert len({r["independence_group"] for r in rows}) == 1
    assert rows[0]["independence_group"] == "ASTRONOMICAL_EPHEMERIS"


def test_moi_nguon_deu_khai_nhom_doc_lap(db_da_nap):
    thieu = db_da_nap.execute(
        "SELECT source_id FROM sources WHERE independence_group = 'UNASSIGNED'").fetchall()
    assert thieu == [], f"nguồn chưa khai nhóm: {[r['source_id'] for r in thieu]}"


def test_khoang_thoi_gian_phu_tren_hai_nghin_nam():
    jdn = [m[1] for m in MOC_DOI_CHIEU]
    so_nam = (max(jdn) - min(jdn)) / 365.2425
    assert so_nam > 2700, f"mới phủ {so_nam:.0f} năm"


# ============ TIME-0005A: tính liên tục =============================

def test_chu_ky_dung_60_ngay(q):
    d = date(2024, 6, 11)
    assert q.can_chi_ngay(d) == q.can_chi_ngay(d + timedelta(days=60))
    for n in range(1, 60):
        assert q.can_chi_ngay(d) != q.can_chi_ngay(d + timedelta(days=n))


def test_khong_dut_quang_qua_moc_doi_lich(q):
    """Tháng 10 năm 1582 lịch Gregory bỏ mười ngày. Chu kỳ Can Chi thì không."""
    truoc = jdn_tu_ngay_julius(1582, 10, 4)
    sau = jdn_tu_ngay_duong(date(1582, 10, 15))
    assert sau - truoc == 1, "hai ngày này phải liền nhau trên trục ngày Julius"
    a = q.can_chi_theo_jdn(truoc)
    b = q.can_chi_theo_jdn(sau)
    assert (CAN.index(b[0]) - CAN.index(a[0])) % 10 == 1
    assert (CHI.index(b[1]) - CHI.index(a[1])) % 12 == 1


def test_khong_dut_quang_qua_nam_khong(q):
    """Không có năm 0. Chu kỳ Can Chi phải đi qua chỗ đó mà không vấp."""
    truoc = jdn_tu_ngay_julius(-1, 12, 31)     # tức năm 2 trước Công nguyên
    sau = jdn_tu_ngay_julius(0, 1, 1)          # tức năm 1 trước Công nguyên
    assert sau - truoc == 1
    a, b = q.can_chi_theo_jdn(truoc), q.can_chi_theo_jdn(sau)
    assert (CAN.index(b[0]) - CAN.index(a[0])) % 10 == 1


def test_lien_tuc_tren_toan_khoang_da_phu(q):
    """Mọi ngày liền nhau phải cách nhau đúng một bước, suốt 2738 năm."""
    random.seed(20260821)
    for _ in range(2000):
        j = random.randint(1458496, 2460473)
        a, b = q.can_chi_theo_jdn(j), q.can_chi_theo_jdn(j + 1)
        assert (CAN.index(b[0]) - CAN.index(a[0])) % 10 == 1
        assert (CHI.index(b[1]) - CHI.index(a[1])) % 12 == 1


# ============ Đối chiếu công thức độc lập của ytliu0 ================

def test_trung_khop_cong_thuc_ytliu(q):
    """T = 1 + mod(JD-1, 10), B = 1 + mod(JD+1, 12). Kiểm 20000 ngày."""
    random.seed(7)
    for _ in range(20000):
        j = random.randint(1400000, 2600000)
        can_ytliu = CAN[(j - 1) % 10]
        chi_ytliu = CHI[(j + 1) % 12]
        assert q.can_chi_theo_jdn(j) == (can_ytliu, chi_ytliu)


# ============ Hai việc dùng bằng chứng khác nhau ====================

def test_moc_neo_sai_van_giu_duoc_tinh_lien_tuc():
    """Đổi mốc neo thì chu kỳ vẫn liên tục — chứng tỏ hai việc tách rời.

    Đây là lý do KHÔNG được dùng tính liên tục để chứng minh mốc neo đúng.
    """
    from dataclasses import replace
    q_sai = replace(quy_uoc_mac_dinh(), moc_ngay_can_index=CAN.index("GIAP"))
    # Vẫn liên tục
    a, b = q_sai.can_chi_theo_jdn(2460473), q_sai.can_chi_theo_jdn(2460474)
    assert (CAN.index(b[0]) - CAN.index(a[0])) % 10 == 1
    # Nhưng sai mốc đối chiếu
    assert q_sai.can_chi_theo_jdn(2458511) != ("GIAP", "TY")


def test_trang_thai_hai_quy_tac_trong_kho(db_da_nap):
    conn = db_da_nap
    for ma, mong in (("TIME-0005A", "VERIFIED"), ("TIME-0005B", "VERIFIED")):
        r = conn.execute("SELECT status, confidence FROM rule_versions "
                         "WHERE rule_version_id = ?", (f"{ma}@1",)).fetchone()
        assert r["status"] == mong, f"{ma} đang là {r['status']}"
    # Mốc neo chỉ MEDIUM: việc định niên câu chép là nghiên cứu hiện đại.
    r = conn.execute("SELECT confidence FROM rule_versions "
                     "WHERE rule_version_id = 'TIME-0005B@1'").fetchone()
    assert r["confidence"] == "MEDIUM"


def test_hai_quy_tac_khong_dung_chung_nguon_chinh(db_da_nap):
    """0005A và 0005B phải tựa vào bằng chứng khác nhau, không trộn."""
    conn = db_da_nap
    nguon = {}
    for ma in ("TIME-0005A", "TIME-0005B"):
        rows = conn.execute(
            "SELECT source_id FROM rule_version_sources "
            "WHERE rule_version_id = ? AND source_level = 'PRIMARY'",
            (f"{ma}@1",)).fetchall()
        nguon[ma] = {r["source_id"] for r in rows}
    # Mốc neo phải có thêm bằng chứng thiên văn mà tính liên tục không cần.
    assert "SRC-THIENVAN-NHATTHUC" in nguon["TIME-0005B"]
    assert "SRC-THIENVAN-NHATTHUC" not in nguon["TIME-0005A"]


def test_khong_con_quy_tac_nao_tua_vao_cho_trong_ma_verified(db_da_nap):
    rows = db_da_nap.execute(
        """SELECT rv.rule_id FROM rule_versions rv
             JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
            WHERE rv.status = 'VERIFIED' AND rvs.source_level = 'PRIMARY'
              AND rvs.source_id = 'SRC-CHUA-CO-NGUON'""").fetchall()
    assert rows == [], f"còn quy tắc giả VERIFIED: {[r['rule_id'] for r in rows]}"


# ============ TIME-0006B: trình bằng chứng, chưa đổi trạng thái =====

def test_thang_chiet_tru_co_thu_giai_lai_dung_vi_du():
    """Giải lại ví dụ trong Tam Mệnh Thông Hội: 5 ngày 3 thời -> 1 tuổi 9 tháng."""
    ngay, thoi = 5, 3
    tuoi, du = divmod(ngay, 3)
    thang = du * 4 + (thoi * 10) // 30
    assert (tuoi, thang) == (1, 9)
    # Và con số 630 ngày mà sách nêu.
    assert round((ngay + thoi / 12) / 3 * 360) == 630


def test_0006b_verified_nhung_0006c_van_chua(db_da_nap):
    """Đã tách hai tầng. Tầng có nguồn được VERIFIED, tầng chưa có thì không."""
    conn = db_da_nap
    b = conn.execute("SELECT status, confidence FROM rule_versions "
                     "WHERE rule_version_id='TIME-0006B@1'").fetchone()
    c = conn.execute("SELECT status, confidence FROM rule_versions "
                     "WHERE rule_version_id='TIME-0006C@1'").fetchone()
    assert (b["status"], b["confidence"]) == ("VERIFIED", "MEDIUM")
    assert (c["status"], c["confidence"]) == ("PROVISIONAL", "LOW")

    n = conn.execute("SELECT COUNT(*) AS n FROM rule_version_passages "
                     "WHERE rule_version_id='TIME-0006B@1'").fetchone()["n"]
    assert n == 1, "phải gắn được đoạn nguyên văn Tam Mệnh Thông Hội"
    # 0006C không được mượn đoạn nguyên văn của 0006B.
    n2 = conn.execute("SELECT COUNT(*) AS n FROM rule_version_passages "
                      "WHERE rule_version_id='TIME-0006C@1'").fetchone()["n"]
    assert n2 == 0


def test_engine_khai_bao_ro_ket_qua_dua_tren_quy_tac_nao():
    """Thời điểm khởi vận phải tự khai là chưa xác minh."""
    from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo
    from loi.lich.engine import CalendarEngine
    e = CalendarEngine(tai_bo()["CAL-V1"])
    dv = e.tinh(1990, 2, 4, 12, 0,
                timezone_name="Asia/Ho_Chi_Minh", gioi_tinh="NAM").dai_van
    assert dv.quy_tac_chiet_tru == "TIME-0006B"
    assert dv.quy_tac_ra_ngay == "TIME-0006C"
    assert dv.tuoi_khoi_van_da_xac_minh, "tuổi khởi vận đã có nguồn"
    assert not dv.thoi_diem_khoi_van_da_xac_minh, (
        "thời điểm khởi vận CHƯA có nguồn, không được khai là đã xác minh")


def test_hai_cach_quy_doi_ra_ngay_lech_nhau_that():
    """Ghi lại bằng mã: chọn 360 hay 365,2422 là khác biệt thật, không nhỏ."""
    from loi.lich.dai_van import NGAY_MOT_NAM_DUONG_LICH
    tuoi = 9.8794
    lech = abs(tuoi * NGAY_MOT_NAM_DUONG_LICH - tuoi * 360)
    assert lech > 30, "nếu lệch nhỏ thì tranh luận này không đáng giữ"
