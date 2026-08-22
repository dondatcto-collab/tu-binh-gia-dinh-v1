"""Kiểm thử tầng cơ sở dữ liệu."""

from __future__ import annotations

import sqlite3

import pytest

from loi.kho_du_lieu.ket_noi import chay_migration, danh_sach_bang

BANG_BAT_BUOC = {
    "users", "profiles", "birth_data",
    "calendar_rulesets", "calendar_ruleset_settings",
    "bazi_charts",
    "rule_registry", "sources", "rule_versions", "rule_version_sources",
    "event_types", "event_mappings", "event_rule_packs",
    "natal_analysis", "da_yun_periods", "year_analysis", "month_analysis",
    "day_analysis", "hour_analysis",
    "fusion_results",
    "golden_cases", "golden_case_expected", "test_runs", "audit_logs",
}


def test_migration_tao_du_bang(db_trong):
    co = danh_sach_bang(db_trong)
    thieu = BANG_BAT_BUOC - co
    assert not thieu, f"thiếu bảng: {sorted(thieu)}"


def test_migration_chay_lai_khong_lam_gi_them(db_trong):
    lan_hai = chay_migration(db_trong)
    assert lan_hai == [], "chạy chuyển đổi lần hai không được chạy lại tệp cũ"


def test_migration_bi_sua_thi_bao_loi(db_trong, tmp_path):
    tep = tmp_path / "0099_thu.sql"
    tep.write_text("CREATE TABLE thu_nghiem (a INTEGER);", encoding="utf-8")
    chay_migration(db_trong, tmp_path)
    tep.write_text("CREATE TABLE thu_nghiem (a INTEGER, b INTEGER);", encoding="utf-8")
    with pytest.raises(RuntimeError, match="MIGRATION_DA_BI_SUA"):
        chay_migration(db_trong, tmp_path)


def test_khoa_ngoai_hoat_dong(db_trong):
    with pytest.raises(sqlite3.IntegrityError):
        db_trong.execute(
            "INSERT INTO profiles (profile_id, user_id, full_name, gender) "
            "VALUES ('P1','KHONG_CO_USER','Thử','NAM')"
        )


def test_rang_buoc_duy_nhat_hoat_dong(db_da_nap):
    conn = db_da_nap
    conn.execute("INSERT INTO users (user_id, display_name) VALUES ('U1','Đạt')")
    conn.execute(
        "INSERT INTO profiles (profile_id, user_id, full_name, gender) "
        "VALUES ('P1','U1','Thử','NAM')"
    )
    conn.execute(
        "INSERT INTO birth_data (birth_data_id, profile_id, birth_year, birth_month, "
        "birth_day, birth_hour, birth_minute, birth_place_text) "
        "VALUES ('B1','P1',1990,2,4,12,0,'Cần Thơ')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO birth_data (birth_data_id, profile_id, birth_year, birth_month, "
            "birth_day, birth_hour, birth_minute, birth_place_text) "
            "VALUES ('B2','P1',1991,3,5,13,0,'Cần Thơ')"
        )


def test_chi_mot_bo_lich_mac_dinh(db_da_nap):
    with pytest.raises(sqlite3.IntegrityError):
        db_da_nap.execute(
            "UPDATE calendar_rulesets SET is_default = 1 WHERE calendar_ruleset_id = 'CAL-V1-23H'"
        )


def test_kiem_tra_check_constraint(db_trong):
    with pytest.raises(sqlite3.IntegrityError):
        db_trong.execute("INSERT INTO users (user_id, display_name) VALUES ('U9','x')")
        db_trong.execute(
            "INSERT INTO profiles (profile_id, user_id, full_name, gender) "
            "VALUES ('P9','U9','Thử','KHAC')"
        )
