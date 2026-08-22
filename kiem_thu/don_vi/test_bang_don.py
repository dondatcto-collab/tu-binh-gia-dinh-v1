"""Test tham số hóa cho hai bảng độn.

Đây là tầng CÀI ĐẶT: kiểm đủ 10 Thiên Can trong bảng triển khai.
Tầng TRI THỨC do ca vàng lo, ở tệp khác.

Bảng mong đợi dưới đây suy thẳng từ nguyên văn cổ thư, không suy từ Engine.
"""

from __future__ import annotations

import pytest

from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN, CHI, quy_uoc_mac_dinh

# --- Suy thẳng từ nguyên văn 五虎遁 --------------------------------
# 甲己之年丙作首 / 乙庚之歲戊為頭 / 丙辛之歲尋庚上 / 丁壬壬位順行流 / 戊癸…甲寅
NGU_HO_TU_NGUYEN_VAN = {
    "GIAP": "BINH", "KY": "BINH",
    "AT": "MAU", "CANH": "MAU",
    "BINH": "CANH", "TAN": "CANH",
    "DINH": "NHAM", "NHAM": "NHAM",
    "MAU": "GIAP", "QUY": "GIAP",
}

# --- Suy thẳng từ nguyên văn 五鼠遁 --------------------------------
# 甲己還加甲 / 乙庚丙作初 / 丙辛從戊起 / 丁壬庚子居 / 戊癸…壬子
NGU_THU_TU_NGUYEN_VAN = {
    "GIAP": "GIAP", "KY": "GIAP",
    "AT": "BINH", "CANH": "BINH",
    "BINH": "MAU", "TAN": "MAU",
    "DINH": "CANH", "NHAM": "CANH",
    "MAU": "NHAM", "QUY": "NHAM",
}

NHOM_TUONG_DUONG = [("GIAP", "KY"), ("AT", "CANH"), ("BINH", "TAN"),
                    ("DINH", "NHAM"), ("MAU", "QUY")]


@pytest.fixture(scope="module")
def q():
    return quy_uoc_mac_dinh()


# ============ Ngũ Hổ Độn: đủ 10 Can ==================================

@pytest.mark.parametrize("can_nam", CAN)
def test_ngu_ho_don_du_10_can(q, can_nam):
    assert q.can_thang_dan(can_nam) == NGU_HO_TU_NGUYEN_VAN[can_nam]


@pytest.mark.parametrize("a,b", NHOM_TUONG_DUONG)
def test_ngu_ho_hai_can_cung_nhom_cho_cung_ket_qua(q, a, b):
    assert q.can_thang_dan(a) == q.can_thang_dan(b)
    assert q.nhom_ngu_ho(a) is q.nhom_ngu_ho(b)


def test_ngu_ho_du_5_nhom_va_moi_nhom_co_nguyen_van(q):
    assert len(q.ngu_ho_don_nhom) == 5
    for n in q.ngu_ho_don_nhom:
        assert len(n.can_nguon) == 2
        assert n.nguyen_van.strip()
        assert n.dich.strip()
    assert len({n.can_dich for n in q.ngu_ho_don_nhom}) == 5


def test_ngu_ho_10_khoa_dung_tu_5_nhom(q):
    assert len(q.ngu_ho_don) == 10
    assert q.ngu_ho_don == NGU_HO_TU_NGUYEN_VAN


# ============ Ngũ Thử Độn: đủ 10 Can =================================

@pytest.mark.parametrize("can_ngay", CAN)
def test_ngu_thu_don_du_10_can(q, can_ngay):
    assert q.can_gio_ty(can_ngay) == NGU_THU_TU_NGUYEN_VAN[can_ngay]


@pytest.mark.parametrize("a,b", NHOM_TUONG_DUONG)
def test_ngu_thu_hai_can_cung_nhom_cho_cung_ket_qua(q, a, b):
    assert q.can_gio_ty(a) == q.can_gio_ty(b)
    assert q.nhom_ngu_thu(a) is q.nhom_ngu_thu(b)


def test_ngu_thu_du_5_nhom_va_moi_nhom_co_nguyen_van(q):
    assert len(q.ngu_thu_don_nhom) == 5
    for n in q.ngu_thu_don_nhom:
        assert len(n.can_nguon) == 2
        assert n.nguyen_van.strip()
    assert len({n.can_dich for n in q.ngu_thu_don_nhom}) == 5


def test_ngu_thu_10_khoa_dung_tu_5_nhom(q):
    assert len(q.ngu_thu_don) == 10
    assert q.ngu_thu_don == NGU_THU_TU_NGUYEN_VAN


# ============ Áp vào Engine thật, đủ 10 Can ==========================

@pytest.mark.parametrize("can_nam", CAN)
def test_engine_dung_dung_can_thang_cho_moi_can_nam(q, can_nam):
    """Với mọi Can năm, Can tháng Engine ra phải khớp công thức suy từ phú."""
    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    # Tìm một năm dương lịch có Can năm cần kiểm, lấy giữa tháng Dần.
    nam = next(y for y in range(1984, 2044) if q.can_chi_nam(y)[0] == can_nam)
    r = e.tinh(nam, 2, 20, 12, 0, timezone_name="Asia/Ho_Chi_Minh", gioi_tinh="NAM")
    assert r.tru_nam.can == can_nam
    assert r.tru_thang.chi == "DAN", "20 tháng 2 phải nằm trong tháng Dần"
    assert r.tru_thang.can == NGU_HO_TU_NGUYEN_VAN[can_nam]


@pytest.mark.parametrize("can_ngay", CAN)
def test_engine_dung_dung_can_gio_cho_moi_can_ngay(q, can_ngay):
    """Với mọi Can ngày, Can giờ Tý sáng sớm phải khớp công thức suy từ phú."""
    from datetime import date, timedelta
    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    d = date(2024, 6, 1)
    while q.can_chi_ngay(d)[0] != can_ngay:
        d += timedelta(days=1)
    # 00:30 nằm trong giờ Tý, và đã qua nửa đêm nên không dính tranh luận TIME-0007.
    r = e.tinh(d.year, d.month, d.day, 0, 30,
               timezone_name="Asia/Ho_Chi_Minh", gioi_tinh="NAM")
    assert r.tru_ngay.can == can_ngay
    assert r.tru_gio.chi == "TY"
    assert r.tru_gio.can == NGU_THU_TU_NGUYEN_VAN[can_ngay]
    assert not r.tru_gio.nam_trong_phan_ty_truoc_nua_dem


def test_can_gio_di_thuan_tu_gio_ty(q):
    """Từ giờ Tý đi thuận qua 12 chi, Can giờ phải bước đều."""
    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    truoc = None
    for gio in range(1, 23, 2):        # 01:00, 03:00, ... đầu mỗi chi
        r = e.tinh(2024, 6, 11, gio, 0,
                   timezone_name="Asia/Ho_Chi_Minh", gioi_tinh="NAM")
        if truoc is not None:
            assert (CAN.index(r.tru_gio.can) - CAN.index(truoc[0])) % 10 == 1
            assert (CHI.index(r.tru_gio.chi) - CHI.index(truoc[1])) % 12 == 1
        truoc = (r.tru_gio.can, r.tru_gio.chi)
