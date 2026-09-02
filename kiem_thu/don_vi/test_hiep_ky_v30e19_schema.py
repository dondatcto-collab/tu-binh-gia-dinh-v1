from loi.ket_qua.hiep_ky_v30e19_overlay import schema_overlay_v30e19


def test_e19_schema_exposes_e18_and_e19_without_score():
    out=schema_overlay_v30e19({})
    assert "hiep_ky_v30e18_tian_hou" in out["implemented_scopes"]
    assert "hiep_ky_v30e19_tian_ma" in out["implemented_scopes"]
    assert out["hiep_ky_v30e18"]["activated_token"]=="天后"
    assert out["hiep_ky_v30e19"]["activated_token"]=="天馬"
    assert out["hiep_ky_v30e19"]["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA"
    assert out["hiep_ky_v25"]["capability"]["active_calculable_count"]==39
    assert out["hiep_ky_v25"]["capability"]["pending_calculator_count"]==42
    assert out["hiep_ky_v30e19"]["numeric_score"] is None
