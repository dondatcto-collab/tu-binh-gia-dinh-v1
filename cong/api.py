"""API stateless cho PWA V1.

Hồ sơ cá nhân KHÔNG được lưu trên máy chủ. PWA gửi hồ sơ trong từng yêu cầu,
Engine tính và trả kết quả. SQLite phía server chỉ chứa rule/source/seed công khai.
"""
from __future__ import annotations

import os
import shutil
import logging
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Vercel chỉ cho ghi an toàn vào /tmp. DB này chỉ chứa rule/source, không có hồ sơ thật.
if os.environ.get("VERCEL"):
    os.environ.setdefault("XEMNGAY_DB_PATH", "/tmp/xemngay-rules-fix5.sqlite3")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so.ho_so import HoSo
from loi.hop_luu.hop_luu import hop_luu
from loi.kho_du_lieu.ket_noi import chay_migration, mo_ket_noi
from loi.kho_du_lieu.nap_mam import nap_mam
from loi.lich.quy_uoc_can_chi import CHI, CHI_VI
from loi.nen.phien_ban import DB_MAC_DINH, ENGINE_VERSION, RULESET_VERSION
from loi.van import dong_thoi_gian as dtg
from loi.quyet_dinh.v1 import quan_he_chi, xep_hang

app = FastAPI(title="Tử Bình Gia Đình V1 — Stateless API")

logger = logging.getLogger("tubinh.api")

@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    error_id = uuid.uuid4().hex[:8].upper()
    logger.exception("API error %s %s %s", error_id, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Hệ thống tạm thời chưa xử lý được yêu cầu. Hãy thử lại sau vài giây.",
            "error_code": f"API-{error_id}",
        },
    )


def _bao_dam_kho_rule() -> None:
    """Chuẩn bị kho rule/source; không lưu hồ sơ người dùng.

    Trên Vercel dùng DB seed đã kiểm tra và copy một lần sang /tmp. Không chạy
    migration/seed ở mỗi cold start để giảm thời gian khởi động và tránh tranh chấp
    ghi SQLite giữa các request. Local/dev vẫn migration + seed idempotent.
    """
    seed = Path(__file__).resolve().parents[1] / "du_lieu" / "kho" / "xemngay-rules-seed.sqlite3"
    if os.environ.get("VERCEL"):
        if not seed.exists():
            raise RuntimeError("RULE_DB_SEED_MISSING")
        DB_MAC_DINH.parent.mkdir(parents=True, exist_ok=True)
        if not DB_MAC_DINH.exists() or DB_MAC_DINH.stat().st_size != seed.stat().st_size:
            tmp = DB_MAC_DINH.with_suffix(".tmp")
            shutil.copy2(seed, tmp)
            tmp.replace(DB_MAC_DINH)
        with mo_ket_noi() as c:
            required = {"rule_registry", "rule_versions", "event_types", "sources"}
            found = {r["name"] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not required.issubset(found):
                raise RuntimeError("RULE_DB_SEED_INVALID")
            if c.execute("SELECT COUNT(*) n FROM event_types WHERE status != 'DEPRECATED'").fetchone()["n"] < 13:
                raise RuntimeError("RULE_DB_EVENT_COVERAGE_INVALID")
        return
    with mo_ket_noi() as c:
        chay_migration(c)
        nap_mam(c)


_bao_dam_kho_rule()


def _conn():
    return mo_ket_noi()


class BirthVao(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int


class ProfileVao(BaseModel):
    profile_id: str
    full_name: str
    gender: str
    birth: BirthVao
    birth_place_text: str
    timezone_name: str = "Asia/Ho_Chi_Minh"
    time_certainty: str = "KNOWN"
    note: str | None = None


class ProfileRequest(BaseModel):
    profile: ProfileVao


class DayRequest(ProfileRequest):
    ngay: str | None = None


class WorkRequest(ProfileRequest):
    viec: str
    tu_ngay: str
    den_ngay: str


class CalendarMonthRequest(ProfileRequest):
    year: int
    month: int
    viec: str | None = None


def _ho_so(v: ProfileVao) -> HoSo:
    if not v.full_name.strip():
        raise HTTPException(400, "Chưa nhập tên.")
    if v.gender not in ("NAM", "NU"):
        raise HTTPException(400, "Giới tính phải là NAM hoặc NU.")
    if not v.birth_place_text.strip():
        raise HTTPException(400, "Chưa nhập nơi sinh.")
    try:
        datetime(v.birth.year, v.birth.month, v.birth.day, v.birth.hour, v.birth.minute)
        ZoneInfo(v.timezone_name)
    except (ValueError, ZoneInfoNotFoundError) as e:
        raise HTTPException(400, "Ngày giờ sinh hoặc múi giờ không hợp lệ.") from e
    return HoSo(
        profile_id=v.profile_id,
        full_name=v.full_name.strip(),
        gender=v.gender,
        birth_year=v.birth.year,
        birth_month=v.birth.month,
        birth_day=v.birth.day,
        birth_hour=v.birth.hour,
        birth_minute=v.birth.minute,
        birth_place_text=v.birth_place_text.strip(),
        timezone_name=v.timezone_name,
        time_certainty=v.time_certainty,
        note=v.note,
    )


def _ngay_ho_so(hs: HoSo, raw: str | None) -> date:
    if raw:
        try:
            return date.fromisoformat(raw)
        except ValueError as e:
            raise HTTPException(400, "Ngày không hợp lệ.") from e
    try:
        return datetime.now(ZoneInfo(hs.timezone_name)).date()
    except ZoneInfoNotFoundError as e:
        raise HTTPException(400, f"Múi giờ hồ sơ không hợp lệ: {hs.timezone_name}") from e


GIO_KHOANG = [
    "23:00–01:00","01:00–03:00","03:00–05:00","05:00–07:00",
    "07:00–09:00","09:00–11:00","11:00–13:00","13:00–15:00",
    "15:00–17:00","17:00–19:00","19:00–21:00","21:00–23:00",
]

def _gio_tham_khao(kq):
    natal = kq.base_state["tu_tru"]["ngay"]["chi"]
    out=[]
    for i,ch in enumerate(CHI):
        qh=quan_he_chi(natal,ch)
        nhan = "Phù hợp tham khảo" if qh.muc=="POSITIVE" else ("Nên cân nhắc" if qh.muc=="CAUTION" else "Trung tính")
        out.append({"chi":ch,"chi_vi":CHI_VI[i],"khoang_gio":GIO_KHOANG[i],"nhan":nhan,"relation":qh.ma,"ly_do":qh.mo_ta})
    return out

@app.get("/api/health")
def health():
    return {
        "ok": True,
        "mode": "STATELESS_LOCAL_PROFILE",
        "engine_version": ENGINE_VERSION,
        "ruleset_version": RULESET_VERSION,
        "profile_storage": "DEVICE_ONLY",
    }


@app.get("/api/tinh-trang")
def tinh_trang():
    with _conn() as c:
        def d(sql: str, *a):
            return c.execute(sql, a).fetchone()["n"]
        return {
            "engine_version": ENGINE_VERSION,
            "ruleset_version": RULESET_VERSION,
            "quy_tac_verified": d("SELECT COUNT(*) n FROM rule_versions WHERE status='VERIFIED'"),
            "quy_tac_provisional": d("SELECT COUNT(*) n FROM rule_versions WHERE status='PROVISIONAL'"),
            "quy_tac_conflicted": d("SELECT COUNT(*) n FROM rule_versions WHERE status='CONFLICTED'"),
            "quy_tac_hiep_ky": d("SELECT COUNT(*) n FROM rule_registry WHERE namespace LIKE 'HK-%' AND is_active=1"),
            "quy_tac_quan_he": d("SELECT COUNT(*) n FROM rule_registry WHERE namespace='BT-REL' AND is_active=1"),
            "cham_diem": "ORDINAL_V1_BASIC",
            "profile_storage": "DEVICE_ONLY",
            "canh_bao": (
                "Lõi tính toán và lớp quyết định V1-basic đã chạy. App có thể trả lời nhịp tháng/ngày "
                "và xếp hạng ngày theo lớp 12 Trực của Hiệp Kỷ + quan hệ Địa Chi cá nhân. "
                "Điểm 0-10 và các lớp sâu chưa được tự bịa khi chưa hiệu chỉnh."
            ),
        }


@app.get("/api/loai-viec")
def loai_viec():
    with _conn() as c:
        rows = c.execute("SELECT code, name_vi, status FROM event_types ORDER BY name_vi").fetchall()
    return [
        {"code": r["code"], "ten": r["name_vi"], "muc_ho_tro": "ACTIVE_BASIC" if r["status"] == "ACTIVE" else "NO_RULE"}
        for r in rows if r["status"] != "DEPRECATED"
    ]


@app.post("/api/stateless/toi-dang-o-dau")
def toi_dang_o_dau(v: ProfileRequest):
    hs = _ho_so(v.profile)
    with _conn() as c:
        return dtg.dung(c, hs).to_dict()


@app.post("/api/stateless/thang-nay")
def thang_nay(v: ProfileRequest):
    hs = _ho_so(v.profile)
    with _conn() as c:
        kq = hop_luu(c, hs)
        return {"don_gian": tang_1(kq, scope="month"), "chuyen_sau": tang_2(kq)}


@app.post("/api/stateless/hom-nay")
def hom_nay(v: DayRequest):
    hs = _ho_so(v.profile)
    d = _ngay_ho_so(hs, v.ngay)
    with _conn() as c:
        kq = hop_luu(c, hs, ngay=d)
        return {
            "ngay": d.isoformat(),
            "don_gian": tang_1(kq, scope="day"),
            "chuyen_sau": tang_2(kq),
            "gio_trong_ngay": _gio_tham_khao(kq),
        }


@app.post("/api/stateless/tai-sao")
def tai_sao(v: DayRequest):
    hs = _ho_so(v.profile)
    d = _ngay_ho_so(hs, v.ngay)
    with _conn() as c:
        kq = hop_luu(c, hs, ngay=d)
        return {"chuyen_sau": tang_2(kq), "truy_nguoc": truy_nguoc_day_du(c, kq)}


@app.post("/api/stateless/lich-thang")
def lich_thang(v: CalendarMonthRequest):
    """Trả trạng thái cho từng ngày trong đúng một tháng để PWA tô lịch.

    Không có việc: dùng quan hệ Địa Chi cá nhân ở lớp V1-basic.
    Có việc: dùng kết luận sự kiện (12 Trực Hiệp Kỷ + quan hệ cá nhân).
    """
    hs = _ho_so(v.profile)
    if not 1900 <= v.year <= 2100 or not 1 <= v.month <= 12:
        raise HTTPException(400, "Tháng cần xem không hợp lệ.")
    first = date(v.year, v.month, 1)
    next_month = date(v.year + (1 if v.month == 12 else 0), 1 if v.month == 12 else v.month + 1, 1)
    last = next_month - timedelta(days=1)
    with _conn() as c:
        out = []
        cur = first
        while cur <= last:
            kq = hop_luu(c, hs, ngay=cur, event_code=v.viec or None)
            if v.viec:
                ev = kq.event_state
                label = ev.get("label", kq.label)
                state = ev.get("event_state", "NEUTRAL")
                detail = {
                    "truc": ev.get("truc_vi"),
                    "personal_relation": ev.get("personal_relation", {}),
                    "coverage": ev.get("coverage"),
                }
            else:
                dg = kq.day_state.get("danh_gia", {})
                label = dg.get("label", kq.label)
                state = dg.get("state", "TRUNG_TINH")
                detail = {"personal_relation": dg.get("relation", {})}
            out.append({
                "ngay": cur.isoformat(),
                "label": label,
                "state": state,
                "detail": detail,
            })
            cur += timedelta(days=1)
    return {
        "year": v.year, "month": v.month, "viec": v.viec,
        "scoring_status": "ORDINAL_V1_BASIC",
        "days": out,
    }


@app.post("/api/stateless/tim-ngay")
def tim_ngay(v: WorkRequest):
    hs = _ho_so(v.profile)
    try:
        a, b = date.fromisoformat(v.tu_ngay), date.fromisoformat(v.den_ngay)
    except ValueError as e:
        raise HTTPException(400, "Khoảng ngày không hợp lệ.") from e
    if b < a:
        raise HTTPException(400, "Khoảng ngày không hợp lệ.")
    if (b - a).days > 92:
        raise HTTPException(400, "Khoảng ngày tối đa là ba tháng.")
    with _conn() as c:
        ds=[]
        cur=a
        while cur <= b:
            kq=hop_luu(c,hs,ngay=cur,event_code=v.viec)
            ev=kq.event_state
            ds.append({
                "ngay":cur.isoformat(),
                "tru_ngay":kq.day_state["tru_ngay"],
                "label":ev.get("label",kq.label),
                "rank_group":ev.get("rank_group",9),
                "truc":ev.get("truc_vi"),
                "event_state":ev.get("event_state"),
                "personal_relation":ev.get("personal_relation",{}),
                "reasons":ev.get("reasons",[]),
                "mapping_status":ev.get("mapping_status"),
                "coverage":ev.get("coverage"),
                "event_note":ev.get("event_note"),
                "score":None,
                "scoring_status":"ORDINAL_V1_BASIC",
            })
            cur += timedelta(days=1)
        ranked=xep_hang(ds)
        return {
            "viec":v.viec,
            "so_ngay_da_quet":len(ds),
            "co_xep_hang_duoc_khong":True,
            "xep_hang_status":"V1_BASIC_PARTIAL_COVERAGE",
            "ghi_chu":"Xếp hạng dùng các Trực được nêu trực tiếp trong mục 宜/忌 của Hiệp Kỷ và quan hệ Địa Chi cá nhân. Không dùng điểm 0-10 chưa hiệu chỉnh.",
            "canh_bao_an_toan": ("Chỉ chọn trong các thời điểm bác sĩ/cơ sở y tế đã xác nhận là có thể linh hoạt; không trì hoãn cấp cứu và không thay thế chỉ định chuyên môn." if v.viec == "DIEU_TRI" else None),
            "top":ranked[:3],
            "cac_ngay":ranked,
        }


# Chặn rõ các API hồ sơ cũ để tránh vô tình lưu dữ liệu cá nhân trên server.
@app.api_route("/api/ho-so", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/ho-so/{profile_id}", methods=["GET", "POST", "PUT", "DELETE"])
def ho_so_cu_khong_con_dung(profile_id: str | None = None):
    raise HTTPException(410, "V1 PWA mới lưu hồ sơ trên thiết bị, không lưu trên máy chủ.")
