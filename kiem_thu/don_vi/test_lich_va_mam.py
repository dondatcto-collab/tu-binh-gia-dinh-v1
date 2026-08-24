"""Kiểm thử bộ quy ước lịch và dữ liệu mầm — release 0.5.0."""
from __future__ import annotations
import pytest, yaml
from loi.kho_du_lieu.nap_mam import dem_ban_ghi_nen, kiem_so_luong, nap_mam
from loi.lich.bo_quy_uoc import CalendarRulesetError, bo_mac_dinh, kiem_khong_hard_code, tai_tat_ca, tai_tu_db, tai_tu_tep
from loi.nen.phien_ban import DUONG_DAN


def test_tai_duoc_v1():
    bo=tai_tu_tep(DUONG_DAN["lich_phap"] / "CAL-V1.yaml")
    assert bo.calendar_ruleset_id=="CAL-V1" and bo.lay("YEAR_BOUNDARY")=="LI_CHUN" and bo.lay("MONTH_BOUNDARY")=="JIE"
    assert bo.moc_doi_ngay=="00:00" and bo.lay_bool("TRUE_SOLAR_TIME") is False and bo.lay_bool("LOCAL_TIMEZONE") is True and bo.lay_bool("HISTORICAL_TIMEZONE") is True and bo.is_default is True


def test_tai_duoc_v1_23h():
    bo=tai_tu_tep(DUONG_DAN["lich_phap"] / "CAL-V1-23H.yaml"); assert bo.calendar_ruleset_id=="CAL-V1-23H" and bo.moc_doi_ngay=="23:00" and bo.status=="EXPERIMENTAL" and bo.is_default is False


def test_phan_biet_duoc_hai_moc_doi_ngay():
    tat_ca=tai_tat_ca(); v1=tat_ca["CAL-V1"]; v23=tat_ca["CAL-V1-23H"]
    assert v1.moc_doi_ngay_phut==0 and v23.moc_doi_ngay_phut==23*60 and v1.doi_ngay_luc_nua_dem is True and v23.doi_ngay_luc_nua_dem is False
    for khoa in ("YEAR_BOUNDARY","MONTH_BOUNDARY","TRUE_SOLAR_TIME","LOCAL_TIMEZONE","HISTORICAL_TIMEZONE"): assert v1.lay(khoa)==v23.lay(khoa)


def test_chi_co_dung_mot_bo_mac_dinh(): assert sum(1 for b in tai_tat_ca().values() if b.is_default)==1


def _viet_cau_hinh(tmp_path,sua:dict):
    goc=yaml.safe_load((DUONG_DAN["lich_phap"] / "CAL-V1.yaml").read_text(encoding="utf-8")); goc.update(sua.get("_goc",{}))
    for k,v in sua.get("_settings",{}).items(): goc["settings"][k]["value"]=v
    for k in sua.get("_xoa",[]): goc["settings"].pop(k,None)
    tep=tmp_path/"CAL-THU.yaml"; tep.write_text(yaml.safe_dump(goc,allow_unicode=True),encoding="utf-8"); return tep


def test_thieu_khoa_bat_buoc_thi_bao_loi(tmp_path):
    with pytest.raises(CalendarRulesetError,match="THIEU_KHOA"): tai_tu_tep(_viet_cau_hinh(tmp_path,{"_xoa":["DAY_BOUNDARY"]}))


def test_moc_doi_ngay_sai_dinh_dang_thi_bao_loi(tmp_path):
    with pytest.raises(CalendarRulesetError,match="MOC_DOI_NGAY_SAI"): tai_tu_tep(_viet_cau_hinh(tmp_path,{"_settings":{"DAY_BOUNDARY":"25:00"}}))


def test_gia_tri_moc_doi_nam_la_thi_bao_loi(tmp_path):
    with pytest.raises(CalendarRulesetError,match="GIA_TRI_LA"): tai_tu_tep(_viet_cau_hinh(tmp_path,{"_settings":{"YEAR_BOUNDARY":"TET_TAY"}}))


def test_bo_thu_nghiem_khong_duoc_lam_mac_dinh(tmp_path):
    with pytest.raises(CalendarRulesetError,match="THU_NGHIEM_LAM_MAC_DINH"): tai_tu_tep(_viet_cau_hinh(tmp_path,{"_goc":{"status":"EXPERIMENTAL","is_default":True}}))


def test_khong_hard_code_moc_lich_trong_ma(): assert kiem_khong_hard_code()==[]


def test_engine_lay_moc_qua_bo_quy_uoc(db_da_nap):
    assert tai_tu_db(db_da_nap,"CAL-V1").moc_doi_ngay_phut==0
    db_da_nap.execute("UPDATE calendar_ruleset_settings SET setting_value='23:00' WHERE calendar_ruleset_id='CAL-V1' AND setting_key='DAY_BOUNDARY'"); db_da_nap.commit()
    assert tai_tu_db(db_da_nap,"CAL-V1").moc_doi_ngay_phut==23*60


def test_seed_lan_dau_dat(db_trong): nap_mam(db_trong); assert kiem_so_luong(db_trong)==[]


def test_seed_lan_hai_khong_tao_trung(db_trong):
    lan1=nap_mam(db_trong); lan2=nap_mam(db_trong); assert lan1==lan2 and kiem_so_luong(db_trong)==[]


def test_seed_lan_ba_van_on_dinh(db_trong):
    nap_mam(db_trong); nap_mam(db_trong); lan3=nap_mam(db_trong); assert lan3["stems"]==10 and lan3["branches"]==12 and lan3["elements"]==5


def test_noi_dung_can_chi_dung(db_da_nap):
    c=db_da_nap; giap=c.execute("SELECT * FROM stems WHERE stem_index=1").fetchone(); quy=c.execute("SELECT * FROM stems WHERE stem_index=10").fetchone(); ty=c.execute("SELECT * FROM branches WHERE branch_index=1").fetchone()
    assert (giap["code"],giap["polarity"],giap["element_code"])==("GIAP","DUONG","MOC") and (quy["code"],quy["polarity"],quy["element_code"])==("QUY","AM","THUY") and (ty["code"],ty["element_code"])==("TY","THUY")
    assert c.execute("SELECT COUNT(*) AS n FROM stems WHERE polarity='DUONG'").fetchone()["n"]==5 and c.execute("SELECT COUNT(*) AS n FROM branches WHERE polarity='DUONG'").fetchone()["n"]==6


def test_vong_sinh_va_vong_khac_khep_kin(db_da_nap):
    c=db_da_nap; sinh=c.execute("SELECT from_element,to_element FROM element_relations WHERE relation='SINH'").fetchall(); khac=c.execute("SELECT from_element,to_element FROM element_relations WHERE relation='KHAC'").fetchall()
    assert len(sinh)==5 and len(khac)==5 and len({r["from_element"] for r in sinh})==5 and len({r["to_element"] for r in sinh})==5 and len({r["from_element"] for r in khac})==5 and len({r["to_element"] for r in khac})==5


def test_12_loai_viec_v1_active_va_thi_cu_backlog(db_da_nap):
    rows=db_da_nap.execute("SELECT code,status FROM event_types ORDER BY code").fetchall(); active=[r["code"] for r in rows if r["status"]=="ACTIVE"]
    assert len(active)==12 and "THI_CU" not in active
    thi=db_da_nap.execute("SELECT status FROM event_types WHERE code='THI_CU'").fetchone(); assert thi is not None and thi["status"]!="ACTIVE"


def test_chi_nap_dung_pham_vi_v1_hien_tai(db_da_nap):
    cho_phep={'TIME','BT-HIDDEN','BT-TG','BT-TG-CONFLICT','BT-ML','BT-SEASON-POWER','BT-REL','BT-BASE','BT-USE','BT-DY','HK-GENERAL','HK-EVENT','FUS'}
    rows=db_da_nap.execute("SELECT rule_id,namespace FROM rule_registry").fetchall(); assert [(r['rule_id'],r['namespace']) for r in rows if r['namespace'] not in cho_phep]==[]
    assert db_da_nap.execute("SELECT COUNT(*) n FROM event_rule_packs").fetchone()["n"]==12
    assert db_da_nap.execute("SELECT COUNT(*) n FROM branch_hidden_stems").fetchone()["n"]==28
    assert db_da_nap.execute("SELECT COUNT(*) n FROM rule_registry WHERE namespace='BT-REL' AND is_active=1").fetchone()["n"]==4
    assert db_da_nap.execute("SELECT COUNT(*) n FROM rule_registry WHERE namespace='HK-EVENT' AND is_active=1").fetchone()["n"]==12
    assert db_da_nap.execute("SELECT COUNT(*) n FROM rule_registry WHERE namespace IN ('BT-BASE','BT-USE','BT-DY') AND is_active=1").fetchone()["n"]==3


def test_khong_quy_tac_lich_nao_bi_bien_thanh_verified_am_tham(db_da_nap):
    rows=db_da_nap.execute("""SELECT rv.rule_id,rv.status,s.source_id FROM rule_versions rv JOIN rule_version_sources rvs ON rvs.rule_version_id=rv.rule_version_id JOIN sources s ON s.source_id=rvs.source_id WHERE rvs.source_level='PRIMARY'""").fetchall()
    for r in rows:
        if r["source_id"]=="SRC-CHUA-CO-NGUON": assert r["status"]!="VERIFIED"


def test_tranh_luan_gio_ty_duoc_ghi_nhan(db_da_nap):
    c=db_da_nap; kc=c.execute("SELECT * FROM known_conflicts WHERE conflict_id='KC-0001'").fetchone(); assert kc is not None and kc["trang_thai"]=="OPEN" and kc["rule_id"]=="TIME-0007"
    rv=c.execute("SELECT status FROM rule_versions WHERE rule_version_id='TIME-0007@1'").fetchone(); assert rv["status"]=="CONFLICTED"


def test_bo_lich_ghi_ro_gio_ty_chua_xac_minh():
    for bo in tai_tat_ca().values(): assert not bo.gio_ty_dem_da_xac_minh and not bo.gio_ty_dem_duoc_cham_diem


def test_bo_mac_dinh_lay_duoc_tu_db(db_da_nap):
    bo=bo_mac_dinh(db_da_nap); assert bo.calendar_ruleset_id=="CAL-V1" and dem_ban_ghi_nen(db_da_nap)["calendar_rulesets"]==2
