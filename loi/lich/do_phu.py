"""Đo độ phủ của hai bảng độn.

Phân biệt hai mức, không được trộn:

  ĐỘ PHỦ NHÓM  — bao nhiêu trên 5 dòng quy tắc cổ được ca vàng chạm tới.
                 Đây là mức TRI THỨC. Ca vàng chịu trách nhiệm mức này.

  ĐỘ PHỦ CAN   — bao nhiêu trên 10 Thiên Can được kiểm trong bảng triển khai.
                 Đây là mức CÀI ĐẶT. Test tham số hóa chịu trách nhiệm mức này.

Ca vàng kiểm quy tắc. Test đơn vị kiểm toàn bảng. Không cái nào thay được cái nào.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from loi.kho_du_lieu import ca_vang
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN, NhomDon, QuyUocCanChi, quy_uoc_mac_dinh


@dataclass(frozen=True)
class DoPhu:
    ten_bang: str
    nhom_da_phu: tuple[str, ...]
    nhom_tong: int
    can_da_phu: tuple[str, ...]
    can_tong: int

    @property
    def nhom(self) -> str:
        return f"{len(self.nhom_da_phu)}/{self.nhom_tong}"

    @property
    def can(self) -> str:
        return f"{len(self.can_da_phu)}/{self.can_tong}"

    @property
    def du_nhom(self) -> bool:
        return len(self.nhom_da_phu) == self.nhom_tong

    @property
    def du_can(self) -> bool:
        return len(self.can_da_phu) == self.can_tong


def _ma_nhom(n: NhomDon) -> str:
    return "/".join(n.can_nguon)


def can_duoc_ca_vang_cham() -> tuple[set[str], set[str]]:
    """Trả về (tập Can năm, tập Can ngày) mà ca vàng ĐÃ DUYỆT chạm tới.

    Chỉ đếm ca đã duyệt. Ca chờ duyệt không được tính vào độ phủ.
    """
    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    can_nam: set[str] = set()
    can_ngay: set[str] = set()
    for ca in ca_vang.tai_tat_ca():
        if ca.category != "GOLD-CAL" or not ca.san_sang_cham:
            continue
        tz = ca.input_payload.get("timezone_name")
        for td in ca.input_payload.get("cac_thoi_diem", []) or []:
            dt = datetime.fromisoformat(td["dia_phuong"])
            r = e.tinh(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                       timezone_name=tz, gioi_tinh="NAM")
            can_nam.add(r.tru_nam.can)
            can_ngay.add(r.tru_ngay.can)
    return can_nam, can_ngay


def do_phu_ngu_ho(quy_uoc: QuyUocCanChi | None = None) -> DoPhu:
    q = quy_uoc or quy_uoc_mac_dinh()
    can_nam, _ = can_duoc_ca_vang_cham()
    nhom = {_ma_nhom(q.nhom_ngu_ho(c)) for c in can_nam}
    return DoPhu("NGU_HO_DON", tuple(sorted(nhom)), len(q.ngu_ho_don_nhom),
                 tuple(sorted(can_nam)), len(CAN))


def do_phu_ngu_thu(quy_uoc: QuyUocCanChi | None = None) -> DoPhu:
    q = quy_uoc or quy_uoc_mac_dinh()
    _, can_ngay = can_duoc_ca_vang_cham()
    nhom = {_ma_nhom(q.nhom_ngu_thu(c)) for c in can_ngay}
    return DoPhu("NGU_THU_DON", tuple(sorted(nhom)), len(q.ngu_thu_don_nhom),
                 tuple(sorted(can_ngay)), len(CAN))


def bao_cao() -> str:
    dong = []
    for dp in (do_phu_ngu_ho(), do_phu_ngu_thu()):
        dong.append(f"{dp.ten_bang}_GROUP_COVERAGE (ca vàng)      = {dp.nhom}")
        dong.append(f"{dp.ten_bang}_STEM_COVERAGE  (ca vàng)      = {dp.can}")
        thieu_nhom = dp.nhom_tong - len(dp.nhom_da_phu)
        if thieu_nhom:
            dong.append(f"   còn thiếu {thieu_nhom} nhóm ở tầng ca vàng")
    return "\n".join(dong)


# ---------------------------------------------------------------
# Đếm bằng chứng: SỐ NGUỒN khác SỐ NHÓM BẰNG CHỨNG ĐỘC LẬP
# ---------------------------------------------------------------

def dem_bang_chung(conn, rule_id: str) -> dict:
    """Đếm nguồn và nhóm bằng chứng độc lập cho một quy tắc.

    Sáu tên nguồn có thể chỉ là hai nhóm bằng chứng. Đếm tên là đếm sai.
    Nhóm NONE (chỗ trống) không được tính vào số nhóm bằng chứng.
    """
    rows = conn.execute(
        """SELECT s.source_id, s.independence_group
             FROM rule_version_sources rvs
             JOIN sources s ON s.source_id = rvs.source_id
            WHERE rvs.rule_version_id = ?""", (f"{rule_id}@1",)).fetchall()
    nhom = {r["independence_group"] for r in rows if r["independence_group"] != "NONE"}
    return {
        "rule_id": rule_id,
        "SOURCE_COUNT": len(rows),
        "INDEPENDENT_EVIDENCE_GROUP_COUNT": len(nhom),
        "groups": tuple(sorted(nhom)),
    }
