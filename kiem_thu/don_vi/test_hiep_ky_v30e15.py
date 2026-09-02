from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_min_ri_v30e15 import MIN_RI_BRANCH_BY_SEASON, active_min_ri_tokens, calculator_status, min_ri_branch
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL", event_code="KHAI_TRUONG", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_min_ri_locks_four_seasons():
    assert MIN_RI_BRANCH_BY_SEASON=={"SPRING":"NGO","SUMMER":"DAU","AUTUMN":"TY","WINTER":"MAO"}
    for month,day in (("DAN","NGO"),("MAO","NGO"),("TI","DAU"),("THAN","TY"),("HOI","MAO")):
        assert min_ri_branch(month)==day
        assert active_min_ri_tokens(month,day)==("民日",)


def test_min_ri_nonmatch_and_invalid_fail_closed():
    assert active_min_ri_tokens("DAN","MAO")==()
    for args in (("INVALID","NGO"),("DAN","INVALID")):
        try: active_min_ri_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_min_ri_verified_event_scope_and_provisional_boundary():
    for event_code in ("KHAI_TRUONG","KY_HOP_DONG","NHAP_TRACH","CAU_TAI"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="民日"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    provisional=[x for x in evidence_for_event("DAM_PHAN") if x.token=="民日"]
    assert len(provisional)==1
    assert all(x.token!="民日" for x in evidence_for_event("CUOI_HOI"))


def test_min_ri_matches_inventory_without_numeric_score():
    out=evaluate_event_v25(_base(event_code="CAU_TAI"),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert "民日" in out["active_hiep_ky_tokens"]
    assert "民日" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    assert out["numeric_score_status"]=="LOCKED_OFF"


def test_min_ri_never_rescues_hard_block():
    out=evaluate_event_v25(_base("JI","KHAI_TRUONG"),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert "民日" in out["matched_yi_tokens"]
    assert out["hard_block"] is True
    assert out["decision_state"]=="BLOCKED"


def test_min_ri_does_not_leak_to_unsupported_event():
    out=evaluate_event_v25(_base(event_code="CUOI_HOI"),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert "民日" in out["active_hiep_ky_tokens"]
    assert "民日" not in out["matched_yi_tokens"]


def test_e15_contract_is_future_proof():
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert token_capability("民日")["calculator"]=="SEASON_DAY_BRANCH_V30E15_MIN_RI"
    assert calculator_status()["active_tokens"]==("民日",)
    assert calculator_status()["numeric_score"] is None
    assert "hiep_ky_v30e15_min_ri" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e15"]["activated_token"]=="民日"
    assert schema["hiep_ky_v30e15"]["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
    assert schema["numeric_score"]=="LOCKED_OFF"
