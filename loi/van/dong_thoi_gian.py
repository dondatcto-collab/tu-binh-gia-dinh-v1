"""Dòng thời gian: Mệnh gốc → Đại vận → Năm → Tháng.

Tệp này CHỈ dựng dữ liệu có thật từ các quy tắc ĐÃ XÁC MINH.
Nơi nào chưa đủ căn cứ thì trả về UNKNOWN kèm lý do, KHÔNG đoán.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

from loi.bat_tu.nguyet_lenh import tu_ket_qua_lich
from loi.bat_tu.tang_can import lay_tang_can
from loi.bat_tu.thap_than import ap_dung_tu_tru, tinh_thap_than
from loi.ho_so.ho_so import HoSo
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN_VI, CHI_VI, CAN, CHI, viet_hoa


@dataclass
class TruVi:
    can: str
    chi: str

    @property
    def vi(self) -> str:
        return viet_hoa(self.can, self.chi)

    def to_dict(self) -> dict[str, Any]:
        return {"can": self.can, "chi": self.chi, "vi": self.vi}


@dataclass
class VanHienTai:
    thu_tu: int
    can: str
    chi: str
    tuoi_bat_dau: float
    nam_bat_dau: int
    nam_ket_thuc: int
    ngay_bat_dau: str
    ngay_ket_thuc: str
    nam_thu_may: int
    trang_thai_quy_doi: str
    canh_bao: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "thu_tu": self.thu_tu,
            "tru": viet_hoa(self.can, self.chi),
            "nam_bat_dau": self.nam_bat_dau,
            "nam_ket_thuc": self.nam_ket_thuc,
            "ngay_bat_dau": self.ngay_bat_dau,
            "ngay_ket_thuc": self.ngay_ket_thuc,
            "nam_thu_may": self.nam_thu_may,
            "tong_so_nam": 10,
            "trang_thai_quy_doi": self.trang_thai_quy_doi,
            "canh_bao": list(self.canh_bao),
        }


@dataclass
class DongThoiGian:
    profile_id: str
    ho_ten: str
    tu_tru: dict[str, TruVi]
    nhat_chu: str
    thap_than_theo_vi_tri: list[dict[str, Any]]
    nguyet_lenh_menh: dict[str, Any]
    dai_van: VanHienTai | None
    nam_hien_tai: TruVi
    thang_hien_tai: TruVi
    nguyet_lenh_hien_tai: dict[str, Any]
    thap_than_nam: str
    thap_than_thang: str
    rule_trace: list[str]
    source_trace: list[str]
    canh_bao: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "ho_ten": self.ho_ten,
            "tu_tru": {k: v.to_dict() for k, v in self.tu_tru.items()},
            "nhat_chu": self.nhat_chu,
            "nhat_chu_vi": CAN_VI[CAN.index(self.nhat_chu)],
            "thap_than_theo_vi_tri": self.thap_than_theo_vi_tri,
            "nguyet_lenh_menh": self.nguyet_lenh_menh,
            "dai_van": self.dai_van.to_dict() if self.dai_van else None,
            "nam_hien_tai": self.nam_hien_tai.to_dict(),
            "thang_hien_tai": self.thang_hien_tai.to_dict(),
            "nguyet_lenh_hien_tai": self.nguyet_lenh_hien_tai,
            "thap_than_nam": self.thap_than_nam,
            "thap_than_thang": self.thap_than_thang,
            "rule_trace": sorted(set(self.rule_trace)),
            "source_trace": sorted(set(self.source_trace)),
            "canh_bao": list(self.canh_bao),
        }


def _engine() -> CalendarEngine:
    return CalendarEngine(tai_bo_lich()["CAL-V1"])


def dung(conn: sqlite3.Connection, hs: HoSo,
         moc: datetime | None = None) -> DongThoiGian:
    e = _engine()
    if moc is None:
        try:
            moc = datetime.now(ZoneInfo(hs.timezone_name))
        except ZoneInfoNotFoundError:
            moc = datetime.now(timezone.utc)

    lich_sinh = e.tinh(hs.birth_year, hs.birth_month, hs.birth_day,
                       hs.birth_hour, hs.birth_minute,
                       timezone_name=hs.timezone_name, gioi_tinh=hs.gender)
    tu_tru = {
        "nam": TruVi(lich_sinh.tru_nam.can, lich_sinh.tru_nam.chi),
        "thang": TruVi(lich_sinh.tru_thang.can, lich_sinh.tru_thang.chi),
        "ngay": TruVi(lich_sinh.tru_ngay.can, lich_sinh.tru_ngay.chi),
        "gio": TruVi(lich_sinh.tru_gio.can, lich_sinh.tru_gio.chi),
    }
    nhat_chu = lich_sinh.tru_ngay.can

    tt = ap_dung_tu_tru(
        conn, nhat_chu,
        {"YEAR": tu_tru["nam"].can, "MONTH": tu_tru["thang"].can,
         "DAY": tu_tru["ngay"].can, "HOUR": tu_tru["gio"].can},
        {"YEAR": tu_tru["nam"].chi, "MONTH": tu_tru["thang"].chi,
         "DAY": tu_tru["ngay"].chi, "HOUR": tu_tru["gio"].chi})
    tt_ds = [x.to_dict() for x in tt]

    nl_menh = tu_ket_qua_lich(conn, lich_sinh).to_dict()

    canh_bao: list[str] = []
    van = None
    if lich_sinh.dai_van is not None:
        dv = lich_sinh.dai_van
        nam_sinh = hs.birth_year
        hien = None
        moc_utc = moc.astimezone(timezone.utc)
        for v in dv.cac_van:
            nam_bd = v.bat_dau_utc.year
            nam_kt = v.ket_thuc_utc.year
            if v.bat_dau_utc <= moc_utc < v.ket_thuc_utc:
                hien = (v, nam_bd, nam_kt)
                break
        if hien:
            v, nam_bd, nam_kt = hien
            # Không dùng riêng năm dương lịch. “Năm thứ mấy” đổi đúng vào ngày kỷ niệm
            # của mốc giao vận đang dùng, thay vì chia thô theo số ngày trung bình/năm.
            so_nam_da_qua = 0
            for n in range(1, 11):
                try:
                    moc_ky_niem = v.bat_dau_utc.replace(year=v.bat_dau_utc.year + n)
                except ValueError:  # 29/02 -> 28/02 ở năm không nhuận
                    moc_ky_niem = v.bat_dau_utc.replace(year=v.bat_dau_utc.year + n, day=28)
                if moc_utc >= moc_ky_niem:
                    so_nam_da_qua = n
                else:
                    break
            van = VanHienTai(
                thu_tu=v.thu_tu, can=v.can, chi=v.chi,
                tuoi_bat_dau=v.tuoi_bat_dau,
                nam_bat_dau=nam_bd, nam_ket_thuc=nam_kt,
                ngay_bat_dau=v.bat_dau_utc.date().isoformat(),
                ngay_ket_thuc=v.ket_thuc_utc.date().isoformat(),
                nam_thu_may=max(1, min(10, so_nam_da_qua + 1)),
                trang_thai_quy_doi=dv.trang_thai_ra_ngay,
                canh_bao=["Mốc chuyển vận tính theo TIME-0006C, quy tắc này "
                          "CHƯA có nguồn. Sai số có thể tới vài tháng."],
            )
        else:
            canh_bao.append("Thời điểm hiện tại nằm ngoài mười vận đã tính.")

    lich_moc = e.tinh(moc.year, moc.month, moc.day, 12, 0,
                      timezone_name=hs.timezone_name, gioi_tinh=hs.gender,
                      tinh_dai_van=False)
    nam_ht = TruVi(lich_moc.tru_nam.can, lich_moc.tru_nam.chi)
    thang_ht = TruVi(lich_moc.tru_thang.can, lich_moc.tru_thang.chi)
    nl_ht = tu_ket_qua_lich(conn, lich_moc).to_dict()

    tt_nam = tinh_thap_than(conn, nhat_chu, nam_ht.can)
    tt_thang = tinh_thap_than(conn, nhat_chu, thang_ht.can)

    rule = ["TIME-0001", "TIME-0002", "TIME-0003", "TIME-0004",
            "TIME-0005A", "TIME-0005B", "TIME-0006", tt_nam.rule_id, tt_thang.rule_id]
    rule += [x["rule_id"] for x in tt_ds if x.get("rule_id")]
    rule += nl_menh["rule_ids"] + nl_ht["rule_ids"]
    if van:
        rule.append("TIME-0006C")

    return DongThoiGian(
        profile_id=hs.profile_id, ho_ten=hs.full_name,
        tu_tru=tu_tru, nhat_chu=nhat_chu,
        thap_than_theo_vi_tri=tt_ds,
        nguyet_lenh_menh=nl_menh,
        dai_van=van,
        nam_hien_tai=nam_ht, thang_hien_tai=thang_ht,
        nguyet_lenh_hien_tai=nl_ht,
        thap_than_nam=tt_nam.ten_god_vi,
        thap_than_thang=tt_thang.ten_god_vi,
        rule_trace=rule,
        source_trace=["SRC-VSOP87-AE", "SRC-UHTB-CHEP",
                      "SRC-XUANTHU-NHATTHUC", "SRC-TMTH-CHEP"],
        canh_bao=canh_bao,
    )
