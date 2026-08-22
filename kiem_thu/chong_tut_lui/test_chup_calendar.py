"""Kiểm thử chống tụt lùi cho Calendar Engine.

ĐỌC KỸ TRƯỚC KHI DÙNG:

Tệp này KHÔNG chứng minh kết quả đúng. Nó chỉ chụp lại kết quả hiện tại và
báo động khi có gì đó đổi mà không ai cố ý đổi.

Lý do phải có nó: bộ kiểm thử đơn vị chỉ kiểm được tính chất cấu trúc, ví dụ
"trụ ngày hôm sau phải cách hôm nay đúng một bước". Nó không kiểm được giá trị
tuyệt đối, vì muốn kiểm giá trị tuyệt đối thì phải có đáp án đã được người duyệt.
Đáp án đó nằm ở ca vàng CAL-0001 và CAL-0002, cả hai đang chờ duyệt.

Nghĩa là: sửa nhầm mốc neo trụ ngày, hoặc sửa nhầm bảng Ngũ Hổ Độn, thì bộ
kiểm thử đơn vị KHÔNG bắt được. Tệp này bắt được.

Khi nào được sửa bảng chụp dưới đây: chỉ khi cố ý đổi quy ước, và phải ghi lý do.
"""

from __future__ import annotations

import pytest

from loi.lich.bo_quy_uoc import tai_tat_ca
from loi.lich.engine import CalendarEngine

TZ = "Asia/Ho_Chi_Minh"

# Bảng chụp ngày 2026-08-21, bộ quy ước GZ-V1, nền astronomy-engine.
# Trạng thái quy ước Can Chi: PROVISIONAL.
BANG_CHUP = {
    ("CAL-V1", 1990, 2, 4, 6, 0): ("KY-TI", "DINH-SUU", "CANH-TY", "KY-MAO"),
    ("CAL-V1", 1990, 2, 4, 12, 0): ("CANH-NGO", "MAU-DAN", "CANH-TY", "NHAM-NGO"),
    ("CAL-V1", 2024, 6, 10, 22, 59): ("GIAP-THIN", "CANH-NGO", "AT-TI", "DINH-HOI"),
    ("CAL-V1", 2024, 6, 10, 23, 0): ("GIAP-THIN", "CANH-NGO", "AT-TI", "BINH-TY"),
    ("CAL-V1", 2024, 6, 11, 0, 0): ("GIAP-THIN", "CANH-NGO", "BINH-NGO", "MAU-TY"),
    ("CAL-V1", 2024, 6, 11, 1, 0): ("GIAP-THIN", "CANH-NGO", "BINH-NGO", "KY-SUU"),
    ("CAL-V1-23H", 2024, 6, 10, 22, 59): ("GIAP-THIN", "CANH-NGO", "AT-TI", "DINH-HOI"),
    ("CAL-V1-23H", 2024, 6, 10, 23, 0): ("GIAP-THIN", "CANH-NGO", "BINH-NGO", "MAU-TY"),
    ("CAL-V1-23H", 2024, 6, 11, 0, 0): ("GIAP-THIN", "CANH-NGO", "BINH-NGO", "MAU-TY"),
}


@pytest.fixture(scope="module")
def engines():
    bo = tai_tat_ca()
    return {k: CalendarEngine(v) for k, v in bo.items()}


@pytest.mark.parametrize("khoa,mong_doi", sorted(BANG_CHUP.items()))
def test_khong_tut_lui(engines, khoa, mong_doi):
    ma_bo, y, m, d, h, mi = khoa
    r = engines[ma_bo].tinh(y, m, d, h, mi, timezone_name=TZ, gioi_tinh="NAM").tom_tat()
    thuc_te = (r["year_pillar"], r["month_pillar"], r["day_pillar"], r["hour_pillar"])
    assert thuc_te == mong_doi, (
        f"{ma_bo} {y}-{m:02d}-{d:02d} {h:02d}:{mi:02d} đổi kết quả. "
        "Nếu đây là thay đổi cố ý thì cập nhật bảng chụp và ghi lý do."
    )


def test_ca_vang_da_thay_the_vai_tro_chinh_cua_bang_chup():
    """Từ khi ca vàng được duyệt, bảng chụp chỉ còn là lưới an toàn.

    Bằng chứng đúng nằm ở ca vàng CAL-0001 và CAL-0002 do người duyệt.
    Bảng chụp chỉ bắt những thay đổi ngoài ý muốn ở vùng ca vàng chưa phủ.
    """
    from loi.kho_du_lieu.ca_vang import tai_tat_ca as tai_ca
    ca_cal = [c for c in tai_ca() if c.category == "GOLD-CAL"]
    da_duyet = [c for c in ca_cal if c.san_sang_cham]
    assert len(da_duyet) >= 2, "phải có ít nhất hai ca lịch pháp đã duyệt"
    for c in da_duyet:
        assert c.reviewed_by, f"{c.case_id} thiếu tên người duyệt"
