from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "giao_dien" / "ui-event-search-v27.js"
PUBLIC = ROOT / "public" / "static" / "ui-event-search-v27.js"
SW_SRC = ROOT / "giao_dien" / "service-worker.js"
SW_PUBLIC = ROOT / "public" / "service-worker.js"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_v11_source_and_public_are_identical():
    assert _text(SRC) == _text(PUBLIC)
    assert _text(SW_SRC) == _text(SW_PUBLIC)


def test_ui_v11_is_decision_first_not_wall_of_text():
    js = _text(SRC)
    assert "3 ngày nên xem trước" in js
    assert "Tất cả ngày đã xét" in js
    assert "compactTopCard" in js
    assert "compactRow" in js
    assert "openDayDetail" in js
    assert "Xem chi tiết ›" in js
    assert "Xem 5 lớp căn cứ" not in js


def test_ui_v11_detail_uses_four_tabs_and_deferred_depth():
    js = _text(SRC)
    for marker in (
        ">Tổng quan</button>",
        ">Cá nhân</button>",
        ">Giờ</button>",
        ">Nguồn</button>",
    ):
        assert marker in js
    assert "u11-sheet" in js
    assert "u11-panel" in js
    assert "@media(max-width:640px)" in js
    assert "height:94vh" in js


def test_ui_v11_preserves_engine_authority_and_block_policy():
    js = _text(SRC)
    assert "UI không tự cộng điểm hay tự suy lại kết quả" in js
    assert "HARD_BLOCK → sự kiện → cá nhân" in js
    assert "không được dùng để đảo ngược điều kiện chặn" in js
    assert "không được cứu ngày đã bị HARD_BLOCK" in js
    assert "matched_yi_tokens" in js
    assert "matched_ji_tokens" in js


def test_ui_v11_keeps_traceability_but_hides_it_until_requested():
    js = _text(SRC)
    assert "Đã xác minh" in js
    assert "Tạm dùng / cần đối chiếu thêm" in js
    assert "Đang chờ xác minh" in js
    assert "Rule ID:" in js
    assert "Source ID:" in js
    assert "source_location" in js
    assert "<details class=\"u11-tech\">" in js


def test_ui_v11_does_not_display_numeric_score():
    js = _text(SRC)
    assert "Không hiển thị điểm tổng hợp" in js
    assert "score}/10" not in js
    assert "numeric_score" not in js


def test_ui_v11_bumps_pwa_cache():
    sw = _text(SW_SRC)
    assert "tubinh-ui-v3.1-ui-v1-1" in sw
    assert "/static/ui-event-search-v27.js?v=2.7" in sw
