"""Calendar Engine — nơi ghép các mảnh lại.

Engine không tự quyết bất cứ mốc nào. Mọi mốc đến từ BoQuyUocLich
và từ tệp quy ước Can Chi.
"""

from __future__ import annotations

from datetime import datetime, timezone

from loi.lich import can_chi_gio, can_chi_ngay, can_chi_nam, can_chi_thang, dai_van
from loi.lich.bo_quy_uoc import BoQuyUocLich
from loi.lich.ket_qua import KetQuaLich, dung_canh_bao
from loi.lich.quy_uoc_can_chi import QuyUocCanChi, quy_uoc_mac_dinh
from loi.lich.thoi_gian import chuan_hoa
from loi.lich.tiet_khi import BoTinhTietKhi
from loi.nen.phien_ban import ENGINE_VERSION


class CalendarEngine:
    def __init__(self, bo_lich: BoQuyUocLich,
                 quy_uoc: QuyUocCanChi | None = None,
                 bo_tiet: BoTinhTietKhi | None = None):
        self.bo_lich = bo_lich
        self.quy_uoc = quy_uoc or quy_uoc_mac_dinh()
        self.bo_tiet = bo_tiet or BoTinhTietKhi(self.quy_uoc)

        khai_bao = bo_lich.lay("GANZHI_RULESET")
        if khai_bao != self.quy_uoc.ruleset_id:
            raise ValueError(
                f"QUY_UOC_CAN_CHI_KHONG_KHOP: bộ lịch khai {khai_bao}, "
                f"đang nạp {self.quy_uoc.ruleset_id}"
            )

    def tinh(self, nam: int, thang: int, ngay: int, gio: int, phut: int,
             giay: int = 0, timezone_name: str | None = None,
             utc_offset_phut: int | None = None,
             gioi_tinh: str | None = None,
             tinh_dai_van: bool = True) -> KetQuaLich:

        thoi_diem = chuan_hoa(self.bo_lich, nam, thang, ngay, gio, phut, giay,
                              timezone_name=timezone_name,
                              utc_offset_phut=utc_offset_phut)

        vi_tri = self.bo_tiet.dinh_vi(thoi_diem.utc)

        tn = can_chi_nam.tinh(self.bo_lich, self.quy_uoc, self.bo_tiet, thoi_diem.utc)
        tt = can_chi_thang.tinh(self.bo_lich, self.quy_uoc, vi_tri, tn.can)
        tg_ngay = can_chi_ngay.tinh(self.bo_lich, self.quy_uoc, thoi_diem.dia_phuong)
        tg_gio = can_chi_gio.tinh(self.bo_lich, self.quy_uoc,
                                  thoi_diem.dia_phuong, tg_ngay)

        dv = None
        if tinh_dai_van and gioi_tinh:
            dv = dai_van.tinh(self.quy_uoc, self.bo_tiet, vi_tri, tn, tt,
                              thoi_diem.utc, gioi_tinh)

        canh_bao = dung_canh_bao(
            thoi_diem, vi_tri, tn, tg_ngay, tg_gio,
            self.quy_uoc.chi_gio_moc_phut, self.quy_uoc.chi_gio_do_dai_phut)

        return KetQuaLich(
            ruleset_id=self.bo_lich.calendar_ruleset_id,
            ruleset_version=self.bo_lich.version,
            ganzhi_ruleset_id=self.quy_uoc.ruleset_id,
            ganzhi_ruleset_version=self.quy_uoc.version,
            engine_version=ENGINE_VERSION,
            boundary_rule={
                "YEAR_BOUNDARY": self.bo_lich.lay("YEAR_BOUNDARY"),
                "MONTH_BOUNDARY": self.bo_lich.lay("MONTH_BOUNDARY"),
                "DAY_BOUNDARY": self.bo_lich.lay("DAY_BOUNDARY"),
                "HOUR_STEM_LATE_ZI": self.bo_lich.lay("HOUR_STEM_LATE_ZI"),
                "TRUE_SOLAR_TIME": self.bo_lich.lay("TRUE_SOLAR_TIME"),
                "LOCAL_TIMEZONE": self.bo_lich.lay("LOCAL_TIMEZONE"),
                "HISTORICAL_TIMEZONE": self.bo_lich.lay("HISTORICAL_TIMEZONE"),
            },
            nen_thien_van=self.bo_tiet.nen.ten,
            calculation_timestamp=datetime.now(timezone.utc).isoformat(),
            thoi_diem=thoi_diem,
            vi_tri_tiet_khi=vi_tri,
            tru_nam=tn, tru_thang=tt, tru_ngay=tg_ngay, tru_gio=tg_gio,
            dai_van=dv,
            canh_bao=canh_bao,
        )
