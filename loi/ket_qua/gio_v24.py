"""V2.4 — chuẩn hóa lớp giờ cá nhân ở mức tham khảo cấu trúc.

Không sinh nhãn giờ tốt/xấu cá nhân. Không numeric score. Không cho giờ đảo
kết quả ngày hoặc HARD_BLOCK. Đây là lớp an toàn cho đến khi có hợp lưu giờ
+ ngày + nền mệnh và ca vàng riêng.
"""
from __future__ import annotations
from typing import Any

HOUR_SCHEMA_VERSION = "2.4-alpha.1"
HOUR_STATUS = "V2_4_HOUR_REFERENCE_ALPHA"


def hour_reference_result(raw: dict[str, Any]) -> dict[str, Any]:
    items = []
    for x in raw.get("gio_trong_ngay") or []:
        items.append({
            "chi": x.get("chi"),
            "chi_vi": x.get("chi_vi"),
            "time_range": x.get("khoang_gio"),
            "relation": x.get("relation"),
            "relation_label": x.get("nhan"),
            "relation_nature": x.get("relation_nature"),
            "explanation": x.get("ly_do"),
            "decision_state": "DESCRIPTIVE_ONLY",
            "is_personal_good_hour": None,
            "is_personal_bad_hour": None,
        })
    return {
        "schema_version": HOUR_SCHEMA_VERSION,
        "kind": "personal_hour_reference",
        "scope": "hour",
        "domain": "general",
        "date": raw.get("ngay"),
        "status": HOUR_STATUS,
        "conclusion": {
            "state": "DESCRIPTIVE_ONLY",
            "label": "Tham khảo cấu trúc giờ",
            "title": "Chưa đủ căn cứ để gọi giờ tốt/xấu cá nhân",
        },
        "plain_explanation": (
            "Ứng dụng đã tính được quan hệ cấu trúc của 12 giờ với nền ngày sinh, "
            "nhưng chưa hoàn tất hợp lưu Can Chi giờ + ngày + nền mệnh bằng ca vàng riêng."
        ),
        "recommended_actions": ["Dùng danh sách giờ để tham khảo cấu trúc, không dùng như quyết định cuối."],
        "cautions": [
            "Không dùng giờ để cứu một ngày đã bị chặn.",
            "Không hiểu quan hệ hợp/xung đơn lẻ là giờ tốt/xấu cá nhân.",
        ],
        "confidence_state": "Chưa đủ căn cứ",
        "hour_structure_ready": True,
        "hour_fusion_ready": False,
        "personal_hour_decision_ready": False,
        "hours": items,
        "evidence": [{"type": "BRANCH_RELATION_STRUCTURE", "status": "STRUCTURAL_ONLY"}],
        "rules": [],
        "sources": [],
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }


def v24_schema_overlay(base: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    out["schema_version"] = HOUR_SCHEMA_VERSION
    out["status"] = HOUR_STATUS
    scopes = list(out.get("implemented_scopes") or [])
    if "personal_hour_reference" not in scopes:
        scopes.append("personal_hour_reference")
    out["implemented_scopes"] = scopes
    pending = [x for x in (out.get("pending_scopes") or []) if x != "personal_hour"]
    if "personal_hour_decision" not in pending:
        pending.append("personal_hour_decision")
    out["pending_scopes"] = pending
    principles = list(out.get("principles") or [])
    principles.append("Giờ V2.4 chỉ là tham khảo cấu trúc; chưa được gọi là giờ tốt/xấu cá nhân")
    out["principles"] = principles
    out["hour_readiness"] = {
        "hour_structure_ready": True,
        "hour_fusion_ready": False,
        "personal_hour_decision_ready": False,
    }
    return out
