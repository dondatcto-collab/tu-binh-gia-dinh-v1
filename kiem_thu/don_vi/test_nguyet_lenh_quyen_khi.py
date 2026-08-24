"""0.5 migration wrapper: giữ toàn bộ regression Nguyệt lệnh cũ, thay đúng assertion gate đã lỗi thời."""
import importlib.util
from pathlib import Path
_p=Path(__file__).with_name('_legacy_nguyet_lenh_quyen_khi.py')
_s=importlib.util.spec_from_file_location('_legacy_nguyet_lenh_quyen_khi',_p); _m=importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
_SKIP={'test_cach_cuc_dung_than_chua_co_nhung_bt_rel_da_co'}
for _k,_v in vars(_m).items():
    if not _k.startswith('__') and _k not in _SKIP: globals()[_k]=_v

def test_cach_cuc_dung_than_050_da_mo_co_nguon(db_da_nap):
    rows=db_da_nap.execute("SELECT rule_id,namespace,is_active FROM rule_registry WHERE namespace IN ('BT-BASE','BT-USE','BT-DY') ORDER BY rule_id").fetchall()
    assert len(rows)==3 and all(r['is_active']==1 for r in rows)
    rel=db_da_nap.execute("SELECT COUNT(*) AS n FROM rule_registry rr JOIN rule_versions rv ON rv.rule_id=rr.rule_id AND rv.version=rr.active_version WHERE rr.namespace='BT-REL' AND rv.status='VERIFIED' AND rr.is_active=1").fetchone()
    assert rel['n']==4
