"""Nạp nguyệt lệnh (BT-ML) và quyền khí theo tiết (BT-SEASON-POWER)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

from loi.bat_tu.nguyet_lenh import MUA_THEO_CHI
from loi.bat_tu.quyen_khi import tinh_dong_thuan
from loi.lich.quy_uoc_can_chi import CAN, CHI, quy_uoc_mac_dinh
from loi.nen.phien_ban import GOC_DU_AN

DUONG_DAN = GOC_DU_AN / "cau_hinh" / "can_chi" / "quyen_khi_theo_tiet.yaml"


def doc_cau_hinh(duong_dan: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load((duong_dan or DUONG_DAN).read_text(encoding="utf-8"))


# ---------------------------------------------------------------
# 3C-1 — Nguyệt lệnh
# ---------------------------------------------------------------

def nap_nguyet_lenh(conn: sqlite3.Connection) -> int:
    q = quy_uoc_mac_dinh()
    jie = [t for t in q.tiet_khi if q.la_mo_thang(t)]
    theo_chi = {t.month_branch: t for t in jie}

    for i, chi in enumerate(CHI):
        mo = theo_chi[chi]
        # Tiết đóng tháng là Tiết mở của Chi kế tiếp.
        dong = theo_chi[CHI[(i + 1) % 12]]
        rule_id = f"BT-ML-{CHI.index(chi) + 1:03d}"
        conn.execute(
            """INSERT INTO rule_registry (rule_id, rule_group, namespace, name_vi,
                   name_original, active_version, is_active)
               VALUES (?,'BT-ML','BT-ML',?,?,1,1)
               ON CONFLICT(rule_id) DO UPDATE SET name_vi = excluded.name_vi""",
            (rule_id, f"Nguyệt lệnh tháng {chi}", mo.name_original),
        )
        rvid = f"{rule_id}@1"
        conn.execute(
            """INSERT INTO rule_versions (rule_version_id, rule_id, version, status,
                   confidence, inputs, preconditions, logic, outputs,
                   effect_class, priority, block_type, severity, mitigatable, notes)
               VALUES (?,?,1,'VERIFIED','HIGH','["MOMENT"]','[]',?,
                   '["MONTH_BRANCH","SEASON","JIE_INTERVAL"]',
                   'EXPLANATORY',100,'NONE','MINOR',0,?)
               ON CONFLICT(rule_version_id) DO UPDATE SET logic = excluded.logic""",
            (rvid, rule_id,
             json.dumps({"kieu": "NGUYET_LENH", "month_branch": chi,
                         "season": MUA_THEO_CHI[chi],
                         "opening_jie": mo.code, "closing_jie": dong.code,
                         "khong_co": ["strength", "score", "ty_le", "vuong_suy"]},
                        ensure_ascii=False),
             "Chỉ xác định Chi tháng, mùa và khoảng tiết. Không đánh giá gì."),
        )
        conn.execute(
            """INSERT INTO rule_version_sources (rule_version_id, source_id,
                   source_level, logic_note)
               VALUES (?,'SRC-UHTB-CHEP','PRIMARY',?)
               ON CONFLICT(rule_version_id, source_id, source_level) DO NOTHING""",
            (rvid, "Tháng mở tại Tiết; xem TIME-0002 và bài phú Địa Chi tàng độn."),
        )
        conn.execute(
            """INSERT INTO month_commands (month_branch, season, opening_jie,
                   closing_jie, rule_id, source_id)
               VALUES (?,?,?,?,?,'SRC-UHTB-CHEP')
               ON CONFLICT(month_branch) DO UPDATE SET
                   season = excluded.season, opening_jie = excluded.opening_jie""",
            (chi, MUA_THEO_CHI[chi], mo.code, dong.code, rule_id),
        )
    return 12


# ---------------------------------------------------------------
# 3C-2 — Quyền khí theo tiết
# ---------------------------------------------------------------

CAM_TU = ("60/30/10", "70/20/10", "percent", "strength", "score",
          "MAIN_QI", "MIDDLE_QI", "RESIDUAL_QI")

# Tên khoá bị cấm. Đột biến kiểu `ty_le: 60` không chứa chuỗi cấm nào,
# nên quét giá trị là không đủ. Phải quét cả tên khoá.
CAM_KHOA = ("ty_le", "trong_so", "weight", "ratio", "percent", "phan_tram",
            "strength", "score", "diem", "manh_yeu", "vai_tro", "semantic_role",
            "vuong_suy", "priority")

# Trạng thái hợp lệ cho một truyền thống. Không được tự nâng lên VERIFIED.
TRANG_THAI_TRUYEN_THONG = ("PROVISIONAL", "CONFLICTED", "NOT_TRANSCRIBED")

# Nguồn KHÔNG được dùng cho quyền khí: chỗ trống chờ nguồn.
NGUON_CAM = ("SRC-CHUA-CO-NGUON",)


def kiem_cau_hinh(raw: dict[str, Any]) -> list[str]:
    """Quét từ cấm trong PHẦN DỮ LIỆU.

    Khối `cam` cố ý chứa các từ đó vì nó là bản liệt kê điều cấm.
    Quét cả khối ấy thì bộ kiểm tự bắt chính mình.
    """
    loi: list[str] = []
    phan_du_lieu = {k: v for k, v in raw.items() if k != "cam"}
    van = json.dumps(phan_du_lieu, ensure_ascii=False)
    for tu in CAM_TU:
        if tu in van:
            loi.append(f"CO_TU_CAM_TRONG_QUYEN_KHI: {tu!r}")

    # Khối `cam` phải tồn tại và phải nêu đủ năm điều.
    if "cam" not in raw or len(raw["cam"]) < 5:
        loi.append("THIEU_KHOI_CAM: cấu hình phải nêu rõ những điều bị cấm")
    def quet_khoa(o, duong: str) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k in CAM_KHOA:
                    loi.append(f"CO_KHOA_CAM_TRONG_QUYEN_KHI: {duong}.{k}")
                quet_khoa(v, f"{duong}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                quet_khoa(v, f"{duong}[{i}]")

    quet_khoa(phan_du_lieu, "goc")

    for tt in raw["truyen_thong"]:
        if tt["status"] not in TRANG_THAI_TRUYEN_THONG:
            loi.append(
                f"TRANG_THAI_LA: {tt['tradition']} = {tt['status']}. "
                "Quyền khí chưa đủ căn cứ để VERIFIED.")
        if tt["source_id"] in NGUON_CAM:
            loi.append(
                f"NGUON_CAM: {tt['tradition']} dùng {tt['source_id']} — "
                "chỗ trống chờ nguồn không được làm nguồn cho quyền khí.")
        for d in tt.get("cac_doan") or []:
            for seg in d.get("doan") or []:
                if seg.get("can") is not None and seg["can"] not in CAN:
                    loi.append(f"CAN_LA: {tt['tradition']}.{d['tiet']} = {seg['can']}")
    return loi


def nap_quyen_khi(conn: sqlite3.Connection, raw: dict[str, Any] | None = None) -> int:
    raw = raw or doc_cau_hinh()
    loi = kiem_cau_hinh(raw)
    if loi:
        raise ValueError("CAU_HINH_QUYEN_KHI_HONG: " + "; ".join(loi))

    so = 0
    for tt in raw["truyen_thong"]:
        rule_id = f"BT-SEASON-POWER-{tt['tradition']}"
        conn.execute(
            """INSERT INTO rule_registry (rule_id, rule_group, namespace, name_vi,
                   active_version, is_active)
               VALUES (?,'BT-SEASON-POWER','BT-SEASON-POWER',?,1,0)
               ON CONFLICT(rule_id) DO UPDATE SET name_vi = excluded.name_vi""",
            (rule_id, f"Quyền khí theo tiết — bản {tt['tradition']}"),
        )
        rvid = f"{rule_id}@1"
        trang_thai = "CONFLICTED" if tt["status"] == "PROVISIONAL" else "PROVISIONAL"
        conn.execute(
            """INSERT INTO rule_versions (rule_version_id, rule_id, version, status,
                   confidence, inputs, preconditions, logic, outputs,
                   effect_class, priority, block_type, severity, mitigatable, notes)
               VALUES (?,?,1,?,'LOW','["SOLAR_TERM"]','[]',?,
                   '["GOVERNING_QI_VARIANTS"]','EXPLANATORY',100,'NONE','MINOR',0,?)
               ON CONFLICT(rule_version_id) DO UPDATE SET
                   logic = excluded.logic, status = excluded.status""",
            (rvid, rule_id, "PROVISIONAL" if tt["status"] != "NOT_TRANSCRIBED"
             else "PROVISIONAL",
             json.dumps({"kieu": "GHI_NGUON", "tradition": tt["tradition"],
                         "so_doan": len(tt.get("cac_doan") or []),
                         "khong_ket_luan": "mạnh yếu, tỷ lệ, vượng suy"},
                        ensure_ascii=False),
             tt["ghi_chu_chung"].strip()),
        )
        conn.execute(
            """INSERT INTO rule_version_sources (rule_version_id, source_id,
                   source_level, logic_note)
               VALUES (?,?,'PRIMARY',?)
               ON CONFLICT(rule_version_id, source_id, source_level) DO NOTHING""",
            (rvid, tt["source_id"], "Chép nguyên trạng, không vá, không hợp nhất."),
        )

        for thu_tu, d in enumerate(tt.get("cac_doan") or [], start=1):
            doan = d.get("doan") or []
            if not doan:
                conn.execute(
                    """INSERT INTO seasonal_governing_qi (entry_id, tradition, solar_term,
                           segment_order, governing_stem, day_count, textual_order,
                           original_text, parse_status, status, source_id, rule_id, notes)
                       VALUES (?,?,?,0,NULL,NULL,?,?,?, 'PROVISIONAL',?,?,?)
                       ON CONFLICT(entry_id) DO UPDATE SET
                           original_text = excluded.original_text""",
                    (f"{tt['tradition']}:{d['tiet']}:0", tt["tradition"], d["tiet"],
                     thu_tu, d["nguyen_van"], d["parse_status"],
                     tt["source_id"], rule_id, d.get("ghi_chu")),
                )
                so += 1
                continue
            for k, seg in enumerate(doan, start=1):
                conn.execute(
                    """INSERT INTO seasonal_governing_qi (entry_id, tradition, solar_term,
                           segment_order, governing_stem, day_count, textual_order,
                           original_text, parse_status, status, source_id, rule_id, notes)
                       VALUES (?,?,?,?,?,?,?,?,?, 'PROVISIONAL',?,?,?)
                       ON CONFLICT(entry_id) DO UPDATE SET
                           governing_stem = excluded.governing_stem,
                           day_count = excluded.day_count""",
                    (f"{tt['tradition']}:{d['tiet']}:{k}", tt["tradition"], d["tiet"],
                     k, seg.get("can"), seg.get("so_ngay"), thu_tu,
                     d["nguyen_van"], d["parse_status"], tt["source_id"], rule_id,
                     seg.get("ghi_chu") or d.get("ghi_chu")),
                )
                so += 1

    for tiet in {r["solar_term"] for r in conn.execute(
            "SELECT DISTINCT solar_term FROM seasonal_governing_qi")}:
        tt_status, so_tt, ly_do = tinh_dong_thuan(conn, tiet)
        conn.execute(
            """INSERT INTO seasonal_qi_agreement (solar_term, agreement_status,
                   tradition_count, notes)
               VALUES (?,?,?,?)
               ON CONFLICT(solar_term) DO UPDATE SET
                   agreement_status = excluded.agreement_status,
                   tradition_count = excluded.tradition_count,
                   notes = excluded.notes""",
            (tiet, tt_status, so_tt, ly_do),
        )
    return so


def nap(conn: sqlite3.Connection) -> dict[str, int]:
    n1 = nap_nguyet_lenh(conn)
    n2 = nap_quyen_khi(conn)
    conn.commit()
    return {"month_commands": n1, "seasonal_governing_qi": n2}
