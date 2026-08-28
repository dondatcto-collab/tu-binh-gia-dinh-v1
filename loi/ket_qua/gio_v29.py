"""V2.9B — hợp lưu giờ cá nhân có quyết định giới hạn, truy nguyên được.

V2.9B không dùng điểm số và không cho giờ cứu một ngày HARD_BLOCK. Khi ngày đã
qua cổng sự kiện, lớp giờ chỉ dùng các quan hệ Địa Chi đã có Rule ID/Source ID
trong kho quy tắc hiện hành để phân loại giờ thành: có thể ưu tiên, thận trọng,
hoặc trung tính. Đây là quyết định giờ giới hạn theo rule đã xác minh, không phải
khẳng định cát/hung tuyệt đối của toàn bộ hệ thống cổ điển.

Nguyên tắc bất biến:
- HARD_BLOCK của ngày/sự kiện thắng toàn bộ giờ.
- Chỉ Lục hợp được mở thành giờ có thể ưu tiên.
- Lục xung/Lục hại/Hình/Tự hình được mở thành giờ thận trọng.
- Không có quan hệ trực tiếp => trung tính, không tự suy thành tốt/xấu.
- numeric_score luôn LOCKED_OFF.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

HOUR_FUSION_POLICY_VERSION = "2.9-beta.1"
HOUR_FUSION_STATUS = "V2_9B_VERIFIED_RELATION_HOUR_DECISION"

_RELATION_RULES: dict[str, dict[str, str]] = {
    "LUC_HOP": {
        "decision_state": "PERSONAL_GOOD_CANDIDATE",
        "decision_label": "Có thể ưu tiên",
        "rule_id": "BT-REL-0001",
        "source_id": "SRC-TMTH-V02-WIKISOURCE",
        "nature": "POSITIVE",
    },
    "LUC_XUNG": {
        "decision_state": "PERSONAL_CAUTION_HOUR",
        "decision_label": "Nên thận trọng",
        "rule_id": "BT-REL-0002",
        "source_id": "SRC-TMTH-V02-WIKISOURCE",
        "nature": "CAUTION",
    },
    "LUC_HAI": {
        "decision_state": "PERSONAL_CAUTION_HOUR",
        "decision_label": "Nên thận trọng",
        "rule_id": "BT-REL-0003",
        "source_id": "SRC-TMTH-V02-WIKISOURCE",
        "nature": "CAUTION",
    },
    "HINH": {
        "decision_state": "PERSONAL_CAUTION_HOUR",
        "decision_label": "Nên thận trọng",
        "rule_id": "BT-REL-0004",
        "source_id": "SRC-TMTH-V02-WIKISOURCE",
        "nature": "CAUTION",
    },
    "TU_HINH": {
        "decision_state": "PERSONAL_CAUTION_HOUR",
        "decision_label": "Nên thận trọng",
        "rule_id": "BT-REL-0004",
        "source_id": "SRC-TMTH-V02-WIKISOURCE",
        "nature": "CAUTION",
    },
}

_RELATION_ALIASES = {
    "XUNG": "LUC_XUNG",
    "HAI": "LUC_HAI",
    "LUC_HOP": "LUC_HOP",
    "LUC_XUNG": "LUC_XUNG",
    "LUC_HAI": "LUC_HAI",
    "HINH": "HINH",
    "TU_HINH": "TU_HINH",
}


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


def _event_day_summary(event_day: dict[str, Any] | None) -> dict[str, Any] | None:
    if not event_day:
        return None
    return {
        "date": event_day.get("date"),
        "conclusion": dict(event_day.get("conclusion") or {}),
        "hard_block": bool((event_day.get("event_context") or {}).get("hard_block")),
        "confidence_state": event_day.get("confidence_state"),
        "confidence_basis": list(event_day.get("confidence_basis") or []),
        "rules": list(event_day.get("rules") or []),
        "sources": list(event_day.get("sources") or []),
    }


def _apply_verified_hour_rule(item: dict[str, Any]) -> dict[str, Any]:
    relation = _RELATION_ALIASES.get(str(item.get("relation") or "").upper())
    rule = _RELATION_RULES.get(relation or "")
    if not rule:
        item["decision_state"] = "PERSONAL_NEUTRAL_HOUR"
        item["decision_label"] = "Trung tính"
        item["is_personal_good_hour"] = False
        item["is_personal_bad_hour"] = False
        item["hour_rule_status"] = "NO_DIRECT_VERIFIED_RELATION"
        item["hour_rule_id"] = None
        item["hour_source_id"] = None
        item["decision_basis"] = "Không có quan hệ Địa Chi trực tiếp thuộc bộ rule giờ V2.9B."
        return item

    item["relation"] = relation
    item["decision_state"] = rule["decision_state"]
    item["decision_label"] = rule["decision_label"]
    item["is_personal_good_hour"] = rule["nature"] == "POSITIVE"
    # CAUTION không được diễn giải thành hung tuyệt đối; vì vậy không bật bad=True.
    item["is_personal_bad_hour"] = False
    item["hour_rule_status"] = "VERIFIED_RELATION_RULE"
    item["hour_rule_id"] = rule["rule_id"]
    item["hour_source_id"] = rule["source_id"]
    item["decision_basis"] = (
        "Quan hệ Địa Chi của giờ với Chi ngày sinh đã có Rule ID/Source ID; "
        "V2.9B chỉ dùng nó để ưu tiên hoặc cảnh báo tương đối."
    )
    return item


def hour_fusion_gate(
    hour_reference: dict[str, Any],
    *,
    event_code: str | None = None,
    event_day: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Hợp lưu ngày/sự kiện trước, sau đó mới áp rule giờ đã truy nguyên."""
    out = deepcopy(hour_reference)
    out["kind"] = "personal_hour_fusion"
    out["hour_fusion_policy_version"] = HOUR_FUSION_POLICY_VERSION
    out["hour_fusion_status"] = HOUR_FUSION_STATUS
    out["event_code"] = event_code
    out["event_day_context_present"] = event_day is not None
    out["event_day"] = _event_day_summary(event_day)
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
        out["confidence_basis"] = list((event_day or {}).get("confidence_basis") or [])
        out["hour_fusion_ready"] = True
        out["personal_hour_decision_ready"] = True
        out["rules"] = list((event_day or {}).get("rules") or [])
        out["sources"] = list((event_day or {}).get("sources") or [])
        for item in hours:
            item["decision_state"] = "INELIGIBLE_BY_DAY"
            item["decision_label"] = "Không xét"
            item["is_personal_good_hour"] = False
            item["is_personal_bad_hour"] = False
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
            "Cần biết loại việc và kết luận của ngày trước khi mở quyết định giờ. "
            "Nếu thiếu bối cảnh này, ứng dụng chỉ hiển thị cấu trúc 12 giờ."
        )
        out["confidence_state"] = "Chưa đủ căn cứ"
        out["confidence_basis"] = ["Thiếu loại việc hoặc kết luận ngày để áp dụng cổng ngày trước giờ."]
        out["hour_fusion_ready"] = False
        out["personal_hour_decision_ready"] = False
        return out

    used_rules: list[str] = []
    used_sources: list[str] = []
    for item in hours:
        item["day_gate"] = "PASS_TO_HOUR_RULES"
        _apply_verified_hour_rule(item)
        if item.get("hour_rule_id") and item["hour_rule_id"] not in used_rules:
            used_rules.append(item["hour_rule_id"])
        if item.get("hour_source_id") and item["hour_source_id"] not in used_sources:
            used_sources.append(item["hour_source_id"])

    out["hours"] = hours
    out["rules"] = used_rules
    out["sources"] = used_sources
    out["evidence"] = [
        {
            "type": "VERIFIED_BRANCH_RELATION_HOUR_POLICY",
            "status": "ACTIVE_LIMITED",
            "rule_count": len(used_rules),
            "source_count": len(used_sources),
        }
    ]
    out["conclusion"] = {
        "state": "HOUR_RULE_DECISION_READY",
        "label": "Đã phân loại giờ theo căn cứ hiện có",
        "title": "Giờ cá nhân đã có lớp ưu tiên/thận trọng giới hạn",
    }
    out["plain_explanation"] = (
        "Ngày đã qua cổng sự kiện. V2.9B dùng các quan hệ Địa Chi đã có Rule ID/Source ID "
        "để phân loại giờ: Lục hợp có thể ưu tiên; Xung/Hại/Hình nên thận trọng; "
        "không có quan hệ trực tiếp thì trung tính. Đây chưa phải hệ cát-hung giờ cổ điển đầy đủ."
    )
    out["confidence_state"] = "Căn cứ vừa"
    out["confidence_basis"] = [
        "Ngày đã qua cổng HARD_BLOCK của sự kiện.",
        "Quyết định giờ chỉ dùng quan hệ Địa Chi có Rule ID/Source ID trong phạm vi V2.9B.",
        "Chưa triển khai đầy đủ hệ cát-hung giờ cổ điển nên không nâng thành khẳng định tuyệt đối.",
    ]
    out["hour_fusion_ready"] = True
    out["personal_hour_decision_ready"] = True
    return out


def v29_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    """Công bố capability V2.9B mà không đổi public schema 2.5."""
    out = dict(base)
    scopes = list(out.get("implemented_scopes") or [])
    for scope in ("personal_hour_event_day_gate", "personal_hour_verified_rule_decision"):
        if scope not in scopes:
            scopes.append(scope)
    out["implemented_scopes"] = scopes
    pending = [x for x in (out.get("pending_scopes") or []) if x != "personal_hour_verified_rule_decision"]
    if "personal_hour_full_classical_auspiciousness" not in pending:
        pending.append("personal_hour_full_classical_auspiciousness")
    out["pending_scopes"] = pending
    out["hour_fusion_v29"] = {
        "policy_version": HOUR_FUSION_POLICY_VERSION,
        "status": HOUR_FUSION_STATUS,
        "event_day_gate_ready": True,
        "verified_hour_rule_decision_ready": True,
        "full_classical_hour_auspiciousness_ready": False,
        "hard_block_can_be_rescued_by_hour": False,
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
    principles = list(out.get("principles") or [])
    note = (
        "V2.9B xét ngày/sự kiện trước giờ; chỉ quan hệ giờ có Rule ID/Source ID mới được "
        "dùng để ưu tiên/thận trọng, và HARD_BLOCK của ngày không thể được giờ đảo ngược."
    )
    if note not in principles:
        principles.append(note)
    out["principles"] = principles
    return out
