"""Trụ giờ.

Hai ranh giới KHÁC NHAU và không được trộn:
  - ranh giới ngày   : khoá DAY_BOUNDARY;
  - ranh giới chi giờ: mốc bắt đầu giờ Tý trong tệp quy ước Can Chi.

Khi hai ranh giới lệch nhau thì Can giờ lấy theo Can ngày nào là điểm
CÓ TRANH LUẬN. Tệp này không tự quyết; nó đọc khoá HOUR_STEM_LATE_ZI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from loi.lich.bo_quy_uoc import BoQuyUocLich
from loi.lich.can_chi_ngay import TruNgay
from loi.lich.quy_uoc_can_chi import CAN, CHI, QuyUocCanChi


class TruGioError(Exception):
    pass


@dataclass(frozen=True)
class TruGio:
    can: str
    chi: str
    chi_index: int
    can_ngay_dung_de_tra: str
    cach_hieu_gio_ty_dem: str
    nam_trong_phan_ty_truoc_nua_dem: bool


def tinh(bo_lich: BoQuyUocLich, quy_uoc: QuyUocCanChi,
         dia_phuong: datetime, tru_ngay: TruNgay) -> TruGio:
    phut = dia_phuong.hour * 60 + dia_phuong.minute
    moc = quy_uoc.chi_gio_moc_phut
    do_dai = quy_uoc.chi_gio_do_dai_phut

    lech = (phut - moc) % (24 * 60)
    buoc = lech // do_dai
    chi_index = (CHI.index(quy_uoc.chi_gio_dau_tien) + buoc) % 12
    chi_gio = CHI[chi_index]

    # Có đang ở phần giờ Tý nằm trước nửa đêm không?
    trong_ty_dem = chi_index == CHI.index("TY") and phut >= moc

    cach_hieu = bo_lich.lay("HOUR_STEM_LATE_ZI")
    if cach_hieu == "DUNG_CAN_NGAY_HIEN_TAI":
        can_tra = tru_ngay.can
    elif cach_hieu == "DUNG_CAN_NGAY_HOM_SAU":
        if trong_ty_dem and not tru_ngay.da_vuot_moc_doi_ngay:
            can_tra = quy_uoc.can_chi_ngay(
                tru_ngay.ngay_lich_phap + timedelta(days=1))[0]
        else:
            can_tra = tru_ngay.can
    else:
        raise TruGioError(f"CACH_HIEU_GIO_TY_LA: {cach_hieu}")

    can_ty = quy_uoc.can_gio_ty(can_tra)
    can_gio = CAN[(CAN.index(can_ty) + buoc) % 10]

    return TruGio(can=can_gio, chi=chi_gio, chi_index=chi_index,
                  can_ngay_dung_de_tra=can_tra,
                  cach_hieu_gio_ty_dem=cach_hieu,
                  nam_trong_phan_ty_truoc_nua_dem=trong_ty_dem)
