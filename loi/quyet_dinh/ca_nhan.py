"""Lớp quyết định cá nhân hóa V1.1.

Không chấm điểm, không tự suy Dụng/Hỷ/Kỵ. Lớp này chỉ hợp lưu những cấu trúc
Engine đã tính được và đã có rule riêng:
- Thập Thần của Can đang xét đối với Nhật chủ;
- Lục hợp/Lục xung/Lục hại/Hình giữa Chi đang xét và CẢ BỐN trụ gốc;
- bối cảnh Đại vận → Năm → Tháng → Ngày.

Phần dịch sang Công việc/Tài chính/Quan hệ/Việc lớn là PRODUCT_INTERPRETATION,
không phải nguyên văn cổ thư. Mọi kết luận đều giữ technical_facts để truy nguồn.
"""
from __future__ import annotations

from typing import Any

from loi.bat_tu.thap_than import tinh_thap_than
from loi.lich.quy_uoc_can_chi import CAN, CAN_VI, CHI, CHI_VI
from loi.quyet_dinh.v1 import quan_he_chi
from loi.bat_tu.phuong_phap_tu_binh import gate_payload

SRC_PRODUCT = "SRC-PRODUCT-V1-SPEC"

# Nhóm ý nghĩa sản phẩm. Đây là lớp diễn giải, KHÔNG phải cát/hung.
TEN_GOD_THEME = {
    "TY_KIEN": ("Hợp tác và tự chủ", "PEER"),
    "KIEP_TAI": ("Nguồn lực chung và cạnh tranh", "PEER"),
    "THUC_THAN": ("Thực thi, tạo đầu ra và chia sẻ", "OUTPUT"),
    "THUONG_QUAN": ("Biểu đạt, thay đổi cách làm và phản biện", "OUTPUT"),
    "THIEN_TAI": ("Giao dịch, nguồn lực và cơ hội tài chính", "WEALTH"),
    "CHINH_TAI": ("Tài chính, tài sản và quản lý nguồn lực", "WEALTH"),
    "THAT_SAT": ("Áp lực, quyết định và xử lý việc khó", "AUTHORITY"),
    "CHINH_QUAN": ("Trách nhiệm, quy tắc và vị trí công việc", "AUTHORITY"),
    "THIEN_AN": ("Học hỏi, hỗ trợ và xử lý thông tin", "RESOURCE"),
    "CHINH_AN": ("Học hỏi, hồ sơ và nguồn hỗ trợ", "RESOURCE"),
}

POSITION_VI = {
    "nam": "trụ năm", "thang": "trụ tháng", "ngay": "trụ ngày", "gio": "trụ giờ",
}


# 0.3.x từng có bảng NÊN/TRÁNH theo nhóm Thập Thần tại đây.
# 0.4.0 loại bỏ hoàn toàn: Thập Thần chỉ mô tả vai trò, không tự sinh cát/hung.

def _three_factors(theme: dict[str, Any], impacts: list[dict[str, Any]], context: list[dict[str, Any]]) -> list[dict[str, str]]:
    factors = [{
        "type": "TEN_GOD",
        "title": theme["ten_god_vi"],
        "plain": f"Can của giai đoạn tạo chủ đề {theme['theme'].lower()}.",
        "rule_id": theme["rule_id"],
    }]
    # Ưu tiên va chạm/cộng hưởng trực tiếp với trụ gốc.
    ordered = sorted(impacts, key=lambda x: 0 if x["level"] == "CAUTION" else 1)
    for x in ordered[:2]:
        factors.append({
            "type": "BRANCH_RELATION",
            "title": f"Tương tác với {x['position_vi']} gốc",
            "plain": (f"Có điểm dễ va chạm/thay đổi với {x['position_vi']} gốc." if x["level"] == "CAUTION" else f"Có tín hiệu phối hợp trực tiếp với {x['position_vi']} gốc."),
            "rule_id": x["rule_id"],
        })
    if len(factors) < 3:
        for x in reversed(context):
            if x.get("label") and x.get("tru") and x.get("ten_god_vi"):
                factors.append({
                    "type": "CONTEXT",
                    "title": x["label"],
                    "plain": f"{x['label']} {x['tru']} tạo bối cảnh {x['ten_god_vi']}.",
                    "rule_id": "CONTEXT_ONLY",
                })
                if len(factors) >= 3:
                    break
    return factors[:3]



def _theme_for(conn, nhat_chu: str, can: str) -> dict[str, Any]:
    tt = tinh_thap_than(conn, nhat_chu, can)
    title, group = TEN_GOD_THEME.get(tt.ten_god, (tt.ten_god_vi, "OTHER"))
    return {
        "ten_god": tt.ten_god,
        "ten_god_vi": tt.ten_god_vi,
        "theme": title,
        "theme_group": group,
        "rule_id": tt.rule_id,
        "source_id": tt.source_id,
        "verification_status": tt.status,
    }


def _branch_impacts(tu_tru: dict, chi_hien_tai: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pos in ("nam", "thang", "ngay", "gio"):
        tru = tu_tru[pos]
        qh = quan_he_chi(tru.chi, chi_hien_tai)
        if qh.ma == "NONE":
            continue
        out.append({
            "position": pos,
            "position_vi": POSITION_VI[pos],
            "natal_branch": tru.chi,
            "natal_branch_vi": CHI_VI[CHI.index(tru.chi)],
            "current_branch": chi_hien_tai,
            "current_branch_vi": CHI_VI[CHI.index(chi_hien_tai)],
            "relation": qh.ma,
            "relation_vi": qh.nhan,
            "level": qh.muc,
            "rule_id": qh.rule_id,
            "source_id": qh.source_id,
            "technical": qh.mo_ta,
        })
    return out



def phan_tich_ca_nhan(conn, *, tu_tru: dict, nhat_chu: str,
                      can_hien_tai: str, chi_hien_tai: str, scope: str,
                      context: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Đọc cấu trúc một tầng thời gian theo đúng cổng phương pháp Tử Bình.

    Khi Cách cục + hỷ/kỵ mệnh gốc chưa được xác lập, Thập Thần và quan hệ Chi
    chỉ là DỮ LIỆU MÔ TẢ. Hàm không được chuyển chúng thành thuận/nghịch,
    NÊN/TRÁNH hay tài lộc tốt/xấu.
    """
    method = gate_payload()
    theme = _theme_for(conn, nhat_chu, can_hien_tai)
    impacts = _branch_impacts(tu_tru, chi_hien_tai)

    horizon = {"month": "Tháng", "day": "Ngày", "year": "Năm", "decade": "Đại vận", "hour": "Giờ"}.get(scope, "Giai đoạn")
    can_vi = CAN_VI[CAN.index(can_hien_tai)]
    chi_vi = CHI_VI[CHI.index(chi_hien_tai)]

    technical_bits = [f"Can {can_vi} đối với Nhật chủ là {theme['ten_god_vi']}"]
    technical_bits += [x["technical"] for x in impacts]

    # Mô tả, không phán lợi/hại.
    relation_names = [x["relation_vi"] + " với " + x["position_vi"] + " gốc" for x in impacts]
    trigger = f"{horizon} {can_vi} {chi_vi}: Thập Thần của Can là {theme['ten_god_vi']}."
    if relation_names:
        trigger += " Có tương tác Địa Chi: " + ", ".join(relation_names[:4]) + "."
    else:
        trigger += " Chưa thấy quan hệ Địa Chi trực tiếp trong nhóm quy tắc hiện đã cài."

    # Không dùng ngôn ngữ thuận/nghịch ở tầng gia đình khi nền mệnh chưa đủ.
    headline = f"{horizon} có chủ đề {theme['theme'].lower()}; chưa đủ căn cứ để kết luận thuận/nghịch cá nhân"
    descriptive = {
        "RESOURCE": "Tín hiệu Thập Thần liên quan học hỏi, thông tin, hồ sơ hoặc nguồn hỗ trợ đang xuất hiện.",
        "AUTHORITY": "Tín hiệu Thập Thần liên quan trách nhiệm, quy tắc, áp lực hoặc vai trò đang xuất hiện.",
        "WEALTH": "Tín hiệu Thập Thần thuộc nhóm Tài đang xuất hiện; chưa đồng nghĩa đây là thời điểm có lợi về tiền.",
        "OUTPUT": "Tín hiệu Thập Thần liên quan đầu ra, biểu đạt hoặc cách thực hiện đang xuất hiện.",
        "PEER": "Tín hiệu Thập Thần liên quan đồng hành, cạnh tranh hoặc nguồn lực chung đang xuất hiện.",
    }.get(theme["theme_group"], "Có tín hiệu cấu trúc của Can thời gian đối với Nhật chủ.")

    relation_desc = (
        "Có quan hệ trực tiếp giữa Chi thời gian và một hoặc nhiều trụ gốc. Quan hệ này chỉ cho biết kiểu tương tác; "
        "chưa được dùng để gọi là tốt/xấu khi hỷ/kỵ mệnh gốc chưa xác lập."
        if impacts else
        "Chưa có quan hệ trực tiếp nổi bật trong nhóm Lục hợp/Lục xung/Lục hại/Hình đang cài; điều này không có nghĩa là thời điểm trung tính hay tốt."
    )

    interpretation = {
        "interpretation_status": "ZPZQ_DESCRIPTIVE_ONLY_0_4",
        "evidence_scope": "TEN_GOD_AND_BRANCH_RELATION_NOT_DECISION",
        "headline": headline,
        "trigger": trigger,
        "chu_de_chinh": theme["theme"],
        "yeu_to_chinh": _three_factors(theme, impacts, context or []),
        "cong_viec": descriptive,
        "tai_chinh": ("Có tín hiệu nhóm Tài ở Can thời gian, nhưng chưa đủ căn cứ để gọi là thuận/nghịch tài chính."
                      if theme["theme_group"] == "WEALTH" else
                      "Chưa có căn cứ Tử Bình đã hoàn chỉnh để kết luận thuận/nghịch tài chính ở thời điểm này."),
        "quan_he": relation_desc,
        "viec_lon": "Chưa dùng lớp cá nhân để quyết định việc lớn cho tới khi Cách cục và hỷ/kỵ mệnh gốc được khóa; nếu chọn một việc, chỉ xem riêng lớp Hiệp Kỷ hiện có và trạng thái nguồn.",
        "nen_cu_the": [],
        "tranh_cu_the": [],
        "focus": [],
        "khong_suy_dien": method["reason_vi"],
        "technical_trigger": "; ".join(technical_bits),
        "methodology": method,
    }

    # relation giữ để tương thích API, nhưng không được coi level là quyết định.
    if impacts:
        p0 = impacts[0]
        rel_compat = {
            "ma": p0["relation"], "nhan": p0["relation_vi"],
            "muc": "STRUCTURAL_ONLY", "mo_ta": p0["technical"],
            "rule_id": p0["rule_id"], "source_id": p0["source_id"],
        }
    else:
        qh = quan_he_chi(tu_tru["ngay"].chi, chi_hien_tai)
        rel_compat = {**qh.__dict__, "muc": "STRUCTURAL_ONLY"}

    return {
        "scope": scope,
        "state": "DESCRIPTIVE_ONLY",
        "label": "Chưa đủ căn cứ thuận/nghịch cá nhân",
        "relation": rel_compat,
        "confidence": "HIGH" if theme.get("verification_status") == "VERIFIED" else "MEDIUM",
        "basis": headline,
        "recommended": [],
        "caution": [],
        "dien_giai": interpretation,
        "theme": theme,
        "branch_impacts": [{**x, "decision_effect": "UNDETERMINED"} for x in impacts],
        "technical_facts": technical_bits,
        "methodology": method,
        "rule_ids": sorted(set([theme["rule_id"], *method["rule_ids"]] + [x["rule_id"] for x in impacts])),
        "source_ids": sorted(set([theme["source_id"], *method["source_ids"]] + [x["source_id"] for x in impacts])),
    }


def bo_sung_event_ca_nhan(event_state: dict[str, Any], personal: dict[str, Any]) -> dict[str, Any]:
    """Gắn dữ liệu cá nhân vào Hiệp Kỷ nhưng KHÔNG đổi hạng khi nền mệnh chưa đủ.

    Đây là sửa lỗi phương pháp của 0.3.x: Lục hợp/Lục xung/Thập Thần không được
    dùng để nâng/hạ ngày thay cho Cách cục + hỷ/kỵ của mệnh gốc.
    """
    out = dict(event_state)
    method = personal.get("methodology") or gate_payload()
    impacts = personal.get("branch_impacts", [])

    out["personal_methodology"] = method
    out["personal_v1_1"] = {
        "theme": personal.get("theme"),
        "branch_impacts": impacts,
        "headline": personal.get("dien_giai", {}).get("headline"),
        "technical_facts": personal.get("technical_facts", []),
        "interpretation_status": "ZPZQ_DESCRIPTIVE_ONLY_0_4",
        "decision_effect": "NONE_UNTIL_NATAL_USE_READY",
    }

    reasons = list(out.get("reasons", []))
    if impacts:
        reasons.append("Có tương tác Địa Chi với mệnh gốc, nhưng 0.4.0 chỉ ghi nhận cấu trúc; chưa dùng để nâng/hạ ngày vì Cách cục và hỷ/kỵ cá nhân chưa hoàn chỉnh.")
    if personal.get("theme", {}).get("ten_god_vi"):
        reasons.append("Thập Thần Can ngày: " + personal["theme"]["ten_god_vi"] + "; đây là mô tả vai trò, không phải nhãn cát/hung.")
    reasons.append("Lớp cá nhân đang ở DESCRIPTIVE_ONLY; thứ hạng hiện tại chỉ phản ánh lớp Hiệp Kỷ đã có nguồn/coverage tương ứng.")
    out["reasons"] = reasons
    out["rule_ids"] = sorted(set(list(out.get("rule_ids", [])) + list(personal.get("rule_ids", []))))
    out["personal_rank_adjustment"] = 0
    return out

