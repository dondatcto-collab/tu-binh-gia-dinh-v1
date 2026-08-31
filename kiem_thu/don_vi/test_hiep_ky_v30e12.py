from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_wang_ri_v30e12 import WANG_RI_BRANCH_BY_SEASON, active_wang_ri_tokens, calculator_status, wang_ri_branch


def _base(state="NEUTRAL", event_code="XUAT_HANH", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_wang_ri_locks_four_seasons():
    assert WANG_RI_BRANCH_BY_SEASON=={"SPRING":"DAN","SUMMER":"TI","AUTUMN":"THAN","WINTER":"HOI"}
    for month, day in (("DAN","DAN"),("MAO","DAN"),("TI","TI"),("THAN","THAN"),("HOI","HOI")):
        assert wang_ri_branch(month)==day
        assert active_wang_ri_tokens(month,day)==("王日",)


def test_wang_ri_nonmatch_and_invalid_fail_closed():
    assert active_wang_ri_tokens("DAN","MAO")==()
    for args in (("INVALID","DAN"),("DAN","INVALID")):
        try: active_wang_ri_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_wang_ri_verified_event_scope_in_inventory():
    for event_code in ("XUAT_HANH","NHAM_CHUC"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="王日"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"


def test_wang_ri_can_support_but_never_override_hard_block():
    favorable=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="DAN")
    assert "王日" in favorable["active_hiep_ky_tokens"]
    assert "王日" in favorable["matched_yi_tokens"]
    assert favorable["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="DAN")
    assert blocked["decision_state"]=="BLOCKED"
    assert blocked["hard_block"] is True


def test_e12_contract_remains_bound_after_later_releases():
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert token_capability("王日")["calculator"]=="SEASON_DAY_BRANCH_V30E12_WANG_RI"
    assert calculator_status()["active_tokens"]==("王日",)
    assert calculator_status()["numeric_score"] is None
    assert "hiep_ky_v30e12_wang_ri" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e12"]["activated_token"]=="王日"
    assert schema["hiep_ky_v30e12"]["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
    assert schema["numeric_score"]=="LOCKED_OFF"
