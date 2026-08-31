from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_coverage_gate_v30e10 import event_coverage_rows, v1_engine_readiness
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_giai_than_v30e10 import GIAI_THAN_BRANCH_BY_MONTH_BRANCH, active_giai_than_tokens, calculator_status
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25


def _base(state="NEUTRAL", event_code="DIEU_TRI", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"THAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_giai_than_locks_all_twelve_months():
    expected={"DAN":"THAN","MAO":"THAN","THIN":"TUAT","TI":"TUAT","NGO":"TY","MUI":"TY","THAN":"DAN","DAU":"DAN","TUAT":"THIN","HOI":"THIN","TY":"NGO","SUU":"NGO"}
    assert GIAI_THAN_BRANCH_BY_MONTH_BRANCH==expected
    for month, day in expected.items():
        assert active_giai_than_tokens(month,day)==("解神",)


def test_giai_than_invalid_and_nonmatch_fail_closed():
    assert active_giai_than_tokens("DAN","MAO")==()
    for args in (("INVALID","THAN"),("DAN","INVALID")):
        try: active_giai_than_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_giai_than_event_scope_is_verified_treatment_only():
    rows=[x for x in evidence_for_event("DIEU_TRI") if x.token=="解神"]
    assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in {"KHAI_TRUONG","KY_HOP_DONG","MUA_TAI_SAN","DONG_THO","NHAP_TRACH","CUOI_HOI","XUAT_HANH","DAM_PHAN","NHAM_CHUC","CAU_TAI","AN_TANG"}:
        assert all(x.token!="解神" for x in evidence_for_event(event_code))


def test_giai_than_positive_gate_without_day_stem():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "解神" in out["active_hiep_ky_tokens"]
    assert "解神" in out["matched_yi_tokens"]
    assert out["matched_ji_tokens"]==[]
    assert out["event_signal_v25"]=="FAVORABLE"
    assert out["label"]=="Ưu tiên"
    assert out["numeric_score"] is None


def test_giai_than_cannot_rescue_jie_sha_caution():
    out=evaluate_event_v25(_base(),_personal(),chi_thang="MAO",chi_ngay="THAN")
    assert "解神" in out["matched_yi_tokens"]
    assert "劫煞" in out["matched_ji_tokens"]
    assert out["event_signal_v25"]=="CAUTION"
    assert out["label"]=="Không ưu tiên"
    assert out["hard_block"] is False


def test_hard_block_still_wins_over_giai_than():
    out=evaluate_event_v25(_base("JI"),_personal(),chi_thang="DAN",chi_ngay="THAN")
    assert "解神" in out["matched_yi_tokens"]
    assert out["hard_block"] is True
    assert out["decision_state"]=="BLOCKED"


def test_capability_and_schema_are_explicit_for_e10():
    cap=capability_inventory()
    assert cap["token_count"]==81
    assert cap["active_calculable_count"]==30
    assert cap["pending_calculator_count"]==51
    assert token_capability("解神")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN"
    assert cap["extension_version"]=="V3_0E10_GIAI_THAN"
    assert cap["numeric_score"] is None
    assert calculator_status()["numeric_score"] is None

    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert "hiep_ky_v30e10_giai_than" in schema["implemented_scopes"]
    assert "hiep_ky_v1_coverage_gate" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e10"]["activated_token"]=="解神"
    assert schema["numeric_score"]=="LOCKED_OFF"


def test_v1_coverage_gate_is_measured_not_claimed_ready():
    rows=event_coverage_rows(); ready=v1_engine_readiness()
    assert len(rows)==12
    assert ready["target_active_rules"]==45
    assert ready["target_band"]==(42,48)
    assert ready["active_calculable_count"]==30
    assert ready["rule_target_gate"] is False
    assert ready["v1_engine_ready"] is False
    assert ready["numeric_score"] is None
