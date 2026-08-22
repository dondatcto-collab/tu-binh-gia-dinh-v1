"""Ánh xạ Tàng Can.

Việc duy nhất của tệp này: cho một Địa Chi, trả về danh sách Thiên Can nó chứa.

KHÔNG luận Thập Thần ở đây.
KHÔNG tính mạnh yếu.
KHÔNG gán tỷ lệ.
KHÔNG gọi tên bản khí, trung khí, dư khí.

Thứ tự trả về là thứ tự của NGUỒN, không phải thứ tự ưu tiên.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from loi.lich.quy_uoc_can_chi import CAN, CAN_VI, CHI, CHI_VI


class TangCanError(Exception):
    pass


@dataclass(frozen=True)
class KetQuaTangCan:
    branch: str
    hidden_stems: tuple[str, ...]
    source_order: tuple[int, ...]
    rule_ids: tuple[str, ...]
    source_status: str
    semantic_role_status: str

    @property
    def hidden_stems_vi(self) -> tuple[str, ...]:
        return tuple(CAN_VI[CAN.index(c)] for c in self.hidden_stems)

    @property
    def branch_vi(self) -> str:
        return CHI_VI[CHI.index(self.branch)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "hidden_stems": list(self.hidden_stems),
            # Giữ dấu vết nguồn: thứ tự này là của NGUỒN, không phải thứ tự ưu tiên.
            "source_order": list(self.source_order),
            "rule_ids": list(self.rule_ids),
            "source_status": self.source_status,
            # Nói rõ là chưa gán vai trò, để tầng trên không tự suy diễn.
            "semantic_role_status": self.semantic_role_status,
        }


def lay_tang_can(conn: sqlite3.Connection, branch: str) -> KetQuaTangCan:
    """Tra Tàng Can của một Địa Chi. Cùng đầu vào luôn cho cùng đầu ra."""
    if branch not in CHI:
        raise TangCanError(
            f"CHI_KHONG_HOP_LE: {branch!r}. Chỉ nhận một trong {', '.join(CHI)}")

    rows = conn.execute(
        """
        SELECT s.code AS stem, h.source_order, h.source_rule_id,
               h.semantic_role, h.semantic_role_status, rv.status AS rule_status
          FROM branch_hidden_stems h
          JOIN branches b ON b.branch_index = h.branch_index
          JOIN stems s    ON s.stem_index = h.stem_index
          JOIN rule_versions rv ON rv.rule_version_id = h.source_rule_id || '@1'
         WHERE b.code = ?
      ORDER BY h.source_order
        """,
        (branch,),
    ).fetchall()

    if not rows:
        raise TangCanError(f"CHUA_NAP_TANG_CAN: Chi {branch} chưa có dữ liệu")

    thu_tu = [r["source_order"] for r in rows]
    if thu_tu != list(range(1, len(rows) + 1)):
        raise TangCanError(f"THU_TU_DUT_QUANG: Chi {branch} có source_order {thu_tu}")

    vai_tro = {r["semantic_role_status"] for r in rows}
    if len(vai_tro) != 1:
        raise TangCanError(f"VAI_TRO_KHONG_NHAT_QUAN: Chi {branch}")

    trang_thai = {r["rule_status"] for r in rows}
    if len(trang_thai) != 1:
        raise TangCanError(f"TRANG_THAI_NGUON_KHONG_NHAT_QUAN: Chi {branch}")

    return KetQuaTangCan(
        branch=branch,
        hidden_stems=tuple(r["stem"] for r in rows),
        source_order=tuple(thu_tu),
        rule_ids=tuple(dict.fromkeys(r["source_rule_id"] for r in rows)),
        source_status=trang_thai.pop(),
        semantic_role_status=vai_tro.pop(),
    )


def lay_tat_ca(conn: sqlite3.Connection) -> dict[str, KetQuaTangCan]:
    return {chi: lay_tang_can(conn, chi) for chi in CHI}


def do_phu_chi(conn: sqlite3.Connection) -> str:
    """BRANCH_COVERAGE — bao nhiêu trên 12 Chi đã có dữ liệu."""
    co = 0
    for chi in CHI:
        try:
            lay_tang_can(conn, chi)
            co += 1
        except TangCanError:
            pass
    return f"{co}/12"


def thu_tu_cac_truyen_thong(conn: sqlite3.Connection, branch: str) -> list[dict]:
    """Trả về thứ tự mà từng truyền thống ghi, không hợp nhất."""
    import json
    rows = conn.execute(
        """SELECT v.tradition, v.stem_order, v.source_id
             FROM hidden_stem_order_variants v
             JOIN branches b ON b.branch_index = v.branch_index
            WHERE b.code = ? ORDER BY v.tradition""",
        (branch,),
    ).fetchall()
    return [{"tradition": r["tradition"],
             "stem_order": json.loads(r["stem_order"]),
             "source_id": r["source_id"]} for r in rows]
