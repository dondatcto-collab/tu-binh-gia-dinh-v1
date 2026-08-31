from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_day_branch_v30e8 import WU_HE_DAY_BRANCHES, active_day_branch_tokens, calculator_status
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _base(state="NEUTRAL", event_code="KY_HOP_DONG", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"DAN","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_wu_he_is_exactly_tiger_and_rabbit_days():
    assert WU_HE_DAY_BRANCHES == frozenset({"DAN","MAO"})
    assert active_day_branch_tokens("DAN") == ("五合",)
    assert active_day_branch_tokens("MAO") == ("五合",)
    for branch in ("TY","SUU","THIN","TI","NGO","MUI","THAN","DAU","TUAT","HOI"): assert active_day_branch_tokens(branch) == ()


def test_wu_he_invalid_day_branch_fails_closed():
    try: active_day_branch_tokens("INVALID")
    except ValueError: pass
    else: raise AssertionError("invalid Chi must fail closed")


def test_wu_he_event_inventory_is_scoped():
    verified=[x for x in evidence_for_event("KY_HOP_DONG") if x.token=="五合"]; assert len(verified)==1 and verified[0].polarity=="YI" and verified[0].evidence_status=="VERIFIED"
    provisional=[x for x in evidence_for_event("DAM_PHAN") if x.token=="五合"]; assert len(provisional)==1 and provisional[0].polarity=="YI" and provisional[0].evidence_status=="PROVISIONAL"
    for event_code in {"KHAI_TRUONG","MUA_TAI_SAN","DONG_THO","NHAP_TRACH","CUOI_HOI","XUAT_HANH","DIEU_TRI","NHAM_CHUC","CAU_TAI","AN_TANG"}: assert all(x.token!="五合" for x in evidence_for_event(event_code))


def test_wu_he_positive_gate_for_verified_contract_event_without_day_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="THIN",chi_ngay="DAN"); assert "五合" in out["active_hiep_ky_tokens"]; assert "五合" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_wu_he_cannot_rescue_month_harm_caution():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="TI",chi_ngay="DAN"); assert "五合" in out["matched_yi_tokens"]; assert "月害" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_wu_he():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT",None),chi_thang="THIN",chi_ngay="MAO"); assert "五合" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_wu_he_does_not_leak_to_unsupported_event():
    out=evaluate_event_v25(_base(event_code="XUAT_HANH"),_personal("SUPPORT",None),chi_thang="THIN",chi_ngay="DAN"); assert "五合" in out["active_hiep_ky_tokens"]; assert "五合" not in out["matched_yi_tokens"]


def test_wu_he_provisional_mapping_is_capped():
    out=evaluate_event_v25(_base(event_code="DAM_PHAN",mapping="PROVISIONAL"),_personal("SUPPORT",None),chi_thang="THIN",chi_ngay="DAN"); assert "五合" in out["matched_yi_tokens"]; assert out["label"]=="Có thể cân nhắc"; assert out["decision_authority"]=="EVENT_PROVISIONAL"


def test_v30e8_capability_schema_and_score_remain_explicit_after_later_releases():
    cap=capability_inventory(); assert cap["token_count"]==81; assert "五合" in cap["active_tokens"]; assert token_capability("五合")["calculator"]=="DAY_BRANCH_V30E8"; assert cap["numeric_score"] is None
    calc=calculator_status(); assert calc["active_tokens"]==("五合",); assert calc["numeric_score"] is None
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert schema["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30e8_wu_he" in schema["implemented_scopes"]
    v=schema["hiep_ky_v30e8"]; assert v["activated_token"]=="五合"; assert v["calculator"]=="DAY_BRANCH_V30E8"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["full_classical_claim"] is False; assert v["numeric_score"] is None
