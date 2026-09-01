from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_yi_ma_v30e17 import YI_MA_BRANCH_BY_MONTH_BRANCH, active_yi_ma_tokens, calculator_status, yi_ma_branch


def _base(state="NEUTRAL", event_code="XUAT_HANH"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"THAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_yi_ma_locks_twelve_months():
    expected={"DAN":"THAN","MAO":"TI","THIN":"DAN","TI":"HOI","NGO":"THAN","MUI":"TI","THAN":"DAN","DAU":"HOI","TUAT":"THAN","HOI":"TI","TY":"DAN","SUU":"HOI"}
    assert YI_MA_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items():
        assert yi_ma_branch(month)==day
        assert active_yi_ma_tokens(month,day)==("驛馬",)


def test_yi_ma_nonmatch_and_invalid_fail_closed():
    assert active_yi_ma_tokens("DAN","DAN")==()
    for args in (("INVALID","THAN"),("DAN","INVALID")):
        try: active_yi_ma_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_yi_ma_verified_scope_is_travel_and_move():
    for event_code in ("XUAT_HANH","NHAP_TRACH"):
        rows=[x for x in evidence_for_event(event_code) if x.token=="驛馬"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("NHAM_CHUC","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI","DIEU_TRI"):
        assert all(x.token!="驛馬" for x in evidence_for_event(event_code))


def test_yi_ma_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "驛馬" in out["active_hiep_ky_tokens"]
    assert "驛馬" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True


def test_e17_capability_contract():
    cap=capability_inventory()
    assert cap["active_calculable_count"]==37
    assert cap["pending_calculator_count"]==44
    assert cap["extension_version"]=="V3_0E17_YI_MA"
    assert token_capability("驛馬")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E17_YI_MA"
    assert calculator_status()["numeric_score"] is None
