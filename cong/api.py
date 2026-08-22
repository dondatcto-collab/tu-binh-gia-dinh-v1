"""Cổng nối cho giao diện.

Cổng này KHÔNG tính gì. Nó chỉ gọi Engine và trả nguyên kết quả.
Mọi kết luận đến từ Engine, không đến từ đây.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pathlib import Path
import os
import secrets
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so import ho_so
from loi.ho_so.ho_so import HoSoError
from loi.hop_luu.hop_luu import hop_luu
from loi.kho_du_lieu.ket_noi import mo_ket_noi
from loi.lich.quy_uoc_can_chi import CHI, CHI_VI
from loi.nen.phien_ban import ENGINE_VERSION, GOC_DU_AN, RULESET_VERSION
from loi.van import dong_thoi_gian as dtg

app = FastAPI(title="Xem ngày — bản V1 cho gia đình")
THU_MUC_GIAO_DIEN = GOC_DU_AN / "giao_dien"
app.mount("/static", StaticFiles(directory=THU_MUC_GIAO_DIEN), name="static")

FAMILY_PIN = os.environ.get("FAMILY_PIN", "").strip()

@app.middleware("http")
async def bao_ve_api_bang_pin(request: Request, call_next):
    """Khi deploy Internet, FAMILY_PIN bảo vệ mọi API chứa dữ liệu gia đình.

    Chạy cục bộ không đặt FAMILY_PIN thì không yêu cầu mã.
    """
    if FAMILY_PIN and request.url.path.startswith("/api/"):
        supplied = request.headers.get("X-Family-Pin", "")
        if not secrets.compare_digest(supplied, FAMILY_PIN):
            return JSONResponse(status_code=401, content={"detail": "PIN_REQUIRED"})
    return await call_next(request)


def _conn():
    return mo_ket_noi()


class HoSoVao(BaseModel):
    full_name: str
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    birth_place_text: str
    timezone_name: str = "Asia/Ho_Chi_Minh"
    note: str | None = None


# ---------------------------------------------------------------
# Hồ sơ
# ---------------------------------------------------------------

@app.get("/api/ho-so")
def ds_ho_so():
    with _conn() as c:
        return [h.to_dict() for h in ho_so.danh_sach(c)]


@app.post("/api/ho-so")
def tao_ho_so(v: HoSoVao):
    with _conn() as c:
        try:
            return ho_so.tao(c, **v.model_dump()).to_dict()
        except HoSoError as e:
            raise HTTPException(400, str(e)) from e


@app.put("/api/ho-so/{profile_id}")
def sua_ho_so(profile_id: str, v: HoSoVao):
    with _conn() as c:
        try:
            return ho_so.sua(c, profile_id, **v.model_dump()).to_dict()
        except HoSoError as e:
            raise HTTPException(400, str(e)) from e


@app.delete("/api/ho-so/{profile_id}")
def xoa_ho_so(profile_id: str):
    with _conn() as c:
        try:
            ho_so.xoa(c, profile_id)
        except HoSoError as e:
            raise HTTPException(404, str(e)) from e
    return {"da_xoa": profile_id}


# ---------------------------------------------------------------
# Bốn câu hỏi của sản phẩm
# ---------------------------------------------------------------

@app.get("/api/toi-dang-o-dau/{profile_id}")
def toi_dang_o_dau(profile_id: str):
    with _conn() as c:
        try:
            hs = ho_so.lay(c, profile_id)
        except HoSoError as e:
            raise HTTPException(404, str(e)) from e
        return dtg.dung(c, hs).to_dict()


@app.get("/api/thang-nay/{profile_id}")
def thang_nay(profile_id: str):
    with _conn() as c:
        try:
            hs = ho_so.lay(c, profile_id)
        except HoSoError as e:
            raise HTTPException(404, str(e)) from e
        kq = hop_luu(c, hs)
        return {"don_gian": tang_1(kq), "chuyen_sau": tang_2(kq)}


@app.get("/api/hom-nay/{profile_id}")
def hom_nay(profile_id: str, ngay: str | None = None):
    with _conn() as c:
        try:
            hs = ho_so.lay(c, profile_id)
        except HoSoError as e:
            raise HTTPException(404, str(e)) from e
        if ngay:
            d = date.fromisoformat(ngay)
        else:
            try:
                d = datetime.now(ZoneInfo(hs.timezone_name)).date()
            except ZoneInfoNotFoundError as e:
                raise HTTPException(400, f"Múi giờ hồ sơ không hợp lệ: {hs.timezone_name}") from e
        kq = hop_luu(c, hs, ngay=d)
        return {
            "ngay": d.isoformat(),
            "don_gian": tang_1(kq),
            "chuyen_sau": tang_2(kq),
            "gio_trong_ngay": [
                {"chi": ch, "chi_vi": CHI_VI[i],
                 "danh_gia": "UNKNOWN"} for i, ch in enumerate(CHI)],
        }


@app.get("/api/tim-ngay/{profile_id}")
def tim_ngay(profile_id: str, viec: str, tu_ngay: str, den_ngay: str):
    a, b = date.fromisoformat(tu_ngay), date.fromisoformat(den_ngay)
    if b < a:
        raise HTTPException(400, "Khoảng ngày không hợp lệ.")
    if (b - a).days > 92:
        raise HTTPException(400, "Khoảng ngày tối đa là ba tháng.")
    with _conn() as c:
        hs = ho_so.lay(c, profile_id)
        ds = []
        cur = a
        while cur <= b:
            kq = hop_luu(c, hs, ngay=cur, event_code=viec)
            ds.append({
                "ngay": cur.isoformat(),
                "tru_ngay": kq.day_state["tru_ngay"],
                "quan_he_voi_ban": kq.day_state["quan_he_voi_nhat_chu"],
                "score": kq.score,
                "label": kq.label,
                "scoring_status": kq.scoring_status,
            })
            cur += timedelta(days=1)
        mau = hop_luu(c, hs, ngay=a, event_code=viec)
        return {
            "viec": viec,
            "so_ngay_da_quet": len(ds),
            "co_xep_hang_duoc_khong": False,
            "ly_do_khong_xep_hang":
                "Chưa có quy tắc Hiệp Kỷ nào và chưa có hệ chấm điểm đã hiệu chỉnh. "
                "Hệ thống KHÔNG xếp hạng ngày khi chưa có căn cứ, vì xếp hạng sai "
                "còn tệ hơn không xếp hạng.",
            "cac_ngay": ds,
            "chua_du_can_cu": [x.to_dict() for x in mau.uncertainties],
        }


@app.get("/api/tai-sao/{profile_id}")
def tai_sao(profile_id: str, ngay: str | None = None):
    with _conn() as c:
        try:
            hs = ho_so.lay(c, profile_id)
        except HoSoError as e:
            raise HTTPException(404, str(e)) from e
        if ngay:
            d = date.fromisoformat(ngay)
        else:
            try:
                d = datetime.now(ZoneInfo(hs.timezone_name)).date()
            except ZoneInfoNotFoundError as e:
                raise HTTPException(400, f"Múi giờ hồ sơ không hợp lệ: {hs.timezone_name}") from e
        kq = hop_luu(c, hs, ngay=d)
        return {
            "chuyen_sau": tang_2(kq),
            "truy_nguoc": truy_nguoc_day_du(c, kq),
        }


@app.get("/api/loai-viec")
def loai_viec():
    with _conn() as c:
        rows = c.execute(
            "SELECT code, name_vi, status FROM event_types ORDER BY name_vi").fetchall()
    return [{"code": r["code"], "ten": r["name_vi"],
             "muc_ho_tro": "NO_RULE" if r["status"] != "ACTIVE" else "ACTIVE"}
            for r in rows]


@app.get("/api/tinh-trang")
def tinh_trang():
    with _conn() as c:
        def d(sql, *a):
            return c.execute(sql, a).fetchone()["n"]
        return {
            "engine_version": ENGINE_VERSION,
            "ruleset_version": RULESET_VERSION,
            "quy_tac_verified": d("SELECT COUNT(*) n FROM rule_versions WHERE status='VERIFIED'"),
            "quy_tac_provisional": d("SELECT COUNT(*) n FROM rule_versions WHERE status='PROVISIONAL'"),
            "quy_tac_conflicted": d("SELECT COUNT(*) n FROM rule_versions WHERE status='CONFLICTED'"),
            "quy_tac_hiep_ky": d("SELECT COUNT(*) n FROM rule_registry WHERE namespace LIKE 'HK-%'"),
            "cham_diem": "NOT_CALIBRATED",
            "canh_bao": "Phần đánh giá tốt xấu CHƯA có nguồn. "
                        "Hệ thống chỉ trả lời phần lịch pháp và cấu trúc lá số.",
        }


# ---------------------------------------------------------------
# Giao diện tĩnh
# ---------------------------------------------------------------

@app.get("/manifest.webmanifest")
def manifest_pwa():
    return FileResponse(THU_MUC_GIAO_DIEN / "manifest.webmanifest", media_type="application/manifest+json")

@app.get("/service-worker.js")
def service_worker():
    return FileResponse(THU_MUC_GIAO_DIEN / "service-worker.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})

@app.get("/icon-192.png")
def icon_192():
    return FileResponse(THU_MUC_GIAO_DIEN / "icons" / "icon-192.png", media_type="image/png")

@app.get("/icon-512.png")
def icon_512():
    return FileResponse(THU_MUC_GIAO_DIEN / "icons" / "icon-512.png", media_type="image/png")

@app.get("/")
def trang_chinh():
    return FileResponse(THU_MUC_GIAO_DIEN / "index.html")


@app.get("/huong-dan")
def huong_dan():
    return FileResponse(THU_MUC_GIAO_DIEN / "huong-dan.html")
