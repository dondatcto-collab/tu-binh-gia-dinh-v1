"""V2.8 — Confidence dựa trên chất lượng bằng chứng, không dựa trên độ mạnh của nhãn.

Module này KHÔNG đổi decision/ranking. Nó chỉ chuẩn hóa mức chắc của cách diễn đạt
và trả về basis có thể truy nguyên để UI giải thích.
"""
from __future__ import annotations

from typing import Any

CONFIDENCE_MODEL_VERSION = "2.8-alpha.1"
CLEAR = "Căn cứ rõ"
MEDIUM = "Căn cứ vừa"
INSUFFICIENT = "Chưa đủ căn cứ"


def _certainty_known(value: str | None) -> bool:
    return str(value or "KNOWN").strip().upper() == "KNOWN"


def _event_confidence(result: dict[str, Any], *, time_certainty: str | None) -> tuple[str, list[str]]:
    technical = dict(result.get("technical") or {})
    event_context = dict(result.get("event_context") or {})
    rules = list(result.get("rules") or [])
    sources = list(result.get("sources") or [])
    mapping = str(technical.get("mapping_status") or "").upper()
    authority = str(technical.get("decision_authority") or "EVENT").upper()
    hard_block = bool(event_context.get("hard_block"))
    matched_yi = list(technical.get("matched_yi_tokens") or [])
    matched_ji = list(technical.get("matched_ji_tokens") or [])
    basis: list[str] = []

    if not rules or not sources:
        basis.append("Thiếu Rule ID hoặc Source ID cho kết luận sự kiện.")
        return INSUFFICIENT, basis

    basis.append("Có Rule ID và Source ID truy nguyên được.")
    if mapping == "PROVISIONAL":
        basis.append("Ánh xạ sự kiện hiện đại đang ở mức PROVISIONAL nên confidence bị chặn ở Căn cứ vừa.")
        return MEDIUM, basis
    if mapping and mapping != "VERIFIED":
        basis.append(f"Trạng thái ánh xạ {mapping} chưa đủ để gọi là Căn cứ rõ.")
        return MEDIUM, basis

    if authority == "PERSONAL" and not _certainty_known(time_certainty):
        basis.append("Lớp cá nhân đang tham gia quyết định nhưng giờ sinh không ở trạng thái KNOWN.")
        return MEDIUM, basis

    if matched_yi and matched_ji and not hard_block:
        basis.append("Có đồng thời evidence thuận và nghịch chưa được một hard-block xác minh giải quyết hoàn toàn.")
        return MEDIUM, basis

    if hard_block:
        basis.append("HARD_BLOCK thuộc lớp sự kiện; độ chắc giờ sinh không làm yếu điều kiện chặn đã truy nguồn.")
    elif authority == "EVENT":
        basis.append("Quyết định do lớp sự kiện làm authority chính.")
    else:
        basis.append(f"Decision authority: {authority or 'UNKNOWN'}.")

    return CLEAR, basis


def _domain_confidence(result: dict[str, Any], *, time_certainty: str | None) -> tuple[str, list[str]]:
    rules = list(result.get("rules") or [])
    sources = list(result.get("sources") or [])
    evidence = list(result.get("evidence") or [])
    basis: list[str] = []
    if not rules or not sources:
        basis.append("Kết luận lĩnh vực chưa có đủ Rule ID và Source ID để gọi là căn cứ rõ.")
        return INSUFFICIENT, basis
    basis.append("Có Rule ID và Source ID cho kết luận lĩnh vực.")
    if not _certainty_known(time_certainty):
        basis.append("Giờ sinh chưa ở trạng thái KNOWN nên lớp cá nhân bị hạ confidence.")
        return MEDIUM, basis
    if evidence:
        basis.append("Có evidence cụ thể đi kèm kết luận.")
        return CLEAR, basis
    basis.append("Có rule/source nhưng evidence trực tiếp còn mỏng.")
    return MEDIUM, basis


def _personal_confidence(result: dict[str, Any], *, time_certainty: str | None) -> tuple[str, list[str]]:
    basis: list[str] = []
    technical = result.get("technical")
    if not technical:
        basis.append("Thiếu dữ liệu kỹ thuật nền để đánh giá độ chắc.")
        return INSUFFICIENT, basis
    if not _certainty_known(time_certainty):
        basis.append("Giờ sinh chưa ở trạng thái KNOWN; kết luận cá nhân chỉ nên đọc ở mức tham khảo.")
        return INSUFFICIENT, basis
    basis.append("Có dữ liệu kỹ thuật nền và giờ sinh ở trạng thái KNOWN.")
    basis.append("Lớp cá nhân hiện chưa có traceability Rule/Source đầy đủ nên không nâng lên Căn cứ rõ.")
    return MEDIUM, basis


def _hour_fusion_confidence(result: dict[str, Any]) -> tuple[str, list[str]]:
    state = str((result.get("conclusion") or {}).get("state") or "")
    event_day = dict(result.get("event_day") or {})
    if state == "BLOCKED_BY_DAY":
        level = event_day.get("confidence_state") or result.get("confidence_state") or MEDIUM
        basis = list(event_day.get("confidence_basis") or result.get("confidence_basis") or [])
        if not basis:
            basis = ["Giờ bị khóa bởi kết luận HARD_BLOCK của ngày; confidence kế thừa từ evidence của ngày."]
        return level, basis
    return INSUFFICIENT, list(result.get("confidence_basis") or [
        "V2.9A mới khóa cổng ngày/sự kiện; chưa có rule giờ VERIFIED để phát sinh quyết định giờ cá nhân."
    ])


def apply_confidence_v28(result: dict[str, Any], *, time_certainty: str | None = "KNOWN") -> dict[str, Any]:
    """Trả bản sao result với confidence_state + confidence_basis V2.8.

    Không thay conclusion, ranking, hard-block hay numeric score.
    """
    out = dict(result)
    kind = str(out.get("kind") or "")

    if kind == "event_search":
        out["results"] = [apply_confidence_v28(x, time_certainty=time_certainty) for x in (out.get("results") or [])]
        out["all_results"] = [apply_confidence_v28(x, time_certainty=time_certainty) for x in (out.get("all_results") or [])]
        out["confidence_model_version"] = CONFIDENCE_MODEL_VERSION
        return out

    if kind == "event_day":
        level, basis = _event_confidence(out, time_certainty=time_certainty)
    elif kind == "domain_period":
        level, basis = _domain_confidence(out, time_certainty=time_certainty)
    elif kind == "personal_hour_reference":
        level, basis = INSUFFICIENT, ["Giờ V2.4 mới là tham khảo cấu trúc; chưa có personal-hour decision fusion."]
    elif kind == "personal_hour_fusion":
        level, basis = _hour_fusion_confidence(out)
    elif kind == "personal_period":
        level, basis = _personal_confidence(out, time_certainty=time_certainty)
    else:
        return out

    out["confidence_state"] = level
    out["confidence_basis"] = basis
    out["confidence_model_version"] = CONFIDENCE_MODEL_VERSION
    out.setdefault("numeric_score", None)
    out.setdefault("numeric_score_status", "LOCKED_OFF")
    return out


def v28_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    out["confidence_model"] = {
        "version": CONFIDENCE_MODEL_VERSION,
        "labels": [CLEAR, MEDIUM, INSUFFICIENT],
        "principle": "Evidence quality -> confidence -> wording; confidence does not alter ranking.",
        "provisional_cap": MEDIUM,
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
    principles = list(out.get("principles") or [])
    note = "Confidence V2.8 đi từ chất lượng bằng chứng; không suy confidence từ nhãn Ưu tiên/Bị chặn."
    if note not in principles:
        principles.append(note)
    out["principles"] = principles
    return out
