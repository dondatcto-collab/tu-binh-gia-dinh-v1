"""Trụ ngày.

Mốc đổi ngày đọc từ khoá DAY_BOUNDARY của bộ quy ước lịch.
Cùng một thời điểm, hai bộ quy ước khác nhau có thể cho hai trụ ngày khác nhau.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from loi.lich.bo_quy_uoc import BoQuyUocLich
from loi.lich.quy_uoc_can_chi import QuyUocCanChi


@dataclass(frozen=True)
class TruNgay:
    can: str
    chi: str
    ngay_lich_phap: date          # ngày mà Can Chi này thuộc về
    ngay_duong_lich: date         # ngày theo lịch thường
    moc_doi_ngay_phut: int
    da_vuot_moc_doi_ngay: bool


def tinh(bo_lich: BoQuyUocLich, quy_uoc: QuyUocCanChi,
         dia_phuong: datetime) -> TruNgay:
    moc_phut = bo_lich.moc_doi_ngay_phut
    phut_hien_tai = dia_phuong.hour * 60 + dia_phuong.minute
    ngay_duong = dia_phuong.date()

    # Mốc 00:00 thì ngày lịch pháp trùng ngày dương lịch.
    # Mốc khác 0 thì từ mốc đó trở đi đã sang ngày lịch pháp kế tiếp.
    vuot = moc_phut > 0 and phut_hien_tai >= moc_phut
    ngay_lich_phap = ngay_duong + timedelta(days=1) if vuot else ngay_duong

    can, chi = quy_uoc.can_chi_ngay(ngay_lich_phap)
    return TruNgay(can=can, chi=chi,
                   ngay_lich_phap=ngay_lich_phap,
                   ngay_duong_lich=ngay_duong,
                   moc_doi_ngay_phut=moc_phut,
                   da_vuot_moc_doi_ngay=vuot)
