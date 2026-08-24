"""Cổng phương pháp Tử Bình Chân Thuyên cho lớp quyết định cá nhân.

Mục tiêu của module này không phải "luận thay" cho các lớp còn thiếu mà là
ngăn Engine dùng dữ liệu trung gian (Thập Thần, hợp/xung/hình/hại) như thể đã
xác lập được hỷ/kỵ cá nhân.

Phương pháp lõi V1 được khóa theo Tử Bình Chân Thuyên:
- lấy nguyệt lệnh làm đề cương;
- xét Nhật can phối nguyệt lệnh để định dụng thần/cách cục;
- mạnh/yếu không được quyết chỉ bằng một tiêu chí đắc/thất lệnh;
- khi luận vận, phải lấy Can Chi vận phối với hỷ/kỵ đã xác lập từ mệnh gốc.

Cho tới khi Pattern/Use engine được cài đủ và nghiệm thu, lớp thời gian chỉ được
mô tả CẤU TRÚC; không được phát sinh nhãn thuận/nghịch hay lời khuyên cá nhân.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

PHUONG_PHAP_ID = "ZPZQ-GEJU-V1"
PHUONG_PHAP_TEN = "Tử Bình Chân Thuyên — nguyệt lệnh/cách cục"

RULE_IDS = (
    "BT-BASE-0401",   # đắc thời không đủ kết luận vượng
    "BT-USE-0401",    # dụng thần chuyên cầu nguyệt lệnh
    "BT-DY-0401",     # vận phối hỷ/kỵ mệnh gốc
)
SOURCE_IDS = ("SRC-ZPZQ-NLC-SCAN", "SRC-ZPZQ-DONGLI")


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
    hour_fusion_ready: bool
    decision_mode: str
    reason_vi: str
    rule_ids: tuple[str, ...]
    source_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["rule_ids"] = list(self.rule_ids)
        d["source_ids"] = list(self.source_ids)
        return d


def trang_thai_hien_tai() -> TrangThaiPhuongPhap:
    """Trạng thái thật của V1 sau khi khóa lại phương pháp.

    Những lớp nền đã có không đồng nghĩa với đã có quyền kết luận lợi/hại.
    `personal_decision_ready=False` là chủ ý an toàn, không phải lỗi chạy.
    """
    return TrangThaiPhuongPhap(
        method_id=PHUONG_PHAP_ID,
        method_name=PHUONG_PHAP_TEN,
        natal_chart_ready=True,
        month_command_ready=True,
        ten_god_ready=True,
        branch_relation_ready=True,
        strength_engine_ready=False,
        pattern_engine_ready=False,
        use_favor_avoid_ready=False,
        transit_fusion_ready=False,
        personal_decision_ready=False,
        hour_fusion_ready=False,
        decision_mode="DESCRIPTIVE_ONLY",
        reason_vi=(
            "Đã có Tứ Trụ, Nguyệt lệnh, Tàng Can, Thập Thần và quan hệ Can/Chi; "
            "chưa cài đủ Cách cục + hỷ/kỵ theo Tử Bình Chân Thuyên. Vì vậy các tầng "
            "Đại vận/Năm/Tháng/Ngày/Giờ chỉ được mô tả cấu trúc, chưa được gọi là "
            "thuận/nghịch cá nhân."
        ),
        rule_ids=RULE_IDS,
        source_ids=SOURCE_IDS,
    )


def cho_phep_ket_luan_ca_nhan() -> bool:
    return trang_thai_hien_tai().personal_decision_ready


def gate_payload() -> dict[str, Any]:
    return trang_thai_hien_tai().to_dict()
