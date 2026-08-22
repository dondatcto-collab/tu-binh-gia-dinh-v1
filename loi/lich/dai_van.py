"""Mốc Đại vận — chỉ phần lịch pháp.

Tệp này KHÔNG luận ý nghĩa Đại vận. Nó chỉ trả lời bốn câu hỏi đo đếm được:
  đi thuận hay đi nghịch;
  đếm tới tiết nào;
  khởi vận lúc mấy tuổi;
  mỗi vận kéo dài từ ngày nào tới ngày nào.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from loi.lich.can_chi_nam import TruNam
from loi.lich.can_chi_thang import TruThang
from loi.lich.quy_uoc_can_chi import CAN, CHI, QuyUocCanChi
from loi.lich.tiet_khi import BoTinhTietKhi, ViTriTietKhi

# --- Hai tầng quy đổi, đứng trên hai quy tắc khác nhau ---------------
# TIME-0006B: chiết trừ ra TUỔI khởi vận. Đã có nguồn Tam Mệnh Thông Hội.
NGAY_DOI_MOT_NAM = 3.0
QUY_TAC_CHIET_TRU = "TIME-0006B"
TRANG_THAI_CHIET_TRU = "VERIFIED"

# TIME-0006C: đổi tuổi đó thành một NGÀY DƯƠNG LỊCH. CHƯA có nguồn.
# Con số dưới đây là lựa chọn của tôi, không phải của sách.
NGAY_MOT_NAM_DUONG_LICH = 365.2422
QUY_TAC_RA_NGAY = "TIME-0006C"
TRANG_THAI_RA_NGAY = "PROVISIONAL"

# Giữ tên cũ để phần khác không vỡ, nhưng nó chỉ nói về tầng chiết trừ.
TRANG_THAI_QUY_DOI = TRANG_THAI_CHIET_TRU


@dataclass(frozen=True)
class MotVan:
    thu_tu: int
    can: str
    chi: str
    tuoi_bat_dau: float
    bat_dau_utc: datetime
    ket_thuc_utc: datetime


@dataclass(frozen=True)
class MocDaiVan:
    chieu: str                     # THUAN hoặc NGHICH
    can_nam: str
    gioi_tinh: str
    tiet_muc_tieu: str
    thoi_diem_tiet_muc_tieu_utc: datetime
    so_ngay_toi_tiet: float
    tuoi_khoi_van: float
    thoi_diem_khoi_van_utc: datetime
    trang_thai_quy_doi: str


    @property
    def thoi_diem_khoi_van_da_xac_minh(self) -> bool:
        """Thời điểm khởi vận CHƯA xác minh, vì nó đứng trên TIME-0006C."""
        return self.trang_thai_ra_ngay == "VERIFIED"

    @property
    def tuoi_khoi_van_da_xac_minh(self) -> bool:
        return self.trang_thai_chiet_tru == "VERIFIED"
    cac_van: tuple[MotVan, ...]

    # Khai báo rõ mỗi con số đứng trên quy tắc nào và quy tắc đó chắc tới đâu.
    quy_tac_chiet_tru: str = QUY_TAC_CHIET_TRU
    trang_thai_chiet_tru: str = TRANG_THAI_CHIET_TRU
    quy_tac_ra_ngay: str = QUY_TAC_RA_NGAY
    trang_thai_ra_ngay: str = TRANG_THAI_RA_NGAY


def _duong_can(can: str) -> bool:
    return CAN.index(can) % 2 == 0


def tinh(quy_uoc: QuyUocCanChi, bo_tiet: BoTinhTietKhi,
         vi_tri: ViTriTietKhi, tru_nam: TruNam, tru_thang: TruThang,
         moc_utc: datetime, gioi_tinh: str, so_van: int = 10) -> MocDaiVan:
    if gioi_tinh not in ("NAM", "NU"):
        raise ValueError(f"GIOI_TINH_LA: {gioi_tinh}")

    # Dương nam và Âm nữ đi thuận. Âm nam và Dương nữ đi nghịch.
    duong = _duong_can(tru_nam.can)
    thuan = (duong and gioi_tinh == "NAM") or (not duong and gioi_tinh == "NU")
    chieu = "THUAN" if thuan else "NGHICH"

    if thuan:
        muc_tieu = vi_tri.jie_sau
        khoang = muc_tieu.thoi_diem_utc - moc_utc
    else:
        muc_tieu = vi_tri.jie_truoc
        khoang = moc_utc - muc_tieu.thoi_diem_utc

    so_ngay = khoang.total_seconds() / 86400.0
    tuoi_khoi = so_ngay / NGAY_DOI_MOT_NAM
    khoi_van = moc_utc + timedelta(days=tuoi_khoi * NGAY_MOT_NAM_DUONG_LICH)

    cac_van = []
    can_i, chi_i = CAN.index(tru_thang.can), CHI.index(tru_thang.chi)
    for k in range(1, so_van + 1):
        buoc = k if thuan else -k
        cac_van.append(MotVan(
            thu_tu=k,
            can=CAN[(can_i + buoc) % 10],
            chi=CHI[(chi_i + buoc) % 12],
            tuoi_bat_dau=tuoi_khoi + (k - 1) * 10,
            bat_dau_utc=khoi_van + timedelta(days=(k - 1) * 10 * NGAY_MOT_NAM_DUONG_LICH),
            ket_thuc_utc=khoi_van + timedelta(days=k * 10 * NGAY_MOT_NAM_DUONG_LICH),
        ))

    return MocDaiVan(
        chieu=chieu,
        can_nam=tru_nam.can,
        gioi_tinh=gioi_tinh,
        tiet_muc_tieu=muc_tieu.dinh_nghia.code,
        thoi_diem_tiet_muc_tieu_utc=muc_tieu.thoi_diem_utc,
        so_ngay_toi_tiet=so_ngay,
        tuoi_khoi_van=tuoi_khoi,
        thoi_diem_khoi_van_utc=khoi_van,
        trang_thai_quy_doi=TRANG_THAI_CHIET_TRU,
        cac_van=tuple(cac_van),
    )
