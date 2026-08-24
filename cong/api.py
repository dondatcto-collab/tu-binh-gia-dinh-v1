"""API stateless cho PWA V1 release 0.5.0.

Hồ sơ cá nhân không lưu trên máy chủ. PWA gửi hồ sơ trong từng yêu cầu;
SQLite phía server chỉ chứa rule/source/seed công khai.
"""
from __future__ import annotations

import os, shutil, logging, uuid, sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if os.environ.get("VERCEL"):
    os.environ.setdefault("XEMNGAY_DB_PATH", "/tmp/xemngay-rules-050.sqlite3")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from loi.giai_thich.giai_thich import tang_1, tang_2, truy_nguoc_day_du
from loi.ho_so.ho_so import HoSo
from loi.hop_luu.hop_luu import hop_luu
from loi.kho_du_lieu.ket_noi import chay_migration, mo_ket_noi
from loi.kho_du_lieu.nap_mam import nap_mam
from loi.lich.quy_uoc_can_chi import CHI, CHI_VI, viet_hoa
from loi.lich.engine import CalendarEngine
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.tiet_khi import TietKhiError
from loi.nen.phien_ban import DB_MAC_DINH, ENGINE_VERSION, RULESET_VERSION
from loi.van import dong_thoi_gian as dtg
from loi.quyet_dinh.v1 import EVENT_RULES, quan_he_chi, xep_hang, danh_gia_event
from loi.quyet_dinh.ca_nhan import phan_tich_ca_nhan, bo_sung_event_ca_nhan
from loi.bat_tu.phuong_phap_tu_binh import gate_payload

ORDINAL_V1_1_PERSONAL = "ORDINAL_V1_1_PERSONAL"
EXPECTED_V1_EVENTS = 12
app = FastAPI(title="Tử Bình Gia Đình V1 — Stateless API")
logger = logging.getLogger("tubinh.api")


def _phan_loai_loi(exc: Exception) -> str:
    if isinstance(exc, ModuleNotFoundError): return "DEPENDENCY_MISSING"
    if isinstance(exc, sqlite3.Error): return "RULE_DB"
    if isinstance(exc, TietKhiError): return "ASTRONOMY_CALENDAR"
    if isinstance(exc, (KeyError, IndexError)): return "DATA_CODE_MISMATCH"
    return "ENGINE_RUNTIME"

@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    error_id=uuid.uuid4().hex[:8].upper(); stage=_phan_loai_loi(exc)
    logger.exception("API error %s stage=%s path=%s: %s",error_id,stage,request.url.path,exc)
    return JSONResponse(status_code=500,content={"detail":"Hệ thống tạm thời chưa xử lý được yêu cầu. Hãy thử lại sau vài giây.","error_code":f"API-{error_id}","error_stage":stage})


def _bao_dam_kho_rule() -> None:
    seed=Path(__file__).resolve().parents[1]/"du_lieu"/"kho"/"xemngay-rules-seed.sqlite3"
    if os.environ.get("VERCEL"):
        DB_MAC_DINH.parent.mkdir(parents=True,exist_ok=True)
        if seed.exists():
            tmp=DB_MAC_DINH.with_suffix(".tmp"); shutil.copy2(seed,tmp); tmp.replace(DB_MAC_DINH)
        else:
            if DB_MAC_DINH.exists(): DB_MAC_DINH.unlink()
            with mo_ket_noi() as c:
                chay_migration(c); nap_mam(c)
        with mo_ket_noi() as c:
            required={"rule_registry","rule_versions","event_types","sources"}
            found={r["name"] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not required.issubset(found): raise RuntimeError("RULE_DB_INVALID")
            active=c.execute("SELECT COUNT(*) n FROM event_types WHERE status='ACTIVE'").fetchone()["n"]
            if active != EXPECTED_V1_EVENTS: raise RuntimeError("RULE_DB_EVENT_COVERAGE_INVALID")
        return
    with mo_ket_noi() as c:
        chay_migration(c); nap_mam(c)

_bao_dam_kho_rule()

def _conn(): return mo_ket_noi()

class BirthVao(BaseModel):
    year:int; month:int; day:int; hour:int; minute:int
class ProfileVao(BaseModel):
    profile_id:str; full_name:str; gender:str; birth:BirthVao; birth_place_text:str
    timezone_name:str="Asia/Ho_Chi_Minh"; time_certainty:str="KNOWN"; note:str|None=None
class ProfileRequest(BaseModel): profile:ProfileVao
class DayRequest(ProfileRequest): ngay:str|None=None
class WorkRequest(ProfileRequest): viec:str; tu_ngay:str; den_ngay:str
class CalendarMonthRequest(ProfileRequest): year:int; month:int; viec:str|None=None


def _ho_so(v:ProfileVao)->HoSo:
    if not v.full_name.strip(): raise HTTPException(400,"Chưa nhập tên.")
    if v.gender not in ("NAM","NU"): raise HTTPException(400,"Giới tính phải là NAM hoặc NU.")
    if not v.birth_place_text.strip(): raise HTTPException(400,"Chưa nhập nơi sinh.")
    try:
        datetime(v.birth.year,v.birth.month,v.birth.day,v.birth.hour,v.birth.minute); ZoneInfo(v.timezone_name)
    except (ValueError,ZoneInfoNotFoundError) as e:
        raise HTTPException(400,"Ngày giờ sinh hoặc múi giờ không hợp lệ.") from e
    return HoSo(profile_id=v.profile_id,full_name=v.full_name.strip(),gender=v.gender,birth_year=v.birth.year,birth_month=v.birth.month,birth_day=v.birth.day,birth_hour=v.birth.hour,birth_minute=v.birth.minute,birth_place_text=v.birth_place_text.strip(),timezone_name=v.timezone_name,time_certainty=v.time_certainty,note=v.note)


def _ngay_ho_so(hs:HoSo,raw:str|None)->date:
    if raw:
        try: return date.fromisoformat(raw)
        except ValueError as e: raise HTTPException(400,"Ngày không hợp lệ.") from e
    try: return datetime.now(ZoneInfo(hs.timezone_name)).date()
    except ZoneInfoNotFoundError as e: raise HTTPException(400,f"Múi giờ hồ sơ không hợp lệ: {hs.timezone_name}") from e

GIO_KHOANG=["23:00–01:00","01:00–03:00","03:00–05:00","05:00–07:00","07:00–09:00","09:00–11:00","11:00–13:00","13:00–15:00","15:00–17:00","17:00–19:00","19:00–21:00","21:00–23:00"]

def _gio_tham_khao(kq):
    natal=kq.base_state["tu_tru"]["ngay"]["chi"]; out=[]
    for i,ch in enumerate(CHI):
        qh=quan_he_chi(natal,ch); nhan=qh.nhan if qh.ma!="NONE" else "Không có quan hệ trực tiếp trong lớp hiện tại"
        out.append({"chi":ch,"chi_vi":CHI_VI[i],"khoang_gio":GIO_KHOANG[i],"nhan":nhan,"relation":qh.ma,"relation_level":"STRUCTURAL_ONLY","relation_nature":qh.muc,"ly_do":qh.mo_ta,"scope":"STRUCTURAL_ONLY_PERSONAL_USE_PENDING"})
    return out


def _tom_tat_phan_tich(dg:dict)->dict:
    d=dg.get("dien_giai",{})
    return {"label":dg.get("label"),"headline":d.get("headline"),"theme":d.get("chu_de_chinh"),"theme_group":dg.get("theme",{}).get("theme_group"),"caution_count":sum(1 for x in dg.get("branch_impacts",[]) if x.get("level")=="CAUTION"),"positive_count":sum(1 for x in dg.get("branch_impacts",[]) if x.get("level")=="POSITIVE")}


def _cau_so_sanh(current:dict,other:dict,label:str)->str:
    a,b=_tom_tat_phan_tich(current),_tom_tat_phan_tich(other)
    if a["theme_group"]!=b["theme_group"]: return f"So với {label}, chủ đề cấu trúc nổi bật thay đổi. Xem chi tiết để biết yếu tố nào đổi."
    if a["caution_count"]!=b["caution_count"] or a["positive_count"]!=b["positive_count"]: return f"So với {label}, số tương tác trực tiếp với cấu trúc sinh thay đổi."
    return f"So với {label}, cấu trúc chính không đổi đáng kể ở lớp hiện có."


def _so_sanh_lien_ke(c,hs:HoSo,kq,d:date,scope:str)->dict:
    base=kq.base_state; tu_tru={k:dtg.TruVi(v["can"],v["chi"]) for k,v in base["tu_tru"].items()}; nhat_chu=base["nhat_chu"]
    e=CalendarEngine(tai_bo_lich()["CAL-V1"]); current=kq.day_state["danh_gia"] if scope=="day" else kq.month_state["danh_gia"]; out={}
    if scope=="day":
        dates=[("hom_qua","hôm qua",d-timedelta(days=1)),("ngay_mai","ngày mai",d+timedelta(days=1))]
        for key,label,dd in dates:
            lich=e.tinh(dd.year,dd.month,dd.day,12,0,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
            q=phan_tich_ca_nhan(c,tu_tru=tu_tru,nhat_chu=nhat_chu,can_hien_tai=lich.tru_ngay.can,chi_hien_tai=lich.tru_ngay.chi,scope="day",context=[])
            out[key]={"ngay":dd.isoformat(),"headline":q.get("dien_giai",{}).get("headline"),"label":q.get("label"),"so_sanh":_cau_so_sanh(current,q,label)}
        return out
    dates=[("thang_truoc","tháng trước",d-timedelta(days=35)),("thang_sau","tháng sau",d+timedelta(days=35))]
    for key,label,dd in dates:
        lich=e.tinh(dd.year,dd.month,dd.day,12,0,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
        q=phan_tich_ca_nhan(c,tu_tru=tu_tru,nhat_chu=nhat_chu,can_hien_tai=lich.tru_thang.can,chi_hien_tai=lich.tru_thang.chi,scope="month",context=[])
        out[key]={"moc":dd.isoformat(),"tru":viet_hoa(lich.tru_thang.can,lich.tru_thang.chi),"headline":q.get("dien_giai",{}).get("headline"),"label":q.get("label"),"so_sanh":_cau_so_sanh(current,q,label)}
    return out

@app.get("/api/health")
def health():
    checks={"rule_db":False,"astronomy":False,"events":0}
    try:
        with _conn() as c:
            checks["events"]=c.execute("SELECT COUNT(*) n FROM event_types WHERE status='ACTIVE'").fetchone()["n"]
            checks["rule_db"]=checks["events"]==EXPECTED_V1_EVENTS
    except Exception: logger.exception("Health check rule DB failed")
    try:
        import astronomy  # noqa: F401
        checks["astronomy"]=True
    except Exception: pass
    return {"ok":bool(checks["rule_db"] and checks["astronomy"]),"mode":"STATELESS_LOCAL_PROFILE","engine_version":ENGINE_VERSION,"ruleset_version":RULESET_VERSION,"profile_storage":"DEVICE_ONLY","checks":checks}

@app.get("/api/tinh-trang")
def tinh_trang():
    with _conn() as c:
        def d(sql:str,*a): return c.execute(sql,a).fetchone()["n"]
        return {"engine_version":ENGINE_VERSION,"ruleset_version":RULESET_VERSION,"quy_tac_verified":d("SELECT COUNT(*) n FROM rule_versions WHERE status='VERIFIED'"),"quy_tac_provisional":d("SELECT COUNT(*) n FROM rule_versions WHERE status='PROVISIONAL'"),"quy_tac_conflicted":d("SELECT COUNT(*) n FROM rule_versions WHERE status='CONFLICTED'"),"quy_tac_hiep_ky":d("SELECT COUNT(*) n FROM rule_registry WHERE namespace LIKE 'HK-%' AND is_active=1"),"quy_tac_quan_he":d("SELECT COUNT(*) n FROM rule_registry WHERE namespace='BT-REL' AND is_active=1"),"so_loai_viec_v1":d("SELECT COUNT(*) n FROM event_types WHERE status='ACTIVE'"),"cham_diem":ORDINAL_V1_1_PERSONAL,"numeric_score":"LOCKED_OFF","profile_storage":"DEVICE_ONLY","phuong_phap_tu_binh":gate_payload(),"canh_bao":"0.5.0 dùng Cách cục/Hỷ-Kỵ đã khóa nguồn; HARD_BLOCK của lớp sự kiện luôn thắng. Không dùng điểm số 0–10."}

@app.get("/api/loai-viec")
def loai_viec():
    with _conn() as c: rows=c.execute("SELECT code,name_vi,status FROM event_types ORDER BY name_vi").fetchall()
    return [{"code":r["code"],"ten":r["name_vi"],"muc_ho_tro":"ACTIVE_BASIC"} for r in rows if r["status"]=="ACTIVE" and r["code"] in EVENT_RULES]

@app.post("/api/stateless/toi-dang-o-dau")
def toi_dang_o_dau(v:ProfileRequest):
    hs=_ho_so(v.profile)
    with _conn() as c: return dtg.dung(c,hs).to_dict()

@app.post("/api/stateless/thang-nay")
def thang_nay(v:ProfileRequest):
    hs=_ho_so(v.profile)
    with _conn() as c:
        kq=hop_luu(c,hs); return {"don_gian":tang_1(kq,scope="month"),"chuyen_sau":tang_2(kq),"so_sanh_lien_ke":_so_sanh_lien_ke(c,hs,kq,_ngay_ho_so(hs,None),"month")}

@app.post("/api/stateless/hom-nay")
def hom_nay(v:DayRequest):
    hs=_ho_so(v.profile); d=_ngay_ho_so(hs,v.ngay)
    with _conn() as c:
        kq=hop_luu(c,hs,ngay=d)
        return {"ngay":d.isoformat(),"don_gian":tang_1(kq,scope="day"),"chuyen_sau":tang_2(kq),"gio_trong_ngay":_gio_tham_khao(kq),"gio_status":"STRUCTURAL_ONLY_PERSONAL_USE_PENDING","gio_note":"Giờ hiện là lớp tham khảo cấu trúc; chưa phải giờ tốt/xấu cá nhân.","so_sanh_lien_ke":_so_sanh_lien_ke(c,hs,kq,d,"day")}

@app.post("/api/stateless/dashboard")
def dashboard(v:ProfileRequest):
    hs=_ho_so(v.profile); d=_ngay_ho_so(hs,None)
    with _conn() as c:
        kq=hop_luu(c,hs,ngay=d); sau=tang_2(kq); cmp_day=_so_sanh_lien_ke(c,hs,kq,d,"day"); cmp_month=_so_sanh_lien_ke(c,hs,kq,d,"month")
        return {"ngay":d.isoformat(),"thang":{"don_gian":tang_1(kq,scope="month"),"chuyen_sau":sau,"so_sanh_lien_ke":cmp_month},"hom_nay":{"don_gian":tang_1(kq,scope="day"),"chuyen_sau":sau,"gio_trong_ngay":_gio_tham_khao(kq),"gio_status":"STRUCTURAL_ONLY_PERSONAL_USE_PENDING","so_sanh_lien_ke":cmp_day},"vi_tri":{"dai_van":kq.decade_state,"nam_hien_tai":kq.year_state.get("tru",{}),"thang_hien_tai":kq.month_state.get("tru",{})}}

@app.post("/api/stateless/tai-sao")
def tai_sao(v:DayRequest):
    hs=_ho_so(v.profile); d=_ngay_ho_so(hs,v.ngay)
    with _conn() as c:
        kq=hop_luu(c,hs,ngay=d); return {"chuyen_sau":tang_2(kq),"truy_nguoc":truy_nguoc_day_du(c,kq)}

@app.post("/api/stateless/lich-thang")
def lich_thang(v:CalendarMonthRequest):
    hs=_ho_so(v.profile)
    if not 1900<=v.year<=2100 or not 1<=v.month<=12: raise HTTPException(400,"Tháng cần xem không hợp lệ.")
    first=date(v.year,v.month,1); next_month=date(v.year+(1 if v.month==12 else 0),1 if v.month==12 else v.month+1,1); last=next_month-timedelta(days=1)
    e=CalendarEngine(tai_bo_lich()["CAL-V1"]); sinh=e.tinh(hs.birth_year,hs.birth_month,hs.birth_day,hs.birth_hour,hs.birth_minute,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
    chi_menh=sinh.tru_ngay.chi; nhat_chu=sinh.tru_ngay.can; tu_tru={"nam":dtg.TruVi(sinh.tru_nam.can,sinh.tru_nam.chi),"thang":dtg.TruVi(sinh.tru_thang.can,sinh.tru_thang.chi),"ngay":dtg.TruVi(sinh.tru_ngay.can,sinh.tru_ngay.chi),"gio":dtg.TruVi(sinh.tru_gio.can,sinh.tru_gio.chi)}
    out=[]; cur=first
    with _conn() as c:
        while cur<=last:
            lich=e.tinh(cur.year,cur.month,cur.day,12,0,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
            personal=phan_tich_ca_nhan(c,tu_tru=tu_tru,nhat_chu=nhat_chu,can_hien_tai=lich.tru_ngay.can,chi_hien_tai=lich.tru_ngay.chi,scope="day",context=[])
            if v.viec:
                ev=bo_sung_event_ca_nhan(danh_gia_event(lich.tru_thang.chi,lich.tru_ngay.chi,chi_menh,v.viec),personal); label=ev.get("label","Chưa có tín hiệu nổi bật"); state=ev.get("decision_state",ev.get("event_state","NEUTRAL")); detail={"truc":ev.get("truc_vi"),"personal_v1_1":ev.get("personal_v1_1",{}),"coverage":ev.get("coverage"),"hard_block":ev.get("hard_block",False)}
            else:
                label=personal.get("label","Chưa có tín hiệu nổi bật"); state=personal.get("state","NEUTRAL"); detail={"theme":personal.get("theme",{}),"branch_impacts":personal.get("branch_impacts",[])}
            out.append({"ngay":cur.isoformat(),"label":label,"state":state,"detail":detail}); cur+=timedelta(days=1)
    return {"year":v.year,"month":v.month,"viec":v.viec,"scoring_status":ORDINAL_V1_1_PERSONAL,"days":out}

@app.post("/api/stateless/tim-ngay")
def tim_ngay(v:WorkRequest):
    hs=_ho_so(v.profile)
    try: a,b=date.fromisoformat(v.tu_ngay),date.fromisoformat(v.den_ngay)
    except ValueError as e: raise HTTPException(400,"Khoảng ngày không hợp lệ.") from e
    if b<a or (b-a).days>92: raise HTTPException(400,"Khoảng ngày không hợp lệ hoặc vượt quá ba tháng.")
    if v.viec not in EVENT_RULES: raise HTTPException(400,"Loại việc chưa được hỗ trợ trong V1.")
    e=CalendarEngine(tai_bo_lich()["CAL-V1"]); sinh=e.tinh(hs.birth_year,hs.birth_month,hs.birth_day,hs.birth_hour,hs.birth_minute,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False); chi_menh=sinh.tru_ngay.chi; nhat_chu=sinh.tru_ngay.can
    tu_tru={"nam":dtg.TruVi(sinh.tru_nam.can,sinh.tru_nam.chi),"thang":dtg.TruVi(sinh.tru_thang.can,sinh.tru_thang.chi),"ngay":dtg.TruVi(sinh.tru_ngay.can,sinh.tru_ngay.chi),"gio":dtg.TruVi(sinh.tru_gio.can,sinh.tru_gio.chi)}
    ds=[]; cur=a
    with _conn() as c:
        while cur<=b:
            lich=e.tinh(cur.year,cur.month,cur.day,12,0,timezone_name=hs.timezone_name,gioi_tinh=hs.gender,tinh_dai_van=False)
            personal=phan_tich_ca_nhan(c,tu_tru=tu_tru,nhat_chu=nhat_chu,can_hien_tai=lich.tru_ngay.can,chi_hien_tai=lich.tru_ngay.chi,scope="day",context=[])
            ev=bo_sung_event_ca_nhan(danh_gia_event(lich.tru_thang.chi,lich.tru_ngay.chi,chi_menh,v.viec),personal)
            ds.append({"ngay":cur.isoformat(),"tru_ngay":viet_hoa(lich.tru_ngay.can,lich.tru_ngay.chi),"label":ev.get("label"),"decision_state":ev.get("decision_state"),"hard_block":ev.get("hard_block",False),"rank_group":ev.get("rank_group",9),"truc":ev.get("truc_vi"),"event_state":ev.get("event_state"),"personal_v1_1":ev.get("personal_v1_1",{}),"reasons":ev.get("reasons",[]),"mapping_status":ev.get("mapping_status"),"coverage":ev.get("coverage"),"event_note":ev.get("event_note"),"score":None,"scoring_status":ORDINAL_V1_1_PERSONAL}); cur+=timedelta(days=1)
    ranked=xep_hang(ds)
    return {"viec":v.viec,"so_ngay_da_quet":len(ds),"co_xep_hang_duoc_khong":True,"xep_hang_status":ORDINAL_V1_1_PERSONAL,"ghi_chu":"Xếp hạng theo thứ bậc HARD_BLOCK > sự kiện > nền cá nhân; không dùng điểm 0–10.","canh_bao_an_toan":("Chỉ chọn trong các thời điểm bác sĩ/cơ sở y tế xác nhận có thể linh hoạt; không trì hoãn cấp cứu." if v.viec=="DIEU_TRI" else None),"top":ranked[:3],"cac_ngay":ranked}

@app.api_route("/api/ho-so",methods=["GET","POST","PUT","DELETE"])
@app.api_route("/api/ho-so/{profile_id}",methods=["GET","POST","PUT","DELETE"])
def ho_so_cu_khong_con_dung(profile_id:str|None=None):
    raise HTTPException(410,"V1 PWA mới lưu hồ sơ trên thiết bị, không lưu trên máy chủ.")
