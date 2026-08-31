from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_guan_ri_v30e13 import GUAN_RI_BRANCH_BY_SEASON, active_guan_ri_tokens, calculator_status, guan_ri_branch


def _base(state="NEUTRAL",event_code="NHAM_CHUC",mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}

def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}

def test_guan_ri_locks_four_seasons():
    assert GUAN_RI_BRANCH_BY_SEASON=={"SPRING":"MAO","SUMMER":"NGO","AUTUMN":"DAU","WINTER":"TY"}
    for month,day in (("DAN","MAO"),("MAO","MAO"),("TI","NGO"),("THAN","DAU"),("HOI","TY")):
        assert guan_ri_branch(month)==day; assert active_guan_ri_tokens(month,day)==("官日",)

def test_guan_ri_nonmatch_and_invalid_fail_closed():
    assert active_guan_ri_tokens("DAN","DAN")==()
    for args in (("INVALID","MAO"),("DAN","INVALID")):
        try: active_guan_ri_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")

def test_guan_ri_verified_scope_is_nham_chuc():
    rows=[x for x in evidence_for_event("NHAM_CHUC") if x.token=="官日"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="官日" for x in evidence_for_event(event_code))

def test_guan_ri_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="MAO")
    assert "官日" in out["active_hiep_ky_tokens"] and "官日" in out["matched_yi_tokens"] and out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="MAO")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True

def test_e13_contract_remains_bound_after_later_releases():
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert token_capability("官日")["calculator"]=="SEASON_DAY_BRANCH_V30E13_GUAN_RI"
    assert calculator_status()["active_tokens"]==("官日",); assert calculator_status()["numeric_score"] is None
    assert "hiep_ky_v30e13_guan_ri" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e13"]["activated_token"]=="官日" and schema["hiep_ky_v30e13"]["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
