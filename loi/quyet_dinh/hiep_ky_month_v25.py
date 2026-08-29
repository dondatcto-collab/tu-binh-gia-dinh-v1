"""Hiệp Kỷ — bộ tính quan hệ Chi tháng/ngày đã khóa công thức.

V2.5 kích hoạt 5 token: 月建, 月破, 三合, 六合, 月害.
V3.0A mở thêm đúng 1 token: 月刑 (Nguyệt Hình), dựa trực tiếp trên
月表一..十二 của 《欽定協紀辨方書》卷20..31.

Không suy rộng sang các thần sát khác và không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

SOURCE_RULES = {
    "月建": "卷四 · 月建: 正月建寅順行十二辰",
    "月破": "卷四/卷二十 · 月破 theo xung của 月建",
    "三合": "卷六 · 三合: mỗi tháng lấy hai Chi cùng tam hợp với 月建",
    "六合": "卷六 · 六合: Chi ngày lục hợp với 月建",
    "月害": "卷六 · 月害: Chi ngày lục hại với 月建",
    "月刑": "卷20–31 · 月表一至十二: từng tháng ghi trực tiếp 月刑所在之支",
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

# V3.0A: bảng này không suy ra từ một công thức hiện đại; nó được chép trực
# tiếp từ 月表一..十二 (卷20..31). Khóa theo Chi tháng -> Chi ngày mang 月刑.
YUE_XING_BY_MONTH_BRANCH = {
    "DAN": "TI",      # 正月: 月建寅，月刑巳
    "MAO": "TY",      # 二月: 月建卯，月刑子
    "THIN": "THIN",   # 三月: 月建辰，月刑辰
    "TI": "THAN",     # 四月: 月建巳，月刑申
    "NGO": "NGO",     # 五月: 月建午，月刑午
    "MUI": "SUU",     # 六月: 月建未，月刑丑
    "THAN": "DAN",    # 七月: 月建申，月刑寅
    "DAU": "DAU",     # 八月: 月建酉，月刑酉
    "TUAT": "MUI",    # 九月: 月建戌，月刑未
    "HOI": "HOI",     # 十月: 月建亥，月刑亥
    "TY": "MAO",      # 十一月: 月建子，月刑卯
    "SUU": "TUAT",    # 十二月: 月建丑，月刑戌
}


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


def yue_xing_branch(chi_thang: str) -> str:
    """Trả Chi ngày mang 月刑 của Chi tháng theo bảng Hiệp Kỷ V3.0A."""
    return YUE_XING_BY_MONTH_BRANCH[_chuan(chi_thang)]


def active_month_tokens(chi_thang: str, chi_ngay: str) -> tuple[str, ...]:
    """Trả token ACTIVE theo quan hệ Chi tháng-ngày, không tính điểm.

    Một ngày có thể đồng thời khớp nhiều token; không được ghi đè evidence.
    """
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
    if d == YUE_XING_BY_MONTH_BRANCH[m]:
        out.append("月刑")
    return tuple(out)


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_RELATIONS_V25_V30A",
        "active_tokens": ("月建", "月破", "三合", "六合", "月害", "月刑"),
        "source_rules": SOURCE_RULES,
        "extension_version": "V3_0A_YUE_XING",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
