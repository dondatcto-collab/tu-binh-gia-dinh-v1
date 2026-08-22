"""Mô hình dữ liệu của Rule Registry.

Một quy tắc gồm hai phần:
  - RuleIdentity: danh tính, không đổi.
  - RuleVersion:  nội dung, mỗi lần sửa là một phiên bản mới.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from loi.nen.trang_thai import (
    BlockType,
    Confidence,
    EffectClass,
    RuleStatus,
    Severity,
    SourceLevel,
)


@dataclass
class RuleSourceLink:
    source_id: str
    source_level: SourceLevel
    source_location: str | None = None
    original_text: str | None = None
    translation_vi: str | None = None
    logic_note: str | None = None


@dataclass
class RuleTestCase:
    rule_test_case_id: str
    description: str
    input_payload: dict[str, Any]
    expected_payload: dict[str, Any] | None = None
    review_status: str = "PENDING"


@dataclass
class RuleIdentity:
    rule_id: str
    rule_group: str
    namespace: str
    name_vi: str
    name_original: str | None = None
    active_version: int | None = None
    is_active: bool = False


@dataclass
class RuleVersion:
    rule_id: str
    version: int
    status: RuleStatus
    effect_class: EffectClass

    inputs: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    logic: dict[str, Any] | None = None
    outputs: list[str] = field(default_factory=list)

    confidence: Confidence = Confidence.LOW
    priority: int = 100
    block_type: BlockType = BlockType.NONE
    severity: Severity = Severity.MINOR
    mitigatable: bool = False
    max_effect: float | None = None

    conflict_group: str | None = None
    duplication_group: str | None = None
    causal_family: str | None = None
    effect_domain: str | None = None

    notes: str | None = None
    locked: bool = False

    sources: list[RuleSourceLink] = field(default_factory=list)
    test_cases: list[RuleTestCase] = field(default_factory=list)

    @property
    def rule_version_id(self) -> str:
        return f"{self.rule_id}@{self.version}"

    def to_row(self) -> dict[str, Any]:
        return {
            "rule_version_id": self.rule_version_id,
            "rule_id": self.rule_id,
            "version": self.version,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "inputs": json.dumps(self.inputs, ensure_ascii=False),
            "preconditions": json.dumps(self.preconditions, ensure_ascii=False),
            "logic": json.dumps(self.logic, ensure_ascii=False) if self.logic else None,
            "outputs": json.dumps(self.outputs, ensure_ascii=False),
            "effect_class": self.effect_class.value,
            "priority": self.priority,
            "block_type": self.block_type.value,
            "severity": self.severity.value,
            "mitigatable": int(self.mitigatable),
            "max_effect": self.max_effect,
            "conflict_group": self.conflict_group,
            "duplication_group": self.duplication_group,
            "causal_family": self.causal_family,
            "effect_domain": self.effect_domain,
            "notes": self.notes,
            "locked": int(self.locked),
        }
