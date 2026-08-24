"""Nạp dữ liệu mầm. Chạy lại nhiều lần vẫn an toàn, không tạo bản ghi trùng.

Chỉ nạp thứ không tranh cãi giữa các trường phái.
Không nạp Thần Sát, không nạp Tàng Can, không nạp quy tắc Hiệp Kỷ.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import yaml

from loi.kho_du_lieu.nap_tang_can import nap as nap_tang_can
from loi.kho_du_lieu.nap_quyen_khi import nap as nap_quyen_khi
from loi.kho_du_lieu.nap_thap_than import nap as nap_thap_than
from loi.kho_du_lieu.nap_quyet_dinh_v1 import nap as nap_quyet_dinh_v1
from loi.lich.bo_quy_uoc import dong_bo_vao_db, tai_tat_ca
from loi.nen.phien_ban import DUONG_DAN


def _doc_yaml(ten_tep: str, thu_muc: Path | None = None) -> dict[str, Any]:
    thu_muc = thu_muc or DUONG_DAN["mam"]
    return yaml.safe_load((thu_muc / ten_tep).read_text(encoding="utf-8"))


def nap_mam(conn: sqlite3.Connection,
            thu_muc_mam: Path | None = None,
            thu_muc_lich: Path | None = None) -> dict[str, int]:
    """Nạp toàn bộ dữ liệu mầm. Trả về số bản ghi từng bảng sau khi nạp."""

    nen = _doc_yaml("can_chi_ngu_hanh.yaml", thu_muc_mam)
    ns = _doc_yaml("namespace_va_loai_viec.yaml", thu_muc_mam)

    for e in nen["elements"]:
        conn.execute(
            """INSERT INTO elements (element_code, name_vi, name_original)
               VALUES (:element_code, :name_vi, :name_original)
               ON CONFLICT(element_code) DO UPDATE SET
                   name_vi = excluded.name_vi,
                   name_original = excluded.name_original""",
            e,
        )

    for r in nen["element_relations"]:
        conn.execute(
            """INSERT INTO element_relations (from_element, to_element, relation)
               VALUES (:from_element, :to_element, :relation)
               ON CONFLICT(from_element, to_element, relation) DO NOTHING""",
            r,
        )

    for s in nen["stems"]:
        conn.execute(
            """INSERT INTO stems (stem_index, code, name_vi, name_original, polarity, element_code)
               VALUES (:stem_index, :code, :name_vi, :name_original, :polarity, :element_code)
               ON CONFLICT(stem_index) DO UPDATE SET
                   code = excluded.code,
                   name_vi = excluded.name_vi,
                   name_original = excluded.name_original,
                   polarity = excluded.polarity,
                   element_code = excluded.element_code""",
            s,
        )

    for b in nen["branches"]:
        conn.execute(
            """INSERT INTO branches (branch_index, code, name_vi, name_original, polarity, element_code)
               VALUES (:branch_index, :code, :name_vi, :name_original, :polarity, :element_code)
               ON CONFLICT(branch_index) DO UPDATE SET
                   code = excluded.code,
                   name_vi = excluded.name_vi,
                   name_original = excluded.name_original,
                   polarity = excluded.polarity,
                   element_code = excluded.element_code""",
            b,
        )

    for n in ns["rule_namespaces"]:
        conn.execute(
            """INSERT INTO rule_namespaces (namespace, name_vi, description)
               VALUES (:namespace, :name_vi, :description)
               ON CONFLICT(namespace) DO UPDATE SET
                   name_vi = excluded.name_vi,
                   description = excluded.description""",
            n,
        )

    for ev in ns["event_types"]:
        conn.execute(
            """INSERT INTO event_types
                   (event_type_id, code, name_vi, name_original, status, notes)
               VALUES (:event_type_id, :code, :name_vi, :name_original, 'PLACEHOLDER',
                       'Chua co bo quy tac Hiep Ky xac minh')
               ON CONFLICT(event_type_id) DO UPDATE SET
                   code = excluded.code,
                   name_vi = excluded.name_vi,
                   name_original = excluded.name_original,
                   updated_at = datetime('now')""",
            ev,
        )

    _nap_nguon_va_quy_tac(conn, _doc_yaml("nguon_va_quy_tac_lich.yaml", thu_muc_mam))

    nap_tang_can(conn, thu_muc_mam)
    nap_thap_than(conn)
    nap_quyen_khi(conn)
    nap_quyet_dinh_v1(conn)

    conn.execute(
        """INSERT INTO known_conflicts
               (conflict_id, rule_id, title_vi, mo_ta, cac_cach_hieu,
                dang_dung, trang_thai, anh_huong_toi)
           VALUES ('KC-0001','TIME-0007',
               'Can giờ Tý phần trước nửa đêm',
               'Khi mốc đổi ngày là nửa đêm mà thời điểm rơi vào phần giờ Tý trước đó, '
               || 'chưa rõ Can giờ tra theo Can ngày đang diễn ra hay Can ngày hôm sau.',
               json_array('DUNG_CAN_NGAY_HIEN_TAI','DUNG_CAN_NGAY_HOM_SAU'),
               'implementation_default, NOT_VERIFIED, NOT_FOR_GOLDEN_SCORING',
               'OPEN',
               'Trụ giờ trong phần giờ Tý trước nửa đêm')
           ON CONFLICT(conflict_id) DO NOTHING"""
    )

    for bo in tai_tat_ca(thu_muc_lich).values():
        dong_bo_vao_db(conn, bo)

    conn.commit()
    return dem_ban_ghi_nen(conn)


def _nap_nguon_va_quy_tac(conn: sqlite3.Connection, raw: dict[str, Any]) -> None:
    """Nạp bảng nguồn và các quy tắc lịch pháp.

    Quy tắc đã bị khoá thì bỏ qua, không ghi đè. Đúng nguyên tắc mục 4.
    """
    import json

    for s in raw["sources"]:
        conn.execute(
            """INSERT INTO sources (source_id, title, author, dynasty_or_year, edition,
                   language, source_type, url_or_file_reference, primary_or_secondary,
                   edition_certainty, provenance_note, independence_group, status, notes)
               VALUES (:source_id, :title, :author, :dynasty_or_year, :edition,
                   :language, :source_type, :url_or_file_reference, :primary_or_secondary,
                   :edition_certainty, :provenance_note, :independence_group, :status, :notes)
               ON CONFLICT(source_id) DO UPDATE SET
                   title = excluded.title, notes = excluded.notes,
                   status = excluded.status,
                   edition_certainty = excluded.edition_certainty,
                   provenance_note = excluded.provenance_note,
                   independence_group = excluded.independence_group,
                   updated_at = datetime('now')""",
            {**s, "edition_certainty": s.get("edition_certainty", "UNKNOWN"),
             "provenance_note": s.get("provenance_note"),
             "independence_group": s.get("independence_group", "UNASSIGNED")},
        )

    for pg in raw.get("passages", []):
        conn.execute(
            """INSERT INTO source_passages
                   (passage_id, source_id, chapter, original_text, translation_vi, derivation_note)
               VALUES (:passage_id, :source_id, :chapter, :original_text,
                       :translation_vi, :derivation_note)
               ON CONFLICT(passage_id) DO UPDATE SET
                   original_text = excluded.original_text,
                   translation_vi = excluded.translation_vi,
                   derivation_note = excluded.derivation_note""",
            {**pg, "derivation_note": pg.get("derivation_note")},
        )

    for r in raw["rules"]:
        conn.execute(
            """INSERT INTO rule_registry
                   (rule_id, rule_group, namespace, name_vi, name_original,
                    active_version, is_active)
               VALUES (?,?,?,?,?,1,?)
               ON CONFLICT(rule_id) DO UPDATE SET
                   name_vi = excluded.name_vi, is_active = excluded.is_active,
                   updated_at = datetime('now')""",
            (r["rule_id"], r["rule_group"], r["namespace"], r["name_vi"],
             r.get("name_original"), int(r.get("is_active", False))),
        )
        rvid = f"{r['rule_id']}@1"
        da_co = conn.execute(
            "SELECT locked FROM rule_versions WHERE rule_version_id = ?", (rvid,)
        ).fetchone()
        if da_co is not None and da_co["locked"]:
            continue
        conn.execute(
            """INSERT INTO rule_versions
                   (rule_version_id, rule_id, version, status, confidence,
                    inputs, preconditions, logic, outputs,
                    effect_class, priority, block_type, severity, mitigatable, notes)
               VALUES (?,?,1,?,?,'[]','[]',?,'[]','EXPLANATORY',100,'NONE','MINOR',0,?)
               ON CONFLICT(rule_version_id) DO UPDATE SET
                   status = excluded.status, logic = excluded.logic,
                   confidence = excluded.confidence, notes = excluded.notes""",
            (rvid, r["rule_id"], r["status"], r.get("confidence", "LOW"),
             json.dumps(r.get("logic"), ensure_ascii=False), r.get("notes")),
        )
        for pid in r.get("passages", []):
            conn.execute(
                """INSERT INTO rule_version_passages (rule_version_id, passage_id)
                   VALUES (?,?) ON CONFLICT DO NOTHING""", (rvid, pid))
        for s in r.get("sources", []):
            conn.execute(
                """INSERT INTO rule_version_sources
                       (rule_version_id, source_id, source_location, source_level, logic_note)
                   VALUES (?,?,?,?,?)
                   ON CONFLICT(rule_version_id, source_id, source_level) DO UPDATE SET
                       logic_note = excluded.logic_note""",
                (rvid, s["source_id"], s.get("source_location"),
                 s["source_level"], s.get("logic_note")),
            )


BANG_NEN = (
    "elements", "element_relations", "stems", "branches",
    "rule_namespaces", "event_types",
    "calendar_rulesets", "calendar_ruleset_settings",
    "sources", "rule_registry", "rule_versions", "rule_version_sources", "known_conflicts",
    "source_passages", "rule_version_passages", "independence_groups",
    "branch_hidden_stems", "hidden_stem_order_variants",
    "ten_gods", "ten_god_naming_variants", "ten_god_source_examples",
    "month_commands", "seasonal_governing_qi", "seasonal_qi_agreement",
)


def dem_ban_ghi_nen(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        bang: conn.execute(f"SELECT COUNT(*) AS n FROM {bang}").fetchone()["n"]
        for bang in BANG_NEN
    }


SO_LUONG_MONG_DOI = {
    "elements": 5,
    "element_relations": 10,
    "stems": 10,
    "branches": 12,
    "rule_namespaces": 27,
    "event_types": 13,
    "calendar_rulesets": 2,
    "calendar_ruleset_settings": 20,
    "sources": 17,
    "rule_registry": 71,
    "rule_versions": 71,
    "rule_version_sources": 96,
    "source_passages": 30,
    "rule_version_passages": 50,
    "independence_groups": 7,
    "branch_hidden_stems": 28,
    "hidden_stem_order_variants": 10,
    "ten_gods": 10,
    "ten_god_naming_variants": 2,
    "ten_god_source_examples": 12,
    "month_commands": 12,
    "known_conflicts": 1,
}


def kiem_so_luong(conn: sqlite3.Connection) -> list[str]:
    """So số bản ghi thực tế với số mong đợi. Rỗng nghĩa là khớp."""
    thuc_te = dem_ban_ghi_nen(conn)
    return [
        f"{bang}: mong đợi {mong}, thực tế {thuc_te.get(bang)}"
        for bang, mong in SO_LUONG_MONG_DOI.items()
        if thuc_te.get(bang) != mong
    ]
