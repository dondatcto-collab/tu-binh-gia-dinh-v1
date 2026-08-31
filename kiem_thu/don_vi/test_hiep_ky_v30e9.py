from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_month_day_branch_v30e9 import TIAN_YI_BRANCH_BY_MONTH_BRANCH, active_month_day_branch_tokens, calculator_status, tian_yi_branch
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _base(state="NEUTRAL", event_code="DIEU_TRI", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"HOI","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_tian_yi_locks_all_twelve_month_rows():
    expected={"DAN":"TUAT","MAO":"HOI","THIN":"TY","TI":"SUU","NGO":"DAN","MUI":"MAO","THAN":"THIN","DAU":"TI","TUAT":"NGO","HOI":"MUI","TY":"THAN","SUU":"DAU"}
    assert TIAN_YI_BRANCH_BY_MONTH_BRANCH==expected
    for month, day_branch in expected.items():
        assert tian_yi_branch(month)==day_branch; assert active_month_day_branch_tokens(month,day_branch)==("天醫",)


def test_tian_yi_negative_and_invalid_inputs_fail_closed():
    assert active_month_day_branch_tokens("DAN","HOI")==()
    for args in (("INVALID","TUAT"),("DAN","INVALID")):
        try: active_month_day_branch_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_tian_yi_event_inventory_is_yi_only_for_treatment():
    rows=[x for x in evidence_for_event("DIEU_TRI") if x.token=="天醫"]
    assert len(rows)==1; assert rows[0].polarity=="YI"; assert rows[0].evidence_status=="VERIFIED"
    for event_code in {"KHAI_TRUONG","KY_HOP_DONG","MUA_TAI_SAN","DONG_THO","NHAP_TRACH","CUOI_HOI","XUAT_HANH","DAM_PHAN","NHAM_CHUC","CAU_TAI","AN_TANG"}: assert all(x.token!="天醫" for x in evidence_for_event(event_code))


def test_tian_yi_positive_gate_for_verified_treatment_without_day_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="HOI")
    assert "天醫" in out["active_hiep_ky_tokens"]; assert "天醫" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_tian_yi_ji_conflict_month_dan_day_tuat_yue_yan_wins():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="DAN",chi_ngay="TUAT")
    assert "天醫" in out["matched_yi_tokens"]; assert "月厭" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_tian_yi():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="HOI")
    assert "天醫" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_tian_yi_does_not_require_current_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="HOI")
    assert "天醫" in out["active_hiep_ky_tokens"]; assert "月徳" not in out["active_hiep_ky_tokens"]


def test_tian_yi_does_not_leak_to_unsupported_event():
    out=evaluate_event_v25(_base(event_code="KY_HOP_DONG"),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="HOI")
    assert "天醫" in out["active_hiep_ky_tokens"]; assert "天醫" not in out["matched_yi_tokens"]


def test_v30e9_capability_schema_and_score_are_explicit():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==29; assert cap["pending_calculator_count"]==52; assert "天醫" in cap["active_tokens"]; assert token_capability("天醫")["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E9"; assert cap["extension_version"]=="V3_0E9_TIAN_YI"; assert cap["numeric_score"] is None
    calc=calculator_status(); assert calc["active_tokens"]==("天醫",); assert calc["numeric_score"] is None
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert schema["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30e9_tian_yi" in schema["implemented_scopes"]
    v=schema["hiep_ky_v30e9"]; assert v["activated_token"]=="天醫"; assert v["calculator"]=="MONTH_BRANCH_DAY_BRANCH_V30E9"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["full_classical_claim"] is False; assert v["numeric_score"] is None
