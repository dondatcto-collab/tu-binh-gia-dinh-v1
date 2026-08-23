"""API stateless cho PWA V1.

Hồ sơ cá nhân KHÔNG được lưu trên máy chủ. PWA gửi hồ sơ trong từng yêu cầu,
Engine tính và trả kết quả. SQLite phía server chỉ chứa rule/source/seed công khai.
"""
from __future__ import annotations

import os
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Vercel chỉ cho ghi an toàn vào /tmp. DB này chỉ chứa rule/source, không có hồ sơ thật.
if os.environ.get("VERCEL"):
    os.environ.setdefault("XEMNGAY_DB_PATH", "/tmp/xemngay-rules.sqlite3")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so.ho_so import HoSo
from loi.hop_luu.hop_luu import hop_luu
from loi.kho_du_lieu.ket_noi import chay_migration, mo_ket_noi
from loi.kho_du_lieu.nap_mam import nap_mam
from loi.lich.quy_uoc_can_chi import CHI, CHI_VI
from loi.nen.phien_ban import DB_MAC_DINH, ENGINE_VERSION, RULESET_VERSION
from loi.van import dong_thoi_gian as dtg

app = FastAPI(title="Tử Bình Gia Đình V1 — Stateless API")


def _bao_dam_kho_rule() -> None:
    """Dựng kho rule/source idempotent. Không nạp hồ sơ người dùng.

    Trên Vercel, sao chép DB seed công khai sang /tmp để tránh ghi vào filesystem
    chỉ đọc và giảm thời gian cold start.
    """
    seed = Path(__file__).resolve().parents[1] / "du_lieu" / "kho" / "xemngay-rules-seed.sqlite3"
    if os.environ.get("VERCEL") and not DB_MAC_DINH.exists() and seed.exists():
        DB_MAC_DINH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(seed, DB_MAC_DINH)
    with mo_ket_noi() as c:
        chay_migration(c)
        # Seed lại idempotent để bảo đảm tương thích khi source/rule được cập nhật.
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
            "quy_tac_hiep_ky": d("SELECT COUNT(*) n FROM rule_registry WHERE namespace LIKE 'HK-%'"),
            "cham_diem": "NOT_CALIBRATED",
            "profile_storage": "DEVICE_ONLY",
            "canh_bao": (
                "Lõi tính toán đã chạy. Các kết luận thuận/nghịch, xếp hạng hoặc điểm số "
                "chỉ được hiển thị khi nhóm quy tắc quyết định tương ứng đã đủ căn cứ xác minh."
            ),
        }


@app.get("/api/loai-viec")
def loai_viec():
    with _conn() as c:
        rows = c.execute("SELECT code, name_vi, status FROM event_types ORDER BY name_vi").fetchall()
    return [
        {"code": r["code"], "ten": r["name_vi"], "muc_ho_tro": "NO_RULE" if r["status"] != "ACTIVE" else "ACTIVE"}
        for r in rows
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
            "gio_trong_ngay": [
                {"chi": ch, "chi_vi": CHI_VI[i], "danh_gia": "UNKNOWN"}
                for i, ch in enumerate(CHI)
            ],
        }


@app.post("/api/stateless/tai-sao")
def tai_sao(v: DayRequest):
    hs = _ho_so(v.profile)
    d = _ngay_ho_so(hs, v.ngay)
    with _conn() as c:
        kq = hop_luu(c, hs, ngay=d)
        return {"chuyen_sau": tang_2(kq), "truy_nguoc": truy_nguoc_day_du(c, kq)}


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
        ds = []
        cur = a
        while cur <= b:
            kq = hop_luu(c, hs, ngay=cur, event_code=v.viec)
            ds.append({
                "ngay": cur.isoformat(),
                "tru_ngay": kq.day_state["tru_ngay"],
                "quan_he_voi_ban": kq.day_state["quan_he_voi_nhat_chu"],
                "score": kq.score,
                "label": kq.label,
                "scoring_status": kq.scoring_status,
            })
            cur += timedelta(days=1)
        mau = hop_luu(c, hs, ngay=a, event_code=v.viec)
        return {
            "viec": v.viec,
            "so_ngay_da_quet": len(ds),
            "co_xep_hang_duoc_khong": False,
            "ly_do_khong_xep_hang": (
                "Bộ quy tắc chọn ngày theo việc và hệ chấm điểm chưa đủ căn cứ để sử dụng. "
                "Hệ thống đã tính cấu trúc từng ngày nhưng không tự xếp hạng khi chưa được phép kết luận."
            ),
            "cac_ngay": ds,
            "chua_du_can_cu": [x.to_dict() for x in mau.uncertainties],
        }


# Chặn rõ các API hồ sơ cũ để tránh vô tình lưu dữ liệu cá nhân trên server.
@app.api_route("/api/ho-so", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/ho-so/{profile_id}", methods=["GET", "POST", "PUT", "DELETE"])
def ho_so_cu_khong_con_dung(profile_id: str | None = None):
    raise HTTPException(410, "V1 PWA mới lưu hồ sơ trên thiết bị, không lưu trên máy chủ.")
