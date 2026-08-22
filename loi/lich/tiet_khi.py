"""Tính tiết khí.

Phần thiên văn được tách sau một lớp vỏ. Đổi thư viện thì chỉ đổi lớp vỏ,
không đụng tới phần còn lại của hệ thống.

Thư viện chính:   astronomy-engine
Thư viện dự phòng: pymeeus

Hai thư viện này thuần thiên văn. Chúng không biết gì về Bát Tự, nên không
áp đặt quy ước Bát Tự nào lên hệ thống của mình.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from loi.lich.quy_uoc_can_chi import QuyUocCanChi, TietKhiDinhNghia, quy_uoc_mac_dinh


class TietKhiError(Exception):
    pass


class NenThienVan(Protocol):
    ten: str

    def tim_kinh_do(self, kinh_do: float, bat_dau_utc: datetime,
                    so_ngay: float) -> datetime | None:
        """Trả về thời điểm UTC mặt trời đạt kinh độ biểu kiến cho trước."""
        ...


class NenAstronomyEngine:
    ten = "astronomy-engine"

    def tim_kinh_do(self, kinh_do, bat_dau_utc, so_ngay):
        import astronomy
        t0 = astronomy.Time.Make(
            bat_dau_utc.year, bat_dau_utc.month, bat_dau_utc.day,
            bat_dau_utc.hour, bat_dau_utc.minute,
            bat_dau_utc.second + bat_dau_utc.microsecond / 1e6,
        )
        t = astronomy.SearchSunLongitude(float(kinh_do), t0, float(so_ngay))
        if t is None:
            return None
        return t.Utc().replace(tzinfo=timezone.utc)


class NenPyMeeus:
    ten = "pymeeus"

    def tim_kinh_do(self, kinh_do, bat_dau_utc, so_ngay):
        from pymeeus.Epoch import Epoch
        from pymeeus.Sun import Sun

        def kinh_do_tai(jde):
            l, _, _ = Sun.apparent_geocentric_position(Epoch(jde))
            return float(l.to_positive())

        lo = Epoch(bat_dau_utc.year, bat_dau_utc.month,
                   bat_dau_utc.day + bat_dau_utc.hour / 24).jde()
        hi = lo + so_ngay
        for _ in range(90):
            giua = (lo + hi) / 2
            lech = (kinh_do_tai(giua) - kinh_do) % 360
            if lech > 180:
                lech -= 360
            if lech < 0:
                lo = giua
            else:
                hi = giua
        e = Epoch(hi)
        y, m, d = e.get_date()
        nguyen = int(d)
        du = d - nguyen
        kq = datetime(y, m, nguyen, tzinfo=timezone.utc) + timedelta(days=du)
        # Epoch của pymeeus dùng thang TT; đổi về UTC bằng ước lượng thô.
        return kq - timedelta(seconds=_uoc_luong_delta_t(y))


def _uoc_luong_delta_t(nam: int) -> float:
    """Ước lượng TT trừ UTC theo năm. Chỉ dùng cho nền dự phòng."""
    bang = {1900: -2.0, 1950: 29.1, 1980: 50.5, 1990: 56.9,
            2000: 63.8, 2010: 66.1, 2020: 69.4, 2030: 72.0}
    moc = sorted(bang)
    if nam <= moc[0]:
        return bang[moc[0]]
    if nam >= moc[-1]:
        return bang[moc[-1]]
    for a, b in zip(moc, moc[1:]):
        if a <= nam <= b:
            ty = (nam - a) / (b - a)
            return bang[a] + ty * (bang[b] - bang[a])
    return 69.0


NEN_CHINH = NenAstronomyEngine()
NEN_DU_PHONG = NenPyMeeus()


@dataclass(frozen=True)
class MocTietKhi:
    dinh_nghia: TietKhiDinhNghia
    thoi_diem_utc: datetime

    def dia_phuong(self, tz) -> datetime:
        return self.thoi_diem_utc.astimezone(tz)


@dataclass(frozen=True)
class ViTriTietKhi:
    truoc: MocTietKhi          # tiết khí gần nhất đã qua
    sau: MocTietKhi            # tiết khí kế tiếp
    jie_truoc: MocTietKhi      # Tiết mở tháng gần nhất đã qua
    jie_sau: MocTietKhi
    nen_thien_van: str

    def khoang_cach_toi_jie_truoc(self, moc_utc: datetime) -> timedelta:
        return moc_utc - self.jie_truoc.thoi_diem_utc

    def khoang_cach_toi_jie_sau(self, moc_utc: datetime) -> timedelta:
        return self.jie_sau.thoi_diem_utc - moc_utc


class BoTinhTietKhi:
    def __init__(self, quy_uoc: QuyUocCanChi | None = None,
                 nen: NenThienVan | None = None):
        self.quy_uoc = quy_uoc or quy_uoc_mac_dinh()
        self.nen = nen or NEN_CHINH
        self._nho: dict[tuple[int, str], datetime] = {}

    # --- tìm một tiết khí trong một năm -----------------------------
    def thoi_diem(self, nam: int, code: str) -> datetime:
        khoa = (nam, code)
        if khoa in self._nho:
            return self._nho[khoa]
        dn = self.quy_uoc.tiet_theo_ma(code)
        # Bắt đầu dò từ trước thời điểm dự kiến khoảng 25 ngày.
        du_kien = _ngay_du_kien(nam, dn.longitude)
        bat_dau = du_kien - timedelta(days=25)
        kq = self.nen.tim_kinh_do(dn.longitude, bat_dau, 50.0)
        if kq is None:
            raise TietKhiError(f"KHONG_TIM_DUOC_TIET_KHI: {code} năm {nam}")
        self._nho[khoa] = kq
        return kq

    def tat_ca_trong_nam(self, nam: int) -> list[MocTietKhi]:
        kq = [MocTietKhi(dn, self.thoi_diem(nam, dn.code))
              for dn in self.quy_uoc.tiet_khi]
        return sorted(kq, key=lambda m: m.thoi_diem_utc)

    # --- định vị một thời điểm --------------------------------------
    def dinh_vi(self, moc_utc: datetime) -> ViTriTietKhi:
        nam = moc_utc.year
        moc = []
        for n in (nam - 1, nam, nam + 1):
            moc.extend(self.tat_ca_trong_nam(n))
        moc.sort(key=lambda m: m.thoi_diem_utc)

        truoc = [m for m in moc if m.thoi_diem_utc <= moc_utc]
        sau = [m for m in moc if m.thoi_diem_utc > moc_utc]
        if not truoc or not sau:
            raise TietKhiError("NGOAI_KHOANG_TINH_DUOC")

        jie_truoc = [m for m in truoc if self.quy_uoc.la_mo_thang(m.dinh_nghia)]
        jie_sau = [m for m in sau if self.quy_uoc.la_mo_thang(m.dinh_nghia)]
        if not jie_truoc or not jie_sau:
            raise TietKhiError("KHONG_DU_JIE")

        return ViTriTietKhi(
            truoc=truoc[-1], sau=sau[0],
            jie_truoc=jie_truoc[-1], jie_sau=jie_sau[0],
            nen_thien_van=self.nen.ten,
        )


def _ngay_du_kien(nam: int, kinh_do: int) -> datetime:
    """Ngày dự kiến thô của một kinh độ mặt trời. Chỉ để đặt mốc dò."""
    # Kinh độ 315 rơi khoảng đầu tháng 2; 0 độ khoảng 20 tháng 3.
    ngay_trong_nam = ((kinh_do - 280) % 360) * 365.2422 / 360 + 1
    return datetime(nam, 1, 1, tzinfo=timezone.utc) + timedelta(days=ngay_trong_nam)


def doi_chieu_hai_nen(nam: int, code: str,
                      quy_uoc: QuyUocCanChi | None = None) -> tuple[datetime, datetime, float]:
    """Chạy cả hai nền thiên văn và trả về độ lệch tính bằng giây.

    Dùng để kiểm tra độc lập, không dùng trong đường tính chính.
    """
    a = BoTinhTietKhi(quy_uoc, NEN_CHINH).thoi_diem(nam, code)
    b = BoTinhTietKhi(quy_uoc, NEN_DU_PHONG).thoi_diem(nam, code)
    return a, b, abs((a - b).total_seconds())
