from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_language_layer_is_loaded_in_both_interfaces():
    for path in ("public/index.html", "giao_dien/index.html"):
        text = read(path)
        assert "/static/ui-language-051.js?v=0.5.1" in text


def test_plain_language_layer_answers_in_everyday_vietnamese():
    text = read("public/static/ui-language-051.js")
    for phrase in (
        "Hôm nay nên chậm lại trước các quyết định quan trọng",
        "Thời điểm này nhìn chung khá thuận với bạn",
        "Thời điểm này tương đối cân bằng",
        "Gợi ý sử dụng kết quả",
        "Nên làm",
        "Cần thận trọng",
    ):
        assert phrase in text


def test_missing_domain_copy_is_clear_and_does_not_fake_a_conclusion():
    text = read("public/static/ui-language-051.js")
    assert "Chưa có tín hiệu riêng đủ mạnh về tiền bạc" in text
    assert "Chưa có tín hiệu riêng đủ mạnh về quan hệ" in text
    assert "Chọn một việc cụ thể để kiểm ngày phù hợp" in text
    assert "không tự biến thành dự đoán riêng về tiền bạc, quan hệ hay một việc cụ thể" in text


def test_progressive_disclosure_keeps_jargon_in_expert_layer():
    text = read("public/static/ui-language-051.js")
    assert "Vì sao app đánh giá như vậy?" in text
    assert "Vì sao app đánh giá tháng như vậy?" in text
    assert "Xem phương pháp Tử Bình & dữ liệu kỹ thuật" in text
    assert "Xem nguồn & quy tắc" in text
    assert "Thông tin tham khảo thêm" in text


def test_month_first_screen_explains_scope():
    text = read("public/static/ui-language-051.js")
    assert "Đây là tổng quan tháng, không phải khẳng định mọi việc đều thuận hoặc nghịch" in text
    assert "Khi chưa có quy tắc riêng đủ mạnh cho tiền bạc hay quan hệ" in text


def test_calendar_wording_remains_plain_and_consistent():
    text = read("public/static/ui-language-051.js")
    for phrase in ("Khá thuận", "Thận trọng", "Không ưu tiên", "Cân bằng"):
        assert phrase in text


def test_mirror_language_layer_is_identical():
    assert read("public/static/ui-language-051.js") == read("giao_dien/ui-language-051.js")
