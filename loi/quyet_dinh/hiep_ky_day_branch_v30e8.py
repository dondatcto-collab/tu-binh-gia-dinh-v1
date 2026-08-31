"""V3.0E8 — bộ tính Ngũ Hợp (五合) theo Chi ngày.

Nguồn khóa: 《欽定協紀辨方書》卷五 · 五合:
- 樞要歷: 五合 là ngày lành trong tháng, phù hợp kết hôn, hội thân hữu, lập券交易.
- 歷例: 五合者寅卯日也 — ngày Dần và ngày Mão.

Rule không phụ thuộc tháng, mùa hay Can ngày. Không dùng điểm số.
"""
from __future__ import annotations

from loi.lich.quy_uoc_can_chi import CHI

WU_HE_DAY_BRANCHES = frozenset({"DAN", "MAO"})


def _chuan_chi(chi: str) -> str:
    value = str(chi or "").strip().upper()
    if value not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {chi}")
    return value


def active_day_branch_tokens(chi_ngay: str) -> tuple[str, ...]:
    day_branch = _chuan_chi(chi_ngay)
    return ("五合",) if day_branch in WU_HE_DAY_BRANCHES else ()


def calculator_status() -> dict:
    return {
        "calculator": "DAY_BRANCH_V30E8",
        "active_tokens": ("五合",),
        "source_rule": "欽定協紀辨方書卷五 · 五合: 歷例曰五合者寅卯日也",
        "extension_version": "V3_0E8_WU_HE",
        "numeric_score": None,
        "numeric_score_status": "LOCKED_OFF",
    }
