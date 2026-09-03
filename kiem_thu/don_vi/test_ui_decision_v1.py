from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "giao_dien" / "ui-event-search-v27.js"
PUBLIC = ROOT / "public" / "static" / "ui-event-search-v27.js"
SW_SRC = ROOT / "giao_dien" / "service-worker.js"
SW_PUBLIC = ROOT / "public" / "service-worker.js"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_source_public_and_pwa_mirrors_are_identical():
    assert _text(SRC) == _text(PUBLIC)
    assert _text(SW_SRC) == _text(SW_PUBLIC)


def test_ui_v12_is_trust_first_and_preserves_engine_authority():
    js = _text(SRC)
    for marker in (
        "TRUST FIRST",
        "LỰA CHỌN #1",
        "So sánh 3 ngày đầu",
        "Riêng với",
        "Giờ tham khảo có căn cứ hiện tại",
        "Căn cứ cổ thư & trạng thái xác minh",
    ):
        assert marker in js
    assert "thứ tự xếp hạng vẫn lấy nguyên từ engine" in js
    assert "UI không tự cộng điểm" in js
    assert "HARD_BLOCK luôn thắng" in js


def test_ui_v12_explains_evidence_in_user_language_without_hiding_traceability():
    js = _text(SRC)
    assert "tokenMeaning" in js
    assert "Đại Hao — tín hiệu hao tán" in js
    assert "Ngũ Phú — tín hiệu thuận liên quan tài lộc" in js
    assert "matched_evidence" in js
    assert "evidence_status" in js
    assert "source_location" in js
    assert "Rule ID:" in js
    assert "Source ID:" in js


def test_ui_v12_is_honest_when_personal_or_hour_data_is_incomplete():
    js = _text(SRC)
    assert "Chưa có căn cứ cá nhân đủ rõ" in js
    assert "không giả vờ cá nhân hóa" in js
    assert "Chưa đủ dữ liệu giờ cá nhân" in js
    assert "Chưa phải “giờ tốt/xấu cá nhân hoàn chỉnh”" in js


def test_ui_v12_has_direct_top3_comparison_but_does_not_recompute_rank():
    js = _text(SRC)
    assert "compareReason" in js
    assert "#1 có" in js
    assert "+${yi(r).length} hỗ trợ" in js
    assert "thứ tự cuối cùng vẫn lấy nguyên từ engine" in js
    assert "numeric_score" not in js


def test_ui_v12_bumps_pwa_cache():
    sw = _text(SW_SRC)
    assert "tubinh-ui-v3.2-trust-first" in sw
    assert "/static/ui-event-search-v27.js?v=2.7" in sw
