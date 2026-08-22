"""Chạy ca vàng đã duyệt bên trong bộ kiểm thử, và đo độ phủ.

Đây là chỗ Engine bị chấm bằng đáp án của người duyệt, không phải bằng
kết quả của chính nó.
"""

from __future__ import annotations

import pytest

from loi.kho_du_lieu import ca_vang
from loi.lich.ca_vang_lich import dang_ky, tinh_ca_lich
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN, quy_uoc_mac_dinh


@pytest.fixture
def da_dang_ky():
    dang_ky()
    yield
    ca_vang.BANG_BO_TINH.pop("GOLD-CAL", None)


def test_ca_vang_lich_phap_dat(db_da_nap, da_dang_ky):
    cac = [c for c in ca_vang.tai_tat_ca() if c.category == "GOLD-CAL"]
    for c in cac:
        ca_vang.dong_bo_vao_db(db_da_nap, c)
    kq = ca_vang.chay(db_da_nap, cac, test_run_id="R-CAL")

    truot = [(cid, ct) for cid, tt, ct in kq.chi_tiet if tt == "FAIL"]
    assert not truot, f"Engine không khớp đáp án đã duyệt: {truot}"
    assert kq.dat == 6
    assert kq.ty_le_dat == 1.0


def test_cal_0001_dat_va_cham_du_bon_lop(db_da_nap, da_dang_ky):
    ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == "CAL-0001")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R-CAL1")
    assert kq.dat == 1
    assert len(ca.dap_an_duoc_cham) == 4
    assert len(ca.dap_an_chua_duyet) == 0


def test_cal_0002_dat_phan_da_duyet_va_bo_qua_phan_tranh_luan(db_da_nap, da_dang_ky):
    ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == "CAL-0002")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R-CAL2")
    assert kq.dat == 1
    assert kq.lop_da_cham == 17
    assert kq.lop_chua_duyet == 2
    conflicted = [e.stage_key for e in ca.dap_an_chua_duyet
                  if e.review_status == "CONFLICTED"]
    assert set(conflicted) == {"CAL-V1:T2300", "CAL-V1:T2359"}


def test_lop_tranh_luan_khong_lam_ca_that_bai(db_da_nap, da_dang_ky):
    """Dù cố tình làm sai phần tranh luận, ca vẫn phải đạt phần đã duyệt."""
    ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == "CAL-0002")
    for e in ca.dap_an_chua_duyet:
        e.payload = {"hour_pillar": "SAI-HOAN-TOAN"}
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R-CAL2B")
    assert kq.dat == 1, "lớp CONFLICTED không được ảnh hưởng tới kết quả chấm"


def test_dung_sai_thoi_diem_tiet_khi_co_hieu_luc(db_da_nap, da_dang_ky):
    """Đáp án tiết khí có dung sai 60 giây. Lệch quá thì phải trượt."""
    ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == "CAL-0001")
    e = next(x for x in ca.expected if x.stage_key.startswith("tiet_khi:"))
    assert e.tolerance_seconds == 60
    e.payload = "1990-02-04T03:14:00Z"          # lệch một tiếng
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R-CAL1C")
    assert kq.truot == 1
    assert "lech" in kq.chi_tiet[0][2]


# --- Độ phủ: nói thật về chỗ ca vàng chưa với tới --------------------

def _can_nam_duoc_cham() -> set[str]:
    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    dung = set()
    for ca in ca_vang.tai_tat_ca():
        if ca.category != "GOLD-CAL" or not ca.san_sang_cham:
            continue
        tz = ca.input_payload.get("timezone_name")
        for td in ca.input_payload.get("cac_thoi_diem", []):
            from datetime import datetime
            dt = datetime.fromisoformat(td["dia_phuong"])
            r = e.tinh(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                       timezone_name=tz, gioi_tinh="NAM")
            dung.add(r.tru_nam.can)
    return dung


def test_do_phu_ngu_ho_don_o_tang_ca_vang():
    """Ca vàng phủ đủ 5 trên 5 NHÓM, nhưng mới 6 trên 10 CAN.

    Không phải thiếu sót. Mỗi nhóm có hai Can cho cùng kết quả; việc chứng minh
    hai Can đó tương đương là của test tham số hóa, không phải của ca vàng.
    Test này chốt con số để không ai đọc 5/5 rồi tưởng là 10/10.
    """
    dung = _can_nam_duoc_cham()
    assert len(dung) == 6, sorted(dung)
    chua = sorted(set(CAN) - dung)
    assert set(chua) == {"AT", "NHAM", "QUY", "TAN"}
    # Bốn Can chưa chạm phải nằm chung nhóm với một Can đã chạm.
    q = quy_uoc_mac_dinh()
    for c in chua:
        cung_nhom = set(q.nhom_ngu_ho(c).can_nguon) - {c}
        assert cung_nhom & dung, f"{c} chưa có Can cùng nhóm nào được ca vàng chạm"


def test_do_phu_ngu_thu_don_con_thieu():
    q = quy_uoc_mac_dinh()
    assert len(q.ngu_thu_don) == 10
    kq = tinh_ca_lich(
        next(c for c in ca_vang.tai_tat_ca() if c.case_id == "CAL-0001").input_payload)
    assert kq, "bộ tính phải trả về kết quả"
    # Ca CAL-0001 chỉ dùng một Can ngày duy nhất là Canh.
    assert len({v for k, v in kq.items() if k.startswith("tru_ngay:")}) == 1
