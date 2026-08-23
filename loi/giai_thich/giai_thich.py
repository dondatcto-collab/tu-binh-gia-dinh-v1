"""Giải thích hai tầng.

LUẬT CỨNG: tầng này CHỈ ĐỌC kết quả hợp lưu. Nó KHÔNG được tự tính,
KHÔNG được thêm luận điểm không có trong Engine, KHÔNG được đoán.

Tầng 1 dùng lời thường cho gia đình. Tầng 2 giữ thuật ngữ và truy nguồn.
Một kết quả UNKNOWN phải được trình bày là "chưa đủ căn cứ để kết luận",
không được mô tả chung chung là "Engine chưa hoàn thiện".
"""

from __future__ import annotations

from typing import Any

from loi.hop_luu.hop_luu import UNKNOWN, KetQuaHopLuu

NHAN_VI = {
    UNKNOWN: "Chưa đủ căn cứ để kết luận",
}


def _noi_dung_chua_du_can_cu(scope: str) -> list[str]:
    """Các câu tầng 1 theo đúng câu hỏi của màn hình, không lộ thuật ngữ."""
    if scope == "month":
        return [
            "Xu hướng tổng thể của tháng đang nghiêng thuận hay nghịch với bạn",
            "Lĩnh vực nào trong tháng nên ưu tiên hoặc nên thận trọng",
            "Việc lớn trong tháng nên chủ động hay nên chờ thêm",
            "Mức đánh giá tổng hợp của tháng",
        ]
    if scope == "day":
        return [
            "Ngày này thuận hay nghịch với bạn ở mức nào",
            "Ngày này có va chạm đáng chú ý với cấu trúc sinh của bạn hay không",
            "Việc nào trong ngày nên ưu tiên, cân nhắc hoặc không ưu tiên",
            "Mức đánh giá tổng hợp của ngày",
        ]
    return [
        "Mức thuận/nghịch tổng hợp của giai đoạn hiện tại",
        "Điều nên ưu tiên và điều nên thận trọng",
    ]


def tang_1(kq: KetQuaHopLuu, scope: str = "day") -> dict[str, Any]:
    """Tầng cho người bình thường: ngắn, đúng phạm vi, không thuật ngữ."""
    d = kq.to_dict()

    if d["score"] is None:
        if scope == "month":
            cau_dau = f"Tháng hiện tại của {d['person']}: chưa đủ căn cứ để chấm mức thuận/nghịch."
            doi_tuong = "tháng này"
        elif scope == "day":
            cau_dau = f"Ngày {d['period']} của {d['person']}: chưa đủ căn cứ để chấm mức thuận/nghịch."
            doi_tuong = "ngày này"
        else:
            cau_dau = "Chưa đủ căn cứ để chấm mức thuận/nghịch."
            doi_tuong = "giai đoạn này"
        vi_sao = (
            "Lõi tính toán đã xác định lịch pháp, cấu trúc sinh và các tầng thời gian liên quan. "
            f"Phần kết luận {doi_tuong} chưa được phép chấm khi các quy tắc quyết định cần thiết "
            "chưa đạt mức xác minh để sử dụng."
        )
    else:
        cau_dau = f"{d['period']}: {d['label']}."
        vi_sao = ""

    quan_sat: list[str] = []
    b = d["base_state"]
    quan_sat.append(
        "Bốn trụ của bạn: " + ", ".join(v["vi"] for v in b["tu_tru"].values()) + "."
    )
    if d["decade_state"].get("tru"):
        dv = d["decade_state"]
        quan_sat.append(
            f"Bạn đang ở giai đoạn mười năm {dv['tru']}, "
            f"năm thứ {dv['nam_thu_may']} trên {dv['tong_so_nam']}, "
            f"từ {dv['nam_bat_dau']} đến {dv['nam_ket_thuc']}."
        )
    quan_sat.append(
        f"Năm hiện tại là {d['year_state']['tru']['vi']}, "
        f"tháng hiện tại là {d['month_state']['tru']['vi']}."
    )
    if scope == "day" and d["day_state"].get("tru_ngay"):
        quan_sat.append(f"Ngày đang xem là {d['day_state']['tru_ngay']}.")

    return {
        "tieu_de": cau_dau,
        "vi_sao_chua_cham_diem": vi_sao,
        "he_thong_biet_gi": quan_sat,
        "he_thong_chua_biet_gi": _noi_dung_chua_du_can_cu(scope),
        "diem_thuan_loi": [x["mo_ta"] for x in d["positive_factors"]],
        "diem_can_luu_y": [x["mo_ta"] for x in d["negative_factors"]],
        "nen_lam": d["recommended"],
        "can_nhac": d["caution"],
        "khong_uu_tien": d["avoid"],
        "canh_bao_trung_thuc": (
            "Kết luận chỉ được hiển thị khi có đủ quy tắc và trạng thái xác minh cần thiết. "
            "Phần chưa đủ căn cứ được giữ ở trạng thái chưa kết luận."
        ),
    }


def tang_2(kq: KetQuaHopLuu) -> dict[str, Any]:
    """Tầng chuyên sâu. Truy được từ kết luận về tới nguồn."""
    d = kq.to_dict()
    return {
        "menh": d["base_state"],
        "dai_van": d["decade_state"],
        "nam": d["year_state"],
        "thang": d["month_state"],
        "ngay": d["day_state"],
        "gio": d["hour_state"],
        "hiep_ky": d["event_state"],
        "than_sat": {"status": UNKNOWN, "ly_do": "Nhóm SS chưa có quy tắc nào."},
        "hop_luu": {
            "score": d["score"],
            "label": d["label"],
            "confidence": d["confidence"],
            "scoring_status": d["scoring_status"],
        },
        "yeu_to": {
            "positive": d["positive_factors"],
            "negative": d["negative_factors"],
            "conflicts": d["conflicts"],
        },
        "chua_du_can_cu": d["uncertainties"],
        "rule_trace": d["rule_trace"],
        "source_trace": d["source_trace"],
    }


def truy_nguoc_day_du(conn, kq: KetQuaHopLuu) -> list[dict[str, Any]]:
    """Result → Rule → Rule Version → Source → Passage → Verification status."""
    chuoi = []
    for rid in sorted(set(kq.rule_trace)):
        rows = conn.execute(
            """SELECT r.rule_id, r.name_vi, rv.version, rv.status, rv.confidence,
                      s.source_id, s.title, s.edition_certainty,
                      s.independence_group, rvs.source_level, rvs.source_location,
                      p.passage_id, p.original_text
                 FROM rule_registry r
                 JOIN rule_versions rv ON rv.rule_id = r.rule_id
            LEFT JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
            LEFT JOIN sources s ON s.source_id = rvs.source_id
            LEFT JOIN rule_version_passages rvp ON rvp.rule_version_id = rv.rule_version_id
            LEFT JOIN source_passages p ON p.passage_id = rvp.passage_id
                WHERE r.rule_id = ? AND (rvs.source_level = 'PRIMARY' OR rvs.source_level IS NULL)
             ORDER BY rv.version DESC LIMIT 1""", (rid,)).fetchall()
        for r in rows:
            chuoi.append({
                "rule_id": r["rule_id"], "name_vi": r["name_vi"],
                "rule_version": f"{r['rule_id']}@{r['version']}",
                "verification_status": r["status"], "confidence": r["confidence"],
                "source_id": r["source_id"], "source_title": r["title"],
                "edition_certainty": r["edition_certainty"],
                "independence_group": r["independence_group"],
                "source_location": r["source_location"],
                "passage_id": r["passage_id"],
                "passage_excerpt": (r["original_text"] or "")[:80] or None,
            })
    return chuoi
