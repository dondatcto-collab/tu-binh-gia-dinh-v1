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


def test_ui_v121_is_user_first_and_preserves_engine_authority():
    js = _text(SRC)
    for marker in (
        "UI V1.2.1 TRUST FIRST",
        "LỰA CHỌN ĐẦU TIÊN",
        "Các lựa chọn đầu",
        "Riêng với",
        "Giờ tham khảo có căn cứ hiện tại",
        "Căn cứ cổ thư & trạng thái xác minh",
    ):
        assert marker in js
    assert "Thứ tự #1–#3 lấy nguyên từ engine" in js
    assert "Đây không phải phép cộng điểm" in js
    assert "HARD_BLOCK luôn thắng" in js


def test_ui_v121_uses_real_profile_name_and_plain_personal_language():
    js = _text(SRC)
    assert "p.full_name" in js
    assert "Lá số hiện không làm ngày này tốt hơn cũng không làm xấu đi" in js
    assert "Xem lý do Tử Bình" in js
    assert "không giả vờ cá nhân hóa" in js


def test_ui_v121_explains_rules_by_user_meaning_and_keeps_traceability():
    js = _text(SRC)
    assert "tokenTitle" in js
    assert "thu tiền, nhận tiền, gom tài hoặc nạp tài" in js
    assert "matched_evidence" in js
    assert "evidence_status" in js
    assert "source_location" in js
    assert "Rule ID:" in js
    assert "Source ID:" in js


def test_ui_v121_groups_days_and_does_not_show_plus_minus_score_like_top3():
    js = _text(SRC)
    for marker in ("Nên xem trước", "Có thể cân nhắc", "Không ưu tiên", "Bị chặn", "groupedDays"):
        assert marker in js
    assert "+${yi(r).length} hỗ trợ" not in js
    assert "−${ji(r).length} cần tránh" not in js
    assert "numeric_score" not in js


def test_ui_v121_is_honest_when_hour_data_is_incomplete():
    js = _text(SRC)
    assert "Chưa đủ dữ liệu giờ cá nhân" in js
    assert "Chưa phải “giờ tốt/xấu cá nhân hoàn chỉnh”" in js


def test_ui_v121_bumps_pwa_cache():
    sw = _text(SW_SRC)
    assert "tubinh-ui-v3.2.1-trust-first" in sw
    assert "/static/ui-event-search-v27.js?v=2.7" in sw
