from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_work_ui_layer_is_loaded_after_core_v2_ui():
    for path in ("public/index.html", "giao_dien/index.html"):
        text = read(path)
        assert "/static/ui-language-051.js?v=0.5.1" in text
        assert "/static/ui-work-v21.js?v=2.1-alpha.1" in text
        assert text.index("ui-language-051.js") < text.index("ui-work-v21.js")


def test_work_ui_consumes_only_canonical_v2_work_endpoint():
    text = read("public/static/ui-work-v21.js")
    assert "/api/v2/cong-viec" in text
    assert "/api/stateless/" not in text
    for field in ("conclusion", "plain_explanation", "recommended_actions", "cautions", "confidence_state", "evidence", "rules", "sources"):
        assert field in text


def test_work_ui_is_plain_language_and_progressively_disclosed():
    text = read("public/static/ui-work-v21.js")
    for phrase in (
        "CÔNG VIỆC HÔM NAY",
        "Vì sao app kết luận về công việc?",
        "Nên làm",
        "Cần lưu ý",
        "Xem dữ liệu kỹ thuật",
        "không suy thăng chức, tăng lương, mất việc",
    ):
        assert phrase in text


def test_work_ui_does_not_redefine_general_v2_decision_logic():
    text = read("public/static/ui-work-v21.js")
    assert "HARD_BLOCK" not in text
    assert "numeric_score" not in text
    assert "theme_group" not in text


def test_work_ui_mirrors_are_identical():
    assert read("public/static/ui-work-v21.js") == read("giao_dien/ui-work-v21.js")
