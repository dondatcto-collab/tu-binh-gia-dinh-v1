import json
from pathlib import Path

from loi.ket_qua.hiep_ky_v25_result import EVENT_SEARCH_CONTRACT, event_search_v25

ROOT = Path(__file__).resolve().parents[2]


def sample(day: str, label: str, rank: int, *, hard_block: bool = False):
    return {
        "ngay": day,
        "label": label,
        "decision_state": "HARD_BLOCK" if hard_block else "FAVORABLE",
        "hard_block": hard_block,
        "rank_group": rank,
        "event_state": "JI" if hard_block else "YI",
        "personal_v1_1": {},
        "reasons": [f"reason-{day}"],
        "mapping_status": "VERIFIED",
        "coverage": "V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5",
        "rule_ids": [f"RULE-{day}"],
        "source_ids": ["SRC-HK-QD-V11-WIKISOURCE"],
        "matched_evidence": [],
        "active_hiep_ky_tokens": [],
        "matched_yi_tokens": [],
        "matched_ji_tokens": [],
        "decision_authority": "EVENT",
        "event_state_v1": "NEUTRAL",
        "event_signal_v25": "BLOCK" if hard_block else "FAVORABLE",
    }


def test_event_search_exposes_top_three_and_complete_ranked_set_without_scores():
    ranked = [
        sample("2026-09-01", "Ưu tiên", 1),
        sample("2026-09-02", "Ưu tiên", 1),
        sample("2026-09-03", "Có thể cân nhắc", 2),
        sample("2026-09-04", "Bị chặn", 9, hard_block=True),
    ]
    raw = {
        "viec": "KY_HOP_DONG",
        "so_ngay_da_quet": len(ranked),
        "xep_hang_status": "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL",
        "top": ranked[:3],
        "cac_ngay": ranked,
    }
    out = event_search_v25(raw)
    assert out["event_search_contract"] == EVENT_SEARCH_CONTRACT == "V2_7_COMPLETE_RESULTS"
    assert len(out["results"]) == 3
    assert len(out["all_results"]) == 4
    assert out["result_count"] == 4
    assert out["top_result_count"] == 3
    assert [x["date"] for x in out["all_results"]] == [x["ngay"] for x in ranked]
    assert out["all_results"][-1]["event_context"]["hard_block"] is True
    assert out["all_results"][-1]["rules"] == ["RULE-2026-09-04"]
    assert out["numeric_score"] is None
    assert all(x["numeric_score"] is None for x in out["all_results"])


def test_v27_complete_result_contract_has_payload_growth_guard_for_max_window():
    ranked = [
        sample(f"2026-{8 + (i // 28):02d}-{(i % 28) + 1:02d}", "Có thể cân nhắc", 3)
        for i in range(93)
    ]
    raw = {
        "viec": "KY_HOP_DONG",
        "so_ngay_da_quet": len(ranked),
        "xep_hang_status": "ORDINAL_V25_HARD_BLOCK_EVENT_PERSONAL",
        "top": ranked[:3],
        "cac_ngay": ranked,
    }
    out = event_search_v25(raw)
    encoded = json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    assert out["result_count"] == 93
    assert len(out["all_results"]) == 93
    assert len(encoded) < 512 * 1024


def test_v27_ui_uses_one_event_search_source_for_search_and_event_calendar():
    ui = (ROOT / "public/static/ui-event-search-v27.js").read_text(encoding="utf-8")
    assert ui.count("/api/v2/tim-ngay") >= 3
    assert "/api/stateless/tim-ngay" not in ui
    assert "all_results" in ui
    assert "3 lựa chọn nên xem trước" in ui
    assert "Xem tất cả" in ui
    assert "Vì sao ngày này được xếp như vậy?" in ui
    assert "Lịch đang đánh giá theo đúng loại việc đã chọn" in ui
    assert "numeric_score" not in ui


def test_v28_ui_explains_confidence_without_changing_decision_tone():
    ui = (ROOT / "public/static/ui-event-search-v27.js").read_text(encoding="utf-8")
    assert "TU_BINH_EVENT_SEARCH_UI_VERSION = '2.8'" in ui
    assert "confidence_basis" in ui
    assert "Vì sao mức căn cứ là" in ui
    assert "Mức căn cứ được đánh giá riêng theo chất lượng bằng chứng" in ui
    assert "function tone(r)" in ui
    assert "confidence_state" not in ui.split("function tone(r)", 1)[1].split("function confidence(r)", 1)[0]


def test_v27_event_module_is_loaded_last_by_single_bootstrap():
    bootstrap = (ROOT / "public/static/ui-bootstrap-v26.js").read_text(encoding="utf-8")
    assert "TU_BINH_PRODUCT_UI_VERSION = '2.7'" in bootstrap
    assert "/static/ui-event-search-v27.js?v=2.7" in bootstrap
    assert bootstrap.index("ui-hour-v24.js") < bootstrap.index("ui-event-search-v27.js")
    index = (ROOT / "public/index.html").read_text(encoding="utf-8")
    assert "ui-event-search-v27.js" not in index


def test_v27_pwa_precaches_event_search_module_and_mirrors_match():
    sw = (ROOT / "public/service-worker.js").read_text(encoding="utf-8")
    assert "tubinh-ui-v2.7" in sw
    assert "/static/ui-event-search-v27.js?v=2.7" in sw
    assert "/static/ui-bootstrap-v26.js?v=2.6" in sw
    assert "/static/ui-bootstrap-v26.js?v=2.7" in sw
    assert (ROOT / "public/static/ui-event-search-v27.js").read_text(encoding="utf-8") == (ROOT / "giao_dien/ui-event-search-v27.js").read_text(encoding="utf-8")
