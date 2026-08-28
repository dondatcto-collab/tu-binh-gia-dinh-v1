"""API V2 chạy song song với V1.

V2.5 giữ các flow cá nhân/domain hiện hành và nâng riêng Event Search qua lớp
Hiệp Kỷ mở rộng có kiểm soát. V2.8 bổ sung confidence dựa trên chất lượng
bằng chứng ở biên API; không đổi engine/ranking/decision hierarchy.

V2.9A đưa bối cảnh loại việc + kết luận ngày vào lớp giờ. Lớp này chỉ có quyền
khóa giờ khi ngày HARD_BLOCK hoặc giữ DESCRIPTIVE_ONLY; chưa sinh giờ tốt/xấu.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from cong.api import DayRequest, ProfileRequest, WorkRequest, hom_nay, thang_nay, toi_dang_o_dau
from cong.tim_ngay_v25 import tim_ngay_v25
from loi.ket_qua.v2 import decade_result, finance_result, personal_result, relationship_result, schema_status, work_result
from loi.ket_qua.gio_v24 import hour_reference_result, v24_schema_overlay
from loi.ket_qua.gio_v29 import hour_fusion_gate
from loi.ket_qua.hiep_ky_v25_result import event_search_v25, v25_schema_overlay
from loi.ket_qua.schema_v25 import canonicalize_v25
from loi.ket_qua.confidence_v28 import apply_confidence_v28, v28_schema_overlay
from loi.linh_vuc.cong_viec import danh_gia_cong_viec
from loi.linh_vuc.quan_he import danh_gia_quan_he
from loi.linh_vuc.tai_chinh import danh_gia_tai_chinh

router = APIRouter(prefix="/api/v2", tags=["v2"])


class DomainRequest(ProfileRequest):
    scope: str = "day"
    ngay: str | None = None


class HourDecisionRequest(DayRequest):
    viec: str | None = None


def _public(result: dict, *, time_certainty: str | None = "KNOWN"):
    return apply_confidence_v28(canonicalize_v25(result), time_certainty=time_certainty)


@router.get("/schema-status")
def v2_schema_status():
    return canonicalize_v25(v28_schema_overlay(v25_schema_overlay(v24_schema_overlay(schema_status()))))


@router.post("/hom-nay")
def v2_hom_nay(v: DayRequest):
    raw = hom_nay(v)
    out = personal_result(raw, scope="day")
    out["date"] = raw.get("ngay")
    return _public(out, time_certainty=v.profile.time_certainty)


@router.post("/thang-nay")
def v2_thang_nay(v: ProfileRequest):
    raw = thang_nay(v)
    return _public(personal_result(raw, scope="month"), time_certainty=v.profile.time_certainty)


@router.post("/dai-van")
def v2_dai_van(v: ProfileRequest):
    raw = toi_dang_o_dau(v)
    return _public(decade_result(raw), time_certainty=v.profile.time_certainty)


def _domain_raw(v: DomainRequest):
    if v.scope == "day":
        return hom_nay(DayRequest(profile=v.profile, ngay=v.ngay))
    if v.scope == "month":
        return thang_nay(ProfileRequest(profile=v.profile))
    raise HTTPException(status_code=400, detail="Domain V2 hiện chỉ hỗ trợ scope day hoặc month.")


@router.post("/cong-viec")
def v2_cong_viec(v: DomainRequest):
    raw = _domain_raw(v)
    out = work_result(danh_gia_cong_viec(raw, scope=v.scope))
    if v.scope == "day": out["date"] = raw.get("ngay")
    return _public(out, time_certainty=v.profile.time_certainty)


@router.post("/tai-chinh")
def v2_tai_chinh(v: DomainRequest):
    raw = _domain_raw(v)
    out = finance_result(danh_gia_tai_chinh(raw, scope=v.scope))
    if v.scope == "day": out["date"] = raw.get("ngay")
    return _public(out, time_certainty=v.profile.time_certainty)


@router.post("/quan-he")
def v2_quan_he(v: DomainRequest):
    raw = _domain_raw(v)
    out = relationship_result(danh_gia_quan_he(raw, scope=v.scope))
    if v.scope == "day": out["date"] = raw.get("ngay")
    return _public(out, time_certainty=v.profile.time_certainty)


@router.post("/gio-ca-nhan")
def v2_gio_ca_nhan(v: HourDecisionRequest):
    """V2.9A: giờ có cổng ngày/sự kiện; chưa phát sinh nhãn giờ tốt/xấu."""
    day_req = DayRequest(profile=v.profile, ngay=v.ngay)
    raw = hom_nay(day_req)
    ref = hour_reference_result(raw)

    if not v.viec:
        return _public(hour_fusion_gate(ref), time_certainty=v.profile.time_certainty)

    event_req = WorkRequest(
        profile=v.profile,
        viec=v.viec,
        tu_ngay=raw.get("ngay"),
        den_ngay=raw.get("ngay"),
    )
    event_raw = tim_ngay_v25(event_req)
    event_search = _public(event_search_v25(event_raw), time_certainty=v.profile.time_certainty)
    event_day = ((event_search.get("all_results") or event_search.get("results") or [None])[0])
    if not event_day:
        raise HTTPException(status_code=500, detail="Không dựng được kết luận ngày để hợp lưu giờ.")

    fused = hour_fusion_gate(ref, event_code=v.viec, event_day=event_day)
    return _public(fused, time_certainty=v.profile.time_certainty)


@router.post("/tim-ngay")
def v2_tim_ngay(v: WorkRequest):
    raw = tim_ngay_v25(v)
    return _public(event_search_v25(raw), time_certainty=v.profile.time_certainty)


def register_v2(app) -> None:
    if not any(getattr(r, "path", "").startswith("/api/v2/") for r in app.routes):
        app.include_router(router)
