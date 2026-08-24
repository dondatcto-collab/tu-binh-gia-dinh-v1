"""API V2 chạy song song với V1 trong giai đoạn alpha.

Không thay đổi engine. Các route này gọi đúng hàm V1 đã nghiệm thu rồi chuẩn hóa
kết quả sang Result Schema V2.
"""
from __future__ import annotations

from fastapi import APIRouter

from cong.api import DayRequest, ProfileRequest, WorkRequest, hom_nay, thang_nay, tim_ngay
from loi.ket_qua.v2 import event_search, personal_result, schema_status

router = APIRouter(prefix="/api/v2", tags=["v2"])


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


@router.post("/tim-ngay")
def v2_tim_ngay(v: WorkRequest):
    raw = tim_ngay(v)
    return event_search(raw)


def register_v2(app) -> None:
    """Đăng ký route V2 vào FastAPI app mà không làm thay đổi route V1."""
    if not any(getattr(r, "path", "").startswith("/api/v2/") for r in app.routes):
        app.include_router(router)
