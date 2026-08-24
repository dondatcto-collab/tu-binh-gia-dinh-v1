"""Lớp quyết định cá nhân 0.5.0 theo Cách cục + Hỷ/Kỵ đã khóa.

Không dùng điểm số. HARD_BLOCK của lớp sự kiện luôn thắng lớp cá nhân.
Lá số/Cách cục AMBIGUOUS tự hạ về DESCRIPTIVE_ONLY.
"""
from __future__ import annotations
from typing import Any

from loi.bat_tu.thap_than import tinh_thap_than
from loi.bat_tu.cach_cuc import phan_tich_menh_goc, phan_tich_hanh_van
from loi.lich.quy_uoc_can_chi import CAN, CAN_VI, CHI, CHI_VI
from loi.quyet_dinh.v1 import quan_he_chi
from loi.bat_tu.phuong_phap_tu_binh import gate_payload

TEN_GOD_THEME = {
    "TY_KIEN": ("Hợp tác và tự chủ", "PEER"), "KIEP_TAI": ("Nguồn lực chung và cạnh tranh", "PEER"),
    "THUC_THAN": ("Thực thi, tạo đầu ra và chia sẻ", "OUTPUT"), "THUONG_QUAN": ("Biểu đạt, thay đổi cách làm và phản biện", "OUTPUT"),
    "THIEN_TAI": ("Giao dịch, nguồn lực và cơ hội tài chính", "WEALTH"), "CHINH_TAI": ("Tài chính, tài sản và quản lý nguồn lực", "WEALTH"),
    "THAT_SAT": ("Áp lực, quyết định và xử lý việc khó", "AUTHORITY"), "CHINH_QUAN": ("Trách nhiệm, quy tắc và vị trí công việc", "AUTHORITY"),
    "THIEN_AN": ("Học hỏi, hỗ trợ và xử lý thông tin", "RESOURCE"), "CHINH_AN": ("Học hỏi, hồ sơ và nguồn hỗ trợ", "RESOURCE"),
}
POSITION_VI = {"nam":"trụ năm","thang":"trụ tháng","ngay":"trụ ngày","gio":"trụ giờ"}


def _theme_for(conn, nhat_chu: str, can: str) -> dict[str, Any]:
    tt=tinh_thap_than(conn,nhat_chu,can); title,group=TEN_GOD_THEME.get(tt.ten_god,(tt.ten_god_vi,"OTHER"))
    return {"ten_god":tt.ten_god,"ten_god_vi":tt.ten_god_vi,"theme":title,"theme_group":group,"rule_id":tt.rule_id,"source_id":tt.source_id,"verification_status":tt.status}


def _branch_impacts(tu_tru: dict, chi_hien_tai: str) -> list[dict[str, Any]]:
    out=[]
    for pos in ("nam","thang","ngay","gio"):
        tru=tu_tru[pos]; qh=quan_he_chi(tru.chi,chi_hien_tai)
        if qh.ma=="NONE": continue
        out.append({"position":pos,"position_vi":POSITION_VI[pos],"natal_branch":tru.chi,"natal_branch_vi":CHI_VI[CHI.index(tru.chi)],"current_branch":chi_hien_tai,"current_branch_vi":CHI_VI[CHI.index(chi_hien_tai)],"relation":qh.ma,"relation_vi":qh.nhan,"level":qh.muc,"rule_id":qh.rule_id,"source_id":qh.source_id,"technical":qh.mo_ta})
    return out


def phan_tich_ca_nhan(conn, *, tu_tru: dict, nhat_chu: str, can_hien_tai: str, chi_hien_tai: str, scope: str, context: list[dict[str, Any]] | None=None) -> dict[str, Any]:
    method=gate_payload(); theme=_theme_for(conn,nhat_chu,can_hien_tai); impacts=_branch_impacts(tu_tru,chi_hien_tai)
    natal=phan_tich_menh_goc(conn,tu_tru=tu_tru,nhat_chu=nhat_chu)
    transit=phan_tich_hanh_van(conn,natal,nhat_chu,can_hien_tai,chi_hien_tai,scope)
    horizon={"month":"Tháng","day":"Ngày","year":"Năm","decade":"Đại vận","hour":"Giờ"}.get(scope,"Giai đoạn")
    can_vi=CAN_VI[CAN.index(can_hien_tai)]; chi_vi=CHI_VI[CHI.index(chi_hien_tai)]
    technical=[f"Can {can_vi} đối với Nhật chủ là {theme['ten_god_vi']}"]+[x["technical"] for x in impacts]

    if not method.get("personal_decision_ready") or natal.get("status")!="READY":
        state="DESCRIPTIVE_ONLY"; label="Chưa đủ căn cứ thuận/nghịch cá nhân"; decision_effect="UNDETERMINED"
        headline=f"{horizon} có chủ đề {theme['theme'].lower()}; Cách cục chưa đủ rõ để kết luận cá nhân"
        recommended=[]; caution=[]
    else:
        state=transit["state"]
        label=transit["label"]
        decision_effect=state
        headline=f"{horizon} {can_vi} {chi_vi}: {label.lower()} theo nền Cách cục đã khóa"
        recommended=["Có thể ưu tiên hơn khi lớp sự kiện không bị chặn."] if state=="SUPPORT" else []
        caution=["Nên thận trọng hơn; không dùng một tầng thời gian để đảo quyết định sự kiện bị chặn."] if state=="CAUTION" else []

    return {
        "scope":scope,"state":state,"label":label,"confidence":"HIGH" if natal.get("status")=="READY" else "LOW",
        "basis":headline,"recommended":recommended,"caution":caution,
        "theme":theme,"natal_pattern":natal,"transit":transit,
        "branch_impacts":[{**x,"decision_effect":decision_effect} for x in impacts],
        "relation":({"ma":impacts[0]["relation"],"nhan":impacts[0]["relation_vi"],"muc":"STRUCTURAL_ONLY","mo_ta":impacts[0]["technical"],"rule_id":impacts[0]["rule_id"],"source_id":impacts[0]["source_id"]} if impacts else {**quan_he_chi(tu_tru["ngay"].chi,chi_hien_tai).__dict__,"muc":"STRUCTURAL_ONLY"}),
        "technical_facts":technical,"methodology":method,
        "dien_giai":{"interpretation_status":"ZPZQ_PERSONAL_0_5" if state!="DESCRIPTIVE_ONLY" else "ZPZQ_DESCRIPTIVE_ONLY_0_5","headline":headline,"trigger":"; ".join(technical),"chu_de_chinh":theme["theme"],"cong_viec":label,"tai_chinh":"Không suy tài lộc chỉ từ Thập Thần; dùng trạng thái nền Cách cục.","quan_he":"Quan hệ Chi là evidence cấu trúc, không tự lật kết luận.","viec_lon":"Khi chọn việc, HARD_BLOCK của Hiệp Kỷ luôn thắng.","focus":[],"khong_suy_dien":method["reason_vi"],"technical_trigger":"; ".join(technical),"methodology":method},
        "rule_ids":sorted(set([theme["rule_id"],*method["rule_ids"],*natal.get("rule_ids",[]),*transit.get("rule_ids",[])]+[x["rule_id"] for x in impacts])),
        "source_ids":sorted(set([theme["source_id"],*method["source_ids"],*natal.get("source_ids",[])]+[x["source_id"] for x in impacts])),
    }


def bo_sung_event_ca_nhan(event_state: dict[str, Any], personal: dict[str, Any]) -> dict[str, Any]:
    """Gate 3: hợp lưu thứ bậc; không trung bình hóa và không có numeric score."""
    out=dict(event_state); pstate=personal.get("state","DESCRIPTIVE_ONLY")
    out["personal_methodology"]=personal.get("methodology") or gate_payload()
    out["personal_v1_1"]={"theme":personal.get("theme"),"branch_impacts":personal.get("branch_impacts",[]),"headline":personal.get("dien_giai",{}).get("headline"),"technical_facts":personal.get("technical_facts",[]),"interpretation_status":"ZPZQ_PERSONAL_0_5","decision_effect":pstate}
    reasons=list(out.get("reasons",[])); reasons.append("Hợp lưu 0.5.0 dùng thứ bậc: HARD_BLOCK > lớp sự kiện > nền cá nhân; không trung bình hóa.")
    ev=out.get("event_state")
    if ev=="JI":
        out["hard_block"]=True; out["decision_state"]="HARD_BLOCK"; out["label"]="Bị chặn"; out["rank_group"]=9
    elif pstate=="SUPPORT" and ev=="YI":
        out["hard_block"]=False; out["decision_state"]="PRIORITY"; out["label"]="Ưu tiên"; out["rank_group"]=1
    elif pstate=="CAUTION" and ev=="YI":
        out["hard_block"]=False; out["decision_state"]="CONSIDER"; out["label"]="Có thể cân nhắc"; out["rank_group"]=2
    elif pstate=="CAUTION" and ev=="NEUTRAL":
        out["hard_block"]=False; out["decision_state"]="NOT_PREFERRED"; out["label"]="Không ưu tiên"; out["rank_group"]=4
    elif pstate=="SUPPORT" and ev=="NEUTRAL":
        out["hard_block"]=False; out["decision_state"]="CONSIDER"; out["label"]="Có thể cân nhắc"; out["rank_group"]=2
    else:
        out["hard_block"]=False; out["decision_state"]="EVENT_ONLY"; out["rank_group"]=out.get("rank_group",3)
    out["score"]=None; out["scoring_status"]="NO_NUMERIC_SCORE"; out["numeric_score_status"]="LOCKED_OFF"
    out["personal_rank_adjustment"]=0
    out["reasons"]=reasons
    out["rule_ids"]=sorted(set(list(out.get("rule_ids",[]))+list(personal.get("rule_ids",[]))))
    return out
