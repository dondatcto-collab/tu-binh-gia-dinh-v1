from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE, evaluate_event_v25


def _base(event_code="KY_HOP_DONG", state="NEUTRAL", mapping="VERIFIED"):
    return {"event_code":event_code,"event_state":state,"mapping_status":mapping,"label":"Chưa có tín hiệu theo việc","rank_group":3,"reasons":[],"rule_ids":["HK-GENERAL-0001"],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def _personal(state="DESCRIPTIVE_ONLY", can_vi=None):
    facts=[f"Can {can_vi} đối với Nhật chủ là kiểm thử"] if can_vi else []
    return {"state":state,"rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":facts}


def test_hard_block_v1_still_wins_everything():
    r=evaluate_event_v25(_base(state="JI"),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="HOI"); assert r["hard_block"] is True; assert r["decision_state"]=="BLOCKED"; assert r["label"]=="Bị chặn"; assert r["rank_group"]==9


def test_new_yi_token_can_support_neutral_event_without_score():
    r=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="THIN",chi_ngay="DAU"); assert r["matched_yi_tokens"]==["六合"]; assert r["event_signal_v25"]=="FAVORABLE"; assert r["label"]=="Ưu tiên"; assert r["score"] is None


def test_v30a_yue_hai_and_yue_xing_both_survive_as_caution_evidence():
    r=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="TI"); assert set(r["matched_ji_tokens"])=={"月害","月刑"}; assert r["event_signal_v25"]=="CAUTION"; assert r["hard_block"] is False; assert r["label"]=="Không ưu tiên"


def test_v30c_yue_yan_is_caution_not_hard_block():
    r=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="TUAT"); assert "月厭" in r["matched_ji_tokens"]; assert r["event_signal_v25"]=="CAUTION"; assert r["hard_block"] is False


def test_personal_cannot_rescue_event_caution():
    r=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="TY",chi_ngay="MAO"); assert r["label"]=="Không ưu tiên"; assert r["rank_group"]==4


def test_provisional_mapping_cannot_be_promoted_to_priority_by_new_signal():
    r=evaluate_event_v25(_base(event_code="DAM_PHAN",mapping="PROVISIONAL"),_personal("SUPPORT"),chi_thang="THIN",chi_ngay="DAU"); assert "六合" in r["matched_yi_tokens"]; assert r["label"]=="Có thể cân nhắc"; assert r["decision_authority"]=="EVENT_PROVISIONAL"


def test_runtime_is_traceable_and_coverage_is_explicitly_partial():
    r=evaluate_event_v25(_base(),_personal(),chi_thang="DAN",chi_ngay="HOI"); assert r["matched_evidence"]; ev=r["matched_evidence"][0]; assert ev["rule_id"] and ev["source_id"] and ev["source_location"]; assert ev["decision_status"]=="ACTIVE"; assert r["coverage"]==COVERAGE=="V3_0E7_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1"; assert r["hiep_ky_extension"]=="V3_0E7_TIAN_XI"


def test_day_stem_rules_fail_closed_but_branch_only_tian_xi_does_not():
    r=evaluate_event_v25(_base(event_code="XUAT_HANH"),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="NGO")
    assert "月徳" not in r["active_hiep_ky_tokens"]; assert "月徳合" not in r["active_hiep_ky_tokens"]; assert "月恩" not in r["active_hiep_ky_tokens"]; assert "四相" not in r["active_hiep_ky_tokens"]; assert "天願" not in r["active_hiep_ky_tokens"]; assert "天赦" not in r["active_hiep_ky_tokens"]
    assert "天喜" in r["active_hiep_ky_tokens"]
