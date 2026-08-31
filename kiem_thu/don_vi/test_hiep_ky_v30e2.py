from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25
from loi.quyet_dinh.hiep_ky_stem_v30e import YUE_DE_HE_STEM_BY_MONTH_BRANCH, active_stem_tokens, yue_de_he_stem


def _base(state="NEUTRAL"):
    return {"event_code":"XUAT_HANH","event_state":state,"mapping_status":"VERIFIED","rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="SUPPORT", stem=None):
    return {"state":state,"current_stem":stem,"current_branch":"MAO","rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def test_yue_de_he_locks_all_twelve_month_rows():
    expected={"DAN":"TAN","NGO":"TAN","TUAT":"TAN","HOI":"KY","MAO":"KY","MUI":"KY","THAN":"DINH","TY":"DINH","THIN":"DINH","TI":"AT","DAU":"AT","SUU":"AT"}
    assert YUE_DE_HE_STEM_BY_MONTH_BRANCH==expected
    for month,stem in expected.items(): assert yue_de_he_stem(month)==stem; assert "月徳合" in active_stem_tokens(month,stem)


def test_yue_de_he_positive_support_gate():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","TAN"),chi_thang="DAN",chi_ngay="MAO"); assert "月徳合" in out["matched_yi_tokens"]; assert out["matched_ji_tokens"]==[]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_yue_de_he_cannot_rescue_jie_sha_caution():
    out=evaluate_event_v25(_base(),_personal("SUPPORT","TAN"),chi_thang="DAN",chi_ngay="HOI"); assert "月徳合" in out["matched_yi_tokens"]; assert "劫煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_hard_block_still_wins_over_yue_de_he():
    out=evaluate_event_v25(_base("JI"),_personal("SUPPORT","TAN"),chi_thang="DAN",chi_ngay="MAO"); assert "月徳合" in out["matched_yi_tokens"]; assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"


def test_v30e2_remains_active_after_later_releases():
    cap=capability_inventory(); assert "月徳合" in cap["active_tokens"]
    s=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert s["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30e2_yue_de_he" in s["implemented_scopes"]
    v=s["hiep_ky_v30e2"]; assert v["activated_token"]=="月徳合"; assert v["calculator"]=="MONTH_BRANCH_DAY_STEM_V30E3"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["numeric_score"] is None
