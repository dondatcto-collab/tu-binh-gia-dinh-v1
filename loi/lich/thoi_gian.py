"""Chuẩn hóa thời gian sinh.

Việc duy nhất của tệp này: biến thời gian người dùng nhập thành một mốc
tuyệt đối, và ghi lại đã dùng múi giờ nào.

Không quyết định bất cứ điều gì về đổi ngày hay đổi năm.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from loi.lich.bo_quy_uoc import BoQuyUocLich


class ThoiGianError(Exception):
    pass


@dataclass(frozen=True)
class ThoiDiemChuanHoa:
    thoi_gian_nhap: str          # nguyên văn người dùng nhập
    timezone_name: str | None
    utc_offset_phut: int
    dia_phuong: datetime         # có gắn múi giờ
    utc: datetime
    dung_mui_gio_lich_su: bool
    dung_gio_mat_troi_that: bool
    kinh_do: float | None = None

    @property
    def phut_trong_ngay(self) -> int:
        return self.dia_phuong.hour * 60 + self.dia_phuong.minute


def chuan_hoa(
    bo_lich: BoQuyUocLich,
    nam: int, thang: int, ngay: int, gio: int, phut: int,
    giay: int = 0,
    timezone_name: str | None = None,
    utc_offset_phut: int | None = None,
    kinh_do: float | None = None,
) -> ThoiDiemChuanHoa:
    """Chuẩn hóa một thời điểm theo bộ quy ước lịch đang dùng.

    Bộ quy ước quyết định có tra múi giờ lịch sử hay không, và có dùng
    giờ mặt trời thật hay không. Hàm này chỉ thi hành.
    """
    dung_lich_su = bo_lich.lay_bool("HISTORICAL_TIMEZONE")
    dung_dia_phuong = bo_lich.lay_bool("LOCAL_TIMEZONE")
    dung_mat_troi = bo_lich.lay_bool("TRUE_SOLAR_TIME")

    if dung_mat_troi:
        # Chưa bật ở V1. Không được lặng lẽ bỏ qua.
        raise ThoiGianError(
            "GIO_MAT_TROI_THAT_CHUA_HO_TRO: bộ quy ước bật TRUE_SOLAR_TIME "
            "nhưng Calendar Engine V1 chưa cài đặt phần này"
        )

    tho = datetime(nam, thang, ngay, gio, phut, giay)

    if not dung_dia_phuong:
        tz = timezone.utc
        ten_tz = "UTC"
    elif timezone_name:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as loi:
            raise ThoiGianError(f"MUI_GIO_KHONG_BIET: {timezone_name}") from loi
        ten_tz = timezone_name
    elif utc_offset_phut is not None:
        tz = timezone(timedelta(minutes=utc_offset_phut))
        ten_tz = None
    else:
        raise ThoiGianError("THIEU_MUI_GIO: cần timezone_name hoặc utc_offset_phut")

    dia_phuong = tho.replace(tzinfo=tz)

    if timezone_name and not dung_lich_su:
        # Không tra lịch sử: dùng độ lệch của thời điểm hiện nay.
        lech_bay_gio = datetime.now(ZoneInfo(timezone_name)).utcoffset()
        dia_phuong = tho.replace(tzinfo=timezone(lech_bay_gio))

    lech = dia_phuong.utcoffset()
    if lech is None:
        raise ThoiGianError("KHONG_XAC_DINH_DUOC_DO_LECH")

    return ThoiDiemChuanHoa(
        thoi_gian_nhap=f"{nam:04d}-{thang:02d}-{ngay:02d} {gio:02d}:{phut:02d}:{giay:02d}",
        timezone_name=ten_tz,
        utc_offset_phut=int(lech.total_seconds() // 60),
        dia_phuong=dia_phuong,
        utc=dia_phuong.astimezone(timezone.utc),
        dung_mui_gio_lich_su=dung_lich_su,
        dung_gio_mat_troi_that=dung_mat_troi,
        kinh_do=kinh_do,
    )
