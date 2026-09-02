from loi.ket_qua.hiep_ky_v30e21_overlay import schema_overlay_v30e21
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_tian_cang_v30e21 import TIAN_CANG_BRANCH_BY_MONTH_BRANCH, active_tian_cang_tokens, calculator_status, tian_cang_branch


def _base(state="NEUTRAL",event_code="CAU_TAI"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}

def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"DAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}

def test_tian_cang_locks_reverse_twelve_months():
    expected={"DAN":"DAN","MAO":"SUU","THIN":"TY","TI":"HOI","NGO":"TUAT","MUI":"DAU","THAN":"THAN","DAU":"MUI","TUAT":"NGO","HOI":"TI","TY":"THIN","SUU":"MAO"}
    assert TIAN_CANG_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items(): assert tian_cang_branch(month)==day and active_tian_cang_tokens(month,day)==("天倉",)

def test_tian_cang_fail_closed():
    assert active_tian_cang_tokens("DAN","MAO")==()
    for args in (("INVALID","DAN"),("DAN","INVALID")):
        try: active_tian_cang_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")

def test_tian_cang_verified_scope_is_cau_tai_only():
    rows=[x for x in evidence_for_event("CAU_TAI") if x.token=="天倉"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","NHAP_TRACH","NHAM_CHUC","KHAI_TRUONG","KY_HOP_DONG","DIEU_TRI"):
        assert all(x.token!="天倉" for x in evidence_for_event(event_code))

def test_tian_cang_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="DAN")
    assert "天倉" in out["active_hiep_ky_tokens"] and "天倉" in out["matched_yi_tokens"] and out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="DAN")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True

def test_e21_release_contract_and_schema():
    assert token_capability("天倉")["calculator"]=="MONTH_REVERSE_BRANCH_V30E21_TIAN_CANG"
    status=calculator_status(); assert status["extension_version"]=="V3_0E21_TIAN_CANG" and status["numeric_score"] is None
    schema=schema_overlay_v30e21({"implemented_scopes":[]}); assert schema["hiep_ky_v30e21"]["activated_token"]=="天倉"
