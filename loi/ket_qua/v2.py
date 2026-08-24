"""Result Schema V2.

UI V2 chỉ đọc một cấu trúc ổn định. Module này không đổi engine,
không chấm điểm số và không tự suy kết luận lĩnh vực khi rule chưa có.
"""
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "2.0-alpha.2"
NUMERIC_SCORE_STATUS = "LOCKED_OFF"


def _label(raw: str | None) -> str:
    x = (raw or "").strip()
    if "Bị chặn" in x or "HARD_BLOCK" in x:
        return "Bị chặn"
    if x == "Ưu tiên":
        return "Ưu tiên"
    if "Không ưu tiên" in x:
        return "Không ưu tiên"
    if "Có thể cân nhắc" in x or x == "Cân nhắc":
        return "Có thể cân nhắc"
    if "Cần thận trọng" in x or "CAUTION" in x:
        return "Nên thận trọng"
    if "Thuận nền mệnh" in x or "SUPPORT" in x:
        return "Khá thuận"
    if "Trung tính" in x or "Cân bằng" in x:
        return "Cân bằng"
    return "Chưa đủ căn cứ"


def _plain(label: str, scope: str) -> tuple[str, str, list[str], list[str]]:
    if label == "Bị chặn":
        return (
            "Không nên chọn thời điểm này cho việc đang xem",
            "Có điều kiện chặn ở lớp chọn ngày. Tín hiệu thuận ở lớp cá nhân không được dùng để đảo ngược kết quả.",
            ["Ưu tiên xem ngày thay thế nếu việc có thể dời."],
            ["Không dùng giờ để cứu một ngày đã bị chặn."],
        )
    if label == "Ưu tiên":
        return (
            "Đây là lựa chọn nên ưu tiên cho việc đang xem",
            "Lớp sự kiện và lớp cá nhân cùng ủng hộ lựa chọn này trong phạm vi quy tắc đã nghiệm thu.",
            ["Có thể ưu tiên thời điểm này khi các điều kiện thực tế cũng phù hợp."],
            ["Không xem kết quả này là bảo đảm chắc chắn cho kết quả đời sống."],
        )
    if label == "Không ưu tiên":
        return (
            "Không nên ưu tiên thời điểm này",
            "Các yếu tố hiện có không ủng hộ việc chọn thời điểm này so với các lựa chọn khác.",
            ["Ưu tiên so sánh thêm các ngày khác."],
            ["Không cố ép một kết luận thuận khi dữ kiện không ủng hộ."],
        )
    if label == "Có thể cân nhắc":
        return (
            "Có thể thực hiện, nhưng nên kiểm kỹ trước việc quan trọng",
            "Tín hiệu hiện tại không xấu rõ rệt nhưng cũng chưa đủ mạnh để gọi là thuận.",
            ["Có thể tiếp tục nếu điều kiện thực tế thuận lợi."],
            ["Kiểm kỹ các quyết định khó đảo ngược."],
        )
    if label == "Nên thận trọng":
        noun = "Hôm nay" if scope == "day" else "Giai đoạn này"
        return (
            f"{noun} nên chậm lại trước các quyết định quan trọng",
            "Nền cá nhân kém thuận hơn bình thường. Việc thường ngày vẫn có thể làm; việc quan trọng nên kiểm riêng trước khi quyết định. Kết luận chung này chưa đủ căn cứ để nói riêng về tiền bạc hay quan hệ.",
            ["Giữ nhịp công việc và sinh hoạt bình thường.", "Kiểm kỹ thông tin trước quyết định quan trọng."],
            ["Hạn chế quyết định vội khi chưa kiểm đủ thông tin.", "Không suy kết luận chung thành dự đoán riêng về tiền bạc hay quan hệ."],
        )
    if label == "Khá thuận":
        noun = "Hôm nay" if scope == "day" else "Giai đoạn này"
        return (
            f"{noun} nhìn chung khá thuận với bạn",
            "Nền cá nhân được hỗ trợ hơn bình thường. Kết luận chung này chưa đủ căn cứ để nói riêng rằng tiền bạc hay quan hệ đều tốt; việc quan trọng vẫn cần kiểm theo đúng loại việc.",
            ["Tiếp tục các kế hoạch đã chuẩn bị rõ ràng.", "Nếu là việc lớn, chọn đúng loại việc để kiểm riêng."],
            ["Không suy từ trạng thái thuận thành chắc chắn có lợi về tiền bạc hay quan hệ."],
        )
    if label == "Cân bằng":
        return (
            "Thời điểm này tương đối cân bằng",
            "Chưa có tín hiệu đủ mạnh để gọi là thuận hay nghịch. Có thể tiếp tục việc thường ngày; chưa đủ căn cứ để kết luận riêng về tiền bạc hay quan hệ, và việc quan trọng nên kiểm riêng.",
            ["Tiếp tục việc thường ngày như bình thường."],
            ["Không xem trạng thái cân bằng là ngày tốt tuyệt đối."],
        )
    return (
        "Chưa có tín hiệu đủ rõ để kết luận mạnh",
        "Ứng dụng chưa có đủ căn cứ ở lớp hiện tại nên không ép kết luận riêng về tiền bạc, quan hệ hoặc một lĩnh vực đời sống khác.",
        ["Với việc quan trọng, kiểm theo đúng loại việc."],
        ["Không tự suy thành kết luận riêng về tiền bạc, quan hệ hoặc sức khỏe."],
    )


def _confidence(label: str, *, hard_block: bool = False) -> str:
    if hard_block or label in {"Bị chặn", "Ưu tiên"}:
        return "Căn cứ rõ"
    if label == "Chưa đủ căn cứ":
        return "Chưa đủ căn cứ"
    return "Căn cứ vừa"


def personal_result(raw: dict[str, Any], *, scope: str, domain: str = "general") -> dict[str, Any]:
    simple = raw.get("don_gian", raw)
    raw_label = simple.get("tom_tat") or simple.get("label") or ""
    label = _label(raw_label)
    title, explanation, yes, caution = _plain(label, scope)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "personal_period",
        "scope": scope,
        "domain": domain,
        "conclusion": {"state": label.upper().replace(" ", "_"), "label": label, "title": title},
        "plain_explanation": explanation,
        "recommended_actions": yes,
        "cautions": caution,
        "confidence_state": _confidence(label),
        "event_context": None,
        "personal_context": {"source_label": raw_label},
        "evidence": [],
        "rules": [],
        "sources": [],
        "technical": raw.get("chuyen_sau"),
        "numeric_score": None,
        "numeric_score_status": NUMERIC_SCORE_STATUS,
    }


def decade_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Chuẩn hóa Đại vận ở tầng phổ thông, chỉ mô tả vị trí giai đoạn.

    Không tự suy tài chính/công việc/quan hệ từ tên Can Chi của Đại vận.
    """
    dv = raw.get("dai_van") or {}
    pillar = dv.get("tru") or "Chưa xác định"
    year_no = dv.get("nam_thu_may")
    start = dv.get("nam_bat_dau")
    end = dv.get("nam_ket_thuc")
    if isinstance(year_no, int) and year_no > 0:
        stage = "đầu" if year_no <= 3 else ("giữa" if year_no <= 7 else "cuối")
        title = f"Bạn đang ở giai đoạn {stage} của vận 10 năm hiện tại"
        explanation = f"Đây là bối cảnh dài hạn của khoảng {start or '—'}–{end or '—'}. Nó không quyết định từng ngày và chưa đủ căn cứ để kết luận riêng về công việc, tiền bạc hay quan hệ."
    else:
        title = "Đã xác định vận 10 năm hiện tại"
        explanation = "Đại vận là bối cảnh dài hạn. Từng năm, tháng và ngày vẫn cần được xét riêng; app không suy lĩnh vực đời sống chỉ từ tên Đại vận."
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "personal_period",
        "scope": "decade",
        "domain": "general",
        "conclusion": {"state": "DESCRIPTIVE_ONLY", "label": "Bối cảnh dài hạn", "title": title},
        "plain_explanation": explanation,
        "recommended_actions": ["Dùng Đại vận để hiểu bối cảnh dài hạn, rồi xem năm, tháng và ngày cho quyết định cụ thể."],
        "cautions": ["Không hiểu một Đại vận là tốt hoặc xấu tuyệt đối cho cả 10 năm."],
        "confidence_state": "Căn cứ vừa" if pillar != "Chưa xác định" else "Chưa đủ căn cứ",
        "event_context": None,
        "personal_context": {"decade_pillar": pillar, "year_in_decade": year_no, "start_year": start, "end_year": end},
        "evidence": [],
        "rules": [],
        "sources": [],
        "technical": raw,
        "numeric_score": None,
        "numeric_score_status": NUMERIC_SCORE_STATUS,
    }


def event_item(item: dict[str, Any], *, event_code: str) -> dict[str, Any]:
    raw_label = item.get("label") or item.get("decision_state") or ""
    label = _label(raw_label)
    hard_block = bool(item.get("hard_block"))
    if hard_block:
        label = "Bị chặn"
    title, explanation, yes, caution = _plain(label, "event")
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "event_day",
        "scope": "day",
        "domain": "event",
        "date": item.get("ngay"),
        "conclusion": {"state": item.get("decision_state") or label.upper().replace(" ", "_"), "label": label, "title": title},
        "plain_explanation": explanation,
        "recommended_actions": yes,
        "cautions": caution,
        "confidence_state": _confidence(label, hard_block=hard_block),
        "event_context": {"event_code": event_code, "hard_block": hard_block, "event_state": item.get("event_state"), "rank_group": item.get("rank_group")},
        "personal_context": item.get("personal_v1_1") or {},
        "evidence": item.get("reasons") or [],
        "rules": [],
        "sources": [],
        "technical": {"truc": item.get("truc"), "coverage": item.get("coverage"), "mapping_status": item.get("mapping_status")},
        "numeric_score": None,
        "numeric_score_status": NUMERIC_SCORE_STATUS,
    }


def event_search(raw: dict[str, Any]) -> dict[str, Any]:
    event_code = raw.get("viec") or ""
    items = [event_item(x, event_code=event_code) for x in (raw.get("top") or [])]
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "event_search",
        "event_code": event_code,
        "scanned_days": raw.get("so_ngay_da_quet"),
        "ranking_mode": "ORDINAL_HARD_BLOCK_EVENT_PERSONAL",
        "numeric_score": None,
        "numeric_score_status": NUMERIC_SCORE_STATUS,
        "results": items,
        "safety_note": raw.get("canh_bao_an_toan"),
        "technical": {"legacy_status": raw.get("xep_hang_status"), "legacy_note": raw.get("ghi_chu")},
    }


def schema_status() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ALPHA_CORE_FLOWS",
        "numeric_score": NUMERIC_SCORE_STATUS,
        "principles": [
            "Người dùng phổ thông hiểu trước",
            "Không đủ căn cứ thì không kết luận",
            "HARD_BLOCK luôn thắng",
            "Mọi kết luận phải truy ngược được",
            "UI không tự suy quyết định từ dữ liệu kỹ thuật",
        ],
        "implemented_scopes": ["day", "month", "decade", "event_search"],
        "pending_scopes": ["work_domain", "finance_domain", "relationship_domain", "personal_hour"],
    }
