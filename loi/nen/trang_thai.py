"""Các tập trạng thái dùng chung. Đây là nguồn duy nhất, không khai báo lại nơi khác."""

from __future__ import annotations

from enum import Enum


class RuleStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PROVISIONAL = "PROVISIONAL"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"


class EffectClass(str, Enum):
    SCORING = "SCORING"
    HARD_BLOCK = "HARD_BLOCK"
    MITIGATION = "MITIGATION"
    EXPLANATORY = "EXPLANATORY"
    EXPERIMENTAL = "EXPERIMENTAL"
    DISABLED = "DISABLED"


class BlockType(str, Enum):
    ABSOLUTE = "ABSOLUTE"
    EVENT_SPECIFIC = "EVENT_SPECIFIC"
    CONDITIONAL = "CONDITIONAL"
    NONE = "NONE"


class Severity(str, Enum):
    MAJOR = "MAJOR"
    MEDIUM = "MEDIUM"
    MINOR = "MINOR"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SourceLevel(str, Enum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CROSS_REFERENCE = "CROSS_REFERENCE"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_REWORK = "NEEDS_REWORK"


class GoldenCategory(str, Enum):
    CAL = "GOLD-CAL"
    BT = "GOLD-BT"
    HK = "GOLD-HK"
    SS = "GOLD-SS"
    FUS = "GOLD-FUS"
    END = "GOLD-END"


class CaseResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"                 # thiếu engine hoặc thiếu dữ liệu
    PENDING_EXCLUDED = "PENDING_EXCLUDED"  # chưa duyệt, không tính vào tỷ lệ


# Chỉ những trạng thái này được đưa vào tính điểm chính thức.
TRANG_THAI_DUOC_CHAM_DIEM = frozenset({RuleStatus.VERIFIED})

# Những hạng tác dụng có tham gia tính điểm.
HANG_TAC_DUNG_CHAM_DIEM = frozenset(
    {EffectClass.SCORING, EffectClass.HARD_BLOCK, EffectClass.MITIGATION}
)
