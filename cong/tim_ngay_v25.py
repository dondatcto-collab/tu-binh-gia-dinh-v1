"""V2.5 event search pipeline.

Tách khỏi endpoint V1 để V1 giữ nguyên hành vi đã nghiệm thu. V2.5 dùng cùng
CalendarEngine và lớp cá nhân, nhưng hợp lưu qua runtime Hiệp Kỷ mở rộng.
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException

from cong.api import WorkRequest, _conn, _ho_so
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import viet_hoa
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.v1 import EVENT_RULES, danh_gia_event
from loi.van import dong_thoi_gian as dtg

V25_RANKING_MODE = "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL"


def tim_ngay_v25(v: WorkRequest) -> dict:
    hs = _ho_so(v.profile)
    try:
        a, b = date.fromisoformat(v.tu_ngay), date.fromisoformat(v.den_ngay)
    except ValueError as exc:
        raise HTTPException(400, "Khoảng ngày không hợp lệ.") from exc
    if b < a or (b - a).days > 92:
        raise HTTPException(400, "Khoảng ngày không hợp lệ hoặc vượt quá ba tháng.")
    if v.viec not in EVENT_RULES:
        raise HTTPException(400, "Loại việc chưa được hỗ trợ trong V2.5.")

    engine = CalendarEngine(tai_bo_lich()["CAL-V1"])
    sinh = engine.tinh(
        hs.birth_year, hs.birth_month, hs.birth_day, hs.birth_hour, hs.birth_minute,
        timezone_name=hs.timezone_name, gioi_tinh=hs.gender, tinh_dai_van=False,
    )
    chi_menh = sinh.tru_ngay.chi
    nhat_chu = sinh.tru_ngay.can
    tu_tru = {
        "nam": dtg.TruVi(sinh.tru_nam.can, sinh.tru_nam.chi),
        "thang": dtg.TruVi(sinh.tru_thang.can, sinh.tru_thang.chi),
        "ngay": dtg.TruVi(sinh.tru_ngay.can, sinh.tru_ngay.chi),
        "gio": dtg.TruVi(sinh.tru_gio.can, sinh.tru_gio.chi),
    }

    ds: list[dict] = []
    cur = a
    with _conn() as conn:
        while cur <= b:
            lich = engine.tinh(
                cur.year, cur.month, cur.day, 12, 0,
                timezone_name=hs.timezone_name, gioi_tinh=hs.gender, tinh_dai_van=False,
            )
            personal = phan_tich_ca_nhan(
                conn,
                tu_tru=tu_tru,
                nhat_chu=nhat_chu,
                can_hien_tai=lich.tru_ngay.can,
                chi_hien_tai=lich.tru_ngay.chi,
                scope="day",
                context=[],
            )
            base = danh_gia_event(lich.tru_thang.chi, lich.tru_ngay.chi, chi_menh, v.viec)
            ev = evaluate_event_v25(
                base,
                personal,
                chi_thang=lich.tru_thang.chi,
                chi_ngay=lich.tru_ngay.chi,
            )
            ds.append({
                "ngay": cur.isoformat(),
                "tru_ngay": viet_hoa(lich.tru_ngay.can, lich.tru_ngay.chi),
                "label": ev.get("label"),
                "decision_state": ev.get("decision_state"),
                "decision_authority": ev.get("decision_authority"),
                "hard_block": ev.get("hard_block", False),
                "rank_group": ev.get("rank_group", 9),
                "truc": ev.get("truc_vi"),
                "event_state": ev.get("event_state"),
                "event_state_v1": ev.get("event_state_v1"),
                "event_signal_v25": ev.get("event_signal_v25"),
                "personal_v1_1": ev.get("personal_v1_1", {}),
                "reasons": ev.get("reasons", []),
                "mapping_status": ev.get("mapping_status"),
                "coverage": ev.get("coverage"),
                "event_note": ev.get("event_note"),
                "active_hiep_ky_tokens": ev.get("active_hiep_ky_tokens", []),
                "matched_yi_tokens": ev.get("matched_yi_tokens", []),
                "matched_ji_tokens": ev.get("matched_ji_tokens", []),
                "matched_evidence": ev.get("matched_evidence", []),
                "rule_ids": ev.get("rule_ids", []),
                "source_ids": ev.get("source_ids", []),
                "score": None,
                "numeric_score": None,
                "numeric_score_status": "LOCKED_OFF",
                "scoring_status": "NO_NUMERIC_SCORE",
            })
            cur += timedelta(days=1)

    ranked = sorted(ds, key=lambda x: (x.get("rank_group", 9), x.get("ngay", "")))
    return {
        "viec": v.viec,
        "so_ngay_da_quet": len(ds),
        "co_xep_hang_duoc_khong": True,
        "xep_hang_status": V25_RANKING_MODE,
        "ghi_chu": "V2.5: 12 Trực + 5 quan hệ Chi tháng-ngày; HARD_BLOCK > sự kiện > cá nhân; không dùng điểm 0–10.",
        "canh_bao_an_toan": (
            "Chỉ chọn trong các thời điểm bác sĩ/cơ sở y tế xác nhận có thể linh hoạt; không trì hoãn cấp cứu."
            if v.viec == "DIEU_TRI" else None
        ),
        "top": ranked[:3],
        "cac_ngay": ranked,
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
