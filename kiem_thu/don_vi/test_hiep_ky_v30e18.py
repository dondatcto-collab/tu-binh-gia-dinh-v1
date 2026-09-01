from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_tian_hou_v30e18 import TIAN_HOU_BRANCH_BY_MONTH_BRANCH, active_tian_hou_tokens, calculator_status, tian_hou_branch


def _base(state="NEUTRAL", event_code="DIEU_TRI"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"THAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_tian_hou_same_position_as_yi_ma_twelve_months():
    expected={"DAN":"THAN","MAO":"TI","THIN":"DAN","TI":"HOI","NGO":"THAN","MUI":"TI","THAN":"DAN","DAU":"HOI","TUAT":"THAN","HOI":"TI","TY":"DAN","SUU":"HOI"}
    assert TIAN_HOU_BRANCH_BY_MONTH_BRANCH==expected
    for month,day in expected.items():
        assert tian_hou_branch(month)==day
        assert active_tian_hou_tokens(month,day)==("天后",)


def test_tian_hou_fail_closed():
    assert active_tian_hou_tokens("DAN","DAN")==()
    for args in (("INVALID","THAN"),("DAN","INVALID")):
        try: active_tian_hou_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_tian_hou_verified_scope_is_dieu_tri_only():
    rows=[x for x in evidence_for_event("DIEU_TRI") if x.token=="天后"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","NHAP_TRACH","NHAM_CHUC","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI"):
        assert all(x.token!="天后" for x in evidence_for_event(event_code))


def test_tian_hou_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "天后" in out["active_hiep_ky_tokens"]
    assert "天后" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True


def test_e18_contract_remains_bound_after_later_releases():
    assert token_capability("天后")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E18_TIAN_HOU"
    status=calculator_status()
    assert status["active_tokens"]==("天后",)
    assert status["numeric_score"] is None
