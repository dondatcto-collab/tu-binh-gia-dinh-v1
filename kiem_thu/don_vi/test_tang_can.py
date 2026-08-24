"""0.5 migration wrapper: giữ regression Tàng Can cũ, thay assertion gate đã lỗi thời."""
import importlib.util
from pathlib import Path
_p=Path(__file__).with_name('_legacy_tang_can.py')
_s=importlib.util.spec_from_file_location('_legacy_tang_can',_p); _m=importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
_SKIP={'test_cach_cuc_dung_than_chua_co_nhung_quan_he_da_co'}
for _k,_v in vars(_m).items():
    if not _k.startswith('__') and _k not in _SKIP: globals()[_k]=_v

def test_cach_cuc_dung_than_050_da_mo_nhung_bt_rel_van_giu_nguon(db_da_nap):
    opened=db_da_nap.execute("SELECT rule_id FROM rule_registry WHERE namespace IN ('BT-BASE','BT-USE','BT-DY') AND is_active=1").fetchall(); assert len(opened)==3
    rel=db_da_nap.execute("SELECT rr.rule_id,rv.status AS verification_status,rr.is_active FROM rule_registry rr JOIN rule_versions rv ON rv.rule_id=rr.rule_id AND rv.version=rr.active_version WHERE rr.namespace='BT-REL' ORDER BY rr.rule_id").fetchall()
    assert [r['rule_id'] for r in rel]==['BT-REL-0001','BT-REL-0002','BT-REL-0003','BT-REL-0004']
    assert all(r['verification_status']=='VERIFIED' and r['is_active']==1 for r in rel)
