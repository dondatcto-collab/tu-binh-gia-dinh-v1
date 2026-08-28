"""Canonical public Result Schema cho sản phẩm V2.5.

Các component V2.1-V2.4 được giữ nguyên semantics đã nghiệm thu. Ở biên API,
response được nâng về một schema public duy nhất; phiên bản component cũ được
giữ trong ``component_schema_version`` để không làm mất truy nguyên.
"""
from __future__ import annotations

from typing import Any

PRODUCT_SCHEMA_VERSION = "2.5-alpha.1"
PRODUCT_STATUS = "V2_5_HIEP_KY_PARTIAL_ACTIVE"


def canonicalize_v25(result: dict[str, Any]) -> dict[str, Any]:
    """Đưa một Result object về schema public V2.5 mà không đổi semantics."""
    out = dict(result)
    component_version = out.get("schema_version")
    if component_version and component_version != PRODUCT_SCHEMA_VERSION:
        out["component_schema_version"] = component_version
    out["schema_version"] = PRODUCT_SCHEMA_VERSION
    out["product_schema_version"] = PRODUCT_SCHEMA_VERSION
    out.setdefault("numeric_score", None)
    out.setdefault("numeric_score_status", "LOCKED_OFF")
    return out
