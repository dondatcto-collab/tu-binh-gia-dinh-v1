from loi.bat_tu.phuong_phap_tu_binh import trang_thai_hien_tai, PHUONG_PHAP_ID
from loi.quyet_dinh.v1 import danh_gia_event


def test_cong_phuong_phap_khoa_dung_trang_thai():
    s = trang_thai_hien_tai()
    assert s.method_id == PHUONG_PHAP_ID == "ZPZQ-GEJU-V1"
    assert s.month_command_ready is True
    assert s.pattern_engine_ready is False
    assert s.use_favor_avoid_ready is False
    assert s.personal_decision_ready is False
    assert s.decision_mode == "DESCRIPTIVE_ONLY"


def test_ba_rule_phuong_phap_co_nguon_va_verified(db_da_nap):
    ids=("BT-BASE-0401","BT-USE-0401","BT-DY-0401")
    rows=db_da_nap.execute(
        "SELECT rv.rule_id, rv.status, s.source_id, s.edition_certainty "
        "FROM rule_versions rv "
        "JOIN rule_version_sources rvs ON rvs.rule_version_id=rv.rule_version_id "
        "JOIN sources s ON s.source_id=rvs.source_id "
        "WHERE rv.rule_id IN (?,?,?)", ids).fetchall()
    assert {r['rule_id'] for r in rows} == set(ids)
    assert all(r['status'] == 'VERIFIED' for r in rows)
    assert any(r['source_id']=='SRC-ZPZQ-NLC-SCAN' and r['edition_certainty']=='PINNED_SCAN' for r in rows)


def test_quan_he_ca_nhan_khong_thay_hang_hiep_ky():
    # Tháng Dần, ngày Tý = Khai; đổi Chi ngày sinh vẫn phải cùng hạng Hiệp Kỷ.
    a=danh_gia_event('DAN','TY','SUU','KHAI_TRUONG')
    b=danh_gia_event('DAN','TY','NGO','KHAI_TRUONG')
    assert a['rank_group'] == b['rank_group'] == 1
    assert a['label'] == b['label'] == 'Phù hợp theo Hiệp Kỷ'
    assert a['personal_relation']['decision_effect'] == 'NONE_UNTIL_NATAL_USE_READY'
    assert b['personal_relation']['decision_effect'] == 'NONE_UNTIL_NATAL_USE_READY'
