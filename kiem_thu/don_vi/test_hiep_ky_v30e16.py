from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_lin_ri_v30e16 import LIN_RI_BRANCH_BY_MONTH_BRANCH, active_lin_ri_tokens, calculator_status, lin_ri_branch
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL", event_code="NHAM_CHUC"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"NGO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_lin_ri_locks_all_twelve_months():
    expected={"DAN":"NGO","MAO":"HOI","THIN":"THAN","TI":"SUU","NGO":"TUAT","MUI":"MAO","THAN":"TY","DAU":"TI","TUAT":"DAN","HOI":"MUI","TY":"THIN","SUU":"DAU"}
    assert LIN_RI_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items():
        assert lin_ri_branch(month)==day
        assert active_lin_ri_tokens(month,day)==("臨日",)


def test_lin_ri_nonmatch_and_invalid_fail_closed():
    assert active_lin_ri_tokens("DAN","DAN")==()
    for args in (("INVALID","NGO"),("DAN","INVALID")):
        try: active_lin_ri_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_lin_ri_verified_scope_is_nham_chuc_only():
    rows=[x for x in evidence_for_event("NHAM_CHUC") if x.token=="臨日"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="臨日" for x in evidence_for_event(event_code))


def test_lin_ri_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert "臨日" in out["active_hiep_ky_tokens"]
    assert "臨日" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True


def test_e16_capability_contract():
    cap=capability_inventory()
    assert cap["active_calculable_count"]==36
    assert cap["pending_calculator_count"]==45
    assert cap["extension_version"]=="V3_0E16_LIN_RI"
    assert token_capability("臨日")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E16_LIN_RI"
    assert calculator_status()["numeric_score"] is None
