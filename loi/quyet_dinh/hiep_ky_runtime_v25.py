"""Runtime Hiệp Kỷ mở rộng có kiểm soát.

V3.0E11 mở 五富 theo Chi tháng + Chi ngày; không phụ thuộc Can ngày.
HARD_BLOCK > EVENT > PERSONAL giữ nguyên; JI thắng YI; không dùng điểm số.
"""
from __future__ import annotations

from typing import Any

from loi.lich.quy_uoc_can_chi import CAN
from loi.quyet_dinh.hiep_ky_day_branch_v30e8 import active_day_branch_tokens
from loi.quyet_dinh.hiep_ky_day_pillar_v30e5 import active_day_pillar_tokens
from loi.quyet_dinh.hiep_ky_evidence_v25 import evidence_for_event
from loi.quyet_dinh.hiep_ky_giai_than_v30e10 import active_giai_than_tokens
from loi.quyet_dinh.hiep_ky_month_day_branch_v30e9 import active_month_day_branch_tokens
from loi.quyet_dinh.hiep_ky_month_v25 import active_month_tokens
from loi.quyet_dinh.hiep_ky_policy_v25 import resolve_conflict
from loi.quyet_dinh.hiep_ky_season_branch_v30e7 import active_season_branch_tokens
from loi.quyet_dinh.hiep_ky_season_day_pillar_v30e6 import active_season_day_pillar_tokens
from loi.quyet_dinh.hiep_ky_season_stem_v30e4 import active_season_stem_tokens
from loi.quyet_dinh.hiep_ky_stem_v30e import active_stem_tokens
from loi.quyet_dinh.hiep_ky_wu_fu_v30e11 import active_wu_fu_tokens

COVERAGE = "V3_0E11_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_3_PLUS_SEASON_STEM_1_PLUS_DAY_PILLAR_1_PLUS_SEASON_DAY_PILLAR_1_PLUS_SEASON_BRANCH_1_PLUS_DAY_BRANCH_1_PLUS_MONTH_DAY_BRANCH_1_PLUS_PAIRED_MONTH_DAY_BRANCH_1_PLUS_QUARTERED_MONTH_DAY_BRANCH_1"
ACTIVE_EXTRA_TOKENS = frozenset({"月建","月破","三合","六合","月害","月刑","劫煞","災煞","月煞","月厭","時徳","月徳","月徳合","月恩","四相","天願","天赦","天喜","五合","天醫","解神","五富"})


def _personal_signal(personal: dict[str, Any]) -> str:
    state = personal.get("state")
    if state == "SUPPORT": return "FAVORABLE"
    if state == "CAUTION": return "CAUTION"
    if state == "DESCRIPTIVE_ONLY": return "UNKNOWN"
    return "NEUTRAL"


def _rank(result: dict[str, Any]) -> int:
    if result["state"] == "BLOCKED": return 9
    if result["label"] == "Ưu tiên": return 1
    if result["label"] == "Có thể cân nhắc": return 2
    if result["label"] == "Không ưu tiên": return 4
    if result["state"] == "INSUFFICIENT": return 5
    return 3


def _effective_day_stem(personal: dict[str, Any], explicit_stem: str | None) -> str | None:
    if explicit_stem in CAN:
        return explicit_stem
    current_stem = personal.get("current_stem")
    return current_stem if current_stem in CAN else None


def evaluate_event_v25(base_event: dict[str, Any], personal: dict[str, Any], *, chi_thang: str, chi_ngay: str, can_ngay: str | None = None) -> dict[str, Any]:
    out = dict(base_event)
    event_code = out.get("event_code")
    active = set(active_month_tokens(chi_thang, chi_ngay))
    active.update(active_season_branch_tokens(chi_thang, chi_ngay))
    active.update(active_day_branch_tokens(chi_ngay))
    active.update(active_month_day_branch_tokens(chi_thang, chi_ngay))
    active.update(active_giai_than_tokens(chi_thang, chi_ngay))
    active.update(active_wu_fu_tokens(chi_thang, chi_ngay))
    effective_can_ngay = _effective_day_stem(personal, can_ngay)
    if effective_can_ngay is not None:
        active.update(active_stem_tokens(chi_thang, effective_can_ngay))
        active.update(active_season_stem_tokens(chi_thang, effective_can_ngay))
        active.update(active_day_pillar_tokens(chi_thang, effective_can_ngay, chi_ngay))
        active.update(active_season_day_pillar_tokens(chi_thang, effective_can_ngay, chi_ngay))

    evidence = tuple(evidence_for_event(event_code)) if event_code else ()
    matched = [x for x in evidence if x.token in active and x.token in ACTIVE_EXTRA_TOKENS]
    yi_hits = [x for x in matched if x.polarity == "YI"]
    ji_hits = [x for x in matched if x.polarity == "JI"]

    base_state = out.get("event_state", "NEUTRAL")
    hard_block = base_state == "JI"
    if hard_block:
        event_signal = "HARD_BLOCK"
    elif ji_hits:
        event_signal = "CAUTION"
    elif base_state == "YI" or yi_hits:
        event_signal = "FAVORABLE"
    else:
        event_signal = "NEUTRAL"

    decision = resolve_conflict(hard_block=hard_block,event_state=event_signal,personal_state=_personal_signal(personal))
    if out.get("mapping_status") == "PROVISIONAL" and decision["label"] == "Ưu tiên":
        decision = {**decision, "state":"CONSIDER", "label":"Có thể cân nhắc", "authority":"EVENT_PROVISIONAL"}

    reasons = list(out.get("reasons") or [])
    if yi_hits:
        reasons.append("Hiệp Kỷ ghi nhận thêm tín hiệu phù hợp: " + ", ".join(x.token for x in yi_hits) + ".")
    if ji_hits:
        reasons.append("Hiệp Kỷ ghi nhận tín hiệu cần thận trọng: " + ", ".join(x.token for x in ji_hits) + "; lớp này chưa tự tạo HARD_BLOCK.")
    reasons.append("Phân xử theo thứ bậc HARD_BLOCK > sự kiện > cá nhân; không cộng/trừ điểm.")

    personal_context = {
        "current_stem": personal.get("current_stem"),
        "current_branch": personal.get("current_branch"),
        "theme": personal.get("theme"),
        "branch_impacts": personal.get("branch_impacts", []),
        "headline": personal.get("dien_giai", {}).get("headline"),
        "technical_facts": personal.get("technical_facts", []),
        "interpretation_status": "ZPZQ_PERSONAL_0_5",
        "decision_effect": personal.get("state", "DESCRIPTIVE_ONLY"),
    }
    rule_ids = sorted(set(list(out.get("rule_ids") or []) + list(personal.get("rule_ids") or []) + [x.rule_id for x in matched]))
    src = set(personal.get("source_ids") or [])
    if out.get("source_id"):
        src.add(out["source_id"])
    src.update(x.source_id for x in matched)

    return {
        **out,
        "event_state_v1": base_state,
        "event_state": "JI" if hard_block else ("YI" if event_signal == "FAVORABLE" else ("CAUTION" if event_signal == "CAUTION" else "NEUTRAL")),
        "event_signal_v25": event_signal,
        "active_hiep_ky_tokens": sorted(active),
        "matched_yi_tokens": [x.token for x in yi_hits],
        "matched_ji_tokens": [x.token for x in ji_hits],
        "matched_evidence": [{"rule_id":x.rule_id,"token":x.token,"polarity":x.polarity,"source_id":x.source_id,"source_location":x.source_location,"evidence_status":x.evidence_status,"decision_status":"ACTIVE"} for x in matched],
        "decision_state": decision["state"],"label": decision["label"],"decision_authority": decision["authority"],
        "hard_block": hard_block,"rank_group": _rank(decision),"personal_v1_1": personal_context,"personal_methodology": personal.get("methodology"),
        "reasons": reasons,"rule_ids": rule_ids,"source_ids": sorted(src),
        "coverage": COVERAGE,"hiep_ky_extension": "V3_0E11_WU_FU",
        "numeric_score": None,"score": None,"numeric_score_status": "LOCKED_OFF","scoring_status": "NO_NUMERIC_SCORE",
    }
