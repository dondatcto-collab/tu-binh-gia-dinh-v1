"""V2.9C — dựng bối cảnh Can Chi giờ + Hỷ/Kỵ cá nhân để hợp lưu giờ.

Không chấm điểm. Không tự giải quyết tranh luận Can giờ Tý 23:00–23:59.
Khoảng Tý được giữ ở chế độ bảo thủ: quan hệ Chi vẫn có thể dùng theo V2.9B,
nhưng Can giờ không được dùng để tăng/giảm quyết định cho tới khi TIME-0007 được khóa.
"""
from __future__ import annotations

from typing import Any

from loi.bat_tu.cach_cuc import phan_tich_hanh_van, phan_tich_menh_goc
from loi.lich.quy_uoc_can_chi import CAN, CAN_VI, CHI, CHI_VI, tai_quy_uoc
from loi.van import dong_thoi_gian as dtg

HOUR_STEM_SOURCE_ID = "SRC-UHTB-CHEP"
HOUR_STEM_RULE_ID = "CAL-NGU-THU-DON"
LATE_ZI_CONFLICT_ID = "TIME-0007"


def _compact_transit(transit: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": transit.get("state"),
        "label": transit.get("label"),
        "stem_ten_god": transit.get("stem_ten_god"),
        "stem_effect": transit.get("stem_effect"),
        "branch_hidden_ten_gods": list(transit.get("branch_hidden_ten_gods") or []),
        "branch_effect": transit.get("branch_effect"),
        "rule_ids": list(transit.get("rule_ids") or []),
    }


def build_personal_hour_context(conn, *, kq: Any, day_can: str, day_chi: str) -> list[dict[str, Any]]:
    """Dựng 12 bối cảnh giờ từ cùng nền mệnh mà engine ngày/tháng đang dùng.

    Các giờ Sửu..Hợi dùng Ngũ Thử Độn VERIFIED để có Can giờ rồi chạy đúng
    `phan_tich_hanh_van(..., scope="hour")` của ZPZQ. Riêng giờ Tý không dùng
    Can giờ để quyết định vì phần 23:00–23:59 còn CONFLICTED giữa hai cách tính.
    """
    base = kq.base_state
    tu_tru = {k: dtg.TruVi(v["can"], v["chi"]) for k, v in base["tu_tru"].items()}
    nhat_chu = base["nhat_chu"]
    natal = phan_tich_menh_goc(conn, tu_tru=tu_tru, nhat_chu=nhat_chu)
    quy_uoc = tai_quy_uoc()
    can_ty = quy_uoc.can_gio_ty(day_can)
    can_ty_index = CAN.index(can_ty)

    out: list[dict[str, Any]] = []
    for i, chi in enumerate(CHI):
        base_item: dict[str, Any] = {
            "chi": chi,
            "chi_vi": CHI_VI[i],
            "day_can": day_can,
            "day_can_vi": CAN_VI[CAN.index(day_can)],
            "day_chi": day_chi,
            "day_chi_vi": CHI_VI[CHI.index(day_chi)],
            "hour_stem_rule_id": HOUR_STEM_RULE_ID,
            "hour_stem_source_id": HOUR_STEM_SOURCE_ID,
            "numeric_score": None,
            "numeric_score_status": "LOCKED_OFF",
        }

        if i == 0:
            base_item.update({
                "hour_can": None,
                "hour_can_vi": None,
                "personal_transit_state": "DESCRIPTIVE_ONLY",
                "personal_transit_label": "Can giờ Tý còn tranh luận",
                "stem_effect": "UNDETERMINED",
                "branch_effect": "UNDETERMINED",
                "personal_rule_ids": [],
                "personal_source_ids": list(natal.get("source_ids") or []),
                "hour_stem_boundary_status": "CONFLICTED_LATE_ZI",
                "hour_stem_conflict_id": LATE_ZI_CONFLICT_ID,
                "hour_stem_note": (
                    "Khoảng 23:00–01:00 đi qua ranh giới ngày. Can giờ phần 23:00–23:59 "
                    "còn hai cách hiểu nên V2.9C không dùng Can giờ Tý để nâng/hạ quyết định."
                ),
            })
            out.append(base_item)
            continue

        can_gio = CAN[(can_ty_index + i) % 10]
        transit = phan_tich_hanh_van(conn, natal, nhat_chu, can_gio, chi, "hour")
        compact = _compact_transit(transit)
        base_item.update({
            "hour_can": can_gio,
            "hour_can_vi": CAN_VI[CAN.index(can_gio)],
            "personal_transit_state": compact["state"],
            "personal_transit_label": compact["label"],
            "stem_ten_god": compact["stem_ten_god"],
            "stem_effect": compact["stem_effect"],
            "branch_hidden_ten_gods": compact["branch_hidden_ten_gods"],
            "branch_effect": compact["branch_effect"],
            "personal_rule_ids": sorted(set([HOUR_STEM_RULE_ID, *compact["rule_ids"]])),
            "personal_source_ids": sorted(set([HOUR_STEM_SOURCE_ID, *list(natal.get("source_ids") or [])])),
            "hour_stem_boundary_status": "VERIFIED_NON_LATE_ZI",
            "hour_stem_conflict_id": None,
            "hour_stem_note": "Can giờ dựng bằng Ngũ Thử Độn VERIFIED; Hỷ/Kỵ dùng cùng engine ZPZQ của ngày/tháng.",
        })
        out.append(base_item)

    return out
