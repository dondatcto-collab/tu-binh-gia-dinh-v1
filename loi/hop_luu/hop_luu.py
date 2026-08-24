"""Hợp lưu 0.5.0 — tầng quyết định cuối có truy nguồn.

Không tạo điểm số. Cách cục/Hỷ-Kỵ đã được nối vào mệnh gốc; phần chưa có
căn cứ vẫn để UNKNOWN và ghi rõ cách gỡ.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

from loi.bat_tu.cach_cuc import phan_tich_menh_goc
from loi.bat_tu.tang_can import lay_tang_can
from loi.bat_tu.thap_than import tinh_thap_than
from loi.ho_so.ho_so import HoSo
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import viet_hoa
from loi.van import dong_thoi_gian as dtg
from loi.quyet_dinh.v1 import danh_gia_event
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan, bo_sung_event_ca_nhan

UNKNOWN = "UNKNOWN"
NOT_CALIBRATED = "NOT_CALIBRATED"
NO_RULE = "NO_RULE_AVAILABLE"

@dataclass
class YeuTo:
    ma: str
    mo_ta: str
    rule_id: str
    source_id: str | None
    verification_status: str
    def to_dict(self) -> dict[str, Any]:
        return {"ma":self.ma,"mo_ta":self.mo_ta,"rule_id":self.rule_id,"source_id":self.source_id,"verification_status":self.verification_status}

@dataclass
class DieuChuaBiet:
    ma: str
    loi_thuong: str
    can_de_tra_loi: str
    ly_do: str
    can_gi_de_go: str
    def to_dict(self) -> dict[str, Any]:
        return {"ma":self.ma,"loi_thuong":self.loi_thuong,"can_de_tra_loi":self.can_de_tra_loi,"ly_do":self.ly_do,"can_gi_de_go":self.can_gi_de_go}

@dataclass
class KetQuaHopLuu:
    person: str
    period: str
    base_state: dict[str, Any]
    decade_state: dict[str, Any]
    year_state: dict[str, Any]
    month_state: dict[str, Any]
    day_state: dict[str, Any]
    hour_state: dict[str, Any]
    event_state: dict[str, Any]
    positive_factors: list[YeuTo] = field(default_factory=list)
    negative_factors: list[YeuTo] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    uncertainties: list[DieuChuaBiet] = field(default_factory=list)
    score: float | None = None
    label: str = UNKNOWN
    confidence: str = "LOW"
    scoring_status: str = NOT_CALIBRATED
    recommended: list[str] = field(default_factory=list)
    caution: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    rule_trace: list[str] = field(default_factory=list)
    source_trace: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {
            "person":self.person,"period":self.period,"base_state":self.base_state,
            "decade_state":self.decade_state,"year_state":self.year_state,"month_state":self.month_state,
            "day_state":self.day_state,"hour_state":self.hour_state,"event_state":self.event_state,
            "positive_factors":[x.to_dict() for x in self.positive_factors],
            "negative_factors":[x.to_dict() for x in self.negative_factors],"conflicts":list(self.conflicts),
            "uncertainties":[x.to_dict() for x in self.uncertainties],"score":self.score,"label":self.label,
            "confidence":self.confidence,"scoring_status":self.scoring_status,"recommended":list(self.recommended),
            "caution":list(self.caution),"avoid":list(self.avoid),"rule_trace":sorted(set(self.rule_trace)),
            "source_trace":sorted(set(self.source_trace)),
        }

CAC_O_CHUA_CO_CAN_CU = [
    DieuChuaBiet("THAN_SAT","Ngày này có điểm phụ nào đáng chú ý không","Thần sát","Nhóm Thần sát chưa đủ bộ quy tắc nguồn; V1 không dùng lớp này để lật kết luận chính.","Bổ sung từng quy tắc khi có nguồn và công thức khởi rõ ràng."),
    DieuChuaBiet("CHAM_DIEM","Mức độ ưu tiên định lượng","Điểm số và nhãn số","Chưa có hệ điểm được hiệu chỉnh bằng ca vàng; đặc tả cấm tự đặt trọng số/ngưỡng.","Chỉ mở điểm số sau một vòng hiệu chỉnh độc lập; hiện dùng nhãn thứ bậc."),
]

def _unknown(ma: str, loi: str, ky_thuat: str, ly_do: str, go: str) -> dict[str, Any]:
    return {"status":UNKNOWN,"ma":ma,"loi_thuong":loi,"can_de_tra_loi":ky_thuat,"ly_do":ly_do,"can_gi_de_go":go}


def hop_luu(conn: sqlite3.Connection, hs: HoSo, ngay: date | None=None, gio_chi: str | None=None, event_code: str | None=None, moc: datetime | None=None) -> KetQuaHopLuu:
    if moc is None:
        try: moc=datetime.now(ZoneInfo(hs.timezone_name))
        except ZoneInfoNotFoundError: moc=datetime.now(timezone.utc)
    ngay=ngay or moc.date()
    try: tz_hs=ZoneInfo(hs.timezone_name)
    except ZoneInfoNotFoundError: tz_hs=timezone.utc

    tl=dtg.dung(conn,hs,moc=datetime(ngay.year,ngay.month,ngay.day,12,0,tzinfo=tz_hs))
    e=CalendarEngine(tai_bo_lich()["CAL-V1"])
    lich=e.tinh(ngay.year,ngay.month,ngay.day,12,0,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
    rule=list(tl.rule_trace); source=list(tl.source_trace)

    natal=phan_tich_menh_goc(conn,tu_tru=tl.tu_tru,nhat_chu=tl.nhat_chu)
    rule.extend(natal.get("rule_ids",[])); source.extend(natal.get("source_ids",[]))

    # Evidence cấu trúc của ngày; không tự phân thuận/nghịch ngoài engine Cách cục.
    tt_ngay=tinh_thap_than(conn,tl.nhat_chu,lich.tru_ngay.can); rule.append(tt_ngay.rule_id)
    tc=lay_tang_can(conn,lich.tru_ngay.chi); rule.extend(tc.rule_ids)
    for can in tc.hidden_stems:
        t=tinh_thap_than(conn,tl.nhat_chu,can); rule.append(t.rule_id)

    context=[]; qd_dai_van=None
    if tl.dai_van is not None:
        qd_dai_van = phan_tich_ca_nhan(conn,tu_tru=tl.tu_tru,nhat_chu=tl.nhat_chu,can_hien_tai=tl.dai_van.can,chi_hien_tai=tl.dai_van.chi,scope="decade",context=[])
        context.append({"label":"Đại vận","tru":viet_hoa(tl.dai_van.can,tl.dai_van.chi),"ten_god_vi":tinh_thap_than(conn,tl.nhat_chu,tl.dai_van.can).ten_god_vi})
    qd_nam = phan_tich_ca_nhan(conn,tu_tru=tl.tu_tru,nhat_chu=tl.nhat_chu,can_hien_tai=tl.nam_hien_tai.can,chi_hien_tai=tl.nam_hien_tai.chi,scope="year",context=context)
    ctx_nam=context+[{"label":"Năm","tru":tl.nam_hien_tai.vi,"ten_god_vi":tl.thap_than_nam}]
    qd_thang = phan_tich_ca_nhan(conn,tu_tru=tl.tu_tru,nhat_chu=tl.nhat_chu,can_hien_tai=tl.thang_hien_tai.can,chi_hien_tai=tl.thang_hien_tai.chi,scope="month",context=ctx_nam)
    ctx_ngay=ctx_nam+[{"label":"Tháng","tru":tl.thang_hien_tai.vi,"ten_god_vi":tl.thap_than_thang}]
    qd_ngay = phan_tich_ca_nhan(conn,tu_tru=tl.tu_tru,nhat_chu=tl.nhat_chu,can_hien_tai=lich.tru_ngay.can,chi_hien_tai=lich.tru_ngay.chi,scope="day",context=ctx_ngay)
    for q in (qd_dai_van,qd_nam,qd_thang,qd_ngay):
        if q:
            rule.extend(q.get("rule_ids",[])); source.extend(q.get("source_ids",[]))

    day_state={"solar_date":ngay.isoformat(),"tru_ngay":viet_hoa(lich.tru_ngay.can,lich.tru_ngay.chi),"quan_he_voi_nhat_chu":tt_ngay.ten_god_vi,"tang_can":list(tc.hidden_stems),"boundary_warning":lich.boundary_warning,"canh_bao":[c.ma for c in lich.canh_bao],"danh_gia":qd_ngay}

    hour_state={"status":"NOT_SELECTED"}
    if gio_chi:
        hour_state={"chi_gio":gio_chi,"danh_gia":_unknown("GIO_HOP_LUU","Giờ này có phù hợp với ngày và người hay không","Hợp lưu giờ","V1 chưa hoàn tất hợp lưu Can Chi giờ với ngày + nền mệnh.","Chỉ mở kết luận giờ sau khi có ca vàng riêng."),"ghi_chu":"Giờ phải được xét trong bối cảnh ngày; V1 hiện chỉ hiển thị tham khảo cấu trúc."}

    event_state={"status":"NOT_SELECTED"}
    if event_code:
        event_state=danh_gia_event(tl.thang_hien_tai.chi,lich.tru_ngay.chi,tl.tu_tru["ngay"].chi,event_code)
        event_state=bo_sung_event_ca_nhan(event_state,qd_ngay)
        rule.extend(event_state.get("rule_ids",[]))
        if event_state.get("source_id"): source.append(event_state["source_id"])

    main_label=event_state.get("label") if event_code else qd_ngay.get("label",UNKNOWN)
    main_conf=event_state.get("confidence",qd_ngay.get("confidence","LOW")) if event_code else qd_ngay.get("confidence","LOW")
    rec=list(qd_ngay.get("recommended",[])); caut=list(qd_ngay.get("caution",[])); avoid=[]
    if event_code and event_state.get("decision_state")=="HARD_BLOCK": avoid.append(f"Không ưu tiên {event_state.get('event_name','việc này')} trong ngày này nếu có thể chọn ngày khác.")
    elif event_code and event_state.get("decision_state") in ("PRIORITY","CONSIDER"): rec.append(f"{event_state.get('event_name','Việc này')} có thể được cân nhắc theo lớp quy tắc hiện đã nghiệm thu.")

    if natal.get("status")=="READY":
        cach_cuc=natal
        dung_hy={"status":"READY","pattern":natal.get("pattern"),"favorable_factors":natal.get("favorable_factors",[]),"avoid_factors":natal.get("avoid_factors",[]),"xiang_shen":natal.get("xiang_shen",[]),"rule_ids":natal.get("rule_ids",[])}
        vuong_suy={"status":"STRUCTURAL_CONDITION_ONLY","ghi_chu":"V1 không dùng một điểm mạnh/yếu độc lập để thay Cách cục."}
    else:
        cach_cuc=natal
        dung_hy=_unknown("DUNG_HY_KY","Yếu tố nào hỗ trợ hoặc phá cấu trúc mệnh","Hỷ/Kỵ theo Cách cục","Cách cục đang AMBIGUOUS nên chưa được phép suy Hỷ/Kỵ.","Làm rõ Cách cục bằng quy tắc nguồn đã khóa.")
        vuong_suy={"status":"STRUCTURAL_CONDITION_ONLY","ghi_chu":"Không dùng mạnh/yếu đơn lẻ để ép chọn Dụng thần."}

    return KetQuaHopLuu(
        person=hs.full_name,period=ngay.isoformat(),
        base_state={"tu_tru":{k:v.to_dict() for k,v in tl.tu_tru.items()},"nhat_chu":tl.nhat_chu,"nguyet_lenh":tl.nguyet_lenh_menh,"vuong_suy":vuong_suy,"cach_cuc":cach_cuc,"dung_hy_ky":dung_hy},
        decade_state=({**tl.dai_van.to_dict(),"danh_gia":qd_dai_van} if tl.dai_van else {"status":UNKNOWN,"ly_do":"Ngoài mười vận đã tính."}),
        year_state={"tru":tl.nam_hien_tai.to_dict(),"quan_he_voi_nhat_chu":tl.thap_than_nam,"danh_gia":qd_nam},
        month_state={"tru":tl.thang_hien_tai.to_dict(),"quan_he_voi_nhat_chu":tl.thap_than_thang,"nguyet_lenh":tl.nguyet_lenh_hien_tai,"danh_gia":qd_thang},
        day_state=day_state,hour_state=hour_state,event_state=event_state,
        positive_factors=[],negative_factors=[],conflicts=[],uncertainties=list(CAC_O_CHUA_CO_CAN_CU),
        score=None,label=main_label or UNKNOWN,confidence=main_conf,scoring_status="ORDINAL_V1_1_PERSONAL",
        recommended=rec,caution=caut,avoid=avoid,rule_trace=rule,source_trace=source)


def quan_sat_trung_lap(conn: sqlite3.Connection, hs: HoSo, ngay: date) -> list[YeuTo]:
    kq=hop_luu(conn,hs,ngay=ngay)
    return kq.positive_factors+kq.negative_factors
