from loi.ket_qua.hiep_ky_v30e20_overlay import schema_overlay_v30e20
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_ji_qi_v30e20 import JI_QI_BRANCH_BY_MONTH_BRANCH, active_ji_qi_tokens, calculator_status, ji_qi_branch
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL",event_code="XUAT_HANH"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}

def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"MAO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}

def test_ji_qi_is_next_branch_after_month_build():
    expected={"TY":"SUU","SUU":"DAN","DAN":"MAO","MAO":"THIN","THIN":"TI","TI":"NGO","NGO":"MUI","MUI":"THAN","THAN":"DAU","DAU":"TUAT","TUAT":"HOI","HOI":"TY"}
    assert JI_QI_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items(): assert ji_qi_branch(month)==day and active_ji_qi_tokens(month,day)==("吉期",)

def test_ji_qi_fail_closed():
    assert active_ji_qi_tokens("DAN","DAN")==()
    for args in (("INVALID","MAO"),("DAN","INVALID")):
        try: active_ji_qi_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")

def test_ji_qi_verified_scope_is_travel_and_office():
    for event_code in ("XUAT_HANH","NHAM_CHUC"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="吉期"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("NHAP_TRACH","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="吉期" for x in evidence_for_event(event_code))

def test_ji_qi_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="MAO")
    assert "吉期" in out["active_hiep_ky_tokens"] and "吉期" in out["matched_yi_tokens"] and out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="MAO")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True

def test_e20_release_contract_and_schema():
    assert token_capability("吉期")["calculator"]=="MONTH_NEXT_BRANCH_V30E20_JI_QI"
    status=calculator_status(); assert status["extension_version"]=="V3_0E20_JI_QI" and status["numeric_score"] is None
    schema=schema_overlay_v30e20({"implemented_scopes":[]}); assert schema["hiep_ky_v30e20"]["activated_token"]=="吉期" and "hiep_ky_v30e20_ji_qi" in schema["implemented_scopes"]
