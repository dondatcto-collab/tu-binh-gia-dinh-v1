"""V2.1 — lớp quyết định lĩnh vực Công việc.

Lớp này KHÔNG tạo một hệ Tử Bình mới. Nó chỉ dùng các dữ kiện đã có và đã
nghiệm thu trong lớp cá nhân 0.5.0: Cách cục/Hỷ-Kỵ, trạng thái hành vận,
Thập Thần và quan hệ Chi. Nếu dữ kiện không đủ hoặc chủ đề hiện tại không trực
tiếp thuộc phạm vi công việc, kết quả phải hạ về INSUFFICIENT.

Không dùng numeric score. Không suy "thăng chức", "tăng lương", "mất việc"
hoặc kết quả đời sống cụ thể từ một Thập Thần đơn lẻ.
"""
from __future__ import annotations

from typing import Any

WORK_RULESET_VERSION = "V2.1-WORK.1"
WORK_POLICY_RULE = "V2-WORK-001"

WORK_GROUPS = {"AUTHORITY", "RESOURCE", "OUTPUT", "PEER"}

GROUP_COPY = {
    "AUTHORITY": {
        "focus": "trách nhiệm, quy tắc và vị trí công việc",
        "support": "Thời điểm này hỗ trợ hơn cho việc xử lý trách nhiệm và công việc có quy tắc rõ",
        "caution": "Nên thận trọng hơn với áp lực, trách nhiệm và quyết định trong công việc",
        "actions": ["Ưu tiên việc có mục tiêu, trách nhiệm và quy trình rõ ràng.", "Kiểm kỹ quyền hạn và cam kết trước khi nhận thêm trách nhiệm."],
    },
    "RESOURCE": {
        "focus": "học hỏi, hồ sơ, chuẩn bị và nguồn hỗ trợ",
        "support": "Thời điểm này thuận hơn cho học hỏi, hồ sơ và chuẩn bị công việc",
        "caution": "Nên kiểm kỹ thông tin, hồ sơ và phần chuẩn bị trước khi tiến công việc",
        "actions": ["Phù hợp hơn cho học, chuẩn bị tài liệu và hoàn thiện hồ sơ.", "Tận dụng nguồn hỗ trợ có sẵn thay vì xử lý vội."],
    },
    "OUTPUT": {
        "focus": "thực thi, trình bày và tạo đầu ra",
        "support": "Thời điểm này thuận hơn cho thực thi, trình bày và tạo đầu ra",
        "caution": "Nên thận trọng hơn khi trình bày, phản biện hoặc thay đổi cách làm",
        "actions": ["Ưu tiên hoàn thành đầu việc cụ thể và tạo đầu ra rõ ràng.", "Chuẩn bị kỹ cách trình bày trước trao đổi quan trọng."],
    },
    "PEER": {
        "focus": "phối hợp, tự chủ và cạnh tranh nguồn lực",
        "support": "Thời điểm này thuận hơn cho phối hợp và chủ động trong công việc",
        "caution": "Nên thận trọng hơn trong phối hợp và phân chia nguồn lực công việc",
        "actions": ["Làm rõ vai trò khi phối hợp với người khác.", "Giữ quyền chủ động ở phần việc thuộc trách nhiệm của mình."],
    },
}


def _scope_state(raw: dict[str, Any], scope: str) -> dict[str, Any]:
    deep = raw.get("chuyen_sau") or {}
    key = "ngay" if scope == "day" else "thang"
    state = deep.get(key) or {}
    return state.get("danh_gia") or {}


def _insufficient(reason: str, *, scope: str, technical: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ruleset_version": WORK_RULESET_VERSION,
        "domain": "work",
        "scope": scope,
        "state": "INSUFFICIENT",
        "label": "Chưa đủ căn cứ riêng về công việc",
        "title": "Chưa có tín hiệu công việc đủ rõ để kết luận riêng",
        "plain_explanation": reason,
        "recommended_actions": ["Tiếp tục công việc thường ngày theo kế hoạch và điều kiện thực tế."],
        "cautions": ["Không suy từ trạng thái chung thành thăng chức, tăng lương, mất việc hoặc kết quả nghề nghiệp cụ thể."],
        "confidence_state": "Chưa đủ căn cứ",
        "evidence": [],
        "rule_ids": [WORK_POLICY_RULE],
        "source_ids": [],
        "technical": technical or {},
    }


def danh_gia_cong_viec(raw: dict[str, Any], *, scope: str = "day") -> dict[str, Any]:
    if scope not in {"day", "month"}:
        return _insufficient("V2.1 Công việc hiện chỉ hỗ trợ ngày và tháng.", scope=scope)

    dg = _scope_state(raw, scope)
    if not dg:
        return _insufficient("Chưa lấy được lớp đánh giá cá nhân đã nghiệm thu cho thời điểm này.", scope=scope)

    pstate = dg.get("state") or "DESCRIPTIVE_ONLY"
    theme = dg.get("theme") or {}
    group = theme.get("theme_group")
    natal = dg.get("natal_pattern") or {}

    if pstate == "DESCRIPTIVE_ONLY" or natal.get("status") != "READY":
        return _insufficient(
            "Cách cục/Hỷ-Kỵ của trường hợp này chưa đủ rõ để tạo kết luận công việc. App chỉ giữ phần mô tả và không ép kết luận.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "natal_status": natal.get("status")},
        )

    if group not in WORK_GROUPS:
        return _insufficient(
            "Chủ đề nổi bật hiện tại không trực tiếp thuộc phạm vi Công việc V2.1. App không dùng tín hiệu Tài hoặc nhóm khác để tự suy thành kết luận nghề nghiệp.",
            scope=scope,
            technical={"personal_state": pstate, "theme_group": group, "theme": theme},
        )

    copy = GROUP_COPY[group]
    impacts = dg.get("branch_impacts") or []
    caution_impacts = [x for x in impacts if x.get("level") == "CAUTION"]
    positive_impacts = [x for x in impacts if x.get("level") == "POSITIVE"]

    if pstate == "SUPPORT":
        state = "SUPPORT"
        label = "Hỗ trợ công việc"
        title = copy["support"]
        explanation = (
            f"Nền Cách cục/Hỷ-Kỵ đang ở trạng thái hỗ trợ và chủ đề Thập Thần trực tiếp liên quan đến {copy['focus']}. "
            "Vì vậy app chỉ kết luận mức hỗ trợ cho cách xử lý công việc, không dự đoán thành tựu nghề nghiệp cụ thể."
        )
        actions = copy["actions"]
        cautions = ["Việc quan trọng như ký hợp đồng, nhậm chức hoặc khai trương vẫn phải kiểm theo đúng loại việc; trạng thái Công việc không được đảo HARD_BLOCK."]
    elif pstate == "CAUTION":
        state = "CAUTION"
        label = "Nên thận trọng trong công việc"
        title = copy["caution"]
        explanation = (
            f"Nền Cách cục/Hỷ-Kỵ đang ở trạng thái cần thận trọng, đồng thời chủ đề nổi bật liên quan đến {copy['focus']}. "
            "Điều này chỉ cho biết nên tăng mức kiểm tra và giảm quyết định vội trong công việc."
        )
        actions = ["Giữ các đầu việc thường ngày và rà soát kỹ trước khi đổi hướng hoặc nhận cam kết mới."]
        cautions = copy["actions"][:1] + ["Không tự hiểu trạng thái này là dấu hiệu chắc chắn mất việc, mâu thuẫn hay thất bại."]
    else:
        state = "NEUTRAL"
        label = "Công việc tương đối cân bằng"
        title = "Công việc hiện chưa có tín hiệu hỗ trợ hay cản trở đủ mạnh"
        explanation = (
            f"Chủ đề hiện tại có liên quan đến {copy['focus']}, nhưng trạng thái nền chưa nghiêng rõ về hỗ trợ hay thận trọng. "
            "Có thể tiếp tục công việc thường ngày và chưa nên suy rộng."
        )
        actions = ["Tiếp tục các đầu việc đang có kế hoạch rõ ràng."]
        cautions = ["Việc khó đảo ngược vẫn nên kiểm riêng theo loại việc và điều kiện thực tế."]

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
    if caution_impacts or positive_impacts:
        evidence.append({
            "type": "BRANCH_RELATIONS",
            "caution_count": len(caution_impacts),
            "positive_count": len(positive_impacts),
            "note": "Quan hệ Chi chỉ là evidence bổ sung, không tự lật kết luận nền.",
        })

    rule_ids = sorted(set([WORK_POLICY_RULE, *(dg.get("rule_ids") or [])]))
    source_ids = sorted(set(dg.get("source_ids") or []))

    return {
        "ruleset_version": WORK_RULESET_VERSION,
        "domain": "work",
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
            "policy_rule": WORK_POLICY_RULE,
        },
    }
