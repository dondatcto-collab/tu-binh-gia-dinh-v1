"""Nguyệt lệnh — lớp 3C-1.

Xác định được, không tranh cãi: Chi tháng, mùa, Tiết mở tháng, Tiết kế tiếp.
Thời gian lấy từ Calendar Engine đã nghiệm thu.

KHÔNG tính điểm. KHÔNG nói mạnh yếu. KHÔNG kết luận vượng suy.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loi.lich.ket_qua import KetQuaLich
from loi.lich.quy_uoc_can_chi import CHI, CHI_VI

# Mùa suy từ Chi tháng. Dần Mão Thìn xuân, Tị Ngọ Mùi hạ, và tiếp như vậy.
MUA_THEO_CHI = {
    "DAN": "XUAN", "MAO": "XUAN", "THIN": "XUAN",
    "TI": "HA", "NGO": "HA", "MUI": "HA",
    "THAN": "THU", "DAU": "THU", "TUAT": "THU",
    "HOI": "DONG", "TY": "DONG", "SUU": "DONG",
}
MUA_VI = {"XUAN": "Xuân", "HA": "Hạ", "THU": "Thu", "DONG": "Đông"}


class NguyetLenhError(Exception):
    pass


@dataclass(frozen=True)
class KetQuaNguyetLenh:
    month_branch: str
    season: str
    current_jie: str
    current_jie_utc: datetime
    next_jie: str
    next_jie_utc: datetime
    rule_ids: tuple[str, ...]
    source_ids: tuple[str, ...]

    @property
    def month_branch_vi(self) -> str:
        return CHI_VI[CHI.index(self.month_branch)]

    @property
    def season_vi(self) -> str:
        return MUA_VI[self.season]

    def to_dict(self) -> dict[str, Any]:
        return {
            "month_branch": self.month_branch,
            "month_branch_vi": self.month_branch_vi,
            "season": self.season,
            "season_vi": self.season_vi,
            "current_jie": self.current_jie,
            "current_jie_utc": self.current_jie_utc.isoformat(),
            "next_jie": self.next_jie,
            "next_jie_utc": self.next_jie_utc.isoformat(),
            "rule_ids": list(self.rule_ids),
            "source_ids": list(self.source_ids),
        }


def tu_ket_qua_lich(conn: sqlite3.Connection, kq: KetQuaLich) -> KetQuaNguyetLenh:
    """Dựng nguyệt lệnh từ kết quả Calendar Engine."""
    chi = kq.tru_thang.chi
    if chi not in MUA_THEO_CHI:
        raise NguyetLenhError(f"CHI_THANG_KHONG_HOP_LE: {chi}")

    r = conn.execute(
        "SELECT season, rule_id, source_id FROM month_commands WHERE month_branch = ?",
        (chi,)).fetchone()
    if r is None:
        raise NguyetLenhError(f"CHUA_NAP_NGUYET_LENH: {chi}")
    if r["season"] != MUA_THEO_CHI[chi]:
        raise NguyetLenhError(f"MUA_KHONG_KHOP: {chi}")

    vt = kq.vi_tri_tiet_khi
    return KetQuaNguyetLenh(
        month_branch=chi,
        season=r["season"],
        current_jie=vt.jie_truoc.dinh_nghia.code,
        current_jie_utc=vt.jie_truoc.thoi_diem_utc,
        next_jie=vt.jie_sau.dinh_nghia.code,
        next_jie_utc=vt.jie_sau.thoi_diem_utc,
        rule_ids=(r["rule_id"], "TIME-0001", "TIME-0002"),
        source_ids=(r["source_id"], "SRC-VSOP87-AE"),
    )


def so_ngay_da_qua_trong_tiet(kq: KetQuaLich) -> float:
    """Số ngày kể từ Tiết mở tháng. Chỉ là số đo, không phải đánh giá."""
    vt = kq.vi_tri_tiet_khi
    return (kq.thoi_diem.utc - vt.jie_truoc.thoi_diem_utc).total_seconds() / 86400.0
