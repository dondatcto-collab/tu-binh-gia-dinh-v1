"""V2.9A — cổng hợp lưu giờ cá nhân an toàn.

Lớp này KHÔNG tự tạo giờ tốt/xấu. Nó chỉ đưa bối cảnh ngày/sự kiện vào lớp giờ
và khóa thứ bậc quyết định trước khi V2.9B có rule giờ đã VERIFIED.

Nguyên tắc bất biến:
- HARD_BLOCK của ngày/sự kiện thắng toàn bộ giờ.
- Một quan hệ hợp/xung của giờ không đủ để gọi giờ tốt/xấu cá nhân.
- Không có bối cảnh việc/ngày => chỉ mô tả cấu trúc.
- Ngày không bị chặn cũng không đồng nghĩa có giờ tốt.
- numeric_score luôn LOCKED_OFF.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

HOUR_FUSION_POLICY_VERSION = "2.9-alpha.1"
HOUR_FUSION_STATUS = "V2_9A_EVENT_DAY_GATED_HOUR_REFERENCE"


def _is_day_hard_block(event_day: dict[str, Any] | None) -> bool:
    if not event_day:
        return False
    ctx = event_day.get("event_context") or {}
    conclusion = event_day.get("conclusion") or {}
    return bool(
        ctx.get("hard_block") is True
        or conclusion.get("state") == "HARD_BLOCK"
        or conclusion.get("label") == "Bị chặn"
    )


def hour_fusion_gate(
    hour_reference: dict[str, Any],
    *,
    event_code: str | None = None,
    event_day: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Hợp lưu bối cảnh ngày vào 12 giờ mà chưa phát minh rule giờ.

    V2.9A chỉ có quyền CHẶN theo ngày hoặc giữ DESCRIPTIVE_ONLY. Muốn phát sinh
    giờ tốt/xấu cá nhân phải sang V2.9B với rule/source giờ VERIFIED và ca vàng.
    """
    out = deepcopy(hour_reference)
    out["hour_fusion_policy_version"] = HOUR_FUSION_POLICY_VERSION
    out["hour_fusion_status"] = HOUR_FUSION_STATUS
    out["event_code"] = event_code
    out["event_day_context_present"] = event_day is not None
    out["numeric_score"] = None
    out["numeric_score_status"] = "LOCKED_OFF"

    hours = list(out.get("hours") or [])
    day_blocked = _is_day_hard_block(event_day)

    if day_blocked:
        out["conclusion"] = {
            "state": "BLOCKED_BY_DAY",
            "label": "Ngày đã bị chặn",
            "title": "Không xét giờ để cứu ngày đã bị chặn",
        }
        out["plain_explanation"] = (
            "Lớp sự kiện đã chặn ngày này. Theo thứ bậc HARD_BLOCK > EVENT > PERSONAL, "
            "mọi giờ trong ngày đều không đủ quyền đảo kết luận của ngày."
        )
        out["confidence_state"] = (event_day or {}).get("confidence_state") or "Căn cứ vừa"
        out["hour_fusion_ready"] = True
        out["personal_hour_decision_ready"] = False
        for item in hours:
            item["decision_state"] = "INELIGIBLE_BY_DAY"
            item["is_personal_good_hour"] = None
            item["is_personal_bad_hour"] = None
            item["day_gate"] = "HARD_BLOCK"
        out["hours"] = hours
        return out

    if event_day is None or not event_code:
        out["conclusion"] = {
            "state": "DESCRIPTIVE_ONLY",
            "label": "Thiếu bối cảnh việc",
            "title": "Chưa đủ căn cứ để xét giờ theo việc cụ thể",
        }
        out["plain_explanation"] = (
            "V2.9 cần biết loại việc và kết luận của ngày trước khi xét giờ. "
            "Nếu thiếu bối cảnh này, ứng dụng chỉ hiển thị cấu trúc 12 giờ."
        )
        out["confidence_state"] = "Chưa đủ căn cứ"
        out["hour_fusion_ready"] = False
        out["personal_hour_decision_ready"] = False
        return out

    out["conclusion"] = {
        "state": "DESCRIPTIVE_ONLY",
        "label": "Ngày đủ điều kiện để xét tiếp giờ",
        "title": "Chưa bật nhãn giờ tốt/xấu cho đến khi rule giờ được xác minh",
    }
    out["plain_explanation"] = (
        "Ngày không bị HARD_BLOCK nên có thể đi tiếp tới lớp giờ. Tuy nhiên V2.9A "
        "chưa dùng quan hệ hợp/xung đơn lẻ để gọi giờ tốt/xấu; cần rule giờ có nguồn "
        "và trạng thái VERIFIED ở V2.9B."
    )
    out["confidence_state"] = "Chưa đủ căn cứ"
    out["hour_fusion_ready"] = True
    out["personal_hour_decision_ready"] = False
    for item in hours:
        item["decision_state"] = "DESCRIPTIVE_ONLY"
        item["is_personal_good_hour"] = None
        item["is_personal_bad_hour"] = None
        item["day_gate"] = "PASS_TO_HOUR_RULES"
    out["hours"] = hours
    return out
