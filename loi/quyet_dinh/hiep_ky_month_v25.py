"""V2.5 — bộ tính Hiệp Kỷ theo Chi tháng/ngày đã khóa công thức.

Phạm vi ACTIVE chỉ gồm 5 token có công thức quan hệ tháng-ngày rõ và trực tiếp:
月建, 月破, 三合, 六合, 月害. Không suy rộng sang các thần sát khác.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

SOURCE_RULES = {
    "月建": "卷四 · 月建: 正月建寅順行十二辰",
    "月破": "卷四/卷二十 · 月破 theo xung của 月建",
    "三合": "卷六 · 三合: mỗi tháng lấy hai Chi cùng tam hợp với 月建",
    "六合": "卷六 · 六合: Chi ngày lục hợp với 月建",
    "月害": "卷六 · 月害: Chi ngày lục hại với 月建",
}

XUNG = {
    "TY":"NGO", "NGO":"TY", "SUU":"MUI", "MUI":"SUU",
    "DAN":"THAN", "THAN":"DAN", "MAO":"DAU", "DAU":"MAO",
    "THIN":"TUAT", "TUAT":"THIN", "TI":"HOI", "HOI":"TI",
}
LUC_HOP = {
    "TY":"SUU", "SUU":"TY", "DAN":"HOI", "HOI":"DAN",
    "MAO":"TUAT", "TUAT":"MAO", "THIN":"DAU", "DAU":"THIN",
    "TI":"THAN", "THAN":"TI", "NGO":"MUI", "MUI":"NGO",
}
LUC_HAI = {
    "TY":"MUI", "MUI":"TY", "SUU":"NGO", "NGO":"SUU",
    "DAN":"TI", "TI":"DAN", "MAO":"THIN", "THIN":"MAO",
    "THAN":"HOI", "HOI":"THAN", "DAU":"TUAT", "TUAT":"DAU",
}
TAM_HOP_NHOM = (
    frozenset({"DAN","NGO","TUAT"}),
    frozenset({"TI","DAU","SUU"}),
    frozenset({"THAN","TY","THIN"}),
    frozenset({"HOI","MAO","MUI"}),
)


def _chuan(chi: str) -> str:
    x = str(chi or "").strip().upper()
    if x not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return x


def tam_hop_partners(chi_thang: str) -> frozenset[str]:
    m = _chuan(chi_thang)
    for nhom in TAM_HOP_NHOM:
        if m in nhom:
            return frozenset(nhom - {m})
    raise AssertionError("TAM_HOP_GROUP_MISSING")


def active_month_tokens(chi_thang: str, chi_ngay: str) -> tuple[str, ...]:
    """Trả token ACTIVE theo đúng quan hệ Chi tháng-ngày, không tính điểm."""
    m, d = _chuan(chi_thang), _chuan(chi_ngay)
    out: list[str] = []
    if d == m:
        out.append("月建")
    if d == XUNG[m]:
        out.append("月破")
    if d in tam_hop_partners(m):
        out.append("三合")
    if d == LUC_HOP[m]:
        out.append("六合")
    if d == LUC_HAI[m]:
        out.append("月害")
    return tuple(out)


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_RELATIONS_V25",
        "active_tokens": ("月建", "月破", "三合", "六合", "月害"),
        "source_rules": SOURCE_RULES,
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
