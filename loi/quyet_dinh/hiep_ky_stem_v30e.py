"""V3.0E — bộ tính cát thần theo Chi tháng + Can ngày.

V3.0E1 mở 月徳 (Nguyệt Đức).
V3.0E2 mở 月徳合 (Nguyệt Đức Hợp).
Nguồn khóa:
- 《欽定協紀辨方書》卷五 · 月徳 / 月徳合.
- 《御定星曆考原》卷三 · 月徳合, dùng bản ghi rõ 己 để loại lỗi OCR 巳.
Không suy rộng sang 月恩, 四相 hoặc cát thần Can-ngày khác. Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CAN, CHI

YUE_DE_STEM_BY_MONTH_BRANCH = {
    "DAN": "BINH", "NGO": "BINH", "TUAT": "BINH",
    "HOI": "GIAP", "MAO": "GIAP", "MUI": "GIAP",
    "THAN": "NHAM", "TY": "NHAM", "THIN": "NHAM",
    "TI": "CANH", "DAU": "CANH", "SUU": "CANH",
}

YUE_DE_HE_STEM_BY_MONTH_BRANCH = {
    "DAN": "TAN", "NGO": "TAN", "TUAT": "TAN",
    "HOI": "KY", "MAO": "KY", "MUI": "KY",
    "THAN": "DINH", "TY": "DINH", "THIN": "DINH",
    "TI": "AT", "DAU": "AT", "SUU": "AT",
}


def _chuan_chi(chi: str) -> str:
    x = str(chi or "").strip().upper()
    if x not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return x


def _chuan_can(can: str) -> str:
    x = str(can or "").strip().upper()
    if x not in CAN:
        raise ValueError(f"CAN_KHONG_HOP_LE: {can}")
    return x


def yue_de_stem(chi_thang: str) -> str:
    return YUE_DE_STEM_BY_MONTH_BRANCH[_chuan_chi(chi_thang)]


def yue_de_he_stem(chi_thang: str) -> str:
    return YUE_DE_HE_STEM_BY_MONTH_BRANCH[_chuan_chi(chi_thang)]


def active_stem_tokens(chi_thang: str, can_ngay: str) -> tuple[str, ...]:
    m, d = _chuan_chi(chi_thang), _chuan_can(can_ngay)
    out: list[str] = []
    if d == YUE_DE_STEM_BY_MONTH_BRANCH[m]:
        out.append("月徳")
    if d == YUE_DE_HE_STEM_BY_MONTH_BRANCH[m]:
        out.append("月徳合")
    return tuple(out)


def calculator_status() -> dict:
    return {
        "calculator": "MONTH_BRANCH_DAY_STEM_V30E2",
        "active_tokens": ("月徳", "月徳合"),
        "source_rules": {
            "月徳": "卷五 · 月徳: 寅午戌月丙、亥卯未月甲、申子辰月壬、巳酉丑月庚",
            "月徳合": "卷五/星曆考原卷三 · 月徳合: 正五九月辛、二六十月己、三七十一月丁、四八十二月乙",
        },
        "extension_version": "V3_0E2_YUE_DE_HE",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
