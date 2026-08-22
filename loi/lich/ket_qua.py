"""Kết quả của Calendar Engine, kèm cảnh báo ranh giới và dấu vết phiên bản."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta

from loi.lich.can_chi_gio import TruGio
from loi.lich.can_chi_ngay import TruNgay
from loi.lich.can_chi_nam import TruNam
from loi.lich.can_chi_thang import TruThang
from loi.lich.dai_van import MocDaiVan
from loi.lich.quy_uoc_can_chi import viet_hoa
from loi.lich.thoi_gian import ThoiDiemChuanHoa
from loi.lich.tiet_khi import ViTriTietKhi

# Sát ranh giới nghĩa là cách mốc không quá bấy nhiêu phút.
NGUONG_CANH_BAO_PHUT = 30


@dataclass(frozen=True)
class CanhBaoRanhGioi:
    ma: str
    ly_do: str
    cach_moc_phut: float | None = None


@dataclass
class KetQuaLich:
    # dấu vết
    ruleset_id: str
    ruleset_version: str
    ganzhi_ruleset_id: str
    ganzhi_ruleset_version: str
    engine_version: str
    boundary_rule: dict[str, str]
    nen_thien_van: str
    calculation_timestamp: str

    # dữ liệu
    thoi_diem: ThoiDiemChuanHoa
    vi_tri_tiet_khi: ViTriTietKhi
    tru_nam: TruNam
    tru_thang: TruThang
    tru_ngay: TruNgay
    tru_gio: TruGio
    dai_van: MocDaiVan | None

    canh_bao: list[CanhBaoRanhGioi] = field(default_factory=list)

    @property
    def boundary_warning(self) -> bool:
        return bool(self.canh_bao)

    @property
    def tu_tru_vi(self) -> str:
        return " | ".join([
            viet_hoa(self.tru_nam.can, self.tru_nam.chi),
            viet_hoa(self.tru_thang.can, self.tru_thang.chi),
            viet_hoa(self.tru_ngay.can, self.tru_ngay.chi),
            viet_hoa(self.tru_gio.can, self.tru_gio.chi),
        ])

    def tom_tat(self) -> dict:
        return {
            "ruleset_id": self.ruleset_id,
            "ruleset_version": self.ruleset_version,
            "boundary_rule": self.boundary_rule,
            "engine_version": self.engine_version,
            "nen_thien_van": self.nen_thien_van,
            "year_pillar": f"{self.tru_nam.can}-{self.tru_nam.chi}",
            "month_pillar": f"{self.tru_thang.can}-{self.tru_thang.chi}",
            "day_pillar": f"{self.tru_ngay.can}-{self.tru_ngay.chi}",
            "hour_pillar": f"{self.tru_gio.can}-{self.tru_gio.chi}",
            "boundary_warning": self.boundary_warning,
            "warnings": [c.ma for c in self.canh_bao],
        }


def dung_canh_bao(thoi_diem: ThoiDiemChuanHoa, vi_tri: ViTriTietKhi,
                  tru_nam: TruNam, tru_ngay: TruNgay, tru_gio: TruGio,
                  chi_gio_moc_phut: int, chi_gio_do_dai_phut: int,
                  nguong_phut: int = NGUONG_CANH_BAO_PHUT) -> list[CanhBaoRanhGioi]:
    kq: list[CanhBaoRanhGioi] = []
    moc_utc = thoi_diem.utc

    def phut(td: timedelta) -> float:
        return abs(td.total_seconds()) / 60.0

    # Sát mốc đổi năm, xét cả mốc phía trước lẫn mốc phía sau.
    cach = tru_nam.cach_moc_gan_nhat(moc_utc)
    if cach is not None:
        d = cach / 60.0
        if d <= nguong_phut:
            kq.append(CanhBaoRanhGioi(
                "SAT_MOC_DOI_NAM",
                "Sát mốc đổi năm. Lệch vài phút có thể đổi cả trụ năm và trụ tháng.",
                d))

    # Sát Tiết mở tháng, cả phía trước lẫn phía sau.
    for nhan, moc in (("TRUOC", vi_tri.jie_truoc), ("SAU", vi_tri.jie_sau)):
        d = phut(moc_utc - moc.thoi_diem_utc)
        if d <= nguong_phut:
            kq.append(CanhBaoRanhGioi(
                "SAT_MOC_DOI_THANG",
                f"Sát {moc.dinh_nghia.name_vi} ({nhan}). Lệch vài phút có thể đổi trụ tháng.",
                d))

    # Sát mốc đổi ngày của bộ quy ước đang dùng.
    phut_ngay = thoi_diem.phut_trong_ngay
    cach_moc_ngay = min(
        abs(phut_ngay - tru_ngay.moc_doi_ngay_phut),
        1440 - abs(phut_ngay - tru_ngay.moc_doi_ngay_phut),
    )
    if cach_moc_ngay <= nguong_phut:
        kq.append(CanhBaoRanhGioi(
            "SAT_MOC_DOI_NGAY",
            "Sát mốc đổi ngày của bộ quy ước đang dùng.", cach_moc_ngay))

    # Sát mốc nửa đêm, kể cả khi bộ quy ước không đổi ngày ở đó.
    cach_nua_dem = min(phut_ngay, 1440 - phut_ngay)
    if cach_nua_dem <= nguong_phut and tru_ngay.moc_doi_ngay_phut != 0:
        kq.append(CanhBaoRanhGioi(
            "SAT_NUA_DEM",
            "Sát nửa đêm. Bộ quy ước khác có thể đổi ngày tại đây.", cach_nua_dem))

    # Sát mốc 23 giờ, kể cả khi bộ quy ước không đổi ngày ở đó.
    cach_moc_ty = min(abs(phut_ngay - chi_gio_moc_phut),
                      1440 - abs(phut_ngay - chi_gio_moc_phut))
    if cach_moc_ty <= nguong_phut and tru_ngay.moc_doi_ngay_phut != chi_gio_moc_phut:
        kq.append(CanhBaoRanhGioi(
            "SAT_MOC_GIO_TY",
            "Sát mốc bắt đầu giờ Tý. Bộ quy ước khác có thể đổi ngày tại đây.",
            cach_moc_ty))

    # Sát đầu hoặc cuối một chi giờ.
    lech_trong_chi = (phut_ngay - chi_gio_moc_phut) % chi_gio_do_dai_phut
    cach_bien_chi = min(lech_trong_chi, chi_gio_do_dai_phut - lech_trong_chi)
    if cach_bien_chi <= nguong_phut:
        kq.append(CanhBaoRanhGioi(
            "SAT_BIEN_CHI_GIO",
            "Sát đầu hoặc cuối một chi giờ.", cach_bien_chi))

    # Giờ Tý phần trước nửa đêm: chỗ hai trường phái hiểu khác nhau.
    if tru_gio.nam_trong_phan_ty_truoc_nua_dem:
        kq.append(CanhBaoRanhGioi(
            "GIO_TY_TRUOC_NUA_DEM",
            f"Đang ở phần giờ Tý trước nửa đêm. Cách hiểu đang dùng: "
            f"{tru_gio.cach_hieu_gio_ty_dem}. Đây là điểm có tranh luận."))

    return kq
