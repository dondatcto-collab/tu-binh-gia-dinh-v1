"""V3.0E10 — ma trận độ phủ Hiệp Kỷ theo 12 loại việc.

Mục tiêu: quyết định khi nào V1 Engine "đủ dùng" bằng độ phủ theo việc,
không chạy theo tỷ lệ 81/81. Module này chỉ đo coverage; không thay đổi quyết định.
"""
from __future__ import annotations

from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_v25 import HK_V25_EVENT_RULES

TARGET_ACTIVE_RULES = 45
TARGET_ACTIVE_RULES_MIN = 42
TARGET_ACTIVE_RULES_MAX = 48
MIN_ACTIVE_YI_PER_VERIFIED_EVENT = 2
MIN_ACTIVE_JI_PER_VERIFIED_EVENT = 2


def _active(token: str) -> bool:
    return token_capability(token)["calculator_status"] == "ACTIVE_CALCULABLE"


def event_coverage_rows() -> tuple[dict, ...]:
    rows: list[dict] = []
    for code, rule in HK_V25_EVENT_RULES.items():
        active_yi = tuple(t for t in rule.yi_tokens if _active(t))
        active_ji = tuple(t for t in rule.ji_tokens if _active(t))
        pending_yi = tuple(t for t in rule.yi_tokens if not _active(t))
        pending_ji = tuple(t for t in rule.ji_tokens if not _active(t))
        yi_ok = len(active_yi) >= MIN_ACTIVE_YI_PER_VERIFIED_EVENT
        ji_ok = len(active_ji) >= MIN_ACTIVE_JI_PER_VERIFIED_EVENT
        rows.append({
            "event_code": code,
            "classical": rule.classical,
            "mapping_status": rule.mapping_status,
            "active_yi_count": len(active_yi),
            "active_ji_count": len(active_ji),
            "active_yi_tokens": active_yi,
            "active_ji_tokens": active_ji,
            "pending_yi_tokens": pending_yi,
            "pending_ji_tokens": pending_ji,
            "verified_balance_gate": (yi_ok and ji_ok) if rule.mapping_status == "VERIFIED" else None,
        })
    return tuple(rows)


def v1_engine_readiness() -> dict:
    cap = capability_inventory()
    rows = event_coverage_rows()
    verified = tuple(r for r in rows if r["mapping_status"] == "VERIFIED")
    failed = tuple(r["event_code"] for r in verified if not r["verified_balance_gate"])
    active_count = int(cap["active_calculable_count"])
    rule_target_gate = TARGET_ACTIVE_RULES_MIN <= active_count <= TARGET_ACTIVE_RULES_MAX
    return {
        "strategy": "COVERAGE_FIRST_NOT_81_OF_81",
        "target_active_rules": TARGET_ACTIVE_RULES,
        "target_band": (TARGET_ACTIVE_RULES_MIN, TARGET_ACTIVE_RULES_MAX),
        "active_calculable_count": active_count,
        "pending_calculator_count": int(cap["pending_calculator_count"]),
        "event_count": len(rows),
        "verified_event_count": len(verified),
        "verified_balance_failed_events": failed,
        "verified_balance_gate": not failed,
        "rule_target_gate": rule_target_gate,
        "v1_engine_ready": bool(rule_target_gate and not failed),
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
