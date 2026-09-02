from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "giao_dien" / "ui-event-search-v27.js"
PUBLIC = ROOT / "public" / "static" / "ui-event-search-v27.js"
SW_SRC = ROOT / "giao_dien" / "service-worker.js"
SW_PUBLIC = ROOT / "public" / "service-worker.js"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_v1_source_and_public_are_identical():
    assert _text(SRC) == _text(PUBLIC)
    assert _text(SW_SRC) == _text(SW_PUBLIC)


def test_ui_v1_exposes_five_layers_without_recomputing_engine_decision():
    js = _text(SRC)
    for marker in (
        "1</span><b>Kết luận",
        "2</span><b>Vì sao?",
        "3</span><b>Cá nhân Tử Bình",
        "4</span><b>Nguồn & quy tắc",
        "5 · Chi tiết kỹ thuật",
    ):
        assert marker in js
    assert "UI không tự cộng điểm hay tự suy lại kết quả" in js
    assert "HARD_BLOCK → sự kiện → cá nhân" in js


def test_ui_v1_preserves_block_and_caution_policy_in_wording():
    js = _text(SRC)
    assert "không được dùng để đảo ngược điều kiện chặn" in js
    assert "không được cứu ngày đã bị HARD_BLOCK" in js
    assert "matched_yi_tokens" in js
    assert "matched_ji_tokens" in js
    assert "matched_evidence" in js


def test_ui_v1_exposes_source_status_and_traceability():
    js = _text(SRC)
    assert "Đã xác minh" in js
    assert "Tạm dùng / cần đối chiếu thêm" in js
    assert "Đang chờ xác minh" in js
    assert "Rule ID:" in js
    assert "Source ID:" in js
    assert "source_location" in js


def test_ui_v1_does_not_display_numeric_score():
    js = _text(SRC)
    assert "Không hiển thị điểm tổng hợp" in js
    assert "score}/10" not in js
    assert "numeric_score}/10" not in js


def test_ui_v1_bumps_pwa_cache():
    sw = _text(SW_SRC)
    assert "tubinh-ui-v3.0-ui-v1" in sw
    assert "/static/ui-event-search-v27.js?v=2.7" in sw
