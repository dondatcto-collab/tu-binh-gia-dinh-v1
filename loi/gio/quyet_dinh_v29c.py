"""V2.9C — hợp lưu quyết định giờ từ hai lớp evidence độc lập đang có.

Lớp 1: quan hệ Địa Chi giờ của V2.9B.
Lớp 2: Can Chi giờ + Hỷ/Kỵ theo Cách cục ZPZQ hiện hành.

Không cộng điểm, không trung bình hóa. Cảnh báo thắng ưu tiên khi evidence xung đột.
Giờ Tý có tranh luận ranh giới Can giờ nên chỉ giữ quyết định quan hệ Chi V2.9B.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

HOUR_SCIENCE_POLICY_VERSION = "2.9C-alpha.1"
HOUR_SCIENCE_STATUS = "V2_9C_STEM_BRANCH_XIJI_FUSION"


def _merge_unique(*parts: list[str]) -> list[str]:
    out: list[str] = []
    for part in parts:
        for x in part or []:
            if x and x not in out:
                out.append(x)
    return out


def _apply_two_layer_decision(item: dict[str, Any], personal: dict[str, Any]) -> None:
    relation_state = item.get("decision_state")
    personal_state = personal.get("personal_transit_state")

    item.update({
        "hour_can": personal.get("hour_can"),
        "hour_can_vi": personal.get("hour_can_vi"),
        "day_can": personal.get("day_can"),
        "day_can_vi": personal.get("day_can_vi"),
        "day_chi": personal.get("day_chi"),
        "day_chi_vi": personal.get("day_chi_vi"),
        "personal_transit_state": personal_state,
        "personal_transit_label": personal.get("personal_transit_label"),
        "stem_ten_god": personal.get("stem_ten_god"),
        "stem_effect": personal.get("stem_effect"),
        "branch_effect": personal.get("branch_effect"),
        "hour_personal_rule_ids": list(personal.get("personal_rule_ids") or []),
        "hour_personal_source_ids": list(personal.get("personal_source_ids") or []),
        "hour_stem_rule_id": personal.get("hour_stem_rule_id"),
        "hour_stem_source_id": personal.get("hour_stem_source_id"),
        "hour_stem_boundary_status": personal.get("hour_stem_boundary_status"),
        "hour_stem_conflict_id": personal.get("hour_stem_conflict_id"),
        "hour_stem_note": personal.get("hour_stem_note"),
    })

    if personal.get("hour_stem_boundary_status") == "CONFLICTED_LATE_ZI":
        item["fusion_alignment"] = "LATE_ZI_GUARDED_RELATION_ONLY"
        item["decision_basis"] = (
            f"{item.get('decision_basis') or ''} Can giờ Tý chưa được dùng vì TIME-0007 còn CONFLICTED."
        ).strip()
        return

    relation_caution = relation_state == "PERSONAL_CAUTION_HOUR"
    relation_support = relation_state == "PERSONAL_GOOD_CANDIDATE"
    personal_caution = personal_state == "CAUTION"
    personal_support = personal_state == "SUPPORT"

    if relation_caution or personal_caution:
        item["decision_state"] = "PERSONAL_CAUTION_HOUR"
        item["decision_label"] = "Nên thận trọng"
        item["is_personal_good_hour"] = False
        item["is_personal_bad_hour"] = False
        item["fusion_alignment"] = (
            "MIXED_CAUTION" if (relation_support or personal_support) else "CAUTION_ALIGNED"
        )
        item["decision_basis"] = (
            "Ít nhất một lớp evidence đã xác minh cho tín hiệu thận trọng; "
            "V2.9C không lấy lớp thuận để triệt tiêu lớp cảnh báo."
        )
        return

    if relation_support and personal_support:
        item["decision_state"] = "PERSONAL_GOOD_CANDIDATE"
        item["decision_label"] = "Ưu tiên hơn"
        item["is_personal_good_hour"] = True
        item["is_personal_bad_hour"] = False
        item["fusion_alignment"] = "DOUBLE_SUPPORT"
        item["decision_basis"] = (
            "Quan hệ Chi thuận và Hỷ/Kỵ theo Can Chi giờ cùng hỗ trợ; đây là đồng thuận hai lớp, "
            "không phải điểm số hay cát tuyệt đối."
        )
        return

    if relation_support:
        item["fusion_alignment"] = "RELATION_SUPPORT_ONLY"
        return

    if personal_support:
        item["decision_state"] = "PERSONAL_GOOD_CANDIDATE"
        item["decision_label"] = "Có thể ưu tiên"
        item["is_personal_good_hour"] = True
        item["is_personal_bad_hour"] = False
        item["fusion_alignment"] = "PERSONAL_SUPPORT_ONLY"
        item["decision_basis"] = (
            "Quan hệ Chi không cho tín hiệu trực tiếp nhưng Can Chi giờ thuận nền Cách cục/Hỷ-Kỵ đã khóa."
        )
        return

    item["fusion_alignment"] = "NEUTRAL_ALIGNED"


def enrich_hour_fusion_v29c(
    fused: dict[str, Any], *, personal_hours: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Nâng output V2.9B bằng evidence Can Chi/Hỷ-Kỵ mà không phá contract cũ."""
    out = deepcopy(fused)
    out["hour_science_policy_version"] = HOUR_SCIENCE_POLICY_VERSION
    out["hour_science_status"] = HOUR_SCIENCE_STATUS
    out["numeric_score"] = None
    out["numeric_score_status"] = "LOCKED_OFF"

    state = str((out.get("conclusion") or {}).get("state") or "")
    if state == "BLOCKED_BY_DAY":
        out["hour_science_ready"] = True
        out["hour_stem_branch_xiji_ready"] = True
        out["hour_science_note"] = "Không chạy lớp Hỷ/Kỵ giờ vì HARD_BLOCK của ngày đã kết thúc quyết định."
        return out

    if state != "HOUR_RULE_DECISION_READY" or not personal_hours:
        out["hour_science_ready"] = False
        out["hour_stem_branch_xiji_ready"] = False
        return out

    by_chi = {x.get("chi"): x for x in personal_hours if x.get("chi")}
    all_personal_rules: list[str] = []
    all_personal_sources: list[str] = []
    guarded = 0
    for item in out.get("hours") or []:
        personal = by_chi.get(item.get("chi"))
        if not personal:
            item["fusion_alignment"] = "PERSONAL_CONTEXT_MISSING"
            continue
        _apply_two_layer_decision(item, personal)
        all_personal_rules = _merge_unique(all_personal_rules, list(personal.get("personal_rule_ids") or []))
        all_personal_sources = _merge_unique(all_personal_sources, list(personal.get("personal_source_ids") or []))
        if personal.get("hour_stem_boundary_status") == "CONFLICTED_LATE_ZI":
            guarded += 1

    out["rules"] = _merge_unique(list(out.get("rules") or []), all_personal_rules)
    out["sources"] = _merge_unique(list(out.get("sources") or []), all_personal_sources)
    evidence = list(out.get("evidence") or [])
    evidence.extend([
        {
            "type": "VERIFIED_HOUR_STEM_NGU_THU_DON",
            "status": "ACTIVE_EXCEPT_LATE_ZI",
            "source_id": "SRC-UHTB-CHEP",
            "conflict_guard": "TIME-0007",
        },
        {
            "type": "ZPZQ_PERSONAL_HOUR_TRANSIT",
            "status": "ACTIVE_LIMITED",
            "policy": "CAUTION_OVERRIDES_SUPPORT_NO_NUMERIC_SCORE",
        },
    ])
    out["evidence"] = evidence
    out["hour_science_ready"] = True
    out["hour_stem_branch_xiji_ready"] = True
    out["late_zi_guarded_hours"] = guarded
    out["conclusion"] = {
        **dict(out.get("conclusion") or {}),
        "title": "Giờ cá nhân đã hợp lưu quan hệ Chi + Can Chi/Hỷ-Kỵ",
        "label": "Đã phân loại giờ theo hai lớp căn cứ",
    }
    out["plain_explanation"] = (
        "Ngày đã qua cổng sự kiện. V2.9C hợp lưu quan hệ Địa Chi của V2.9B với Can Chi giờ "
        "và Hỷ/Kỵ theo Cách cục ZPZQ. Cảnh báo không bị tín hiệu thuận xóa; đồng thuận hai lớp "
        "được gọi là ‘Ưu tiên hơn’. Giờ Tý vẫn giữ bảo thủ vì TIME-0007 còn tranh luận."
    )
    out["confidence_state"] = "Căn cứ vừa"
    out["confidence_basis"] = [
        "Ngày đã qua cổng HARD_BLOCK của sự kiện.",
        "Quan hệ Chi giờ có Rule ID/Source ID và Ngũ Thử Độn có nguồn VERIFIED.",
        "Hỷ/Kỵ giờ tái sử dụng cùng engine Cách cục ZPZQ đã khóa cho ngày/tháng.",
        "TIME-0007 của Can giờ Tý còn CONFLICTED nên lớp Can giờ Tý bị khóa bảo thủ.",
        "Chưa triển khai toàn bộ hệ cát-hung giờ cổ điển nên confidence không nâng thành tuyệt đối.",
    ]
    return out


def v29c_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    scopes = list(out.get("implemented_scopes") or [])
    scope = "personal_hour_stem_branch_xiji_fusion"
    if scope not in scopes:
        scopes.append(scope)
    out["implemented_scopes"] = scopes
    out["hour_science_v29c"] = {
        "policy_version": HOUR_SCIENCE_POLICY_VERSION,
        "status": HOUR_SCIENCE_STATUS,
        "stem_branch_xiji_fusion_ready": True,
        "nguthudon_source_verified": True,
        "hour_stem_source_id": "SRC-UHTB-CHEP",
        "late_zi_conflict_guard": True,
        "late_zi_conflict_id": "TIME-0007",
        "full_classical_hour_auspiciousness_ready": False,
        "hard_block_can_be_rescued_by_hour": False,
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
    principles = list(out.get("principles") or [])
    note = (
        "V2.9C hợp lưu quan hệ Chi + Can Chi/Hỷ-Kỵ theo thứ bậc bảo thủ; cảnh báo thắng tín hiệu thuận, "
        "và Can giờ Tý không tham gia quyết định khi TIME-0007 còn CONFLICTED."
    )
    if note not in principles:
        principles.append(note)
    out["principles"] = principles
    return out
