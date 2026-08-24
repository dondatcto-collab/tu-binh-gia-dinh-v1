"""API V2 chạy song song với V1.

Không thay đổi engine nền. Các route gọi hàm V1 đã nghiệm thu, sau đó đi qua
lớp domain/Result Schema V2. UI không được tự suy quyết định từ dữ liệu kỹ thuật.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from cong.api import DayRequest, ProfileRequest, WorkRequest, hom_nay, thang_nay, tim_ngay, toi_dang_o_dau
from loi.ket_qua.v2 import decade_result, event_search, finance_result, personal_result, relationship_result, schema_status, work_result
from loi.ket_qua.gio_v24 import hour_reference_result, v24_schema_overlay
from loi.linh_vuc.cong_viec import danh_gia_cong_viec
from loi.linh_vuc.quan_he import danh_gia_quan_he
from loi.linh_vuc.tai_chinh import danh_gia_tai_chinh

router = APIRouter(prefix="/api/v2", tags=["v2"])


class DomainRequest(ProfileRequest):
    scope: str = "day"
    ngay: str | None = None


@router.get("/schema-status")
def v2_schema_status():
    return v24_schema_overlay(schema_status())


@router.post("/hom-nay")
def v2_hom_nay(v: DayRequest):
    raw = hom_nay(v)
    out = personal_result(raw, scope="day")
    out["date"] = raw.get("ngay")
    return out


@router.post("/thang-nay")
def v2_thang_nay(v: ProfileRequest):
    raw = thang_nay(v)
    return personal_result(raw, scope="month")


@router.post("/dai-van")
def v2_dai_van(v: ProfileRequest):
    raw = toi_dang_o_dau(v)
    return decade_result(raw)


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
    return out


@router.post("/tai-chinh")
def v2_tai_chinh(v: DomainRequest):
    raw = _domain_raw(v)
    out = finance_result(danh_gia_tai_chinh(raw, scope=v.scope))
    if v.scope == "day": out["date"] = raw.get("ngay")
    return out


@router.post("/quan-he")
def v2_quan_he(v: DomainRequest):
    raw = _domain_raw(v)
    out = relationship_result(danh_gia_quan_he(raw, scope=v.scope))
    if v.scope == "day": out["date"] = raw.get("ngay")
    return out


@router.post("/gio-ca-nhan")
def v2_gio_ca_nhan(v: DayRequest):
    """V2.4: chỉ tham khảo cấu trúc 12 giờ; chưa sinh nhãn tốt/xấu cá nhân."""
    raw = hom_nay(v)
    return hour_reference_result(raw)


@router.post("/tim-ngay")
def v2_tim_ngay(v: WorkRequest):
    raw = tim_ngay(v)
    return event_search(raw)


def register_v2(app) -> None:
    if not any(getattr(r, "path", "").startswith("/api/v2/") for r in app.routes):
        app.include_router(router)
