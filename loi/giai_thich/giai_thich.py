"""Giải thích hai tầng.

LUẬT CỨNG: tầng này CHỈ ĐỌC kết quả hợp lưu. Nó KHÔNG được tự tính,
KHÔNG được thêm luận điểm không có trong Engine, KHÔNG được đoán.

Khi Engine trả UNKNOWN thì lời giải thích phải NÓI RÕ LÀ CHƯA BIẾT,
không được lấp bằng câu chữ mơ hồ nghe như một kết luận.
"""

from __future__ import annotations

from typing import Any

from loi.hop_luu.hop_luu import NOT_CALIBRATED, UNKNOWN, KetQuaHopLuu

NHAN_VI = {
    UNKNOWN: "Chưa đủ căn cứ để chấm",
}


def tang_1(kq: KetQuaHopLuu) -> dict[str, Any]:
    """Tầng cho người bình thường. Câu ngắn, không thuật ngữ."""
    d = kq.to_dict()
    chua_biet = [x["loi_thuong"] for x in d["uncertainties"]]

    if d["score"] is None:
        cau_dau = (
            f"Hệ thống CHƯA thể chấm điểm ngày {d['period']} cho {d['person']}."
        )
        vi_sao = (
            "Lý do: phần đánh giá tốt xấu của hệ thống chưa có đủ sách gốc. "
            "Hệ thống đã tính xong phần lịch pháp và phần cấu trúc lá số, "
            "nhưng chưa có căn cứ để nói ngày này thuận hay nghịch với bạn."
        )
    else:
        cau_dau = f"Ngày {d['period']}: {d['label']}."
        vi_sao = ""

    quan_sat = []
    b = d["base_state"]
    quan_sat.append(
        "Bốn trụ của bạn: "
        + ", ".join(v["vi"] for v in b["tu_tru"].values()) + ".")
    if d["decade_state"].get("tru"):
        dv = d["decade_state"]
        quan_sat.append(
            f"Bạn đang ở giai đoạn mười năm {dv['tru']}, "
            f"năm thứ {dv['nam_thu_may']} trên {dv['tong_so_nam']}, "
            f"từ {dv['nam_bat_dau']} đến {dv['nam_ket_thuc']}.")
    quan_sat.append(
        f"Năm nay là {d['year_state']['tru']['vi']}, "
        f"tháng này là {d['month_state']['tru']['vi']}.")
    if d["day_state"].get("tru_ngay"):
        quan_sat.append(f"Ngày này là {d['day_state']['tru_ngay']}.")

    return {
        "tieu_de": cau_dau,
        "vi_sao_chua_cham_diem": vi_sao,
        "he_thong_biet_gi": quan_sat,
        "he_thong_chua_biet_gi": chua_biet,
        "diem_thuan_loi": [x["mo_ta"] for x in d["positive_factors"]],
        "diem_can_luu_y": [x["mo_ta"] for x in d["negative_factors"]],
        "nen_lam": d["recommended"],
        "can_nhac": d["caution"],
        "khong_uu_tien": d["avoid"],
        "canh_bao_trung_thuc": (
            "Đây KHÔNG phải lời khuyên chắc chắn. Hệ thống chỉ nói được "
            "những gì tra được từ sách gốc, và nói rõ chỗ nào chưa tra được."
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
