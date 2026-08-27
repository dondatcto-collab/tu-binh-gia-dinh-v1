"""Sinh evidence traceable từ inventory Hiệp Kỷ V2.5.

Không tính ngày, không tính thần sát, không thay đổi quyết định. Mục tiêu duy nhất:
mỗi token cổ thư phải có Rule ID ổn định và vị trí nguồn rõ ràng trước khi kích hoạt.
"""
from __future__ import annotations

import hashlib

from loi.quyet_dinh.hiep_ky_policy_v25 import RuleEvidence
from loi.quyet_dinh.hiep_ky_v25 import HK_V25_EVENT_RULES


def _rule_id(event_code: str, polarity: str, token: str) -> str:
    digest = hashlib.sha1(f"{event_code}|{polarity}|{token}".encode("utf-8")).hexdigest()[:10].upper()
    return f"HK25-{event_code}-{polarity}-{digest}"


def evidence_for_event(event_code: str) -> tuple[RuleEvidence, ...]:
    rule = HK_V25_EVENT_RULES[event_code]
    evidence_status = "VERIFIED" if rule.mapping_status == "VERIFIED" else "PROVISIONAL"
    items: list[RuleEvidence] = []
    for token in rule.yi_tokens:
        items.append(
            RuleEvidence(
                rule_id=_rule_id(event_code, "YI", token),
                event_code=event_code,
                token=token,
                polarity="YI",
                source_id=rule.source_id,
                source_location=rule.source_location,
                evidence_status=evidence_status,
            )
        )
    for token in rule.ji_tokens:
        items.append(
            RuleEvidence(
                rule_id=_rule_id(event_code, "JI", token),
                event_code=event_code,
                token=token,
                polarity="JI",
                source_id=rule.source_id,
                source_location=rule.source_location,
                evidence_status=evidence_status,
            )
        )
    return tuple(items)


def all_evidence() -> tuple[RuleEvidence, ...]:
    items: list[RuleEvidence] = []
    for event_code in HK_V25_EVENT_RULES:
        items.extend(evidence_for_event(event_code))
    return tuple(items)


def evidence_status() -> dict:
    items = all_evidence()
    return {
        "event_count": len(HK_V25_EVENT_RULES),
        "evidence_count": len(items),
        "rule_id_count": len({x.rule_id for x in items}),
        "source_location_count": len({x.source_location for x in items}),
        "decision_status": "INVENTORY_ONLY",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
