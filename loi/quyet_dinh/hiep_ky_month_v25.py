"""Hiệp Kỷ — bộ tính quan hệ Chi tháng/ngày đã khóa công thức.

V2.5 kích hoạt 5 token: 月建, 月破, 三合, 六合, 月害.
V3.0A mở thêm 月刑 (Nguyệt Hình).
V3.0B mở thêm 劫煞, 災煞, 月煞.
V3.0C mở thêm 月厭 (Nguyệt Yếm), khóa trực tiếp từ 月表一..十二
của 《欽定協紀辨方書》卷20..31.

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
    "劫煞": "卷20–31 · 月表一至十二: từng tháng ghi trực tiếp 劫煞所在之支",
    "災煞": "卷20–31 · 月表一至十二: từng tháng ghi trực tiếp 災煞所在之支",
    "月煞": "卷20–31 · 月表一至十二: từng tháng ghi trực tiếp 月煞所在之支",
    "月厭": "卷20–31 · 月表一至十二: từng tháng ghi trực tiếp 月厭所在之支",
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

# Các bảng dưới đây khóa trực tiếp từ 月表一..十二 (卷20..31), không suy
# từ công thức hiện đại. Mỗi bảng ánh xạ Chi tháng -> Chi ngày mang thần sát.
YUE_XING_BY_MONTH_BRANCH = {
    "DAN": "TI", "MAO": "TY", "THIN": "THIN", "TI": "THAN",
    "NGO": "NGO", "MUI": "SUU", "THAN": "DAN", "DAU": "DAU",
    "TUAT": "MUI", "HOI": "HOI", "TY": "MAO", "SUU": "TUAT",
}
JIE_SHA_BY_MONTH_BRANCH = {
    "DAN": "HOI", "MAO": "THAN", "THIN": "TI", "TI": "DAN",
    "NGO": "HOI", "MUI": "THAN", "THAN": "TI", "DAU": "DAN",
    "TUAT": "HOI", "HOI": "THAN", "TY": "TI", "SUU": "DAN",
}
ZAI_SHA_BY_MONTH_BRANCH = {
    "DAN": "TY", "MAO": "DAU", "THIN": "NGO", "TI": "MAO",
    "NGO": "TY", "MUI": "DAU", "THAN": "NGO", "DAU": "MAO",
    "TUAT": "TY", "HOI": "DAU", "TY": "NGO", "SUU": "MAO",
}
YUE_SHA_BY_MONTH_BRANCH = {
    "DAN": "SUU", "MAO": "TUAT", "THIN": "MUI", "TI": "THIN",
    "NGO": "SUU", "MUI": "TUAT", "THAN": "MUI", "DAU": "THIN",
    "TUAT": "SUU", "HOI": "TUAT", "TY": "MUI", "SUU": "THIN",
}
YUE_YAN_BY_MONTH_BRANCH = {
    "DAN": "TUAT", "MAO": "DAU", "THIN": "THAN", "TI": "MUI",
    "NGO": "NGO", "MUI": "TI", "THAN": "THIN", "DAU": "MAO",
    "TUAT": "DAN", "HOI": "SUU", "TY": "TY", "SUU": "HOI",
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
    return YUE_XING_BY_MONTH_BRANCH[_chuan(chi_thang)]


def jie_sha_branch(chi_thang: str) -> str:
    return JIE_SHA_BY_MONTH_BRANCH[_chuan(chi_thang)]


def zai_sha_branch(chi_thang: str) -> str:
    return ZAI_SHA_BY_MONTH_BRANCH[_chuan(chi_thang)]


def yue_sha_branch(chi_thang: str) -> str:
    return YUE_SHA_BY_MONTH_BRANCH[_chuan(chi_thang)]


def yue_yan_branch(chi_thang: str) -> str:
    return YUE_YAN_BY_MONTH_BRANCH[_chuan(chi_thang)]


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
    if d == JIE_SHA_BY_MONTH_BRANCH[m]:
        out.append("劫煞")
    if d == ZAI_SHA_BY_MONTH_BRANCH[m]:
        out.append("災煞")
    if d == YUE_SHA_BY_MONTH_BRANCH[m]:
        out.append("月煞")
    if d == YUE_YAN_BY_MONTH_BRANCH[m]:
        out.append("月厭")
    return tuple(out)


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_RELATIONS_V25_V30C",
        "active_tokens": ("月建", "月破", "三合", "六合", "月害", "月刑", "劫煞", "災煞", "月煞", "月厭"),
        "source_rules": SOURCE_RULES,
        "extension_version": "V3_0C_YUE_YAN",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
