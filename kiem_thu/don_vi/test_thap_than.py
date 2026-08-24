"""0.5 migration wrapper: giữ regression Thập Thần cũ, thay assertion gate đã lỗi thời."""
import importlib.util
from pathlib import Path
_p=Path(__file__).with_name('_legacy_thap_than.py')
_s=importlib.util.spec_from_file_location('_legacy_thap_than',_p); _m=importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
_SKIP={'test_chua_lam_vuong_suy_cach_cuc_nhung_bt_rel_da_mo'}
for _k,_v in vars(_m).items():
    if not _k.startswith('__') and _k not in _SKIP: globals()[_k]=_v

def test_050_mo_cach_cuc_nhung_quyen_khi_khong_tu_cham_diem(db_da_nap):
    opened=db_da_nap.execute("SELECT rule_id FROM rule_registry WHERE namespace IN ('BT-BASE','BT-USE','BT-DY') AND is_active=1").fetchall(); assert len(opened)==3
    rel=db_da_nap.execute("SELECT COUNT(*) AS n FROM rule_registry rr JOIN rule_versions rv ON rv.rule_id=rr.rule_id AND rv.version=rr.active_version WHERE rr.namespace='BT-REL' AND rv.status='VERIFIED' AND rr.is_active=1").fetchone(); assert rel['n']==4
    qk=db_da_nap.execute("SELECT is_active FROM rule_registry WHERE namespace='BT-SEASON-POWER'").fetchall(); assert all(r['is_active']==0 for r in qk)
