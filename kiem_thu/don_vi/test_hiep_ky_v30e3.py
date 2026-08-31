from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25
from loi.quyet_dinh.hiep_ky_stem_v30e import YUE_EN_STEM_BY_MONTH_BRANCH, active_stem_tokens, yue_en_stem


def _base(state="NEUTRAL"):
    return {"event_code":"XUAT_HANH","event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"MAO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_yue_en_locks_all_twelve_month_rows():
    expected={"DAN":"BINH","MAO":"DINH","THIN":"CANH","TI":"KY","NGO":"MAU","MUI":"TAN","THAN":"NHAM","DAU":"QUY","TUAT":"CANH","HOI":"AT","TY":"GIAP","SUU":"TAN"}
    assert YUE_EN_STEM_BY_MONTH_BRANCH==expected
    for month,stem in expected.items(): assert yue_en_stem(month)==stem; assert "月恩" in active_stem_tokens(month,stem)


def test_yue_en_nonmatching_stem_is_not_active(): assert "月恩" not in active_stem_tokens("DAN","GIAP")


def test_yue_en_positive_support_gate():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","BINH"),chi_thang="DAN",chi_ngay="MAO"); assert "月恩" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_yue_en_cannot_rescue_jie_sha_caution():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","BINH"),chi_thang="DAN",chi_ngay="HOI"); assert "月恩" in out["matched_yi_tokens"]; assert "劫煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_yue_en():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT","BINH"),chi_thang="DAN",chi_ngay="MAO"); assert "月恩" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_yue_en_fails_closed_without_current_stem():
    out=evaluate_event_v25(_base(),_personal("SUPPORT",None),chi_thang="DAN",chi_ngay="MAO"); assert "月恩" not in out["active_hiep_ky_tokens"]


def test_v30e3_capability_and_schema_are_explicit_after_v30e8():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==28; assert cap["pending_calculator_count"]==53; assert {"月恩","四相","天願","天赦","天喜","五合"}.issubset(set(cap["active_tokens"])); assert cap["coverage"]=="12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1_PLUS_DAY_BRANCH_1"; assert cap["extension_version"]=="V3_0E8_WU_HE"; assert cap["numeric_score"] is None
    s=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert s["hiep_ky_v25"]["effective_coverage"]==COVERAGE=="V3_0E8_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1_PLUS_DAY_BRANCH_1"; assert "hiep_ky_v30e3_yue_en" in s["implemented_scopes"]
    v=s["hiep_ky_v30e3"]; assert v["activated_token"]=="月恩"; assert v["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["numeric_score"] is None
