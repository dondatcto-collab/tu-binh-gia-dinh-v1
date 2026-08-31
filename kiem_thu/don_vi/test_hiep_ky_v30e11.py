from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_coverage_gate_v30e10 import v1_engine_readiness
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_wu_fu_v30e11 import WU_FU_BRANCH_BY_MONTH_BRANCH, active_wu_fu_tokens, calculator_status, wu_fu_branch


def _base(state="NEUTRAL", event_code="KHAI_TRUONG", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT"):
    return {"state":state,"current_stem":None,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_wu_fu_locks_all_twelve_months_from_four_meng_cycle():
    expected={"DAN":"HOI","MAO":"DAN","THIN":"TI","TI":"THAN","NGO":"HOI","MUI":"DAN","THAN":"TI","DAU":"THAN","TUAT":"HOI","HOI":"DAN","TY":"TI","SUU":"THAN"}
    assert WU_FU_BRANCH_BY_MONTH_BRANCH==expected
    for month, day in expected.items():
        assert wu_fu_branch(month)==day
        assert active_wu_fu_tokens(month,day)==("五富",)


def test_wu_fu_nonmatch_and_invalid_inputs_fail_closed():
    assert active_wu_fu_tokens("DAN","DAN")==()
    for args in (("INVALID","HOI"),("DAN","INVALID")):
        try: active_wu_fu_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_wu_fu_event_scope_is_exactly_three_verified_events():
    supported={"KHAI_TRUONG","KY_HOP_DONG","CAU_TAI"}
    for event_code in supported:
        rows=[x for x in evidence_for_event(event_code) if x.token=="五富"]
        assert len(rows)==1 and rows[0].polarity=="YI" and rows[0].evidence_status=="VERIFIED"
    for event_code in {"MUA_TAI_SAN","DONG_THO","NHAP_TRACH","CUOI_HOI","XUAT_HANH","DIEU_TRI","DAM_PHAN","NHAM_CHUC","AN_TANG"}:
        assert all(x.token!="五富" for x in evidence_for_event(event_code))


def test_wu_fu_positive_gate_without_day_stem():
    out=evaluate_event_v25(_base(event_code="CAU_TAI"),_personal(),chi_thang="MAO",chi_ngay="DAN")
    assert "五富" in out["active_hiep_ky_tokens"]
    assert "五富" in out["matched_yi_tokens"]
    assert out["matched_ji_tokens"]==[]
    assert out["event_signal_v25"]=="FAVORABLE"
    assert out["label"]=="Ưu tiên"
    assert out["numeric_score"] is None


def test_wu_fu_cannot_rescue_month_xing_caution():
    out=evaluate_event_v25(_base(event_code="KHAI_TRUONG"),_personal(),chi_thang="TI",chi_ngay="THAN")
    assert "五富" in out["matched_yi_tokens"]
    assert "月刑" in out["matched_ji_tokens"]
    assert out["event_signal_v25"]=="CAUTION"
    assert out["label"]=="Không ưu tiên"
    assert out["hard_block"] is False


def test_hard_block_still_wins_over_wu_fu():
    out=evaluate_event_v25(_base("JI","KY_HOP_DONG"),_personal(),chi_thang="DAN",chi_ngay="HOI")
    assert "五富" in out["matched_yi_tokens"]
    assert out["hard_block"] is True
    assert out["decision_state"]=="BLOCKED"


def test_wu_fu_does_not_leak_to_unsupported_event():
    out=evaluate_event_v25(_base(event_code="CUOI_HOI"),_personal(),chi_thang="DAN",chi_ngay="HOI")
    assert "五富" in out["active_hiep_ky_tokens"]
    assert "五富" not in out["matched_yi_tokens"]


def test_e11_capability_schema_and_readiness_are_explicit():
    cap=capability_inventory()
    assert cap["token_count"]==81
    assert cap["active_calculable_count"]==31
    assert cap["pending_calculator_count"]==50
    assert token_capability("五富")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E11_WU_FU"
    assert cap["extension_version"]=="V3_0E11_WU_FU"
    assert cap["numeric_score"] is None
    assert calculator_status()["numeric_score"] is None

    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert "hiep_ky_v30e11_wu_fu" in schema["implemented_scopes"]
    assert schema["hiep_ky_v30e11"]["activated_token"]=="五富"
    assert schema["hiep_ky_v30e11"]["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
    assert schema["hiep_ky_v30e11"]["creates_hard_block"] is False
    assert schema["numeric_score"]=="LOCKED_OFF"

    ready=v1_engine_readiness()
    assert ready["active_calculable_count"]==31
    assert ready["verified_balance_gate"] is True
    assert ready["rule_target_gate"] is False
    assert ready["v1_engine_ready"] is False
