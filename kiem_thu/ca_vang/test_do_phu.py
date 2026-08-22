"""Đo và chốt độ phủ hai bảng độn.

Hai mức khác nhau, không được trộn:

  TẦNG TRI THỨC  — ca vàng phủ được bao nhiêu trên 5 nhóm quy tắc cổ.
  TẦNG CÀI ĐẶT   — test tham số hóa phủ được bao nhiêu trên 10 Thiên Can.

Ca vàng chưa được người duyệt thì KHÔNG tính vào độ phủ tri thức.
"""

from __future__ import annotations

import pytest

from loi.kho_du_lieu import ca_vang
from loi.lich.do_phu import do_phu_ngu_ho, do_phu_ngu_thu
from loi.lich.quy_uoc_can_chi import CAN, quy_uoc_mac_dinh

import kiem_thu.don_vi.test_bang_don as bang_don


# ============ Tầng cài đặt: phải đủ 10 trên 10 ======================

def test_cai_dat_phu_du_10_can_ngu_ho():
    """Test tham số hóa ở test_bang_don.py phải liệt kê đủ 10 Thiên Can."""
    assert set(bang_don.NGU_HO_TU_NGUYEN_VAN) == set(CAN)
    assert len(bang_don.NGU_HO_TU_NGUYEN_VAN) == 10


def test_cai_dat_phu_du_10_can_ngu_thu():
    assert set(bang_don.NGU_THU_TU_NGUYEN_VAN) == set(CAN)
    assert len(bang_don.NGU_THU_TU_NGUYEN_VAN) == 10


def test_cai_dat_phu_du_5_nhom_ca_hai_bang():
    q = quy_uoc_mac_dinh()
    nhom_ho = {n.can_nguon for n in q.ngu_ho_don_nhom}
    nhom_thu = {n.can_nguon for n in q.ngu_thu_don_nhom}
    assert len(nhom_ho) == 5 and len(nhom_thu) == 5
    assert set(bang_don.NHOM_TUONG_DUONG) == {tuple(n) for n in nhom_ho}
    assert set(bang_don.NHOM_TUONG_DUONG) == {tuple(n) for n in nhom_thu}


# ============ Tầng tri thức: đo bằng ca vàng ĐÃ DUYỆT ================

def test_do_phu_tri_thuc_chi_dem_ca_da_duyet():
    """Ca chưa duyệt không được làm đẹp con số độ phủ."""
    tat_ca = [c for c in ca_vang.tai_tat_ca() if c.category == "GOLD-CAL"]
    cho_duyet = [c for c in tat_ca if not c.san_sang_cham]
    assert not cho_duyet, "hiện mọi ca lịch pháp đã được duyệt"
    # Nhưng cơ chế loại ca chưa duyệt vẫn phải còn hiệu lực.
    from loi.lich.do_phu import can_duoc_ca_vang_cham
    from dataclasses import replace
    goc = ca_vang.tai_tat_ca
    try:
        ca_vang.tai_tat_ca = lambda *a, **k: [
            replace(c, review_status="PENDING") for c in goc()]
        can_nam, _ = can_duoc_ca_vang_cham()
        assert can_nam == set(), "ca chưa duyệt vẫn bị tính vào độ phủ"
    finally:
        ca_vang.tai_tat_ca = goc


def test_do_phu_nhom_ngu_ho_da_du_5_tren_5():
    dp = do_phu_ngu_ho()
    assert dp.nhom == "5/5", dp.nhom_da_phu
    assert dp.du_nhom
    assert set(dp.nhom_da_phu) == {"GIAP/KY", "AT/CANH", "BINH/TAN",
                                   "DINH/NHAM", "MAU/QUY"}


def test_do_phu_nhom_ngu_thu_da_du_5_tren_5():
    dp = do_phu_ngu_thu()
    assert dp.nhom == "5/5", dp.nhom_da_phu
    assert dp.du_nhom


def test_do_phu_can_o_tang_ca_vang_van_chua_du_10():
    """Nói thẳng: ca vàng phủ 5/5 NHÓM nhưng mới 6/10 CAN.

    Không sao, vì mỗi nhóm có hai Can cho cùng kết quả — điều đó do test
    tham số hóa chứng minh, không phải việc của ca vàng.
    Test này chốt con số để không ai đọc nhầm 5/5 thành 10/10.
    """
    for dp in (do_phu_ngu_ho(), do_phu_ngu_thu()):
        assert dp.du_nhom, f"{dp.ten_bang} phải đủ nhóm"
        assert not dp.du_can, f"{dp.ten_bang} chưa đủ 10 Can ở tầng ca vàng"
        assert len(dp.can_da_phu) == 6, f"{dp.ten_bang}: {dp.can}"


def test_moi_nhom_deu_co_it_nhat_mot_ca_vang_cham_toi():
    q = quy_uoc_mac_dinh()
    for ten, dp, nhom_ds in (("Ngũ Hổ", do_phu_ngu_ho(), q.ngu_ho_don_nhom),
                             ("Ngũ Thử", do_phu_ngu_thu(), q.ngu_thu_don_nhom)):
        tat_ca_nhom = {"/".join(n.can_nguon) for n in nhom_ds}
        assert set(dp.nhom_da_phu) == tat_ca_nhom, f"{ten} còn thiếu nhóm"


def test_ca_moi_deu_ghi_duong_suy_ra_dap_an():
    """Mỗi ca mới phải cho người duyệt thấy: nguyên văn -> quy tắc -> đáp án."""
    for ma in ("CAL-0003", "CAL-0004", "CAL-0005", "CAL-0006"):
        ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == ma)
        assert ca.review_status == "APPROVED"
        assert ca.reviewed_by, f"{ma} thiếu tên người duyệt"
        for e in ca.expected:
            assert e.source_note, f"{ma}.{e.stage_key} thiếu đường suy ra"
            for tu in ("EXPECTED_DERIVATION", "SOURCE_RULE_ID", "SOURCE_ID"):
                assert tu in e.source_note, f"{ma}.{e.stage_key} thiếu {tu}"
            assert "nguyên văn" in e.source_note
            assert "GHI CHÚ VỀ NỀN TẢNG" in e.source_note, (
                f"{ma}.{e.stage_key} chưa nói rõ đứng trên quy tắc nền nào")
            assert "PROVISIONAL" not in e.source_note.split("GHI CHÚ VỀ NỀN TẢNG")[1], (
                f"{ma}.{e.stage_key} còn ghi chú cũ nói TIME-0005 là PROVISIONAL")


def test_ca_moi_tranh_hoan_toan_khoang_gio_ty_tranh_luan():
    """Ca mới không được chạm vào khoảng giờ còn tranh luận."""
    from datetime import datetime
    for ma in ("CAL-0003", "CAL-0004", "CAL-0005", "CAL-0006"):
        ca = next(c for c in ca_vang.tai_tat_ca() if c.case_id == ma)
        for td in ca.input_payload["cac_thoi_diem"]:
            dt = datetime.fromisoformat(td["dia_phuong"])
            assert dt.hour < 23, f"{ma} chạm vào khoảng tranh luận TIME-0007"
