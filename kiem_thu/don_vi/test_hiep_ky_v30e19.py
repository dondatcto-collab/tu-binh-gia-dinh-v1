from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_tian_ma_v30e19 import TIAN_MA_BRANCH_BY_MONTH_BRANCH, active_tian_ma_tokens, calculator_status, tian_ma_branch


def _base(state="NEUTRAL",event_code="XUAT_HANH"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}

def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"NGO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}

def test_tian_ma_locks_twelve_months():
    expected={"DAN":"NGO","MAO":"THAN","THIN":"TUAT","TI":"TY","NGO":"DAN","MUI":"THIN","THAN":"NGO","DAU":"THAN","TUAT":"TUAT","HOI":"TY","TY":"DAN","SUU":"THIN"}
    assert TIAN_MA_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items():
        assert tian_ma_branch(month)==day
        assert active_tian_ma_tokens(month,day)==("天馬",)

def test_tian_ma_nonmatch_and_invalid_fail_closed():
    assert active_tian_ma_tokens("DAN","DAN")==()
    for args in (("INVALID","NGO"),("DAN","INVALID")):
        try: active_tian_ma_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")

def test_tian_ma_verified_scope_is_travel_and_move():
    for event_code in ("XUAT_HANH","NHAP_TRACH"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="天馬"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("NHAM_CHUC","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="天馬" for x in evidence_for_event(event_code))

def test_tian_ma_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert "天馬" in out["active_hiep_ky_tokens"] and "天馬" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="NGO")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True

def test_e19_release_contract_is_future_proof():
    row=token_capability("天馬")
    assert row["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E19_TIAN_MA"
    status=calculator_status(); assert status["extension_version"]=="V3_0E19_TIAN_MA"; assert status["numeric_score"] is None
