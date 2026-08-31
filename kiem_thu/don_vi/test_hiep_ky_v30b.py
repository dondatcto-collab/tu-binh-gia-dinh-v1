from loi.ket_qua.hiep_ky_v25_result import v25_schema_overlay
from loi.quyet_dinh.hiep_ky_capability_v25 import capability_inventory
from loi.quyet_dinh.hiep_ky_runtime_v25 import COVERAGE,evaluate_event_v25


def _neutral_personal(state="NEUTRAL"):
    return {"state":state,"rule_ids":[],"source_ids":[]}


def test_v30b_tokens_remain_active_after_v30e9():
    cap=capability_inventory(); assert cap["token_count"]==81; assert cap["active_calculable_count"]==29; assert cap["pending_calculator_count"]==52; assert {"劫煞","災煞","月煞"}.issubset(set(cap["active_tokens"])); assert {"天喜","五合","天醫"}.issubset(set(cap["active_tokens"])); assert cap["extension_version"]=="V3_0E9_TIAN_YI"; assert cap["numeric_score"] is None


def test_v30b_favorable_relation_cannot_override_jie_sha_caution():
    base={"event_code":"KY_HOP_DONG","event_state":"NEUTRAL","mapping_status":"VERIFIED","rule_ids":[],"reasons":[]}; out=evaluate_event_v25(base,_neutral_personal("SUPPORT"),chi_thang="DAN",chi_ngay="HOI"); assert "六合" in out["matched_yi_tokens"]; assert "劫煞" in out["matched_ji_tokens"]; assert out["event_signal_v25"]=="CAUTION"; assert out["label"]=="Không ưu tiên"; assert out["hard_block"] is False


def test_v30b_existing_hard_block_still_wins():
    base={"event_code":"KY_HOP_DONG","event_state":"JI","mapping_status":"VERIFIED","rule_ids":[],"reasons":[]}; out=evaluate_event_v25(base,_neutral_personal("SUPPORT"),chi_thang="DAN",chi_ngay="HOI"); assert out["hard_block"] is True; assert out["decision_state"]=="BLOCKED"; assert out["event_state"]=="JI"


def test_v30b_schema_remains_explicit_after_v30e9():
    s=v25_schema_overlay({"implemented_scopes":[],"pending_scopes":[],"principles":[]}); assert s["hiep_ky_v25"]["coverage"]=="V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5"; assert s["hiep_ky_v25"]["effective_coverage"]==COVERAGE; v=s["hiep_ky_v30b"]; assert v["extension_version"]=="V3_0B_SAT_TRIO"; assert v["activated_tokens"]==["劫煞","災煞","月煞"]; assert v["decision_effect"]=="CAUTION_ONLY"; assert v["creates_hard_block"] is False; assert "hiep_ky_v30b_sat_trio" in s["implemented_scopes"]
