"""Bộ nạp quy ước Can Chi.

Toàn bộ bảng tra nằm ở tệp cấu hình. Tệp này chỉ đọc và kiểm tra.
Không có bảng nào được chép cứng vào đây.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml

from loi.nen.phien_ban import GOC_DU_AN

THU_MUC_CAN_CHI = GOC_DU_AN / "cau_hinh" / "can_chi"

CAN = ("GIAP", "AT", "BINH", "DINH", "MAU", "KY", "CANH", "TAN", "NHAM", "QUY")
CHI = ("TY", "SUU", "DAN", "MAO", "THIN", "TI", "NGO", "MUI", "THAN", "DAU", "TUAT", "HOI")

def jdn_tu_ngay_duong(ngay: date) -> int:
    """Đổi ngày dương lịch (lịch Gregory) sang số ngày Julius."""
    y, m, d = ngay.year, ngay.month, ngay.day
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def jdn_tu_ngay_julius(y: int, m: int, d: int) -> int:
    """Đổi ngày lịch Julius sang số ngày Julius. Dùng cho mốc cổ."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - 32083


CAN_VI = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")
CHI_VI = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")


class QuyUocCanChiError(Exception):
    pass


@dataclass(frozen=True)
class NhomDon:
    """Một dòng quy tắc trong bài phú độn. Hai Can trong nhóm cho cùng kết quả."""
    can_nguon: tuple[str, ...]
    can_dich: str
    nguyen_van: str
    dich: str


@dataclass(frozen=True)
class TietKhiDinhNghia:
    code: str
    name_vi: str
    name_original: str
    longitude: int
    kind: str                 # JIE hoặc QI
    month_branch: str | None  # chi tháng mà tiết này mở ra


@dataclass(frozen=True)
class QuyUocCanChi:
    ruleset_id: str
    version: str
    status: str
    tiet_khi: tuple[TietKhiDinhNghia, ...]
    moc_nam: int
    ngu_ho_don_nhom: tuple[NhomDon, ...]
    ngu_thu_don_nhom: tuple[NhomDon, ...]
    moc_ngay_jdn: int
    moc_ngay_can_index: int
    moc_ngay_chi_index: int
    chi_gio_moc_phut: int
    chi_gio_do_dai_phut: int
    chi_gio_dau_tien: str
    kind_mo_thang: str
    anh_xa_moc_doi_nam: dict[str, str]
    anh_xa_moc_doi_thang: dict[str, str]

    # --- tra cứu ----------------------------------------------------
    @property
    def cac_jie(self) -> tuple[TietKhiDinhNghia, ...]:
        return tuple(t for t in self.tiet_khi if self.la_mo_thang(t))

    def la_mo_thang(self, t: TietKhiDinhNghia) -> bool:
        return t.kind == self.kind_mo_thang

    def tiet_theo_ma(self, code: str) -> TietKhiDinhNghia:
        for t in self.tiet_khi:
            if t.code == code:
                return t
        raise QuyUocCanChiError(f"KHONG_CO_TIET_KHI: {code}")

    # 10 khóa tra cứu do mã dựng từ 5 nhóm, không liệt kê tay.
    @property
    def ngu_ho_don(self) -> dict[str, str]:
        return _bang_tu_nhom(self.ngu_ho_don_nhom)

    @property
    def ngu_thu_don(self) -> dict[str, str]:
        return _bang_tu_nhom(self.ngu_thu_don_nhom)

    def nhom_ngu_ho(self, can_nam: str) -> NhomDon:
        for n in self.ngu_ho_don_nhom:
            if can_nam in n.can_nguon:
                return n
        raise QuyUocCanChiError(f"NGU_HO_DON_THIEU: {can_nam}")

    def nhom_ngu_thu(self, can_ngay: str) -> NhomDon:
        for n in self.ngu_thu_don_nhom:
            if can_ngay in n.can_nguon:
                return n
        raise QuyUocCanChiError(f"NGU_THU_DON_THIEU: {can_ngay}")

    def can_thang_dan(self, can_nam: str) -> str:
        return self.nhom_ngu_ho(can_nam).can_dich

    def can_gio_ty(self, can_ngay: str) -> str:
        return self.nhom_ngu_thu(can_ngay).can_dich

    def can_chi_ngay(self, ngay: date) -> tuple[str, str]:
        return self.can_chi_theo_jdn(jdn_tu_ngay_duong(ngay))

    def can_chi_theo_jdn(self, jdn: int) -> tuple[str, str]:
        """Tra Can Chi từ số ngày Julius. Đây là đường đi chính.

        Số ngày Julius không phụ thuộc loại lịch nào, nên dùng được cho cả
        mốc năm 720 trước Công nguyên lẫn ngày hôm nay.
        """
        lech = jdn - self.moc_ngay_jdn
        return (CAN[(self.moc_ngay_can_index + lech) % 10],
                CHI[(self.moc_ngay_chi_index + lech) % 12])

    def can_chi_nam(self, nam: int) -> tuple[str, str]:
        return (CAN[(nam - self.moc_nam) % 10], CHI[(nam - self.moc_nam) % 12])


def _bang_tu_nhom(nhom: tuple[NhomDon, ...]) -> dict[str, str]:
    return {c: n.can_dich for n in nhom for c in n.can_nguon}


def _doc_nhom(raw: dict, khoa_nguon: str, khoa_dich: str, ten: str) -> tuple[NhomDon, ...]:
    nhom = tuple(
        NhomDon(
            can_nguon=tuple(x[khoa_nguon]),
            can_dich=x[khoa_dich],
            nguyen_van=x["nguyen_van"],
            dich=x["dich"],
        )
        for x in raw["nhom"]
    )
    if len(nhom) != 5:
        raise QuyUocCanChiError(f"{ten}_SO_NHOM_SAI: cần 5, đang có {len(nhom)}")
    phu = [c for n in nhom for c in n.can_nguon]
    if sorted(phu) != sorted(CAN):
        raise QuyUocCanChiError(f"{ten}_KHONG_PHU_DU_10_CAN: {sorted(phu)}")
    for n in nhom:
        if len(n.can_nguon) != 2:
            raise QuyUocCanChiError(f"{ten}_NHOM_PHAI_CO_2_CAN: {n.can_nguon}")
        if n.can_dich not in CAN:
            raise QuyUocCanChiError(f"{ten}_GIA_TRI_LA: {n.can_dich}")
        if not n.nguyen_van.strip() or not n.dich.strip():
            raise QuyUocCanChiError(f"{ten}_THIEU_NGUYEN_VAN: {n.can_nguon}")
    if len({n.can_dich for n in nhom}) != 5:
        raise QuyUocCanChiError(f"{ten}_TRUNG_CAN_DICH")
    return nhom


def tai_quy_uoc(duong_dan: Path | None = None) -> QuyUocCanChi:
    duong_dan = duong_dan or (THU_MUC_CAN_CHI / "quy_uoc_can_chi.yaml")
    raw = yaml.safe_load(duong_dan.read_text(encoding="utf-8"))

    tiet = tuple(
        TietKhiDinhNghia(
            code=t["code"], name_vi=t["name_vi"], name_original=t["name_original"],
            longitude=int(t["longitude"]), kind=t["kind"],
            month_branch=t.get("month_branch"),
        )
        for t in raw["tiet_khi"]
    )
    if len(tiet) != 24:
        raise QuyUocCanChiError(f"SO_TIET_KHI_SAI: cần 24, đang có {len(tiet)}")
    kind_mo = raw["kind_mo_thang"]
    jie = [t for t in tiet if t.kind == kind_mo]
    if len(jie) != 12:
        raise QuyUocCanChiError(f"SO_JIE_SAI: cần 12, đang có {len(jie)}")
    if len({t.month_branch for t in jie}) != 12:
        raise QuyUocCanChiError("JIE_TRUNG_CHI_THANG")
    if sorted(t.longitude for t in tiet) != sorted(range(0, 360, 15)):
        raise QuyUocCanChiError("KINH_DO_TIET_KHI_KHONG_DEU")

    ho = _doc_nhom(raw["ngu_ho_don"], "can_nam", "can_thang_dan", "NGU_HO_DON")
    thu = _doc_nhom(raw["ngu_thu_don"], "can_ngay", "can_gio_ty", "NGU_THU_DON")

    moc = raw["tru_ngay"]["moc"]
    if moc["can"] not in CAN or moc["chi"] not in CHI:
        raise QuyUocCanChiError("MOC_NGAY_SAI")
    if not isinstance(moc.get("jdn"), int):
        raise QuyUocCanChiError("MOC_NGAY_THIEU_JDN")

    cg = raw["chi_gio"]
    if cg["do_dai_phut"] * 12 != 24 * 60:
        raise QuyUocCanChiError("DO_DAI_CHI_GIO_SAI")

    return QuyUocCanChi(
        ruleset_id=raw["ruleset_id"],
        version=str(raw["version"]),
        status=raw["status"],
        tiet_khi=tiet,
        moc_nam=int(raw["tru_nam"]["moc_nam"]),
        ngu_ho_don_nhom=ho,
        ngu_thu_don_nhom=thu,
        moc_ngay_jdn=int(moc["jdn"]),
        moc_ngay_can_index=CAN.index(moc["can"]),
        moc_ngay_chi_index=CHI.index(moc["chi"]),
        chi_gio_moc_phut=int(cg["moc_bat_dau_phut"]),
        chi_gio_do_dai_phut=int(cg["do_dai_phut"]),
        chi_gio_dau_tien=cg["chi_dau_tien"],
        kind_mo_thang=kind_mo,
        anh_xa_moc_doi_nam=dict(raw["anh_xa_moc_doi_nam"]),
        anh_xa_moc_doi_thang=dict(raw["anh_xa_moc_doi_thang"]),
    )


@lru_cache(maxsize=4)
def quy_uoc_mac_dinh() -> QuyUocCanChi:
    return tai_quy_uoc()


def viet_hoa(can: str, chi: str) -> str:
    return f"{CAN_VI[CAN.index(can)]} {CHI_VI[CHI.index(chi)]}"
