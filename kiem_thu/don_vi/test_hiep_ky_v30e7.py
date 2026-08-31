from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25
from loi.quyet_dinh.hiep_ky_season_branch_v30e7 import TIAN_XI_BRANCH_BY_MONTH_BRANCH, active_season_branch_tokens, calculator_status, tian_xi_branch


def _base(state="NEUTRAL", event_code="CUOI_HOI", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None, branch="NGO"):
    return {"state":state,"current_stem":stem,"current_branch":branch,"rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_tian_xi_locks_four_seasons_across_all_twelve_month_branches():
    expected={"DAN":"NGO","MAO":"NGO","THIN":"NGO","TI":"SUU","NGO":"SUU","MUI":"SUU","THAN":"THIN","DAU":"THIN","TUAT":"THIN","HOI":"MUI","TY":"MUI","SUU":"MUI"}
    assert TIAN_XI_BRANCH_BY_MONTH_BRANCH==expected
    for month,day_branch in expected.items(): assert tian_xi_branch(month)==day_branch; assert active_season_branch_tokens(month,day_branch)==("天喜",)


def test_tian_xi_negative_and_invalid_inputs_fail_closed():
    assert active_season_branch_tokens("DAN","MAO")==()
    for args in (("INVALID","NGO"),("DAN","INVALID")):
        try: active_season_branch_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Chi must fail closed")


def test_tian_xi_event_inventory_is_yi_only_where_event_lists_it():
    supported={"CUOI_HOI","XUAT_HANH","DAM_PHAN","NHAM_CHUC"}
    for event_code in supported:
        rows=[x for x in evidence_for_event(event_code) if x.token=="天喜"]; assert len(rows)==1; assert rows[0].polarity=="YI"
    for event_code in {"KHAI_TRUONG","KY_HOP_DONG","MUA_TAI_SAN","DONG_THO","NHAP_TRACH","DIEU_TRI","CAU_TAI","AN_TANG"}: assert all(x.token!="天喜" for x in evidence_for_event(event_code))


def test_tian_xi_positive_gate_for_verified_marriage_event_without_day_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="NGO"); assert "天喜" in out["active_hiep_ky_tokens"]; assert "天喜" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_tian_xi_ji_conflict_month_ngo_day_suu_month_sha_wins():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="NGO",chi_ngay="SUU"); assert "天喜" in out["matched_yi_tokens"]; assert "月煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_tian_xi():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="NGO"); assert "天喜" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_tian_xi_does_not_require_current_stem_but_stem_rules_still_fail_closed():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="NGO"); assert "天喜" in out["active_hiep_ky_tokens"]; assert "月徳" not in out["active_hiep_ky_tokens"]; assert "月徳合" not in out["active_hiep_ky_tokens"]; assert "月恩" not in out["active_hiep_ky_tokens"]


def test_tian_xi_does_not_leak_to_unsupported_opening_event():
    out=evaluate_event_v25(_base(event_code="KHAI_TRUONG"),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="NGO"); assert "天喜" in out["active_hiep_ky_tokens"]; assert "天喜" not in out["matched_yi_tokens"]


def test_provisional_event_cannot_be_promoted_to_absolute_priority_by_tian_xi():
    out=evaluate_event_v25(_base(event_code="DAM_PHAN",mapping="PROVISIONAL"),_personal("SUPPORT",None),chi_thang="MAO",chi_ngay="NGO"); assert "天喜" in out["matched_yi_tokens"]; assert out["label"]=="Có thể cân nhắc"; assert out["decision_authority"]=="EVENT_PROVISIONAL"


def test_v30e7_capability_schema_and_score_are_explicit_after_v30e9():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==29; assert cap["pending_calculator_count"]==52; assert {"天喜","五合","天醫"}.issubset(set(cap["active_tokens"])); assert token_capability("天喜")["calculator"]=="SEASON_DAY_BRANCH_V30E7"; assert cap["extension_version"]=="V3_0E9_TIAN_YI"; assert cap["numeric_score"] is None
    calc=calculator_status(); assert calc["active_tokens"]==("天喜",); assert calc["numeric_score"] is None
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert schema["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30e7_tian_xi" in schema["implemented_scopes"]
    v=schema["hiep_ky_v30e7"]; assert v["activated_token"]=="天喜"; assert v["calculator"]=="SEASON_DAY_BRANCH_V30E7"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["full_classical_claim"] is False; assert v["numeric_score"] is None
