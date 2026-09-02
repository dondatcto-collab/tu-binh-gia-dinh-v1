from loi.quyet_dinh.hiep_ky_capability_v25 import token_capability
from loi.quyet_dinh.hiep_ky_chu_shen_v30e22 import CHU_SHEN_DAY_BRANCHES, active_chu_shen_tokens, calculator_status
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL",event_code="DIEU_TRI"):
    return {"event_code":event_code,"event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"THAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_chu_shen_is_shen_you_days_only():
    assert CHU_SHEN_DAY_BRANCHES==frozenset({"THAN","DAU"})
    assert active_chu_shen_tokens("THAN")==("除神",)
    assert active_chu_shen_tokens("DAU")==("除神",)
    for branch in ("TY","SUU","DAN","MAO","THIN","TI","NGO","MUI","TUAT","HOI"):
        assert active_chu_shen_tokens(branch)==()


def test_chu_shen_invalid_fails_closed():
    try: active_chu_shen_tokens("INVALID")
    except ValueError: pass
    else: raise AssertionError("invalid Chi must fail closed")


def test_chu_shen_verified_scope_is_dieu_tri_only():
    rows=[x for x in evidence_for_event("DIEU_TRI") if x.token=="除神"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in ("XUAT_HANH","NHAP_TRACH","NHAM_CHUC","KHAI_TRUONG","KY_HOP_DONG","CAU_TAI"):
        assert all(x.token!="除神" for x in evidence_for_event(event_code))


def test_chu_shen_support_and_hard_block_precedence():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "除神" in out["active_hiep_ky_tokens"] and "除神" in out["matched_yi_tokens"]
    assert out["numeric_score"] is None
    blocked=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert blocked["decision_state"]=="BLOCKED" and blocked["hard_block"] is True


def test_e22_contract_future_proof():
    assert token_capability("除神")["calculator"]=="DAY_BRANCH_V30E22_CHU_SHEN"
    assert calculator_status()["active_tokens"]==("除神",)
    assert calculator_status()["numeric_score"] is None
