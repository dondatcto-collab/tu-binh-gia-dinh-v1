"""Nạp bảng Tàng Can vào kho quy tắc.

Tạo 12 quy tắc BT-HIDDEN-001 tới BT-HIDDEN-012, mỗi Chi một quy tắc.
Mỗi quy tắc chỉ chứa DỮ LIỆU CẤU TRÚC: Chi này có những Can nào.
Không điểm số, không tốt xấu, không thứ tự ưu tiên huyền học.

Thêm một quy tắc riêng BT-HIDDEN-ORDER-001 cho câu hỏi THỨ TỰ,
vì các nguồn không thống nhất về thứ tự.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

from loi.lich.quy_uoc_can_chi import CAN, CHI
from loi.nen.phien_ban import DUONG_DAN

# Chi nào ứng với quy tắc số mấy. Theo đúng thứ tự Tý tới Hợi.
MA_QUY_TAC = {chi: f"BT-HIDDEN-{i:03d}" for i, chi in enumerate(CHI, start=1)}
MA_QUY_TAC_THU_TU = "BT-HIDDEN-ORDER-001"


def doc_bang(thu_muc: Path | None = None) -> dict[str, Any]:
    thu_muc = thu_muc or DUONG_DAN["mam"]
    return yaml.safe_load((thu_muc / "tang_can.yaml").read_text(encoding="utf-8"))


def kiem_bang(raw: dict[str, Any]) -> list[str]:
    """Kiểm bảng trước khi nạp. Rỗng nghĩa là sạch."""
    loi: list[str] = []
    bang = raw["bang"]

    if len(bang) != 12:
        loi.append(f"SO_CHI_SAI: cần 12, đang có {len(bang)}")

    thay = [r["branch"] for r in bang]
    if sorted(thay) != sorted(CHI):
        loi.append(f"THIEU_HOAC_THUA_CHI: {sorted(set(CHI) - set(thay))}")
    if thay != list(CHI):
        loi.append("SAI_THU_TU_CHI: bảng phải liệt kê từ Tý tới Hợi")

    for r in bang:
        chi = r["branch"]
        stems = r["stems"]
        if not 1 <= len(stems) <= 3:
            loi.append(f"SO_CAN_LA: {chi} có {len(stems)} Can")
        if len(set(stems)) != len(stems):
            loi.append(f"TRUNG_CAN: {chi} lặp Can")
        la = [c for c in stems if c not in CAN]
        if la:
            loi.append(f"CAN_KHONG_HOP_LE: {chi} có {la}")
        if not r.get("nguyen_van", "").strip():
            loi.append(f"THIEU_NGUYEN_VAN: {chi}")
        # Cấm mọi dấu vết tỷ lệ lọt vào dữ liệu cấu trúc.
        for khoa in r:
            if khoa in {"ty_le", "trong_so", "weight", "ratio", "percent", "so_ngay"}:
                loi.append(f"CO_TY_LE_TRONG_DU_LIEU_CAU_TRUC: {chi}.{khoa}")

    # Dị biệt thứ tự phải giữ nguyên tập Can, chỉ khác thứ tự.
    for d in raw.get("thu_tu_di_biet", []):
        if sorted(d["uhtb"]) != sorted(d["ban_doi_sau"]):
            loi.append(f"DI_BIET_DOI_CA_TAP_CAN: {d['branch']} — "
                       "đây không còn là khác thứ tự nữa, phải xét lại")
    return loi


def nap(conn: sqlite3.Connection, thu_muc: Path | None = None) -> dict[str, int]:
    raw = doc_bang(thu_muc)
    loi = kiem_bang(raw)
    if loi:
        raise ValueError("BANG_TANG_CAN_HONG: " + "; ".join(loi))

    source_id = raw["source_id"]
    passage_id = raw["passage_id"]

    for r in raw["bang"]:
        chi = r["branch"]
        rule_id = MA_QUY_TAC[chi]
        conn.execute(
            """INSERT INTO rule_registry
                   (rule_id, rule_group, namespace, name_vi, name_original,
                    active_version, is_active)
               VALUES (?,?,?,?,?,1,1)
               ON CONFLICT(rule_id) DO UPDATE SET
                   name_vi = excluded.name_vi, updated_at = datetime('now')""",
            (rule_id, "BT-HIDDEN", "BT-HIDDEN",
             f"Tàng Can của Chi {chi}", r["nguyen_van"]),
        )
        rvid = f"{rule_id}@1"
        conn.execute(
            """INSERT INTO rule_versions
                   (rule_version_id, rule_id, version, status, confidence,
                    inputs, preconditions, logic, outputs,
                    effect_class, priority, block_type, severity, mitigatable, notes)
               VALUES (?,?,1,'VERIFIED','MEDIUM',
                       '["EARTHLY_BRANCH"]','[]',?,'["HIDDEN_STEMS"]',
                       'EXPLANATORY',100,'NONE','MINOR',0,?)
               ON CONFLICT(rule_version_id) DO UPDATE SET
                   logic = excluded.logic, notes = excluded.notes""",
            (rvid, rule_id,
             json.dumps({"kieu": "DU_LIEU_CAU_TRUC", "branch": chi,
                         "hidden_stems": r["stems"],
                         "khong_co": ["ty_le", "trong_so", "vai_tro_ngu_nghia"]},
                        ensure_ascii=False),
             r.get("ghi_chu_nguyen_van") or "Dữ liệu cấu trúc, không chấm điểm."),
        )
        for lop, sid in (("PRIMARY", source_id),
                         ("CROSS_REFERENCE", "SRC-BANG-DOI-SAU")):
            conn.execute(
                """INSERT INTO rule_version_sources
                       (rule_version_id, source_id, source_location, source_level,
                        original_text, translation_vi, logic_note)
                   VALUES (?,?,?,?,?,?,?)
                   ON CONFLICT(rule_version_id, source_id, source_level)
                   DO UPDATE SET logic_note = excluded.logic_note""",
                (rvid, sid, "Hựu Địa Chi tàng độn ca", lop,
                 r["nguyen_van"], r["dich"],
                 "Tập Can trùng khớp ở cả hai nguồn."
                 if lop == "CROSS_REFERENCE" else "Suy thẳng từ câu phú."),
            )
        conn.execute(
            """INSERT INTO rule_version_passages (rule_version_id, passage_id)
               VALUES (?,?) ON CONFLICT DO NOTHING""", (rvid, passage_id))

        for thu_tu, can in enumerate(r["stems"], start=1):
            conn.execute(
                """INSERT INTO branch_hidden_stems
                       (branch_index, stem_index, source_order,
                        semantic_role, semantic_role_status, source_rule_id)
                   VALUES (?,?,?,NULL,'NOT_ASSIGNED',?)
                   ON CONFLICT(branch_index, stem_index) DO UPDATE SET
                       source_order = excluded.source_order,
                       source_rule_id = excluded.source_rule_id""",
                (CHI.index(chi) + 1, CAN.index(can) + 1, thu_tu, rule_id),
            )

    _nap_quy_tac_thu_tu(conn, raw)
    conn.commit()
    return dem(conn)


def _nap_quy_tac_thu_tu(conn: sqlite3.Connection, raw: dict[str, Any]) -> None:
    """Câu hỏi THỨ TỰ là một quy tắc riêng, và nó đang CONFLICTED."""
    di_biet = raw.get("thu_tu_di_biet", [])
    conn.execute(
        """INSERT INTO rule_registry
               (rule_id, rule_group, namespace, name_vi, name_original,
                active_version, is_active)
           VALUES (?,?,?,?,?,1,0)
           ON CONFLICT(rule_id) DO UPDATE SET name_vi = excluded.name_vi""",
        (MA_QUY_TAC_THU_TU, "BT-HIDDEN", "BT-HIDDEN",
         "Thứ tự liệt kê Tàng Can — các nguồn không thống nhất", None),
    )
    rvid = f"{MA_QUY_TAC_THU_TU}@1"
    conn.execute(
        """INSERT INTO rule_versions
               (rule_version_id, rule_id, version, status, confidence,
                inputs, preconditions, logic, outputs,
                effect_class, priority, block_type, severity, mitigatable, notes)
           VALUES (?,?,1,'CONFLICTED','LOW',
                   '["EARTHLY_BRANCH"]','[]',?,'["SOURCE_ORDER"]',
                   'EXPLANATORY',100,'NONE','MINOR',0,?)
           ON CONFLICT(rule_version_id) DO UPDATE SET
               logic = excluded.logic, notes = excluded.notes""",
        (rvid, MA_QUY_TAC_THU_TU,
         json.dumps({"kieu": "TRANH_LUAN",
                     "cau_hoi": "Tàng Can liệt kê theo thứ tự nào?",
                     "so_chi_di_biet": len(di_biet),
                     "chi_di_biet": [d["branch"] for d in di_biet]},
                    ensure_ascii=False),
         "Tập Can thì mọi nguồn thống nhất. Thứ tự thì khác nhau ở 5 Chi. "
         "Hệ thống lưu thứ tự của Uyên Hải Tử Bình vào source_order, "
         "và KHÔNG gán nghĩa cho thứ tự đó."),
    )
    # CHỈ hai nguồn nói về TẬP và THỨ TỰ Tàng Can tĩnh.
    # Tam Mệnh Thông Hội KHÔNG được dùng ở đây — nó nói về quyền khí theo mùa,
    # là một khái niệm khác. Nó thuộc nhóm BT-SEASON-POWER, làm sau.
    for sid, lop in (("SRC-UHTB-CHEP", "PRIMARY"),
                     ("SRC-BANG-DOI-SAU", "CROSS_REFERENCE")):
        conn.execute(
            """INSERT INTO rule_version_sources
                   (rule_version_id, source_id, source_level, logic_note)
               VALUES (?,?,?,?)
               ON CONFLICT(rule_version_id, source_id, source_level) DO NOTHING""",
            (rvid, sid, lop, "Hai nguồn ghi thứ tự khác nhau."),
        )

    for d in di_biet:
        for truyen_thong, thu_tu, sid in (
                ("UYEN_HAI_TU_BINH", d["uhtb"], "SRC-UHTB-CHEP"),
                ("BANG_DOI_SAU", d["ban_doi_sau"], "SRC-BANG-DOI-SAU")):
            conn.execute(
                """INSERT INTO hidden_stem_order_variants
                       (variant_id, branch_index, tradition, stem_order, source_id, notes)
                   VALUES (?,?,?,?,?,?)
                   ON CONFLICT(variant_id) DO UPDATE SET stem_order = excluded.stem_order""",
                (f"{d['branch']}:{truyen_thong}", CHI.index(d["branch"]) + 1,
                 truyen_thong, json.dumps(thu_tu, ensure_ascii=False), sid,
                 "Cùng tập Can, khác thứ tự."),
            )


def dem(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        b: conn.execute(f"SELECT COUNT(*) AS n FROM {b}").fetchone()["n"]
        for b in ("branch_hidden_stems", "hidden_stem_order_variants")
    }
