from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE,evaluate_event_v25


def _personal(state="NEUTRAL"):
    return {"state":state,"rule_ids":[],"source_ids":[],"branch_impacts":[],"theme":{},"dien_giai":{},"technical_facts":[]}


def _base(code="XUAT_HANH",state="NEUTRAL",mapping="VERIFIED"):
    return {"event_code":code,"event_state":state,"mapping_status":mapping,"rule_ids":[],"reasons":[],"source_id":"SRC-HK-QD-V11-WIKISOURCE"}


def test_v30d_shi_de_remains_active_after_v30e9():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==29; assert cap["pending_calculator_count"]==52; assert {"時徳","月徳","月徳合","月恩","四相","天願","天赦","天喜","五合","天醫"}.issubset(set(cap["active_tokens"])); assert cap["extension_version"]=="V3_0E9_TIAN_YI"


def test_v30d_shi_de_can_support_verified_neutral_event():
    out=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="NGO"); assert "時徳" in out["active_hiep_ky_tokens"]; assert "時徳" in out["matched_yi_tokens"]; assert out["event_signal_v25"]=="FAVORABLE"; assert out["label"]=="Ưu tiên"; assert out["numeric_score"] is None


def test_v30d_ji_still_wins_when_shi_de_overlaps_zai_sha():
    out=evaluate_event_v25(_base(),_personal("SUPPORT"),chi_thang="THIN",chi_ngay="NGO"); assert "時徳" in out["matched_yi_tokens"]; assert "災煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_v30d_existing_hard_block_still_wins():
    out=evaluate_event_v25(_base(state="JI"),_personal("SUPPORT"),chi_thang="DAN",chi_ngay="NGO"); assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"; assert out["label"]=="Bị chặn"


def test_v30d_schema_remains_explicit_after_v30e9():
    s=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert s["hiep_ky_v25"]["coverage"]=="V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"; assert s["hiep_ky_v25"]["effective_coverage"]==COVERAGE; assert "hiep_ky_v30d_shi_de" in s["implemented_scopes"]; v=s["hiep_ky_v30d"]; assert v["activated_token"]=="時徳"; assert v["calculator"]=="MONTH_BRANCH_RELATIONS_V25_V30D"; assert v["decision_effect"]=="FAVORABLE_SUPPORT_ONLY"; assert v["creates_hard_block"] is False; assert v["numeric_score"] is None
