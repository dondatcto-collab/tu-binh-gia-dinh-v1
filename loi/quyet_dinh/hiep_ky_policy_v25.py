"""V2.5 — policy thuần dữ liệu cho evidence và phân xử xung đột Hiệp Kỷ.

Module này KHÔNG tính thần sát. Nó chỉ khóa contract để các bộ tính sau này
không thể vượt thứ bậc HARD_BLOCK > EVENT > PERSONAL hoặc bật điểm số.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EvidenceStatus = Literal["VERIFIED", "PROVISIONAL", "PENDING"]
SignalState = Literal["HARD_BLOCK", "FAVORABLE", "CAUTION", "NEUTRAL", "UNKNOWN"]
DecisionState = Literal["BLOCKED", "FAVORABLE", "CONSIDER", "NEUTRAL", "INSUFFICIENT"]

NUMERIC_SCORE_STATUS = "LOCKED_OFF"
DECISION_HIERARCHY = "HARD_BLOCK > EVENT > PERSONAL"


@dataclass(frozen=True)
class RuleEvidence:
    rule_id: str
    event_code: str
    token: str
    polarity: Literal["YI", "JI"]
    source_id: str
    source_location: str
    evidence_status: EvidenceStatus
    decision_status: Literal["INVENTORY_ONLY", "ACTIVE"] = "INVENTORY_ONLY"
    numeric_score: None = None


def resolve_conflict(
    *,
    hard_block: bool,
    event_state: SignalState,
    personal_state: SignalState,
) -> dict:
    """Phân xử ordinal, tuyệt đối không cộng/trừ điểm.

    5 nguyên tắc khóa:
    1) personal + event thuận => FAVORABLE;
    2) HARD_BLOCK thắng mọi tín hiệu;
    3) event thuận + personal nghịch => CONSIDER;
    4) bối cảnh thuận không cứu HARD_BLOCK/ngày bị chặn;
    5) personal chỉ phá hòa khi event không có quyết định mạnh.
    """
    if hard_block or event_state == "HARD_BLOCK":
        state, label, authority = "BLOCKED", "Bị chặn", "HARD_BLOCK"
    elif event_state == "FAVORABLE":
        if personal_state in {"CAUTION", "HARD_BLOCK"}:
            state, label, authority = "CONSIDER", "Có thể cân nhắc", "EVENT_WITH_PERSONAL_CAUTION"
        else:
            state, label, authority = "FAVORABLE", "Ưu tiên", "EVENT"
    elif event_state == "CAUTION":
        state, label, authority = "CONSIDER", "Không ưu tiên", "EVENT"
    elif event_state in {"NEUTRAL", "UNKNOWN"}:
        if personal_state == "FAVORABLE":
            state, label, authority = "CONSIDER", "Có thể cân nhắc", "PERSONAL_TIE_BREAK"
        elif personal_state in {"CAUTION", "HARD_BLOCK"}:
            state, label, authority = "CONSIDER", "Không ưu tiên", "PERSONAL_TIE_BREAK"
        elif event_state == "UNKNOWN" and personal_state == "UNKNOWN":
            state, label, authority = "INSUFFICIENT", "Chưa đủ căn cứ", "NONE"
        else:
            state, label, authority = "NEUTRAL", "Chưa có tín hiệu rõ", "NONE"
    else:
        state, label, authority = "INSUFFICIENT", "Chưa đủ căn cứ", "NONE"

    return {
        "state": state,
        "label": label,
        "authority": authority,
        "hierarchy": DECISION_HIERARCHY,
        "numeric_score": None,
        "numeric_score_status": NUMERIC_SCORE_STATUS,
    }
