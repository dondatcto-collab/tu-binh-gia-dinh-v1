from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_da_hao_v30e23 import DA_HAO_BRANCH_BY_MONTH_BRANCH, active_da_hao_tokens, calculator_status, da_hao_branch
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL",event_code="KHAI_TRUONG"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"THAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_da_hao_is_month_opposition_all_twelve_months():
    expected={"DAN":"THAN","MAO":"DAU","THIN":"TUAT","TI":"HOI","NGO":"TY","MUI":"SUU","THAN":"DAN","DAU":"MAO","TUAT":"THIN","HOI":"TI","TY":"NGO","SUU":"MUI"}
    assert DA_HAO_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items():
        assert da_hao_branch(month)==day
        assert active_da_hao_tokens(month,day)==("大耗",)


def test_da_hao_nonmatch_and_invalid_fail_closed():
    assert active_da_hao_tokens("DAN","DAN")==()
    for args in (("INVALID","THAN"),("DAN","INVALID")):
        try: active_da_hao_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_da_hao_verified_ji_scope():
    for event_code in ("KHAI_TRUONG","KY_HOP_DONG","CAU_TAI"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="大耗"]
        assert len(rows)==1 and rows[0].polarity=="JI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("DIEU_TRI","XUAT_HANH","NHAP_TRACH","NHAM_CHUC"):
        assert all(x.token!="大耗" for x in evidence_for_event(event_code))


def test_da_hao_creates_caution_not_independent_hard_block():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "大耗" in out["active_hiep_ky_tokens"] and "大耗" in out["matched_ji_tokens"]
    assert out["event_signal_v25"]=="CAUTION" and out["hard_block"] is False
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True


def test_e23_contract_future_proof():
    assert token_capability("大耗")["calculator"]=="MONTH_OPPOSITION_V30E23_DA_HAO"
    assert calculator_status()["active_tokens"]==("大耗",)
    assert calculator_status()["numeric_score"] is None
