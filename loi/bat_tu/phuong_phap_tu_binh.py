"""Cổng phương pháp Tử Bình Chân Thuyên cho release 0.5.0 + trạng thái V2.9C.

Phân biệt rõ ba lớp: cấu trúc giờ, quyết định giờ cá nhân có hợp lưu Can Chi/Hỷ-Kỵ,
và hệ cát-hung giờ cổ điển đầy đủ. V2.9C mở sâu lớp thứ hai nhưng không được
suy diễn rằng toàn bộ hệ giờ cổ điển đã hoàn tất.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

PHUONG_PHAP_ID = "ZPZQ-GEJU-V1"
PHUONG_PHAP_TEN = "Tử Bình Chân Thuyên — nguyệt lệnh/cách cục"
RULE_IDS = (
    "BT-BASE-0401","BT-USE-0401","BT-DY-0401",
    "BT-REL-0001","BT-REL-0002","BT-REL-0003","BT-REL-0004",
)
SOURCE_IDS = (
    "SRC-ZPZQ-NLC-SCAN", "SRC-ZPZQ-DONGLI", "SRC-TMTH-V02-WIKISOURCE",
    "SRC-UHTB-CHEP",
)

@dataclass(frozen=True)
class TrangThaiPhuongPhap:
    method_id: str
    method_name: str
    natal_chart_ready: bool
    month_command_ready: bool
    ten_god_ready: bool
    branch_relation_ready: bool
    strength_engine_ready: bool
    pattern_engine_ready: bool
    use_favor_avoid_ready: bool
    transit_fusion_ready: bool
    personal_decision_ready: bool
    hour_structure_ready: bool
    hour_fusion_ready: bool
    personal_hour_decision_ready: bool
    decision_mode: str
    reason_vi: str
    rule_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    def to_dict(self) -> dict[str, Any]:
        d=asdict(self); d["rule_ids"]=list(self.rule_ids); d["source_ids"]=list(self.source_ids); return d

def trang_thai_hien_tai() -> TrangThaiPhuongPhap:
    return TrangThaiPhuongPhap(
        method_id=PHUONG_PHAP_ID, method_name=PHUONG_PHAP_TEN,
        natal_chart_ready=True, month_command_ready=True, ten_god_ready=True,
        branch_relation_ready=True, strength_engine_ready=True, pattern_engine_ready=True,
        use_favor_avoid_ready=True, transit_fusion_ready=True,
        personal_decision_ready=True,
        hour_structure_ready=True,
        hour_fusion_ready=True,
        personal_hour_decision_ready=True,
        decision_mode="ZPZQ_PERSONAL",
        reason_vi=("Engine 0.5.0 đã khóa Cách cục/Hỷ-Kỵ cho quyết định cá nhân. "
                   "V2.9C giữ cổng ngày/sự kiện của V2.9B và hợp lưu sâu thêm Can Chi giờ với "
                   "Hỷ/Kỵ theo cùng engine ZPZQ; quan hệ Chi vẫn là một lớp evidence độc lập. "
                   "Ngũ Thử Độn dùng nguồn VERIFIED SRC-UHTB-CHEP. Riêng Can giờ Tý 23:00–23:59 "
                   "không được dùng để nâng/hạ quyết định vì TIME-0007 còn CONFLICTED. "
                   "Đây chưa phải hệ cát-hung giờ cổ điển đầy đủ và không dùng numeric score."),
        rule_ids=RULE_IDS, source_ids=SOURCE_IDS)

def cho_phep_ket_luan_ca_nhan() -> bool:
    return trang_thai_hien_tai().personal_decision_ready

def cho_phep_ket_luan_gio_ca_nhan() -> bool:
    return trang_thai_hien_tai().personal_hour_decision_ready

def gate_payload() -> dict[str, Any]:
    return trang_thai_hien_tai().to_dict()
