"""V2.3 — lớp quyết định lĩnh vực Quan hệ.

Phạm vi V2.3 chỉ là quan hệ xã hội/phối hợp thường ngày. Không dùng một Thập
Thần hay một hợp/xung đơn lẻ để suy thành yêu đương, hôn nhân, chia tay, ngoại
tình hoặc kết quả quan hệ cụ thể. Chỉ khi Cách cục/Hỷ-Kỵ READY, trạng thái cá
nhân có hiệu lực và chủ đề Thập Thần thuộc PEER mới cho phép kết luận mức hỗ
trợ/thận trọng trong tương tác và phối hợp.

Quan hệ Chi chỉ là evidence bổ sung, không tự lật kết luận nền. Không numeric score.
"""
from __future__ import annotations

from typing import Any

RELATIONSHIP_RULESET_VERSION = "V2.3-RELATIONSHIP.1"
RELATIONSHIP_POLICY_RULE = "V2-REL-001"


def _scope_state(raw: dict[str, Any], scope: str) -> dict[str, Any]:
    deep = raw.get("chuyen_sau") or {}
    key = "ngay" if scope == "day" else "thang"
    state = deep.get(key) or {}
    return state.get("danh_gia") or {}


def _insufficient(reason: str, *, scope: str, technical: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ruleset_version": RELATIONSHIP_RULESET_VERSION,
        "domain": "relationship",
        "scope": scope,
        "state": "INSUFFICIENT",
        "label": "Chưa đủ căn cứ riêng về quan hệ",
        "title": "Chưa có tín hiệu quan hệ đủ rõ để kết luận riêng",
        "plain_explanation": reason,
        "recommended_actions": ["Duy trì giao tiếp và phối hợp theo tình huống thực tế."],
        "cautions": ["Không suy một Thập Thần, hợp/xung hoặc trạng thái chung thành dự báo tình cảm, hôn nhân hay mâu thuẫn chắc chắn."],
        "confidence_state": "Chưa đủ căn cứ",
        "evidence": [],
        "rule_ids": [RELATIONSHIP_POLICY_RULE],
        "source_ids": [],
        "technical": technical or {},
    }


def danh_gia_quan_he(raw: dict[str, Any], *, scope: str = "day") -> dict[str, Any]:
    if scope not in {"day", "month"}:
        return _insufficient("V2.3 Quan hệ hiện chỉ hỗ trợ ngày và tháng.", scope=scope)

    dg = _scope_state(raw, scope)
    if not dg:
        return _insufficient("Chưa lấy được lớp đánh giá cá nhân đã nghiệm thu cho thời điểm này.", scope=scope)

    pstate = dg.get("state") or "DESCRIPTIVE_ONLY"
    theme = dg.get("theme") or {}
    group = theme.get("theme_group")
    natal = dg.get("natal_pattern") or {}
    impacts = dg.get("branch_impacts") or []

    if pstate == "DESCRIPTIVE_ONLY" or natal.get("status") != "READY":
        return _insufficient(
            "Cách cục/Hỷ-Kỵ chưa đủ rõ để tạo kết luận quan hệ. App giữ phần mô tả và không ép dự báo.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "natal_status": natal.get("status")},
        )

    if group != "PEER":
        return _insufficient(
            "Chủ đề nổi bật hiện tại không thuộc nhóm phối hợp/người ngang vai. App không dùng Quan, Ấn, Tài hay Thực/Thương để tự suy thành kết luận quan hệ.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "theme": theme},
        )

    if pstate == "SUPPORT":
        state = "SUPPORT"
        label = "Hỗ trợ tương tác và phối hợp"
        title = "Thời điểm này thuận hơn cho trao đổi, phối hợp và làm rõ vai trò"
        explanation = (
            "Nền Cách cục/Hỷ-Kỵ đang ở trạng thái hỗ trợ và chủ đề nổi bật thuộc nhóm người ngang vai/phối hợp. "
            "Vì vậy app chỉ kết luận mức hỗ trợ cho giao tiếp và phối hợp thường ngày, không dự đoán tình cảm hay hôn nhân."
        )
        actions = ["Chủ động trao đổi rõ vai trò, kỳ vọng và phần việc của mỗi bên.", "Ưu tiên giao tiếp trực tiếp, rõ ràng khi cần phối hợp."]
        cautions = ["Không hiểu trạng thái này là bảo đảm quan hệ tốt, hòa hợp tình cảm hay kết quả hôn nhân."]
    elif pstate == "CAUTION":
        state = "CAUTION"
        label = "Nên thận trọng trong tương tác"
        title = "Nên chậm lại và làm rõ thông tin trước trao đổi quan trọng"
        explanation = (
            "Chủ đề nổi bật thuộc nhóm phối hợp/người ngang vai nhưng nền Cách cục/Hỷ-Kỵ đang ở trạng thái cần thận trọng. "
            "Điều này chỉ cho biết nên tăng mức rõ ràng và giảm phản ứng vội, không có nghĩa chắc chắn xảy ra mâu thuẫn."
        )
        actions = ["Giữ trao đổi ngắn gọn, xác nhận lại điều đã thống nhất trước quyết định chung."]
        cautions = ["Tránh suy diễn ý người khác khi thông tin chưa rõ.", "Không hiểu trạng thái này là dự báo chắc chắn cãi vã, chia tay hay đổ vỡ."]
    else:
        state = "NEUTRAL"
        label = "Quan hệ tương đối cân bằng"
        title = "Chưa có tín hiệu hỗ trợ hay cản trở quan hệ đủ mạnh"
        explanation = (
            "Chủ đề hiện tại thuộc nhóm phối hợp/người ngang vai nhưng trạng thái nền chưa nghiêng rõ về hỗ trợ hay thận trọng. "
            "Có thể duy trì tương tác bình thường và chưa nên suy rộng."
        )
        actions = ["Duy trì giao tiếp và phối hợp như kế hoạch hiện có."]
        cautions = ["Các quyết định quan hệ quan trọng vẫn phải dựa trên giao tiếp và dữ kiện thực tế."]

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
            "note": "Quan hệ Chi chỉ là evidence bổ sung, không tự lật kết luận nền và không tự tạo dự báo tình cảm/hôn nhân.",
        })

    rule_ids = sorted(set([RELATIONSHIP_POLICY_RULE, *(dg.get("rule_ids") or [])]))
    source_ids = sorted(set(dg.get("source_ids") or []))

    return {
        "ruleset_version": RELATIONSHIP_RULESET_VERSION,
        "domain": "relationship",
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
            "policy_rule": RELATIONSHIP_POLICY_RULE,
            "relationship_scope": "SOCIAL_COLLABORATION_ONLY",
        },
    }
