from loi.nen.phien_ban import ENGINE_VERSION, RULESET_VERSION
from loi.quyet_dinh.v1 import (
    EVENT_RULES, HIEP_KY_COVERAGE, NUMERIC_SCORE_STATUS,
    V1_EVENT_COVERAGE, danh_gia_event,
)
from loi.quyet_dinh.ca_nhan import bo_sung_event_ca_nhan
from loi.bat_tu.cach_cuc import MONTH_MAIN_QI
from loi.bat_tu.phuong_phap_tu_binh import trang_thai_hien_tai

EXPECTED_EVENTS = {
    "AN_TANG","CAU_TAI","CUOI_HOI","DAM_PHAN","DIEU_TRI","DONG_THO",
    "KHAI_TRUONG","KY_HOP_DONG","MUA_TAI_SAN","NHAM_CHUC","NHAP_TRACH","XUAT_HANH",
}


def _personal(state):
    return {"state":state,"theme":{},"branch_impacts":[],"rule_ids":[],"technical_facts":[],"dien_giai":{},"methodology":{"decision_mode":"ZPZQ_PERSONAL"}}


def _event(state):
    return {"event_state":state,"mapping_status":"VERIFIED","rank_group":1 if state=="YI" else 3,"label":"base","reasons":[],"rule_ids":[],"score":None}


def test_release_version_locked():
    assert ENGINE_VERSION == "0.5.0-zpzq-fusion"
    assert RULESET_VERSION == "RS-2026.08-ZPZQ.2"


def test_gate2_exactly_12_official_events():
    assert set(EVENT_RULES) == EXPECTED_EVENTS
    assert "THI_CU" not in EVENT_RULES
    assert V1_EVENT_COVERAGE == "12/12"
    assert HIEP_KY_COVERAGE == "PARTIAL_12_TRUC_ONLY"


def test_gate2_all_events_run_all_12_truc_without_numeric_score():
    for code in EXPECTED_EVENTS:
        for day_chi in ("DAN","MAO","THIN","TI","NGO","MUI","THAN","DAU","TUAT","HOI","TY","SUU"):
            d = danh_gia_event("DAN", day_chi, "MAO", code)
            assert d["support_level"] == "ACTIVE_BASIC"
            assert d["score"] is None
            assert d["numeric_score_status"] == "LOCKED_OFF"
            assert d["coverage"] == "PARTIAL_12_TRUC_ONLY"


def test_gate2_locked_narrow_labels():
    assert EVENT_RULES["NHAP_TRACH"].ten == "Chuyển nhà / di dời"
    assert EVENT_RULES["DIEU_TRI"].ten == "Khám / điều trị"
    assert EVENT_RULES["DAM_PHAN"].ten == "Họp / gặp gỡ"
    assert EVENT_RULES["NHAM_CHUC"].ten == "Nhận chức / nhậm chức"
    assert EVENT_RULES["CAU_TAI"].ten == "Thu / nhận tiền"


def test_gate1_month_selector_is_explicit_not_hidden_order_proxy():
    assert MONTH_MAIN_QI == {"TY":"QUY","DAN":"GIAP","MAO":"AT","TI":"BINH","NGO":"DINH","THAN":"CANH","DAU":"TAN","HOI":"NHAM"}
    assert trang_thai_hien_tai().personal_decision_ready is True


def test_gate3_gold_1_personal_and_hiep_ky_same_direction():
    r = bo_sung_event_ca_nhan(_event("YI"), _personal("SUPPORT"))
    assert (r["decision_state"], r["label"], r["score"]) == ("PRIORITY","Ưu tiên",None)


def test_gate3_gold_2_hard_block_always_wins():
    r = bo_sung_event_ca_nhan(_event("JI"), _personal("SUPPORT"))
    assert r["hard_block"] is True
    assert r["decision_state"] == "HARD_BLOCK"
    assert r["label"] == "Bị chặn"


def test_gate3_gold_3_hiep_ky_good_personal_adverse_is_only_consider():
    r = bo_sung_event_ca_nhan(_event("YI"), _personal("CAUTION"))
    assert (r["decision_state"], r["label"]) == ("CONSIDER","Có thể cân nhắc")


def test_gate3_gold_4_bad_day_not_rescued_by_larger_favorable_context():
    r = bo_sung_event_ca_nhan(_event("JI"), _personal("SUPPORT"))
    assert r["decision_state"] == "HARD_BLOCK"
    assert r["rank_group"] == 9


def test_gate3_gold_5_personal_only_breaks_tie_without_hard_block():
    supportive = bo_sung_event_ca_nhan(_event("NEUTRAL"), _personal("SUPPORT"))
    adverse = bo_sung_event_ca_nhan(_event("NEUTRAL"), _personal("CAUTION"))
    assert supportive["rank_group"] < adverse["rank_group"]
    assert supportive["hard_block"] is False and adverse["hard_block"] is False


def test_gate3_numeric_score_locked_off():
    assert NUMERIC_SCORE_STATUS == "LOCKED_OFF"
    for ev in ("YI","JI","NEUTRAL"):
        for p in ("SUPPORT","CAUTION","NEUTRAL","DESCRIPTIVE_ONLY"):
            r=bo_sung_event_ca_nhan(_event(ev),_personal(p))
            assert r["score"] is None
            assert r["numeric_score_status"] == "LOCKED_OFF"
