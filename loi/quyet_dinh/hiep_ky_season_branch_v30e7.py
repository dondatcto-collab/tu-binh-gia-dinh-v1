"""V3.0E7 — bộ tính Thiên Hỷ (天喜) theo mùa + Chi ngày.

Nguồn khóa:
- 《御定星曆考原》卷三 · 天喜: 春午、夏丑、秋辰、冬未.
- 《欽定協紀辨方書》卷五 · 天喜, dùng làm đối chiếu cùng hệ quy tắc.

Quy ước tháng tiết khí hiện hành:
- Xuân: Dần, Mão, Thìn -> ngày Ngọ.
- Hạ: Tỵ, Ngọ, Mùi -> ngày Sửu.
- Thu: Thân, Dậu, Tuất -> ngày Thìn.
- Đông: Hợi, Tý, Sửu -> ngày Mùi.

Thiên Hỷ chỉ cần mùa hiện hành và Chi ngày; không phụ thuộc Can ngày.
Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

TIAN_XI_BRANCH_BY_MONTH_BRANCH: dict[str, str] = {
    "DAN": "NGO", "MAO": "NGO", "THIN": "NGO",
    "TI": "SUU", "NGO": "SUU", "MUI": "SUU",
    "THAN": "THIN", "DAU": "THIN", "TUAT": "THIN",
    "HOI": "MUI", "TY": "MUI", "SUU": "MUI",
}


def _chuan_chi(chi: str) -> str:
    value = str(chi or "").strip().upper()
    if value not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return value


def tian_xi_branch(chi_thang: str) -> str:
    return TIAN_XI_BRANCH_BY_MONTH_BRANCH[_chuan_chi(chi_thang)]


def active_season_branch_tokens(chi_thang: str, chi_ngay: str) -> tuple[str, ...]:
    month = _chuan_chi(chi_thang)
    day_branch = _chuan_chi(chi_ngay)
    return ("天喜",) if day_branch == TIAN_XI_BRANCH_BY_MONTH_BRANCH[month] else ()


def calculator_status() -> dict:
    return {
        "calculator": "SEASON_DAY_BRANCH_V30E7",
        "active_tokens": ("天喜",),
        "source_rule": "御定星曆考原卷三 · 天喜: 春午、夏丑、秋辰、冬未",
        "extension_version": "V3_0E7_TIAN_XI",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
