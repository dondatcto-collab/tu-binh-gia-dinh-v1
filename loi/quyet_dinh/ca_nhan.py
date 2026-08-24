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
from loi.lich.quy_uoc_can_chi import CAN, CAN_VI, CHI, CHI_VI, viet_hoa
from loi.quyet_dinh.v1 import quan_he_chi

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


ACTION_BY_GROUP = {
    "RESOURCE": {
        "nen": [
            "Rà lại hồ sơ, dữ liệu và điều kiện trước khi quyết định.",
            "Xin ý kiến/hỗ trợ ở phần mình còn thiếu thông tin.",
            "Dành thời gian học nhanh hoặc chuẩn bị nền trước khi triển khai."
        ],
        "tranh": [
            "Chốt việc lớn khi thông tin còn thiếu hoặc chỉ dựa vào cảm giác.",
            "Bỏ qua bước kiểm chứng vì nghĩ mình đã hiểu đủ."
        ],
    },
    "AUTHORITY": {
        "nen": [
            "Chốt trách nhiệm, deadline và tiêu chuẩn hoàn thành.",
            "Xử lý việc tồn đọng cần kỷ luật hoặc quyết định dứt khoát.",
            "Làm việc theo checklist, quy trình hoặc văn bản rõ ràng."
        ],
        "tranh": [
            "Nhận thêm nghĩa vụ khi chưa rõ phạm vi trách nhiệm.",
            "Đối đầu trực diện với quy trình/quy định khi chưa có phương án thay thế."
        ],
    },
    "WEALTH": {
        "nen": [
            "Rà dòng tiền, giá, điều khoản và khả năng thu hồi trước giao dịch.",
            "Ưu tiên việc có đầu ra tài chính hoặc nguồn lực đo được.",
            "Chốt con số và giới hạn rủi ro trước khi cam kết."
        ],
        "tranh": [
            "Ra quyết định tiền bạc chỉ vì cơ hội có vẻ hấp dẫn.",
            "Cam kết khoản lớn khi chưa rõ điều kiện thoát hoặc thu hồi."
        ],
    },
    "OUTPUT": {
        "nen": [
            "Hoàn tất sản phẩm, báo cáo hoặc đầu ra cụ thể đang dang dở.",
            "Trình bày, trao đổi, phản biện hoặc thử một cách làm mới có thể kiểm chứng.",
            "Biến ý tưởng thành bước thực hiện có kết quả quan sát được."
        ],
        "tranh": [
            "Tranh luận chỉ để thắng mà không tạo ra kết quả cụ thể.",
            "Mở quá nhiều hướng mới trước khi đóng việc đang làm."
        ],
    },
    "PEER": {
        "nen": [
            "Chốt ai làm gì, quyền quyết định và phần nguồn lực của từng người.",
            "Trao đổi trực tiếp với người cùng vai để giảm hiểu nhầm.",
            "Tách rõ việc chung và phần trách nhiệm cá nhân."
        ],
        "tranh": [
            "Dùng nguồn lực chung mà chưa thống nhất nguyên tắc.",
            "Để cạnh tranh vai trò biến thành xung đột cá nhân."
        ],
    },
}


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


def _actionable(theme_group: str, caution: bool, positive: bool) -> tuple[list[str], list[str]]:
    pack = ACTION_BY_GROUP.get(theme_group, {
        "nen": ["Làm rõ mục tiêu, điều kiện và đầu ra trước khi hành động."],
        "tranh": ["Không quyết định khi điều kiện chính còn mơ hồ."],
    })
    nen = list(pack["nen"][:3])
    tranh = list(pack["tranh"][:2])
    if caution:
        nen.insert(0, "Chuẩn bị phương án B cho phần việc khó đảo ngược hoặc dễ đổi lịch.")
        tranh.insert(0, "Không khóa kế hoạch quá sớm khi còn dấu hiệu va chạm/thay đổi.")
    elif positive:
        nen.insert(0, "Ưu tiên việc cần phối hợp, xác nhận hoặc nối lại đầu mối đang dang dở.")
    return nen[:4], tranh[:3]


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


def _context_line(context: list[dict[str, Any]]) -> str:
    bits = []
    for x in context:
        if not x:
            continue
        label = x.get("label")
        tru = x.get("tru")
        ten_god = x.get("ten_god_vi")
        if label and tru and ten_god:
            bits.append(f"{label} {tru} mang chủ đề {ten_god}")
    return "; ".join(bits)


def _work_text(group: str, caution: bool, positive: bool) -> str:
    base = {
        "RESOURCE": "Nổi bật việc học nhanh, xử lý hồ sơ/thông tin, xin hỗ trợ hoặc củng cố nền tảng trước khi hành động.",
        "AUTHORITY": "Nổi bật trách nhiệm, quy trình, deadline và việc cần quyết định rõ ràng; phù hợp xử lý phần việc có tiêu chuẩn cụ thể.",
        "WEALTH": "Nổi bật giao dịch, nguồn lực, chi phí và kết quả có thể đo được; nên làm rõ con số và điều kiện trước khi chốt.",
        "OUTPUT": "Nổi bật việc tạo đầu ra, trình bày, giao tiếp và thay đổi cách làm; nên biến ý tưởng thành sản phẩm hoặc kết quả cụ thể.",
        "PEER": "Nổi bật phối hợp, phân chia nguồn lực và ranh giới trách nhiệm với người cùng làm; nên chốt ai làm gì ngay từ đầu.",
    }.get(group, "Nên làm rõ mục tiêu, điều kiện và đầu ra cụ thể trước khi hành động.")
    if caution:
        return base + " Đồng thời có va chạm cấu trúc, nên chừa phương án B và tránh khóa kế hoạch quá sớm."
    if positive:
        return base + " Có thêm tín hiệu phối hợp trực tiếp, thuận hơn cho việc cần thống nhất với người khác."
    return base


def _finance_text(group: str, caution: bool) -> str:
    if group == "WEALTH":
        t = "Tài chính/giao dịch là chủ đề trực tiếp của nhịp này: nên rà dòng tiền, giá, điều khoản, thời hạn và khả năng thu hồi trước khi cam kết."
    elif group == "PEER":
        t = "Tiền bạc không phải tín hiệu chính; nếu có hùn vốn, chia chi phí hoặc dùng nguồn lực chung, cần quy định rõ phần của từng người."
    elif group == "AUTHORITY":
        t = "Tiền bạc không phải tín hiệu chính; chú ý các khoản gắn với nghĩa vụ, quy định, hợp đồng hoặc chi phí bắt buộc."
    else:
        t = "Chưa có tín hiệu đủ trực tiếp để gọi đây là nhịp tài lộc; giao dịch lớn nên xét riêng theo đúng loại việc và điều kiện thực tế."
    if caution:
        t += " Có va chạm cấu trúc nên tránh quyết định tài chính chỉ vì áp lực thời gian."
    return t


def _relationship_text(group: str, impacts: list[dict[str, Any]]) -> str:
    pos = [x for x in impacts if x["level"] == "POSITIVE"]
    neg = [x for x in impacts if x["level"] == "CAUTION"]
    if pos and neg:
        return "Quan hệ có tín hiệu đan xen: có điểm dễ phối hợp nhưng cũng có điểm dễ lệch nhịp. Nên tách từng vấn đề, thống nhất việc cụ thể thay vì suy diễn ý nhau."
    if neg:
        return "Có tương tác trực tiếp với cấu trúc gốc theo hướng dễ lệch nhịp hoặc thay đổi kỳ vọng. Nên nói rõ việc, thời hạn và điều cần người kia xác nhận."
    if pos:
        return "Có quan hệ phối hợp trực tiếp với cấu trúc gốc; thuận hơn cho trao đổi, nối lại việc dang dở và thống nhất cách làm."
    if group == "PEER":
        return "Chủ đề người cùng vai nổi bật; nên làm rõ ranh giới trách nhiệm, quyền quyết định và phần nguồn lực dùng chung."
    return "Chưa có tương tác Chi trực tiếp đủ nổi bật để đưa ra cảnh báo hoặc ưu tiên riêng về quan hệ."


def _big_task_text(group: str, caution: bool) -> str:
    if caution:
        return "Không mặc định phải hoãn, nhưng việc khó đảo ngược nên có phương án dự phòng và dùng mục Tìm ngày theo đúng loại việc trước khi chốt."
    if group in {"AUTHORITY", "WEALTH"}:
        return "Có chủ đề phù hợp với việc cần quyết định hoặc cam kết, nhưng thời điểm cuối cùng vẫn phải xét riêng theo đúng loại việc trong mục Tìm ngày."
    return "Nhịp chung không đủ để xác nhận một việc lớn là tốt/xấu; dùng mục Tìm ngày để xét đúng sự kiện trước khi chốt."


def phan_tich_ca_nhan(conn, *, tu_tru: dict, nhat_chu: str,
                      can_hien_tai: str, chi_hien_tai: str, scope: str,
                      context: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Phân tích cá nhân hóa một tầng thời gian mà không suy Dụng/Hỷ/Kỵ."""
    theme = _theme_for(conn, nhat_chu, can_hien_tai)
    impacts = _branch_impacts(tu_tru, chi_hien_tai)
    caution_impacts = [x for x in impacts if x["level"] == "CAUTION"]
    positive_impacts = [x for x in impacts if x["level"] == "POSITIVE"]

    if caution_impacts and positive_impacts:
        label = "Tín hiệu đan xen"
        state = "MIXED"
    elif caution_impacts:
        label = "Có điểm cần lưu ý"
        state = "CAN_NHAC"
    elif positive_impacts:
        label = "Khá thuận"
        state = "THUAN"
    else:
        label = "Chủ đề rõ, chưa có va chạm nổi bật"
        state = "THEME_ONLY"

    horizon = {"month": "Tháng", "day": "Ngày", "year": "Năm", "decade": "Đại vận"}.get(scope, "Giai đoạn")
    impact_plain = []
    for x in impacts[:4]:
        if x["level"] == "CAUTION":
            impact_plain.append(f"{x['relation_vi']} với {x['position_vi']} gốc")
        else:
            impact_plain.append(f"{x['relation_vi']} với {x['position_vi']} gốc")
    if caution_impacts and positive_impacts:
        headline = f"{horizon} nhấn mạnh {theme['theme'].lower()}, đồng thời có cả tín hiệu phối hợp và điểm cần điều chỉnh"
    elif caution_impacts:
        headline = f"{horizon} nhấn mạnh {theme['theme'].lower()}, kèm điểm dễ thay đổi hoặc lệch nhịp"
    elif positive_impacts:
        headline = f"{horizon} nhấn mạnh {theme['theme'].lower()}, kèm tín hiệu phối hợp trực tiếp"
    else:
        headline = f"{horizon} nhấn mạnh {theme['theme'].lower()}"

    can_vi = CAN_VI[CAN.index(can_hien_tai)]
    chi_vi = CHI_VI[CHI.index(chi_hien_tai)]
    technical_bits = [f"Can {can_vi} đối với Nhật chủ là {theme['ten_god_vi']}"]
    technical_bits += [x["technical"] for x in impacts]

    ctx = _context_line(context or [])
    trigger_plain = f"Chủ đề chính của {horizon.lower()} là {theme['theme'].lower()}."
    if impacts:
        trigger_plain += " Đồng thời có " + ", ".join(impact_plain[:2]) + "."
    if ctx:
        trigger_plain += " Bối cảnh phía trên: " + ctx + "."

    nen_cu_the, tranh_cu_the = _actionable(
        theme["theme_group"], bool(caution_impacts), bool(positive_impacts))
    yeu_to_chinh = _three_factors(theme, impacts, context or [])
    interpretation = {
        "interpretation_status": "PRODUCT_INTERPRETATION_V1_2",
        "evidence_scope": "TEN_GOD_PLUS_ALL_NATAL_BRANCH_RELATIONS_PLUS_CONTEXT",
        "headline": headline,
        "trigger": trigger_plain,
        "chu_de_chinh": theme["theme"],
        "yeu_to_chinh": yeu_to_chinh,
        "cong_viec": _work_text(theme["theme_group"], bool(caution_impacts), bool(positive_impacts)),
        "tai_chinh": _finance_text(theme["theme_group"], bool(caution_impacts)),
        "quan_he": _relationship_text(theme["theme_group"], impacts),
        "viec_lon": _big_task_text(theme["theme_group"], bool(caution_impacts)),
        "nen_cu_the": nen_cu_the,
        "tranh_cu_the": tranh_cu_the,
        "focus": [],
        "khong_suy_dien": "Không dùng riêng Thập Thần hoặc một quan hệ Địa Chi để kết luận thành bại, sức khỏe hay tài lộc tuyệt đối; việc lớn vẫn xét theo đúng loại việc.",
        "technical_trigger": "; ".join(technical_bits),
    }
    if theme["theme_group"] == "RESOURCE":
        interpretation["focus"] = ["Củng cố thông tin, hồ sơ và nguồn hỗ trợ", "Học nhanh trước khi chốt việc mới"]
    elif theme["theme_group"] == "AUTHORITY":
        interpretation["focus"] = ["Chốt trách nhiệm, deadline và quy trình", "Xử lý việc khó theo checklist"]
    elif theme["theme_group"] == "WEALTH":
        interpretation["focus"] = ["Rà dòng tiền và điều kiện giao dịch", "Ưu tiên việc có kết quả đo được"]
    elif theme["theme_group"] == "OUTPUT":
        interpretation["focus"] = ["Biến ý tưởng thành đầu ra cụ thể", "Giao tiếp rõ và cải tiến cách làm"]
    else:
        interpretation["focus"] = ["Chốt ranh giới trách nhiệm", "Quản lý nguồn lực dùng chung"]
    if caution_impacts:
        interpretation["focus"].append("Giữ phương án dự phòng cho điểm dễ thay đổi")

    # Giữ field relation để tương thích lớp hợp lưu cũ; ưu tiên tín hiệu caution,
    # sau đó positive, cuối cùng là quan hệ với trụ ngày gốc.
    primary = (caution_impacts or positive_impacts)
    if primary:
        p0 = primary[0]
        rel_compat = {
            "ma": p0["relation"], "nhan": p0["relation_vi"],
            "muc": p0["level"], "mo_ta": p0["technical"],
            "rule_id": p0["rule_id"], "source_id": p0["source_id"],
        }
    else:
        rel_compat = quan_he_chi(tu_tru["ngay"].chi, chi_hien_tai).__dict__

    return {
        "scope": scope,
        "state": state,
        "label": label,
        "relation": rel_compat,
        "confidence": "MEDIUM" if impacts or theme.get("verification_status") == "VERIFIED" else "LOW",
        "basis": headline,
        "recommended": list(interpretation["nen_cu_the"]),
        "caution": list(interpretation["tranh_cu_the"]),
        "dien_giai": interpretation,
        "theme": theme,
        "branch_impacts": impacts,
        "technical_facts": technical_bits,
        "rule_ids": sorted(set([theme["rule_id"]] + [x["rule_id"] for x in impacts])),
        "source_ids": sorted(set([theme["source_id"], SRC_PRODUCT] + [x["source_id"] for x in impacts])),
    }


def bo_sung_event_ca_nhan(event_state: dict[str, Any], personal: dict[str, Any]) -> dict[str, Any]:
    """Bổ sung cá nhân hóa cho kết quả Hiệp Kỷ mà không dùng trọng số số học.

    Hiệp Kỷ vẫn là lớp sự kiện chính. Quan hệ cá nhân chỉ điều chỉnh nhãn/rank
    trong giới hạn an toàn; không thể cứu một Trực đang ở nhóm Kỵ.
    """
    out = dict(event_state)
    impacts = personal.get("branch_impacts", [])
    cautions = [x for x in impacts if x.get("level") == "CAUTION"]
    positives = [x for x in impacts if x.get("level") == "POSITIVE"]
    es = out.get("event_state")
    verified = out.get("mapping_status") == "VERIFIED"

    if es == "JI":
        # HARD BLOCK của lớp sự kiện: cá nhân không đảo ngược.
        out["rank_group"] = 5
        out["label"] = "Không ưu tiên"
    elif es == "YI":
        if not verified:
            out["rank_group"] = max(2, int(out.get("rank_group", 2)))
            out["label"] = "Có thể cân nhắc"
        elif cautions:
            out["rank_group"] = 2
            out["label"] = "Phù hợp nhưng cần cân nhắc cá nhân"
        elif positives:
            out["rank_group"] = 0
            out["label"] = "Ưu tiên"
        else:
            out["rank_group"] = 1
            out["label"] = "Phù hợp"
    else:
        if cautions:
            out["rank_group"] = 4
            out["label"] = "Cân nhắc"
        elif positives:
            out["rank_group"] = 2
            out["label"] = "Có thể cân nhắc"
        else:
            out["rank_group"] = 3
            out["label"] = "Chưa có tín hiệu nổi bật"

    out["personal_v1_1"] = {
        "theme": personal.get("theme"),
        "branch_impacts": impacts,
        "headline": personal.get("dien_giai", {}).get("headline"),
        "technical_facts": personal.get("technical_facts", []),
        "interpretation_status": "PRODUCT_INTERPRETATION_V1_2",
    }
    reasons = list(out.get("reasons", []))
    if cautions:
        reasons.append("Ngày này có va chạm trực tiếp với một hoặc nhiều trụ gốc của người được chọn; lớp cá nhân hạ mức ưu tiên nhưng không thay quy tắc Hiệp Kỷ.")
    elif positives:
        reasons.append("Ngày này có quan hệ phối hợp trực tiếp với ít nhất một trụ gốc; lớp cá nhân dùng tín hiệu này để phá hòa trong cùng lớp sự kiện.")
    if personal.get("theme", {}).get("theme"):
        reasons.append("Chủ đề Thập Thần của Can ngày: " + personal["theme"]["theme"] + ".")
    out["reasons"] = reasons
    out["rule_ids"] = sorted(set(list(out.get("rule_ids", [])) + list(personal.get("rule_ids", []))))
    return out
