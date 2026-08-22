"""Trụ tháng.

Mốc đổi tháng đọc từ khoá MONTH_BOUNDARY. Can tháng tra bảng Ngũ Hổ Độn
trong tệp cấu hình, không chép cứng ở đây.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from loi.lich.bo_quy_uoc import BoQuyUocLich
from loi.lich.quy_uoc_can_chi import CAN, CHI, QuyUocCanChi
from loi.lich.tiet_khi import BoTinhTietKhi, ViTriTietKhi


class TruThangError(Exception):
    pass


@dataclass(frozen=True)
class TruThang:
    can: str
    chi: str
    tiet_mo_thang: str
    thoi_diem_mo_thang_utc: datetime
    moc_ap_dung: str


def tinh(bo_lich: BoQuyUocLich, quy_uoc: QuyUocCanChi,
         vi_tri: ViTriTietKhi, can_nam: str) -> TruThang:
    moc_quy_uoc = bo_lich.lay("MONTH_BOUNDARY")
    if quy_uoc.anh_xa_moc_doi_thang.get(moc_quy_uoc) != quy_uoc.kind_mo_thang:
        raise TruThangError(
            f"MOC_DOI_THANG_CHUA_HO_TRO: {moc_quy_uoc}. "
            "Không được lặng lẽ dùng mốc khác thay thế."
        )

    mo = vi_tri.jie_truoc
    chi_thang = mo.dinh_nghia.month_branch
    if chi_thang is None:
        raise TruThangError(f"TIET_KHONG_MO_THANG: {mo.dinh_nghia.code}")

    # Can tháng Dần tra theo Can năm, rồi đi tiếp theo số bước từ Dần.
    can_dan = quy_uoc.can_thang_dan(can_nam)
    buoc = (CHI.index(chi_thang) - CHI.index("DAN")) % 12
    can_thang = CAN[(CAN.index(can_dan) + buoc) % 10]

    return TruThang(can=can_thang, chi=chi_thang,
                    tiet_mo_thang=mo.dinh_nghia.code,
                    thoi_diem_mo_thang_utc=mo.thoi_diem_utc,
                    moc_ap_dung=moc_quy_uoc)
