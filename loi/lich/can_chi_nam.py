"""Trụ năm.

Mốc đổi năm KHÔNG do tệp này quyết định. Nó đọc khoá YEAR_BOUNDARY
từ bộ quy ước lịch đang dùng.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from loi.lich.bo_quy_uoc import BoQuyUocLich
from loi.lich.quy_uoc_can_chi import QuyUocCanChi
from loi.lich.tiet_khi import BoTinhTietKhi


class TruNamError(Exception):
    pass


@dataclass(frozen=True)
class TruNam:
    can: str
    chi: str
    nam_can_chi: int              # năm mà chu kỳ Can Chi đang thuộc về
    moc_ap_dung: str              # giá trị YEAR_BOUNDARY đã dùng
    bat_dau_utc: datetime | None  # mốc mở đầu năm Can Chi này
    ket_thuc_utc: datetime | None # mốc mở đầu năm Can Chi kế tiếp

    def cach_moc_gan_nhat(self, moc_utc: datetime):
        """Khoảng cách tới mốc đổi năm gần nhất, dù mốc đó ở trước hay sau."""
        cac_moc = [m for m in (self.bat_dau_utc, self.ket_thuc_utc) if m is not None]
        if not cac_moc:
            return None
        return min(abs((moc_utc - m).total_seconds()) for m in cac_moc)


def tinh(bo_lich: BoQuyUocLich, quy_uoc: QuyUocCanChi,
         bo_tiet: BoTinhTietKhi, moc_utc: datetime) -> TruNam:
    moc_quy_uoc = bo_lich.lay("YEAR_BOUNDARY")

    if moc_quy_uoc in quy_uoc.anh_xa_moc_doi_nam:
        code = quy_uoc.anh_xa_moc_doi_nam[moc_quy_uoc]
        nam_duong = moc_utc.year
        moc_nam_nay = bo_tiet.thoi_diem(nam_duong, code)
        if moc_utc < moc_nam_nay:
            nam_can_chi = nam_duong - 1
            bat_dau = bo_tiet.thoi_diem(nam_can_chi, code)
            ket_thuc = moc_nam_nay
        else:
            nam_can_chi = nam_duong
            bat_dau = moc_nam_nay
            ket_thuc = bo_tiet.thoi_diem(nam_duong + 1, code)
    else:
        raise TruNamError(
            f"MOC_DOI_NAM_CHUA_HO_TRO: {moc_quy_uoc}. "
            "Không được lặng lẽ dùng mốc khác thay thế."
        )

    can, chi = quy_uoc.can_chi_nam(nam_can_chi)
    return TruNam(can=can, chi=chi, nam_can_chi=nam_can_chi,
                  moc_ap_dung=moc_quy_uoc,
                  bat_dau_utc=bat_dau, ket_thuc_utc=ket_thuc)
