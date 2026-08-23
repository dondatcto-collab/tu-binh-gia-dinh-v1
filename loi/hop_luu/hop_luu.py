"""Hợp lưu — tầng quyết định cuối.

NGUYÊN TẮC CỦA TỆP NÀY:

Nó dựng ĐẦY ĐỦ cấu trúc kết quả mà sản phẩm cần. Nhưng nó CHỈ điền những ô
có căn cứ từ quy tắc đã xác minh. Ô nào chưa có căn cứ thì để UNKNOWN kèm
lý do cụ thể, và đưa vào danh sách `uncertainties`.

Nó KHÔNG tự nghĩ công thức, KHÔNG tự đặt trọng số, KHÔNG tạo điểm giả.
Điểm số để None và đánh dấu NOT_CALIBRATED cho tới khi có hệ chấm điểm
được hiệu chỉnh bằng ca vàng đã duyệt.

Tầng giao diện và tầng giải thích KHÔNG được tự tính thêm gì.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

from loi.bat_tu.nguyet_lenh import tu_ket_qua_lich
from loi.bat_tu.tang_can import lay_tang_can
from loi.bat_tu.thap_than import tinh_thap_than
from loi.ho_so.ho_so import HoSo
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import viet_hoa
from loi.van.dong_thoi_gian import DongThoiGian
from loi.van import dong_thoi_gian as dtg
from loi.quyet_dinh.v1 import danh_gia_giai_doan, danh_gia_event

UNKNOWN = "UNKNOWN"
NOT_CALIBRATED = "NOT_CALIBRATED"
NO_RULE = "NO_RULE_AVAILABLE"


@dataclass
class YeuTo:
    """Một yếu tố có thật, truy ngược được tới quy tắc và nguồn."""
    ma: str
    mo_ta: str
    rule_id: str
    source_id: str | None
    verification_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ma": self.ma, "mo_ta": self.mo_ta,
            "rule_id": self.rule_id, "source_id": self.source_id,
            "verification_status": self.verification_status,
        }


@dataclass
class DieuChuaBiet:
    """Một ô mà hệ thống CỐ Ý không kết luận, kèm lý do và cách gỡ.

    Có HAI cách diễn đạt cho cùng một điều:
      loi_thuong  — cho người không biết Tử Bình. Tuyệt đối không thuật ngữ.
      can_de_tra_loi — tên kỹ thuật, chỉ dùng ở tầng chuyên sâu.
    """
    ma: str
    loi_thuong: str
    can_de_tra_loi: str
    ly_do: str
    can_gi_de_go: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ma": self.ma, "loi_thuong": self.loi_thuong,
            "can_de_tra_loi": self.can_de_tra_loi,
            "ly_do": self.ly_do, "can_gi_de_go": self.can_gi_de_go,
        }


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
            "person": self.person, "period": self.period,
            "base_state": self.base_state, "decade_state": self.decade_state,
            "year_state": self.year_state, "month_state": self.month_state,
            "day_state": self.day_state, "hour_state": self.hour_state,
            "event_state": self.event_state,
            "positive_factors": [x.to_dict() for x in self.positive_factors],
            "negative_factors": [x.to_dict() for x in self.negative_factors],
            "conflicts": list(self.conflicts),
            "uncertainties": [x.to_dict() for x in self.uncertainties],
            "score": self.score,
            "label": self.label,
            "confidence": self.confidence,
            "scoring_status": self.scoring_status,
            "recommended": list(self.recommended),
            "caution": list(self.caution),
            "avoid": list(self.avoid),
            "rule_trace": sorted(set(self.rule_trace)),
            "source_trace": sorted(set(self.source_trace)),
        }


# ---------------------------------------------------------------
# Những ô V1 cần nhưng kho quy tắc CHƯA CÓ
# ---------------------------------------------------------------

CAC_O_CHUA_CO_CAN_CU = [
    DieuChuaBiet(
        "VUONG_SUY",
        "Sức của bạn đang mạnh hay yếu so với thời tiết trong năm",
        "Nhật chủ mạnh hay yếu",
        "Muốn xét vượng suy phải biết Can nào đương quyền trong đoạn tiết khí. "
        "Đó là nhóm BT-SEASON-POWER, hiện cả 22 tiết đều INSUFFICIENT_SOURCES.",
        "Cần bảng chia ngày của Tam Mệnh Thông Hội hoặc một nguồn cổ thứ hai."),
    DieuChuaBiet(
        "CACH_CUC",
        "Kiểu vận mệnh tổng thể của bạn thuộc dạng nào",
        "Cách cục của lá số",
        "Nhóm BT-PAT chưa có quy tắc nào. Việc xét thành bại cứu ứng cần "
        "nguồn Tử Bình Chân Thuyên mà tôi chưa có trong tay.",
        "Cần phần Luận cách cục của Tử Bình Chân Thuyên."),
    DieuChuaBiet(
        "DUNG_HY_KY",
        "Điều gì hợp với bạn và điều gì không hợp",
        "Dụng thần, Hỷ thần, Kỵ thần",
        "Nhóm BT-USE chưa có quy tắc nào, và nó đứng trên vượng suy lẫn cách cục "
        "— cả hai đều chưa xác định được.",
        "Cần giải xong vượng suy và cách cục trước."),
    DieuChuaBiet(
        "THAN_SAT",
        "Ngày này có điểm gì đáng chú ý riêng không",
        "Thần sát",
        "Nhóm SS chưa có quy tắc nào.",
        "Cần nguồn và công thức khởi cho từng Thần sát."),
    DieuChuaBiet(
        "CHAM_DIEM",
        "Chấm điểm ngày từ 0 tới 10",
        "Điểm số và nhãn",
        "Chưa có hệ chấm điểm nào được hiệu chỉnh bằng ca vàng đã duyệt. "
        "Đặc tả cấm tự chốt ngưỡng chỉ vì ví dụ trong lệnh.",
        "Cần ca vàng nhóm GOLD-FUS đã duyệt để hiệu chỉnh."),
]


def _trang_thai_chua_biet(ma: str) -> dict[str, Any]:
    d = next(x for x in CAC_O_CHUA_CO_CAN_CU if x.ma == ma)
    return {"status": UNKNOWN, "ly_do": d.ly_do, "can_gi_de_go": d.can_gi_de_go}


# ---------------------------------------------------------------
# Hợp lưu
# ---------------------------------------------------------------

def hop_luu(conn: sqlite3.Connection, hs: HoSo,
            ngay: date | None = None,
            gio_chi: str | None = None,
            event_code: str | None = None,
            moc: datetime | None = None) -> KetQuaHopLuu:
    if moc is None:
        try:
            moc = datetime.now(ZoneInfo(hs.timezone_name))
        except ZoneInfoNotFoundError:
            moc = datetime.now(timezone.utc)
    ngay = ngay or moc.date()
    try:
        tz_hs = ZoneInfo(hs.timezone_name)
    except ZoneInfoNotFoundError:
        tz_hs = timezone.utc
    tl = dtg.dung(conn, hs, moc=datetime(ngay.year, ngay.month, ngay.day,
                                         12, 0, tzinfo=tz_hs))

    e = CalendarEngine(tai_bo_lich()["CAL-V1"])
    lich_ngay = e.tinh(ngay.year, ngay.month, ngay.day, 12, 0,
                       timezone_name=hs.timezone_name, gioi_tinh=hs.gender,
                       tinh_dai_van=False)

    duong = []
    am = []
    rule = list(tl.rule_trace)

    # --- Yếu tố CÓ THẬT: quan hệ Thập Thần giữa Nhật chủ và Can ngày ---
    tt_ngay = tinh_thap_than(conn, tl.nhat_chu, lich_ngay.tru_ngay.can)
    yt_ngay = YeuTo(
        ma="THAP_THAN_NGAY",
        mo_ta=f"Can ngày là {viet_hoa(lich_ngay.tru_ngay.can, lich_ngay.tru_ngay.chi)}, "
              f"đối với bạn thuộc quan hệ {tt_ngay.ten_god_vi}.",
        rule_id=tt_ngay.rule_id, source_id=tt_ngay.source_id,
        verification_status=tt_ngay.status)
    rule.append(tt_ngay.rule_id)

    # Quan hệ Thập Thần là SỰ KIỆN CẤU TRÚC, chưa phải tốt hay xấu.
    # Muốn nói thuận hay nghịch phải biết Dụng Hỷ Kỵ — mà cái đó chưa có.
    trung_lap = [yt_ngay]

    tc = lay_tang_can(conn, lich_ngay.tru_ngay.chi)
    for thu_tu, can in zip(tc.source_order, tc.hidden_stems):
        t = tinh_thap_than(conn, tl.nhat_chu, can)
        trung_lap.append(YeuTo(
            ma=f"THAP_THAN_TANG_CAN_{thu_tu}",
            mo_ta=f"Chi ngày chứa {viet_hoa(can, lich_ngay.tru_ngay.chi).split()[0]}, "
                  f"thuộc quan hệ {t.ten_god_vi}.",
            rule_id=t.rule_id, source_id=t.source_id,
            verification_status=t.status))
        rule.append(t.rule_id)
    rule.append(tc.rule_ids[0])

    canh_bao_bien = [c.ma for c in lich_ngay.canh_bao]

    # Lớp quyết định V1-basic: dùng quan hệ Địa Chi đã xác minh để trả lời
    # nhịp tháng/ngày, không suy Dụng-Hỷ-Kỵ và không chấm điểm số.
    qd_thang = danh_gia_giai_doan(tl.tu_tru["ngay"].chi, tl.thang_hien_tai.chi, "month")
    qd_ngay = danh_gia_giai_doan(tl.tu_tru["ngay"].chi, lich_ngay.tru_ngay.chi, "day")

    qh_ngay = qd_ngay["relation"]
    yt_qh = YeuTo(
        ma=f"QUAN_HE_NGAY_{qh_ngay['ma']}", mo_ta=qh_ngay["mo_ta"],
        rule_id=qh_ngay["rule_id"], source_id=qh_ngay["source_id"],
        verification_status="VERIFIED" if qh_ngay["ma"] != "NONE" else "PROVISIONAL")
    rule.append(qh_ngay["rule_id"])
    if qh_ngay["muc"] == "POSITIVE":
        duong.append(yt_qh)
    elif qh_ngay["muc"] == "CAUTION":
        am.append(yt_qh)

    day_state = {
        "solar_date": ngay.isoformat(),
        "tru_ngay": viet_hoa(lich_ngay.tru_ngay.can, lich_ngay.tru_ngay.chi),
        "quan_he_voi_nhat_chu": tt_ngay.ten_god_vi,
        "tang_can": list(tc.hidden_stems),
        "boundary_warning": lich_ngay.boundary_warning,
        "canh_bao": canh_bao_bien,
        "danh_gia": qd_ngay,
    }

    hour_state: dict[str, Any] = {"status": UNKNOWN}
    if gio_chi:
        hour_state = {
            "chi_gio": gio_chi,
            "danh_gia": _trang_thai_chua_biet("DUNG_HY_KY"),
            "ghi_chu": "Giờ chỉ được xét trong bối cảnh ngày. "
                       "Chưa đánh giá được ngày thì chưa đánh giá được giờ.",
        }

    event_state: dict[str, Any] = {"status": "NOT_SELECTED"}
    if event_code:
        event_state = danh_gia_event(
            tl.thang_hien_tai.chi, lich_ngay.tru_ngay.chi,
            tl.tu_tru["ngay"].chi, event_code)
        rule.extend(event_state.get("rule_ids", []))
        if event_state.get("source_id"):
            # source_trace chỉ chứa ID; tầng giải thích tra chi tiết từ DB.
            pass

    # Quan hệ Can Chi và Hiệp Kỷ V1-basic đã có lớp tối thiểu. Phần chưa có
    # vẫn giữ rõ: vượng suy/cách cục/dụng hỷ kỵ/thần sát/điểm tuyệt đối.
    chua_biet = list(CAC_O_CHUA_CO_CAN_CU)

    # Nhãn chính trả lời câu hỏi hiện tại: nếu có việc thì ưu tiên kết luận theo
    # việc; nếu không có việc thì dùng nhịp ngày. Điểm 0-10 vẫn không bịa.
    main_label = event_state.get("label") if event_code else qd_ngay["label"]
    main_conf = ("MEDIUM" if event_code and event_state.get("support_level") == "ACTIVE_BASIC"
                 else qd_ngay.get("confidence", "LOW"))
    rec = list(qd_ngay.get("recommended", []))
    caut = list(qd_ngay.get("caution", []))
    avoid_list: list[str] = []
    if event_code and event_state.get("event_state") == "JI":
        avoid_list.append(f"Không ưu tiên {event_state.get('event_name','việc này')} trong ngày này nếu có thể chọn ngày khác.")
    elif event_code and event_state.get("event_state") == "YI":
        rec.append(f"{event_state.get('event_name','Việc này')} có tín hiệu phù hợp ở lớp 12 Trực của Hiệp Kỷ V1-basic.")

    return KetQuaHopLuu(
        person=hs.full_name,
        period=ngay.isoformat(),
        base_state={
            "tu_tru": {k: v.to_dict() for k, v in tl.tu_tru.items()},
            "nhat_chu": tl.nhat_chu,
            "nguyet_lenh": tl.nguyet_lenh_menh,
            "vuong_suy": _trang_thai_chua_biet("VUONG_SUY"),
            "cach_cuc": _trang_thai_chua_biet("CACH_CUC"),
            "dung_hy_ky": _trang_thai_chua_biet("DUNG_HY_KY"),
        },
        decade_state=(tl.dai_van.to_dict() if tl.dai_van
                      else {"status": UNKNOWN, "ly_do": "Ngoài mười vận đã tính."}),
        year_state={"tru": tl.nam_hien_tai.to_dict(),
                    "quan_he_voi_nhat_chu": tl.thap_than_nam,
                    "danh_gia": danh_gia_giai_doan(tl.tu_tru["ngay"].chi, tl.nam_hien_tai.chi, "year")},
        month_state={"tru": tl.thang_hien_tai.to_dict(),
                     "quan_he_voi_nhat_chu": tl.thap_than_thang,
                     "nguyet_lenh": tl.nguyet_lenh_hien_tai,
                     "danh_gia": qd_thang},
        day_state=day_state,
        hour_state=hour_state,
        event_state=event_state,
        positive_factors=duong,
        negative_factors=am,
        conflicts=[],
        uncertainties=chua_biet,
        score=None,
        label=main_label or UNKNOWN,
        confidence=main_conf,
        scoring_status="ORDINAL_V1_BASIC",
        recommended=rec,
        caution=caut,
        avoid=avoid_list,
        rule_trace=rule,
        source_trace=list(tl.source_trace) + ([event_state.get("source_id")] if event_code and event_state.get("source_id") else []) + [qh_ngay["source_id"]],
    )


def quan_sat_trung_lap(conn: sqlite3.Connection, hs: HoSo,
                       ngay: date) -> list[YeuTo]:
    """Những gì hệ thống QUAN SÁT ĐƯỢC về một ngày, chưa đánh giá tốt xấu."""
    kq = hop_luu(conn, hs, ngay=ngay)
    return kq.positive_factors + kq.negative_factors
