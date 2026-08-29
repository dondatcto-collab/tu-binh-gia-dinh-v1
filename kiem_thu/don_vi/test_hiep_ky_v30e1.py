from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_runtime_v25 import evaluate_event_v25
from loi.quyet_dinh.hiep_ky_stem_v30e import YUE_DE_STEM_BY_MONTH_BRANCH, active_stem_tokens, calculator_status, yue_de_stem


def _base(state="NEUTRAL"):
    return {"event_code":"XUAT_HANH","event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", current_stem=None, technical_facts=None):
    return {"state":state,"rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"current_stem":current_stem,"current_branch":"THIN","technical_facts":list(technical_facts or [])}


def test_yue_de_locks_all_twelve_month_branch_to_day_stem_rows():
    expected={"DAN":"BINH","NGO":"BINH","TUAT":"BINH","HOI":"GIAP","MAO":"GIAP","MUI":"GIAP","THAN":"NHAM","TY":"NHAM","THIN":"NHAM","TI":"CANH","DAU":"CANH","SUU":"CANH"}
    assert YUE_DE_STEM_BY_MONTH_BRANCH==expected
    for month_branch,day_stem in expected.items():
        assert yue_de_stem(month_branch)==day_stem; assert "月徳" in active_stem_tokens(month_branch,day_stem)


def test_yue_de_negative_and_invalid_inputs_fail_closed():
    assert "月徳" not in active_stem_tokens("DAN","GIAP")
    for args in (("INVALID","BINH"),("DAN","INVALID")):
        try: active_stem_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Can/Chi must fail closed")


def test_v30e1_yue_de_remains_active_after_v30e6():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==26; assert cap["pending_calculator_count"]==55; assert "月徳" in cap["active_tokens"]; assert token_capability("月徳")["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"


def test_yue_de_can_support_verified_neutral_event():
    out=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="THIN",can_ngay="BINH")
    assert "月徳" in out["active_hiep_ky_tokens"]; assert "月徳" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_yue_de_uses_typed_current_stem_contract_for_live_pipeline():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","BINH"),chi_thang="DAN",chi_ngay="THIN")
    assert "月徳" in out["active_hiep_ky_tokens"]; assert "月徳" in out["matched_yi_tokens"]; assert out["personal_v1_1"]["current_stem"]=="BINH"


def test_technical_text_is_not_parsed_for_day_stem_anymore():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None,["Can Bính đối với Nhật chủ là kiểm thử"]),chi_thang="DAN",chi_ngay="THIN")
    assert "月徳" not in out["active_hiep_ky_tokens"]; assert out["matched_yi_tokens"]==[]


def test_invalid_typed_current_stem_fails_closed():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","INVALID"),chi_thang="DAN",chi_ngay="THIN")
    assert "月徳" not in out["active_hiep_ky_tokens"]; assert out["matched_yi_tokens"]==[]


def test_explicit_day_stem_remains_backward_compatible_and_takes_precedence():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","GIAP"),chi_thang="DAN",chi_ngay="THIN",can_ngay="BINH")
    assert "月徳" in out["active_hiep_ky_tokens"]; assert "月徳" in out["matched_yi_tokens"]


def test_ji_wins_when_yue_de_overlaps_zai_sha():
    out=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="TY",can_ngay="BINH")
    assert "月徳" in out["matched_yi_tokens"]; assert "災煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False; assert out["numeric_score"] is None


def test_existing_hard_block_still_wins_over_yue_de():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="THIN",can_ngay="BINH")
    assert "月徳" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"; assert out["label"]=="Bị chặn"


def test_missing_day_stem_never_implicitly_activates_yue_de():
    out=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="THIN"); assert "月徳" not in out["active_hiep_ky_tokens"]


def test_v30e1_schema_remains_explicit_after_v30e6():
    calc=calculator_status(); assert calc["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"; assert calc["active_tokens"]==("月徳","月徳合","月恩"); assert calc["numeric_score"] is None
    s=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert "hiep_ky_v30e1_yue_de" in s["implemented_scopes"]
    v=s["hiep_ky_v30e1"]; assert v["activated_token"]=="月徳"; assert v["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["full_classical_claim"] is False; assert v["numeric_score"] is None
