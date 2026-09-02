from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory


def test_e23_schema_exposes_43_active_and_recent_rules():
    out=v25_schema_overlay({})
    cap=capability_inventory()
    assert cap["active_calculable_count"]==43
    assert cap["pending_calculator_count"]==38
    assert cap["extension_version"]=="V3_0E23_DA_HAO"
    for scope in ("hiep_ky_v30e20_ji_qi","hiep_ky_v30e21_tian_cang","hiep_ky_v30e22_chu_shen","hiep_ky_v30e23_da_hao"):
        assert scope in out["implemented_scopes"]
    assert out["hiep_ky_v30e22"]["activated_token"]=="除神"
    assert out["hiep_ky_v30e23"]["activated_token"]=="大耗"
    assert out["hiep_ky_v30e23"]["decision_effect"]=="CAUTION_ONLY"
    assert out["hiep_ky_v30e23"]["creates_hard_block"] is False
    assert out["numeric_score"]=="LOCKED_OFF"
