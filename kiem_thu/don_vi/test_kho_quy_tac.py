"""Kiểm thử Rule Registry: bộ kiểm định, phiên bản, khoá, nhật ký, truy ngược nguồn."""

from __future__ import annotations

import json
import sqlite3

import pytest

from loi.kho_quy_tac.kiem_dinh import (
    RegistryValidationError,
    bat_buoc_hop_le,
    kiem_phien_ban,
    kiem_toan_kho,
    truy_nguoc_quy_tac,
)
from loi.kho_quy_tac.mo_hinh import RuleSourceLink, RuleVersion
from loi.nen.trang_thai import (
    BlockType,
    Confidence,
    EffectClass,
    RuleStatus,
    SourceLevel,
)

LOGIC_MAU = {"kieu": "so_sanh", "ve_trai": "day_branch", "phep": "XUNG", "ve_phai": "month_branch"}


def _nguon_chinh() -> RuleSourceLink:
    return RuleSourceLink(
        source_id="SRC-HIEPKY-QD",
        source_level=SourceLevel.PRIMARY,
        source_location="quyển 1",
        original_text="…",
        translation_vi="…",
        logic_note="…",
    )


def _quy_tac_tot(**doi) -> RuleVersion:
    tham_so = dict(
        rule_id="HK-DAY-0001",
        version=1,
        status=RuleStatus.VERIFIED,
        effect_class=EffectClass.SCORING,
        logic=LOGIC_MAU,
        outputs=["EVENT_SCORE_DELTA"],
        max_effect=-10.0,
        confidence=Confidence.MEDIUM,
        sources=[_nguon_chinh()],
    )
    tham_so.update(doi)
    return RuleVersion(**tham_so)


# --- V01 -----------------------------------------------------------

def test_verified_thieu_nguon_thi_truot():
    rv = _quy_tac_tot(sources=[])
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V01" in ma
    with pytest.raises(RegistryValidationError):
        bat_buoc_hop_le(rv)


def test_verified_chi_co_nguon_doi_chieu_thi_truot():
    rv = _quy_tac_tot(sources=[RuleSourceLink("SRC-TMTH", SourceLevel.CROSS_REFERENCE)])
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V01" in ma


def test_provisional_khong_can_nguon_primary():
    rv = _quy_tac_tot(status=RuleStatus.PROVISIONAL, sources=[])
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V01" not in ma


# --- V02 -----------------------------------------------------------

def test_quy_tac_cham_diem_thieu_logic_thi_truot():
    rv = _quy_tac_tot(logic=None)
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V02" in ma


def test_quy_tac_giai_thich_khong_can_logic():
    rv = _quy_tac_tot(effect_class=EffectClass.EXPLANATORY, logic=None,
                      outputs=[], max_effect=None)
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V02" not in ma


# --- V03 -----------------------------------------------------------

def test_hard_block_thieu_block_type_thi_truot():
    rv = _quy_tac_tot(effect_class=EffectClass.HARD_BLOCK, block_type=BlockType.NONE)
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V03" in ma


def test_hard_block_co_block_type_thi_dat():
    rv = _quy_tac_tot(effect_class=EffectClass.HARD_BLOCK,
                      block_type=BlockType.EVENT_SPECIFIC)
    assert not [x for x in kiem_phien_ban(rv) if x.muc == "LOI"]


def test_than_sat_khong_duoc_lam_hard_block():
    rv = _quy_tac_tot(rule_id="SS-0001", effect_class=EffectClass.HARD_BLOCK,
                      block_type=BlockType.ABSOLUTE)
    ma = [x.ma for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    assert "V03" in ma


# --- Ghi vào kho, V04, V05, V06, V10 --------------------------------

def _them_nguon(conn: sqlite3.Connection, source_id="SRC-HIEPKY-QD"):
    conn.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
                                primary_or_secondary, status, edition,
                                independence_group)
           VALUES (?,?,?,?,?,?,?,?)
           ON CONFLICT(source_id) DO NOTHING""",
        (source_id, "欽定協紀辨方書", "zh-Hant", "CLASSIC", "PRIMARY", "ACTIVE",
         "bản chữ Hán", "CLASSICAL_TEXT"),
    )


def _ghi_quy_tac(conn: sqlite3.Connection, rv: RuleVersion, is_active=True,
                 gan_nguon=True) -> None:
    conn.execute(
        """INSERT INTO rule_registry (rule_id, rule_group, namespace, name_vi, active_version, is_active)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(rule_id) DO UPDATE SET
               active_version = excluded.active_version, is_active = excluded.is_active""",
        (rv.rule_id, "HK-DAY", rv.rule_id.rsplit("-", 1)[0], "Quy tắc thử",
         rv.version, int(is_active)),
    )
    row = rv.to_row()
    conn.execute(
        f"INSERT INTO rule_versions ({','.join(row)}) "
        f"VALUES ({','.join(':' + k for k in row)})",
        row,
    )
    if gan_nguon:
        for s in rv.sources:
            _them_nguon(conn, s.source_id)
            conn.execute(
                """INSERT INTO rule_version_sources
                       (rule_version_id, source_id, source_location, source_level,
                        original_text, translation_vi, logic_note)
                   VALUES (?,?,?,?,?,?,?)""",
                (rv.rule_version_id, s.source_id, s.source_location, s.source_level.value,
                 s.original_text, s.translation_vi, s.logic_note),
            )
    conn.commit()


def _chi_loi(conn):
    """Chỉ lấy mục chặn. Cảnh báo không được coi là lỗi."""
    return [x for x in kiem_toan_kho(conn) if x.muc == "LOI"]


def test_kho_sach_thi_khong_co_loi(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot())
    assert _chi_loi(db_da_nap) == []


def test_co_thu_thieu_edition_certainty_thi_bi_canh_bao(db_da_nap):
    """V12 cảnh báo, không chặn. Nguồn cổ phải nói rõ mức chắc chắn về bản in."""
    _ghi_quy_tac(db_da_nap, _quy_tac_tot())
    canh_bao = [x for x in kiem_toan_kho(db_da_nap)
                if x.ma == "V12" and x.doi_tuong == "SRC-HIEPKY-QD"]
    assert len(canh_bao) == 1
    assert canh_bao[0].muc == "CANH_BAO"


def test_verified_ma_nguon_chinh_van_la_cho_trong_thi_bi_chan(db_da_nap):
    """V11 — không được lấy chỗ trống làm nguồn rồi tuyên bố đã xác minh."""
    conn = db_da_nap
    conn.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
               primary_or_secondary, edition_certainty, status, independence_group)
           VALUES ('SRC-TRONG','Chỗ trống','vi','OTHER','SECONDARY','NOT_APPLICABLE',
                   'PENDING','NONE')""")
    rv = _quy_tac_tot(rule_id="HK-DAY-0002",
                      sources=[RuleSourceLink("SRC-TRONG", SourceLevel.PRIMARY)])
    _ghi_quy_tac(conn, rv, is_active=False)
    ma = [x.ma for x in _chi_loi(conn)]
    assert "V11" in ma


def test_rejected_khong_duoc_active(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot(status=RuleStatus.REJECTED), is_active=True)
    ma = [x.ma for x in kiem_toan_kho(db_da_nap)]
    assert "V04" in ma


def test_provisional_khong_duoc_bat_de_cham_diem(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot(status=RuleStatus.PROVISIONAL), is_active=True)
    ma = [x.ma for x in kiem_toan_kho(db_da_nap)]
    assert "V10" in ma


def test_active_version_khong_ton_tai_thi_bao_loi(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot())
    db_da_nap.execute("UPDATE rule_registry SET active_version = 99 WHERE rule_id='HK-DAY-0001'")
    ma = [x.ma for x in kiem_toan_kho(db_da_nap)]
    assert "V04" in ma


def test_verified_thieu_nguon_trong_kho_bi_bat(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot(), gan_nguon=False)
    ma = [x.ma for x in kiem_toan_kho(db_da_nap)]
    assert "V01" in ma


# --- Phiên bản và khoá ----------------------------------------------

def test_sua_phien_ban_da_khoa_thi_bi_chan(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot())
    conn.execute("UPDATE rule_versions SET locked = 1 WHERE rule_version_id = 'HK-DAY-0001@1'")
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError, match="RULE_VERSION_LOCKED"):
        conn.execute(
            "UPDATE rule_versions SET logic = '{}' WHERE rule_version_id = 'HK-DAY-0001@1'"
        )


def test_xoa_phien_ban_da_khoa_thi_bi_chan(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot())
    conn.execute("UPDATE rule_versions SET locked = 1 WHERE rule_version_id = 'HK-DAY-0001@1'")
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError, match="RULE_VERSION_LOCKED"):
        conn.execute("DELETE FROM rule_versions WHERE rule_version_id = 'HK-DAY-0001@1'")


def test_sua_quy_tac_bang_cach_tao_phien_ban_moi(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot())
    conn.execute("UPDATE rule_versions SET locked = 1 WHERE rule_version_id = 'HK-DAY-0001@1'")
    conn.commit()

    rv2 = _quy_tac_tot(version=2, max_effect=-6.0)
    row = rv2.to_row()
    conn.execute(
        f"INSERT INTO rule_versions ({','.join(row)}) "
        f"VALUES ({','.join(':' + k for k in row)})", row)
    _them_nguon(conn)
    conn.execute(
        """INSERT INTO rule_version_sources (rule_version_id, source_id, source_level)
           VALUES (?,?,?)""", (rv2.rule_version_id, "SRC-HIEPKY-QD", "PRIMARY"))
    conn.execute("UPDATE rule_registry SET active_version = 2 WHERE rule_id = 'HK-DAY-0001'")
    conn.commit()

    ban_ghi = conn.execute(
        "SELECT version, max_effect, locked FROM rule_versions "
        "WHERE rule_id='HK-DAY-0001' ORDER BY version").fetchall()
    assert [r["version"] for r in ban_ghi] == [1, 2]
    assert ban_ghi[0]["max_effect"] == -10.0, "phiên bản cũ phải giữ nguyên"
    assert ban_ghi[0]["locked"] == 1
    assert _chi_loi(conn) == []


def test_nhat_ky_ghi_khi_tao_va_doi_trang_thai(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot(status=RuleStatus.PROVISIONAL), is_active=False)
    tao = conn.execute(
        "SELECT * FROM audit_logs WHERE entity_id='HK-DAY-0001@1' AND action='CREATE'"
    ).fetchall()
    assert len(tao) == 1

    conn.execute("UPDATE rule_versions SET status='VERIFIED' WHERE rule_version_id='HK-DAY-0001@1'")
    conn.commit()
    doi = conn.execute(
        "SELECT before_payload, after_payload FROM audit_logs "
        "WHERE entity_id='HK-DAY-0001@1' AND action='STATUS_CHANGE'").fetchone()
    assert json.loads(doi["before_payload"])["status"] == "PROVISIONAL"
    assert json.loads(doi["after_payload"])["status"] == "VERIFIED"


def test_nhat_ky_ghi_khi_gan_nguon(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot())
    n = db_da_nap.execute(
        "SELECT COUNT(*) AS n FROM audit_logs "
        "WHERE action='SOURCE_CHANGE' AND entity_id='HK-DAY-0001@1'").fetchone()["n"]
    assert n == 1


# --- Truy ngược: kết quả -> quy tắc -> phiên bản -> nguồn -------------

def _dung_mot_ket_qua(conn: sqlite3.Connection) -> str:
    conn.execute("INSERT INTO users (user_id, display_name) VALUES ('U1','Đạt')")
    conn.execute("INSERT INTO profiles (profile_id, user_id, full_name, gender) "
                 "VALUES ('P1','U1','Thử','NAM')")
    conn.execute(
        """INSERT INTO bazi_charts
           (chart_id, profile_id, calendar_ruleset_id,
            year_stem_index, year_branch_index, month_stem_index, month_branch_index,
            day_stem_index, day_branch_index, day_master_stem_index,
            ruleset_version, engine_version)
           VALUES ('C1','P1','CAL-V1',1,1,1,1,1,1,1,'RS-T','EV-T')""")
    conn.execute(
        """INSERT INTO day_analysis
           (day_analysis_id, chart_id, solar_date, stem_index, branch_index,
            ruleset_version, engine_version)
           VALUES ('D1','C1','2026-09-01',1,1,'RS-T','EV-T')""")
    conn.execute(
        """INSERT INTO fusion_results
           (fusion_result_id, profile_id, day_analysis_id, ruleset_version, engine_version)
           VALUES ('F1','P1','D1','RS-T','EV-T')""")
    conn.execute(
        """INSERT INTO fusion_findings
           (fusion_result_id, finding_kind, rule_version_id, severity, detail_vi)
           VALUES ('F1','NEGATIVE','HK-DAY-0001@1','MEDIUM','thử truy ngược')""")
    conn.commit()
    return "F1"


def test_truy_nguoc_ve_toi_sach_nguon(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot())
    _dung_mot_ket_qua(conn)
    chuoi = truy_nguoc_quy_tac(conn, "F1")
    assert len(chuoi) == 1
    mat_xich = chuoi[0]
    assert mat_xich["rule_id"] == "HK-DAY-0001"
    assert mat_xich["rule_version_id"] == "HK-DAY-0001@1"
    assert mat_xich["source_id"] == "SRC-HIEPKY-QD"
    assert mat_xich["edition"] == "bản chữ Hán"


def test_dung_quy_tac_thi_tu_dong_khoa(db_da_nap):
    conn = db_da_nap
    _ghi_quy_tac(conn, _quy_tac_tot())
    assert conn.execute(
        "SELECT locked FROM rule_versions WHERE rule_version_id='HK-DAY-0001@1'"
    ).fetchone()["locked"] == 0

    _dung_mot_ket_qua(conn)

    assert conn.execute(
        "SELECT locked FROM rule_versions WHERE rule_version_id='HK-DAY-0001@1'"
    ).fetchone()["locked"] == 1
    assert _chi_loi(conn) == []

    with pytest.raises(sqlite3.IntegrityError, match="RULE_VERSION_LOCKED"):
        conn.execute("UPDATE rule_versions SET logic='{}' "
                     "WHERE rule_version_id='HK-DAY-0001@1'")


def test_khung_nhin_rule_sources_hoat_dong(db_da_nap):
    _ghi_quy_tac(db_da_nap, _quy_tac_tot())
    row = db_da_nap.execute(
        "SELECT rule_id, title, source_level FROM rule_sources "
        "WHERE rule_id = 'HK-DAY-0001'").fetchone()
    assert row["rule_id"] == "HK-DAY-0001"
    assert row["source_level"] == "PRIMARY"
