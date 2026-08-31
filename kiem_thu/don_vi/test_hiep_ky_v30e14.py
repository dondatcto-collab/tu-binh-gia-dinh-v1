from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_xiang_ri_v30e14 import XIANG_RI_BRANCH_BY_SEASON, active_xiang_ri_tokens, calculator_status, xiang_ri_branch


def _base(state="NEUTRAL",event_code="NHAM_CHUC",mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}

def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}

def test_xiang_ri_locks_four_seasons():
    assert XIANG_RI_BRANCH_BY_SEASON=={"SPRING":"TI","SUMMER":"THAN","AUTUMN":"HOI","WINTER":"DAN"}
    for month,day in (("DAN","TI"),("MAO","TI"),("TI","THAN"),("THAN","HOI"),("HOI","DAN")):
        assert xiang_ri_branch(month)==day; assert active_xiang_ri_tokens(month,day)==("相日",)

def test_xiang_ri_nonmatch_and_invalid_fail_closed():
    assert active_xiang_ri_tokens("DAN","DAN")==()
    for args in (("INVALID","TI"),("DAN","INVALID")):
        try: active_xiang_ri_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")

def test_xiang_ri_verified_scope_is_nham_chuc():
    rows=[x for x in evidence_for_event("NHAM_CHUC") if x.token=="相日"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="相日" for x in evidence_for_event(event_code))

def test_xiang_ri_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="TI")
    assert "相日" in out["active_hiep_ky_tokens"] and "相日" in out["matched_yi_tokens"] and out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="TI")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True

def test_e14_contract_and_shou_ri_guard():
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert token_capability("相日")["calculator"]=="SEASON_DAY_BRANCH_V30E14_XIANG_RI"
    assert token_capability("守日")["calculator_status"]=="PENDING_CALCULATOR"
    assert calculator_status()["active_tokens"]==("相日",); assert calculator_status()["numeric_score"] is None
    assert "hiep_ky_v30e14_xiang_ri" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e14"]["activated_token"]=="相日" and schema["hiep_ky_v30e14"]["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
