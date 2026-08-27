"""V2.5 — runtime Hiệp Kỷ mở rộng có kiểm soát.

Giữ 12 Trực V1 làm lớp quyết định gốc. Năm token tháng-ngày đã có bộ tính
được dùng bổ sung: tín hiệu JI mới chỉ tạo CAUTION, không tự tạo HARD_BLOCK.
HARD_BLOCK hiện vẫn chỉ đến từ lớp sự kiện V1 đã nghiệm thu.
"""
from __future__ import annotations

from typing import Any

from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_month_v25 import active_month_tokens
from loi.quyet_dinh.hiep_ky_policy_v25 import resolve_conflict

COVERAGE = "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"
ACTIVE_EXTRA_TOKENS = frozenset({"月建", "月破", "三合", "六合", "月害"})


def _personal_signal(personal: dict[str, Any]) -> str:
    state = personal.get("state")
    if state == "SUPPORT":
        return "FAVORABLE"
    if state == "CAUTION":
        return "CAUTION"
    if state == "DESCRIPTIVE_ONLY":
        return "UNKNOWN"
    return "NEUTRAL"


def _rank(result: dict[str, Any]) -> int:
    if result["state"] == "BLOCKED":
        return 9
    if result["label"] == "Ưu tiên":
        return 1
    if result["label"] == "Có thể cân nhắc":
        return 2
    if result["label"] == "Không ưu tiên":
        return 4
    if result["state"] == "INSUFFICIENT":
        return 5
    return 3


def evaluate_event_v25(
    base_event: dict[str, Any],
    personal: dict[str, Any],
    *,
    chi_thang: str,
    chi_ngay: str,
) -> dict[str, Any]:
    """Hợp lưu event V1 + 5 token Hiệp Kỷ tháng-ngày + nền cá nhân."""
    out = dict(base_event)
    event_code = out.get("event_code")
    active = set(active_month_tokens(chi_thang, chi_ngay))
    evidence = tuple(evidence_for_event(event_code)) if event_code else ()
    matched = [x for x in evidence if x.token in active and x.token in ACTIVE_EXTRA_TOKENS]
    yi_hits = [x for x in matched if x.polarity == "YI"]
    ji_hits = [x for x in matched if x.polarity == "JI"]

    base_state = out.get("event_state", "NEUTRAL")
    hard_block = base_state == "JI"
    if hard_block:
        event_signal = "HARD_BLOCK"
    elif ji_hits:
        event_signal = "CAUTION"
    elif base_state == "YI" or yi_hits:
        event_signal = "FAVORABLE"
    else:
        event_signal = "NEUTRAL"

    decision = resolve_conflict(
        hard_block=hard_block,
        event_state=event_signal,
        personal_state=_personal_signal(personal),
    )

    # Ánh xạ hiện đại PROVISIONAL không được nâng thành "Ưu tiên" chỉ nhờ tín hiệu mới.
    if out.get("mapping_status") == "PROVISIONAL" and decision["label"] == "Ưu tiên":
        decision = {**decision, "state": "CONSIDER", "label": "Có thể cân nhắc", "authority": "EVENT_PROVISIONAL"}

    reasons = list(out.get("reasons") or [])
    if yi_hits:
        reasons.append("Hiệp Kỷ V2.5 ghi nhận thêm tín hiệu phù hợp: " + ", ".join(x.token for x in yi_hits) + ".")
    if ji_hits:
        reasons.append("Hiệp Kỷ V2.5 ghi nhận tín hiệu cần thận trọng: " + ", ".join(x.token for x in ji_hits) + "; lớp này chưa tự tạo HARD_BLOCK.")
    reasons.append("V2.5 phân xử theo thứ bậc HARD_BLOCK > sự kiện > cá nhân; không cộng/trừ điểm.")

    personal_context = {
        "theme": personal.get("theme"),
        "branch_impacts": personal.get("branch_impacts", []),
        "headline": personal.get("dien_giai", {}).get("headline"),
        "technical_facts": personal.get("technical_facts", []),
        "interpretation_status": "ZPZQ_PERSONAL_0_5",
        "decision_effect": personal.get("state", "DESCRIPTIVE_ONLY"),
    }
    rule_ids = sorted(set(list(out.get("rule_ids") or []) + list(personal.get("rule_ids") or []) + [x.rule_id for x in matched]))
    src = set(personal.get("source_ids") or [])
    if out.get("source_id"):
        src.add(out["source_id"])
    src.update(x.source_id for x in matched)

    return {
        **out,
        "event_state_v1": base_state,
        "event_state": "JI" if hard_block else ("YI" if event_signal == "FAVORABLE" else ("CAUTION" if event_signal == "CAUTION" else "NEUTRAL")),
        "event_signal_v25": event_signal,
        "active_hiep_ky_tokens": sorted(active),
        "matched_yi_tokens": [x.token for x in yi_hits],
        "matched_ji_tokens": [x.token for x in ji_hits],
        "matched_evidence": [
            {"rule_id": x.rule_id, "token": x.token, "polarity": x.polarity, "source_id": x.source_id,
             "source_location": x.source_location, "evidence_status": x.evidence_status, "decision_status": "ACTIVE"}
            for x in matched
        ],
        "decision_state": decision["state"],
        "label": decision["label"],
        "decision_authority": decision["authority"],
        "hard_block": hard_block,
        "rank_group": _rank(decision),
        "personal_v1_1": personal_context,
        "personal_methodology": personal.get("methodology"),
        "reasons": reasons,
        "rule_ids": rule_ids,
        "source_ids": sorted(src),
        "coverage": COVERAGE,
        "numeric_score": None,
        "score": None,
        "numeric_score_status": "LOCKED_OFF",
        "scoring_status": "NO_NUMERIC_SCORE",
    }
