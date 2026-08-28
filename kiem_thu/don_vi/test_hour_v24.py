from pathlib import Path

from loi.bat_tu.phuong_phap_tu_binh import cho_phep_ket_luan_gio_ca_nhan, trang_thai_hien_tai
from loi.ket_qua.gio_v24 import HOUR_SCHEMA_VERSION, HOUR_STATUS, hour_reference_result, v24_schema_overlay

ROOT = Path(__file__).resolve().parents[2]


def sample_raw():
    return {
        "ngay": "2026-08-24",
        "gio_trong_ngay": [
            {"chi": "TY", "chi_vi": "Tý", "khoang_gio": "23:00–01:00", "nhan": "Lục hợp", "relation": "LUC_HOP", "relation_nature": "POSITIVE", "ly_do": "Quan hệ cấu trúc."}
        ],
    }


def test_hour_method_gate_now_allows_limited_v29b_decision_but_not_full_classical_claim():
    s = trang_thai_hien_tai()
    assert s.hour_structure_ready is True
    assert s.hour_fusion_ready is True
    assert s.personal_hour_decision_ready is True
    assert cho_phep_ket_luan_gio_ca_nhan() is True
    assert s.decision_mode == "ZPZQ_PERSONAL"
    assert "chưa phải hệ cát-hung giờ cổ điển đầy đủ" in s.reason_vi
    assert "BT-REL-0001" in s.rule_ids
    assert "SRC-TMTH-V02-WIKISOURCE" in s.source_ids


def test_hour_reference_itself_remains_descriptive_without_event_context():
    out = hour_reference_result(sample_raw())
    assert out["schema_version"] == HOUR_SCHEMA_VERSION == "2.4-alpha.1"
    assert out["status"] == HOUR_STATUS
    assert out["conclusion"]["state"] == "DESCRIPTIVE_ONLY"
    assert out["hours"][0]["is_personal_good_hour"] is None
    assert out["hours"][0]["is_personal_bad_hour"] is None
    assert out["numeric_score"] is None
    assert out["numeric_score_status"] == "LOCKED_OFF"


def test_legacy_v24_overlay_still_describes_reference_layer_only():
    out = v24_schema_overlay({"implemented_scopes": ["day"], "pending_scopes": ["personal_hour"], "principles": []})
    assert out["schema_version"] == "2.4-alpha.1"
    assert "personal_hour_reference" in out["implemented_scopes"]
    assert "personal_hour_decision" in out["pending_scopes"]
    assert out["hour_readiness"]["hour_fusion_ready"] is False


def test_v2_api_keeps_hour_reference_and_routes_it_through_v29_gate():
    text = (ROOT / "cong/api_v2.py").read_text(encoding="utf-8")
    assert '"/gio-ca-nhan"' in text
    assert "hour_reference_result" in text
    assert "hour_fusion_gate" in text
    assert "HourDecisionRequest" in text
    assert "tim_ngay_v25" in text


def test_hour_ui_reads_only_v2_and_mirrors_are_identical():
    pub = (ROOT / "public/static/ui-hour-v24.js").read_text(encoding="utf-8")
    mirror = (ROOT / "giao_dien/ui-hour-v24.js").read_text(encoding="utf-8")
    assert pub == mirror
    assert "/api/v2/gio-ca-nhan" in pub
    assert "/api/stateless/" not in pub
    assert "PERSONAL_GOOD_CANDIDATE" in pub
    assert "không phải cát/hung tuyệt đối" in pub


def test_hour_can_never_rescue_hard_block_in_copy_contract():
    old = (ROOT / "loi/ket_qua/gio_v24.py").read_text(encoding="utf-8")
    new = (ROOT / "loi/ket_qua/gio_v29.py").read_text(encoding="utf-8")
    assert "Không dùng giờ để cứu một ngày đã bị chặn" in old
    assert "Không xét giờ để cứu ngày đã bị chặn" in new
