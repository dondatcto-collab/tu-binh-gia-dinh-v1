from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_day_pillar_v30e5 import TIAN_YUAN_DAY_PILLAR_BY_MONTH_BRANCH, active_day_pillar_tokens, calculator_status, tian_yuan_day_pillar
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _base(state="NEUTRAL", event_code="KHAI_TRUONG", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"NGO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_tian_yuan_locks_all_twelve_month_day_pillars():
    expected={"DAN":("GIAP","NGO"),"MAO":("GIAP","TUAT"),"THIN":("AT","DAU"),"TI":("BINH","TY"),"NGO":("DINH","SUU"),"MUI":("MAU","NGO"),"THAN":("GIAP","DAN"),"DAU":("BINH","THIN"),"TUAT":("TAN","MAO"),"HOI":("MAU","THIN"),"TY":("GIAP","TY"),"SUU":("QUY","MUI")}
    assert TIAN_YUAN_DAY_PILLAR_BY_MONTH_BRANCH==expected
    for month,pillar in expected.items(): assert tian_yuan_day_pillar(month)==pillar; assert active_day_pillar_tokens(month,*pillar)==("天願",)


def test_tian_yuan_requires_full_day_pillar_and_invalid_inputs_fail_closed():
    assert active_day_pillar_tokens("DAN","GIAP","TY")==(); assert active_day_pillar_tokens("DAN","BINH","NGO")==()
    for args in (("INVALID","GIAP","NGO"),("DAN","INVALID","NGO"),("DAN","GIAP","INVALID")):
        try: active_day_pillar_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Can/Chi must fail closed")


def test_tian_yuan_event_inventory_is_yi_only_where_classical_event_lists_it():
    supported={"KHAI_TRUONG","KY_HOP_DONG","DONG_THO","NHAP_TRACH","CUOI_HOI","XUAT_HANH","DAM_PHAN","NHAM_CHUC","CAU_TAI","AN_TANG"}
    for event_code in supported:
        rows=[x for x in evidence_for_event(event_code) if x.token=="天願"]; assert len(rows)==1; assert rows[0].polarity=="YI"
    for event_code in {"MUA_TAI_SAN","DIEU_TRI"}: assert all(x.token!="天願" for x in evidence_for_event(event_code))


def test_tian_yuan_positive_support_gate_for_verified_opening_event():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","GIAP"),chi_thang="DAN",chi_ngay="NGO"); assert "天願" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_tian_yuan_cannot_rescue_yue_sha_caution():
    out=evaluate_event_v25(_base(event_code="XUAT_HANH"),_personal("SUPPORT","GIAP"),chi_thang="MAO",chi_ngay="TUAT"); assert "天願" in out["matched_yi_tokens"]; assert "月煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_tian_yuan():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT","GIAP"),chi_thang="DAN",chi_ngay="NGO"); assert "天願" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_tian_yuan_fails_closed_without_current_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="DAN",chi_ngay="NGO"); assert "天願" not in out["active_hiep_ky_tokens"]


def test_tian_yuan_does_not_leak_to_unsupported_medical_event():
    out=evaluate_event_v25(_base(event_code="DIEU_TRI"),_personal("SUPPORT","GIAP"),chi_thang="DAN",chi_ngay="NGO"); assert "天願" in out["active_hiep_ky_tokens"]; assert "天願" not in out["matched_yi_tokens"]


def test_provisional_event_cannot_be_promoted_to_absolute_priority_by_tian_yuan():
    out=evaluate_event_v25(_base(event_code="DAM_PHAN",mapping="PROVISIONAL"),_personal("SUPPORT","GIAP"),chi_thang="DAN",chi_ngay="NGO"); assert "天願" in out["matched_yi_tokens"]; assert out["label"]=="Có thể cân nhắc"; assert out["decision_authority"]=="EVENT_PROVISIONAL"


def test_v30e5_capability_schema_and_score_are_explicit_after_v30e8():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==28; assert cap["pending_calculator_count"]==53; assert {"天願","天赦","天喜","五合"}.issubset(set(cap["active_tokens"])); assert token_capability("天願")["calculator"]=="MONTH_BRANCH_DAY_PILLAR_V30E5"; assert cap["coverage"]=="12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1_PLUS_DAY_BRANCH_1"; assert cap["extension_version"]=="V3_0E8_WU_HE"; assert cap["numeric_score"] is None
    calc=calculator_status(); assert calc["active_tokens"]==("天願",); assert calc["numeric_score"] is None
    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert schema["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30e5_tian_yuan" in schema["implemented_scopes"]
    v=schema["hiep_ky_v30e5"]; assert v["activated_token"]=="天願"; assert v["calculator"]=="MONTH_BRANCH_DAY_PILLAR_V30E5"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["full_classical_claim"] is False; assert v["numeric_score"] is None
