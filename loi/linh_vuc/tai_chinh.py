"""V2.2 — lớp quyết định lĩnh vực Tiền bạc.

Chỉ dùng dữ kiện đã có từ lớp cá nhân 0.5.0. Không dùng một Tài tinh đơn lẻ
để suy thành có tiền, trúng tiền, tăng thu nhập hay đầu tư sinh lời. Chỉ khi
Cách cục/Hỷ-Kỵ READY, trạng thái cá nhân có hiệu lực và chủ đề Thập Thần thuộc
WEALTH mới cho phép kết luận mức hỗ trợ/thận trọng trong quản lý nguồn lực.

Không numeric score. Không dự đoán lợi nhuận hay kết quả tài chính cụ thể.
"""
from __future__ import annotations

from typing import Any

FINANCE_RULESET_VERSION = "V2.2-FINANCE.1"
FINANCE_POLICY_RULE = "V2-FIN-001"


def _scope_state(raw: dict[str, Any], scope: str) -> dict[str, Any]:
    deep = raw.get("chuyen_sau") or {}
    key = "ngay" if scope == "day" else "thang"
    state = deep.get(key) or {}
    return state.get("danh_gia") or {}


def _insufficient(reason: str, *, scope: str, technical: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ruleset_version": FINANCE_RULESET_VERSION,
        "domain": "finance",
        "scope": scope,
        "state": "INSUFFICIENT",
        "label": "Chưa đủ căn cứ riêng về tiền bạc",
        "title": "Chưa có tín hiệu tiền bạc đủ rõ để kết luận riêng",
        "plain_explanation": reason,
        "recommended_actions": ["Giữ kế hoạch thu chi và quyết định tài chính theo dữ liệu thực tế."],
        "cautions": ["Không suy một Tài tinh hoặc trạng thái chung thành chắc chắn có tiền, tăng thu nhập hay đầu tư có lãi."],
        "confidence_state": "Chưa đủ căn cứ",
        "evidence": [],
        "rule_ids": [FINANCE_POLICY_RULE],
        "source_ids": [],
        "technical": technical or {},
    }


def danh_gia_tai_chinh(raw: dict[str, Any], *, scope: str = "day") -> dict[str, Any]:
    if scope not in {"day", "month"}:
        return _insufficient("V2.2 Tiền bạc hiện chỉ hỗ trợ ngày và tháng.", scope=scope)

    dg = _scope_state(raw, scope)
    if not dg:
        return _insufficient("Chưa lấy được lớp đánh giá cá nhân đã nghiệm thu cho thời điểm này.", scope=scope)

    pstate = dg.get("state") or "DESCRIPTIVE_ONLY"
    theme = dg.get("theme") or {}
    group = theme.get("theme_group")
    natal = dg.get("natal_pattern") or {}

    if pstate == "DESCRIPTIVE_ONLY" or natal.get("status") != "READY":
        return _insufficient(
            "Cách cục/Hỷ-Kỵ chưa đủ rõ để tạo kết luận tiền bạc. App không ép một dự báo tài chính từ dữ kiện mô tả.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "natal_status": natal.get("status")},
        )

    if group != "WEALTH":
        return _insufficient(
            "Chủ đề nổi bật hiện tại không thuộc nhóm Tài. App không dùng Quan, Ấn, Thực/Thương hay Tỷ/Kiếp để tự suy thành kết luận tiền bạc.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "theme": theme},
        )

    impacts = dg.get("branch_impacts") or []
    if pstate == "SUPPORT":
        state = "SUPPORT"
        label = "Hỗ trợ quản lý tiền bạc"
        title = "Thời điểm này thuận hơn cho quản lý nguồn lực và xử lý việc tiền bạc đã có kế hoạch"
        explanation = (
            "Nền Cách cục/Hỷ-Kỵ đang ở trạng thái hỗ trợ và chủ đề nổi bật thuộc nhóm Tài. "
            "Vì vậy app chỉ kết luận mức hỗ trợ cho quản lý nguồn lực, không dự đoán có tiền, tăng thu nhập hay sinh lời."
        )
        actions = ["Ưu tiên rà soát thu chi, ngân sách và các khoản đã có kế hoạch rõ.", "Có thể xử lý việc tài chính thường ngày khi số liệu thực tế phù hợp."]
        cautions = ["Việc mua tài sản, ký hợp đồng hoặc giao dịch quan trọng vẫn phải kiểm theo đúng loại việc; kết luận Tiền bạc không được đảo HARD_BLOCK."]
    elif pstate == "CAUTION":
        state = "CAUTION"
        label = "Nên thận trọng về tiền bạc"
        title = "Nên tăng mức kiểm tra trước quyết định tiền bạc quan trọng"
        explanation = (
            "Chủ đề nổi bật thuộc nhóm Tài nhưng nền Cách cục/Hỷ-Kỵ đang ở trạng thái cần thận trọng. "
            "Điều này chỉ cho biết nên giảm quyết định vội và kiểm số liệu kỹ hơn, không có nghĩa chắc chắn mất tiền."
        )
        actions = ["Giữ các khoản chi thường ngày theo kế hoạch và kiểm lại số liệu trước cam kết mới."]
        cautions = ["Hạn chế quyết định tài chính khó đảo ngược khi chưa kiểm đủ thông tin.", "Không hiểu trạng thái này là dự báo chắc chắn thua lỗ hay mất tiền."]
    else:
        state = "NEUTRAL"
        label = "Tiền bạc tương đối cân bằng"
        title = "Chưa có tín hiệu hỗ trợ hay cản trở tiền bạc đủ mạnh"
        explanation = (
            "Chủ đề hiện tại thuộc nhóm Tài nhưng trạng thái nền chưa nghiêng rõ về hỗ trợ hay thận trọng. "
            "Có thể duy trì kế hoạch tài chính thường ngày và chưa nên suy rộng."
        )
        actions = ["Tiếp tục quản lý thu chi theo kế hoạch hiện có."]
        cautions = ["Quyết định lớn vẫn cần dựa trên số liệu thực tế và kiểm ngày riêng nếu thuộc nhóm việc quan trọng."]

    evidence = [
        {
            "type": "TEN_GOD_THEME",
            "theme_group": group,
            "theme": theme.get("theme"),
            "ten_god": theme.get("ten_god"),
            "ten_god_vi": theme.get("ten_god_vi"),
            "rule_id": theme.get("rule_id"),
            "source_id": theme.get("source_id"),
            "verification_status": theme.get("verification_status"),
        },
        {
            "type": "PERSONAL_TRANSIT",
            "state": pstate,
            "natal_pattern": natal.get("pattern"),
            "natal_status": natal.get("status"),
        },
    ]
    if impacts:
        evidence.append({
            "type": "BRANCH_RELATIONS",
            "count": len(impacts),
            "note": "Quan hệ Chi chỉ là evidence bổ sung, không tự lật kết luận nền và không tự tạo dự báo tiền bạc.",
        })

    rule_ids = sorted(set([FINANCE_POLICY_RULE, *(dg.get("rule_ids") or [])]))
    source_ids = sorted(set(dg.get("source_ids") or []))

    return {
        "ruleset_version": FINANCE_RULESET_VERSION,
        "domain": "finance",
        "scope": scope,
        "state": state,
        "label": label,
        "title": title,
        "plain_explanation": explanation,
        "recommended_actions": actions,
        "cautions": cautions,
        "confidence_state": "Căn cứ vừa",
        "evidence": evidence,
        "rule_ids": rule_ids,
        "source_ids": source_ids,
        "technical": {
            "theme_group": group,
            "personal_state": pstate,
            "branch_impacts": impacts,
            "natal_pattern": natal,
            "policy_rule": FINANCE_POLICY_RULE,
        },
    }
