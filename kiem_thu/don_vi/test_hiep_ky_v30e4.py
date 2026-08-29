from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory, token_capability
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25
from loi.quyet_dinh.hiep_ky_season_stem_v30e4 import (
    SI_XIANG_STEMS_BY_MONTH_BRANCH,
    active_season_stem_tokens,
    calculator_status,
    si_xiang_stems,
)
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event


def _base(state="NEUTRAL", event_code="XUAT_HANH", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"MAO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_si_xiang_locks_all_four_seasons_and_twelve_months():
    expected={
        "DAN":("BINH","DINH"),"MAO":("BINH","DINH"),"THIN":("BINH","DINH"),
        "TI":("MAU","KY"),"NGO":("MAU","KY"),"MUI":("MAU","KY"),
        "THAN":("NHAM","QUY"),"DAU":("NHAM","QUY"),"TUAT":("NHAM","QUY"),
        "HOI":("GIAP","AT"),"TY":("GIAP","AT"),"SUU":("GIAP","AT"),
    }
    assert SI_XIANG_STEMS_BY_MONTH_BRANCH==expected
    for month, stems in expected.items():
        assert si_xiang_stems(month)==stems
        for stem in stems:
            assert active_season_stem_tokens(month,stem)==("四相",)


def test_si_xiang_nonmatching_and_invalid_inputs_fail_closed():
    assert active_season_stem_tokens("DAN","GIAP")==()
    for args in (("INVALID","BINH"),("DAN","INVALID")):
        try: active_season_stem_tokens(*args)
        except ValueError: pass
        else: raise AssertionError("invalid Can/Chi must fail closed")


def test_si_xiang_event_inventory_is_yi_only_for_supported_events():
    supported={"DONG_THO","NHAP_TRACH","XUAT_HANH","DIEU_TRI","DAM_PHAN","NHAM_CHUC","CAU_TAI"}
    for event_code in supported:
        rows=[x for x in evidence_for_event(event_code) if x.token=="四相"]
        assert len(rows)==1
        assert rows[0].polarity=="YI"
    for event_code in {"KHAI_TRUONG","KY_HOP_DONG","MUA_TAI_SAN","CUOI_HOI","AN_TANG"}:
        assert all(x.token!="四相" for x in evidence_for_event(event_code))


def test_si_xiang_positive_support_gate_uses_second_spring_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","DINH"),chi_thang="DAN",chi_ngay="MAO")
    assert out["matched_yi_tokens"]==["四相"]
    assert out["matched_ji_tokens"]==[]
    assert out["event_signal_v25"]=="FAVORABLE"
    assert out["label"]=="Ưu tiên"
    assert out["numeric_score"] is None


def test_si_xiang_cannot_rescue_jie_sha_caution():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","DINH"),chi_thang="DAN",chi_ngay="HOI")
    assert "四相" in out["matched_yi_tokens"]
    assert "劫煞" in out["matched_ji_tokens"]
    assert out["event_signal_v25"]=="CAUTION"
    assert out["label"]=="Không ưu tiên"
    assert out["hard_block"] is False


def test_hard_block_still_wins_over_si_xiang():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT","DINH"),chi_thang="DAN",chi_ngay="MAO")
    assert "四相" in out["matched_yi_tokens"]
    assert out["hard_block"] is True
    assert out["decision_state"]=="BLOCKED"


def test_si_xiang_fails_closed_without_current_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="DAN",chi_ngay="MAO")
    assert "四相" not in out["active_hiep_ky_tokens"]


def test_provisional_event_cannot_be_promoted_to_absolute_priority():
    out=evaluate_event_v25(_base(event_code="DAM_PHAN",mapping="PROVISIONAL"),_personal("SUPPORT","DINH"),chi_thang="DAN",chi_ngay="MAO")
    assert "四相" in out["matched_yi_tokens"]
    assert out["label"]=="Có thể cân nhắc"
    assert out["decision_authority"]=="EVENT_PROVISIONAL"


def test_v30e4_capability_schema_and_score_are_explicit_after_v30e5():
    cap=capability_inventory()
    assert cap["token_count"]==81
    assert cap["active_calculable_count"]==25
    assert cap["pending_calculator_count"]==56
    assert "四相" in cap["active_tokens"]
    assert "天願" in cap["active_tokens"]
    assert token_capability("四相")["calculator"]=="SEASON_DAY_STEM_V30E4"
    assert cap["coverage"]=="12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1"
    assert cap["extension_version"]=="V3_0E5_TIAN_YUAN"
    assert cap["numeric_score"] is None

    calc=calculator_status()
    assert calc["active_tokens"]==("四相",)
    assert calc["numeric_score"] is None

    schema=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]})
    assert schema["hiep_ky_v25"]["effective_coverage"]==COVERAGE
    assert "hiep_ky_v30e4_si_xiang" in schema["implemented_scopes"]
    v=schema["hiep_ky_v30e4"]
    assert v["activated_token"]=="四相"
    assert v["calculator"]=="SEASON_DAY_STEM_V30E4"
    assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"
    assert v["creates_hard_block"] is False
    assert v["full_classical_claim"] is False
    assert v["numeric_score"] is None
