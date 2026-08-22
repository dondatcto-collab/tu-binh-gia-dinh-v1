"""Quyền khí theo tiết — lớp 3C-2.

Việc duy nhất: GHI LẠI từng nguồn nói gì, theo từng tiết khí.
KHÔNG hợp nhất. KHÔNG trung bình hóa. KHÔNG kết luận mạnh yếu.

Nếu các nguồn không đồng thuận thì agreement_status = CONFLICTED.
Đó là một KẾT QUẢ HỢP LỆ, không phải lỗi.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any


class QuyenKhiError(Exception):
    pass


@dataclass(frozen=True)
class BienTheQuyenKhi:
    tradition: str
    source_id: str
    solar_term: str
    segment_order: int
    governing_stem: str | None
    day_count: int | None
    textual_order: int
    original_text: str
    parse_status: str
    status: str
    notes: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tradition": self.tradition,
            "source": self.source_id,
            "stem": self.governing_stem,
            "interval": {"segment_order": self.segment_order,
                         "day_count": self.day_count},
            "textual_order": self.textual_order,
            "original_text": self.original_text,
            "parse_status": self.parse_status,
            "status": self.status,
        }


@dataclass
class KetQuaQuyenKhi:
    solar_term: str
    governing_qi_variants: list[BienTheQuyenKhi] = field(default_factory=list)
    agreement_status: str = "INSUFFICIENT_SOURCES"
    conflicts: list[str] = field(default_factory=list)
    rule_ids: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "solar_term": self.solar_term,
            "governing_qi_variants": [v.to_dict() for v in self.governing_qi_variants],
            "agreement_status": self.agreement_status,
            "conflicts": list(self.conflicts),
            "rule_ids": list(self.rule_ids),
            "source_ids": list(self.source_ids),
        }


def lay_quyen_khi(conn: sqlite3.Connection, solar_term: str) -> KetQuaQuyenKhi:
    rows = conn.execute(
        """SELECT * FROM seasonal_governing_qi
            WHERE solar_term = ?
         ORDER BY tradition, segment_order""", (solar_term,)).fetchall()

    bien_the = [BienTheQuyenKhi(
        tradition=r["tradition"], source_id=r["source_id"],
        solar_term=r["solar_term"], segment_order=r["segment_order"],
        governing_stem=r["governing_stem"], day_count=r["day_count"],
        textual_order=r["textual_order"], original_text=r["original_text"],
        parse_status=r["parse_status"], status=r["status"], notes=r["notes"],
    ) for r in rows]

    tt = conn.execute(
        "SELECT agreement_status, notes FROM seasonal_qi_agreement WHERE solar_term = ?",
        (solar_term,)).fetchone()

    return KetQuaQuyenKhi(
        solar_term=solar_term,
        governing_qi_variants=bien_the,
        agreement_status=tt["agreement_status"] if tt else "INSUFFICIENT_SOURCES",
        conflicts=[tt["notes"]] if tt and tt["agreement_status"] == "CONFLICTED" else [],
        rule_ids=sorted({r["rule_id"] for r in rows}),
        source_ids=sorted({r["source_id"] for r in rows}),
    )


def tinh_dong_thuan(conn: sqlite3.Connection, solar_term: str) -> tuple[str, int, str]:
    """Xét mức đồng thuận giữa các truyền thống cho một tiết.

    Một truyền thống thì KHÔNG đủ để nói đồng thuận. Trả INSUFFICIENT_SOURCES.
    """
    rows = conn.execute(
        """SELECT tradition, segment_order, governing_stem, day_count, parse_status
             FROM seasonal_governing_qi WHERE solar_term = ?
         ORDER BY tradition, segment_order""", (solar_term,)).fetchall()
    if not rows:
        return "INSUFFICIENT_SOURCES", 0, "Chưa nguồn nào chép tiết này."

    theo_tt: dict[str, list] = {}
    for r in rows:
        theo_tt.setdefault(r["tradition"], []).append(
            (r["segment_order"], r["governing_stem"], r["day_count"]))

    so_tt = len(theo_tt)
    if so_tt < 2:
        ten = next(iter(theo_tt))
        ngo = [r for r in rows if r["parse_status"] in ("SUSPECT_TEXT", "PARTIAL",
                                                        "NO_DAY_COUNT")]
        ly_do = (f"Chỉ có {ten}. Không đủ để nói hai nguồn có đồng thuận hay không."
                 + (f" Ngoài ra {len(ngo)} đoạn chưa đọc chắc." if ngo else ""))
        return "INSUFFICIENT_SOURCES", so_tt, ly_do

    cac_bang = list(theo_tt.values())
    if all(b == cac_bang[0] for b in cac_bang[1:]):
        return "AGREED", so_tt, "Các truyền thống chép giống nhau."
    return "CONFLICTED", so_tt, "Các truyền thống chép khác nhau. Không hợp nhất."


def thong_ke(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT agreement_status, COUNT(*) AS n FROM seasonal_qi_agreement "
        "GROUP BY agreement_status").fetchall()
    return {r["agreement_status"]: r["n"] for r in rows}
