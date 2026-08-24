"""API V2 chạy song song với V1.

Không thay đổi engine nền. Các route gọi hàm V1 đã nghiệm thu, sau đó đi qua
lớp domain/Result Schema V2. UI không được tự suy quyết định từ dữ liệu kỹ thuật.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from cong.api import DayRequest, ProfileRequest, WorkRequest, hom_nay, thang_nay, tim_ngay, toi_dang_o_dau
from loi.ket_qua.v2 import decade_result, event_search, personal_result, schema_status, work_result
from loi.linh_vuc.cong_viec import danh_gia_cong_viec

router = APIRouter(prefix="/api/v2", tags=["v2"])


class WorkDomainRequest(ProfileRequest):
    scope: str = "day"
    ngay: str | None = None


@router.get("/schema-status")
def v2_schema_status():
    return schema_status()


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


@router.post("/cong-viec")
def v2_cong_viec(v: WorkDomainRequest):
    """V2.1 Công việc: hỗ trợ scope day/month, không chấm điểm."""
    if v.scope == "day":
        raw = hom_nay(DayRequest(profile=v.profile, ngay=v.ngay))
    elif v.scope == "month":
        raw = thang_nay(ProfileRequest(profile=v.profile))
    else:
        raise HTTPException(status_code=400, detail="Công việc V2.1 hiện chỉ hỗ trợ scope day hoặc month.")
    decision = danh_gia_cong_viec(raw, scope=v.scope)
    out = work_result(decision)
    if v.scope == "day":
        out["date"] = raw.get("ngay")
    return out


@router.post("/tim-ngay")
def v2_tim_ngay(v: WorkRequest):
    raw = tim_ngay(v)
    return event_search(raw)


def register_v2(app) -> None:
    """Đăng ký route V2 vào FastAPI app mà không làm thay đổi route V1."""
    if not any(getattr(r, "path", "").startswith("/api/v2/") for r in app.routes):
        app.include_router(router)
