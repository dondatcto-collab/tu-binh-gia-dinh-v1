"""Nạp mười Thập Thần vào kho quy tắc.

Mỗi ô là một quy tắc BT-TG-001 tới BT-TG-010.
Thêm một quy tắc BT-TG-CONFLICT-001 cho chỗ các nguồn gọi tên khác nhau.
"""

from __future__ import annotations

import json
import sqlite3

from loi.bat_tu.thap_than import doc_cau_hinh
from loi.lich.quy_uoc_can_chi import CAN


def nap(conn: sqlite3.Connection) -> dict[str, int]:
    raw = doc_cau_hinh()
    source_id = raw["source_id"]
    passage_id = raw["passage_id"]

    for x in raw["thap_than"]:
        conn.execute(
            """INSERT INTO ten_gods (ten_god_code, rule_id, name_vi, name_original,
                   relation_direction, polarity_relation, source_id, status)
               VALUES (?,?,?,?,?,?,?,'VERIFIED')
               ON CONFLICT(ten_god_code) DO UPDATE SET
                   name_vi = excluded.name_vi, status = excluded.status""",
            (x["code"], x["rule_id"], x["name_vi"], x["name_original"],
             x["chieu"], x["tinh"], source_id),
        )
        conn.execute(
            """INSERT INTO rule_registry (rule_id, rule_group, namespace, name_vi,
                   name_original, active_version, is_active)
               VALUES (?,'BT-TG','BT-TG',?,?,1,1)
               ON CONFLICT(rule_id) DO UPDATE SET name_vi = excluded.name_vi""",
            (x["rule_id"], f"Thập Thần {x['name_vi']}", x["name_original"]),
        )
        rvid = f"{x['rule_id']}@1"
        conn.execute(
            """INSERT INTO rule_versions (rule_version_id, rule_id, version, status,
                   confidence, inputs, preconditions, logic, outputs,
                   effect_class, priority, block_type, severity, mitigatable, notes)
               VALUES (?,?,1,'VERIFIED','MEDIUM',
                   '["DAY_MASTER_STEM","TARGET_STEM"]','[]',?,'["TEN_GOD"]',
                   'EXPLANATORY',100,'NONE','MINOR',0,?)
               ON CONFLICT(rule_version_id) DO UPDATE SET logic = excluded.logic""",
            (rvid, x["rule_id"],
             json.dumps({"kieu": "QUAN_HE", "relation_direction": x["chieu"],
                         "polarity_relation": x["tinh"], "ten_god": x["code"],
                         "khong_co": ["strength", "score", "favorable", "hy_ky"]},
                        ensure_ascii=False),
             "Suy ra từ hai chiều quan hệ, không tra bảng mười nhân mười."),
        )
        conn.execute(
            """INSERT INTO rule_version_sources (rule_version_id, source_id,
                   source_location, source_level, logic_note)
               VALUES (?,?,'quyển một, đoạn năm loại','PRIMARY',?)
               ON CONFLICT(rule_version_id, source_id, source_level) DO NOTHING""",
            (rvid, source_id, "Định nghĩa quan hệ và quy ước đồng tính khác tính."),
        )
        conn.execute(
            """INSERT INTO rule_version_passages (rule_version_id, passage_id)
               VALUES (?,?) ON CONFLICT DO NOTHING""", (rvid, passage_id))

    for v in raw["vi_du_trong_nguyen_van"]:
        if v["nhat_chu"] not in CAN or v["doi_tuong"] not in CAN:
            raise ValueError(f"VI_DU_CO_CAN_LA: {v}")
        conn.execute(
            """INSERT INTO ten_god_source_examples (example_id, day_master, target_stem,
                   ten_god_code, source_id, original_text, translation_vi)
               VALUES (?,?,?,?,?,?,?)
               ON CONFLICT(example_id) DO UPDATE SET
                   original_text = excluded.original_text""",
            (f"{v['nhat_chu']}-{v['doi_tuong']}", v["nhat_chu"], v["doi_tuong"],
             v["ket_qua"], source_id, v["nguyen_van"], v["dich"]),
        )

    _nap_di_biet(conn, raw)
    conn.commit()
    return dem(conn)


def _nap_di_biet(conn: sqlite3.Connection, raw: dict) -> None:
    d = raw["lich_su_thuat_ngu"]
    conn.execute(
        """INSERT INTO rule_registry (rule_id, rule_group, namespace, name_vi,
               active_version, is_active)
           VALUES (?,'BT-TG-CONFLICT','BT-TG-CONFLICT',
               'Lịch sử thuật ngữ Tỷ Kiên và Dương Nhận — KHÔNG phải cùng khái niệm',1,0)
           ON CONFLICT(rule_id) DO NOTHING""", (d["rule_id"],))
    rvid = f"{d['rule_id']}@1"
    conn.execute(
        """INSERT INTO rule_versions (rule_version_id, rule_id, version, status,
               confidence, inputs, preconditions, logic, outputs,
               effect_class, priority, block_type, severity, mitigatable, notes)
           VALUES (?,?,1,'CONFLICTED','LOW','[]','[]',?,'[]',
               'EXPLANATORY',100,'NONE','MINOR',0,?)
           ON CONFLICT(rule_version_id) DO UPDATE SET logic = excluded.logic""",
        (rvid, d["rule_id"],
         json.dumps({"kieu": "LICH_SU_THUAT_NGU",
                     "quan_he": d["quan_he"],
                     "o": d["o_lien_quan"],
                     "cac_khai_niem": [
                         {"ten": c["ten"], "thuoc_nhom": c["thuoc_nhom"],
                          "loai": c["loai_khai_niem"],
                          "xac_dinh_bang": c["xac_dinh_bang"]}
                         for c in d["cac_cach_dung"]],
                     "canh_bao": "NOT_A_DIRECT_ALIAS"},
                    ensure_ascii=False),
         d["quyet_dinh"].strip()),
    )
    conn.execute(
        """INSERT INTO rule_version_sources (rule_version_id, source_id,
               source_level, logic_note)
           VALUES (?,?,'PRIMARY',?)
           ON CONFLICT(rule_version_id, source_id, source_level) DO NOTHING""",
        (rvid, raw["source_id"],
         "NOT_A_DIRECT_ALIAS. Hai khái niệm khác nhau, xác định bằng thứ khác nhau."),
    )
    for c in d["cac_cach_dung"]:
        conn.execute(
            """INSERT INTO ten_god_naming_variants (variant_id, relation_direction,
                   polarity_relation, variant_name, name_original, source_id,
                   source_quote, is_active_convention, alias_relation,
                   concept_group, concept_kind, determined_by, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(variant_id) DO UPDATE SET
                   source_quote = excluded.source_quote,
                   alias_relation = excluded.alias_relation,
                   concept_group = excluded.concept_group""",
            (f"DONG_HANH-DONG_TINH:{c['ten']}",
             d["o_lien_quan"]["chieu"], d["o_lien_quan"]["tinh"],
             c["ten"], c.get("name_original"), raw["source_id"], c["nguyen_van"],
             int(c["la_quy_uoc_dang_dung"]), d["quan_he"],
             c["thuoc_nhom"], c["loai_khai_niem"], c["xac_dinh_bang"],
             c.get("ghi_chu") or c["nguon"]),
        )


def dem(conn: sqlite3.Connection) -> dict[str, int]:
    return {b: conn.execute(f"SELECT COUNT(*) AS n FROM {b}").fetchone()["n"]
            for b in ("ten_gods", "ten_god_naming_variants", "ten_god_source_examples")}
