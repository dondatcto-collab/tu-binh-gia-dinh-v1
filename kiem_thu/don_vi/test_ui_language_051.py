from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_language_layer_is_loaded_in_both_interfaces():
    for path in ("public/index.html", "giao_dien/index.html"):
        text = read(path)
        assert "/static/ui-language-051.js?v=0.5.1" in text


def test_language_layer_uses_plain_vietnamese_statuses():
    text = read("public/static/ui-language-051.js")
    for phrase in (
        "Khá thuận với nền mệnh",
        "Nên thận trọng hơn",
        "Tương đối cân bằng",
        "Không nên chọn cho việc này",
        "Nhấn để xem vì sao",
    ):
        assert phrase in text


def test_missing_domain_copy_does_not_fake_a_conclusion():
    text = read("public/static/ui-language-051.js")
    assert "Tài chính:" in text
    assert "Quan hệ:" in text
    assert "Chưa có tín hiệu riêng nổi bật" in text
    assert "Chọn một việc cụ thể để xem" in text


def test_today_page_is_progressive_disclosure():
    text = read("public/static/ui-language-051.js")
    assert "Hôm nay nên hiểu thế nào?" in text
    assert "Vì sao có kết luận này?" in text
    assert "Thông tin tham khảo thêm" in text
    assert "Xem nguồn & quy tắc" in text


def test_mirror_language_layer_is_identical():
    assert read("public/static/ui-language-051.js") == read("giao_dien/ui-language-051.js")
