"""Lớp quyết định V1: 12 việc chính thức, không dùng điểm số tự đặt.

Hiệp Kỷ trong V1 chỉ triển khai phần 12 Trực đã khóa nguồn. Quan hệ Địa Chi
cá nhân vẫn được lưu làm evidence cấu trúc, không tự sinh kết luận tốt/xấu.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from loi.lich.quy_uoc_can_chi import CHI as CHI_NATIVE, CHI_VI as CHI_VI_NATIVE

CHI = list(CHI_NATIVE)
CHI_VI = dict(zip(CHI, CHI_VI_NATIVE))
CHI_ALIAS = {
    "ZI":"TY", "CHOU":"SUU", "YIN":"DAN", "MAO":"MAO",
    "CHEN":"THIN", "SI":"TI", "WU":"NGO", "WEI":"MUI",
    "SHEN":"THAN", "YOU":"DAU", "XU":"TUAT", "HAI":"HOI",
}
TRUC = ["KIEN","TRU","MAN","BINH","DINH","CHAP","PHA","NGUY","THANH","THU","KHAI","BE"]
TRUC_VI = {
    "KIEN":"Kiến","TRU":"Trừ","MAN":"Mãn","BINH":"Bình","DINH":"Định","CHAP":"Chấp",
    "PHA":"Phá","NGUY":"Nguy","THANH":"Thành","THU":"Thu","KHAI":"Khai","BE":"Bế",
}
V1_EVENT_COVERAGE = "12/12"
HIEP_KY_COVERAGE = "PARTIAL_12_TRUC_ONLY"
NUMERIC_SCORE_STATUS = "LOCKED_OFF"
BACKLOG_EVENT_CODES = frozenset({"THI_CU"})

LUC_HOP = {frozenset(x) for x in [("TY","SUU"),("DAN","HOI"),("MAO","TUAT"),("THIN","DAU"),("TI","THAN"),("NGO","MUI")]}
LUC_XUNG = {frozenset(x) for x in [("TY","NGO"),("SUU","MUI"),("DAN","THAN"),("MAO","DAU"),("THIN","TUAT"),("TI","HOI")]}
LUC_HAI = {frozenset(x) for x in [("TY","MUI"),("SUU","NGO"),("DAN","TI"),("MAO","THIN"),("THAN","HOI"),("DAU","TUAT")]}
HINH_CAP = {frozenset(x) for x in [("TY","MAO"),("DAN","TI"),("TI","THAN"),("DAN","THAN"),("SUU","TUAT"),("TUAT","MUI"),("SUU","MUI")]}
TU_HINH = {"THIN","NGO","DAU","HOI"}

SRC_REL = "SRC-TMTH-V02-WIKISOURCE"
SRC_HK11 = "SRC-HK-QD-V11-WIKISOURCE"
SRC_PRODUCT = "SRC-PRODUCT-V1-SPEC"

@dataclass(frozen=True)
class QuanHeChi:
    ma: str
    nhan: str
    muc: str
    mo_ta: str
    rule_id: str
    source_id: str

@dataclass(frozen=True)
class EventRule:
    code: str
    ten: str
    classical: str
    yi_truc: frozenset[str]
    ji_truc: frozenset[str]
    mapping_status: str
    source_location: str
    note: str = ""

# Phạm vi V1 đã khóa: 12 việc. Thi/phỏng vấn chuyển BACKLOG_NOT_V1.
EVENT_RULES = {
    "KHAI_TRUONG": EventRule("KHAI_TRUONG","Khai trương","開市",frozenset({"MAN","THANH","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 開市"),
    "KY_HOP_DONG": EventRule("KY_HOP_DONG","Ký hợp đồng / giao dịch quan trọng","立券交易",frozenset({"MAN"}),frozenset({"PHA","BINH","THU"}),"VERIFIED","卷十一 · 立券交易"),
    "MUA_TAI_SAN": EventRule("MUA_TAI_SAN","Mua tài sản lớn","納財",frozenset({"MAN","THU"}),frozenset({"PHA","BINH"}),"PROVISIONAL","卷十一 · 納財","Nhóm hiện đại rộng; V1 dùng 納財 làm đại diện."),
    "DONG_THO": EventRule("DONG_THO","Động thổ / sửa nhà","興造動土/修造",frozenset({"KHAI"}),frozenset({"KIEN","PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 興造動土"),
    "NHAP_TRACH": EventRule("NHAP_TRACH","Chuyển nhà / di dời","般移/移徙",frozenset({"THANH","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 般移〈移徙同〉"),
    "CUOI_HOI": EventRule("CUOI_HOI","Cưới hỏi","嫁娶",frozenset(),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 嫁娶","Các cát thần cưới hỏi khác chưa tính trong V1."),
    "XUAT_HANH": EventRule("XUAT_HANH","Đi xa / xuất hành","出行",frozenset({"KIEN","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 行幸遣使〈出行同〉"),
    "DIEU_TRI": EventRule("DIEU_TRI","Khám / điều trị","求醫療病",frozenset({"TRU","PHA","KHAI"}),frozenset({"KIEN","BINH","THU","MAN","BE"}),"VERIFIED","卷十一 · 求醫療病","Chỉ dùng khi thời điểm đã linh hoạt về mặt y khoa; không trì hoãn cấp cứu."),
    "DAM_PHAN": EventRule("DAM_PHAN","Họp / gặp gỡ","會親友",frozenset({"KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"PROVISIONAL","卷十一 · 宴會〈會親友同〉","Ánh xạ hiện đại ở mức PROVISIONAL."),
    "NHAM_CHUC": EventRule("NHAM_CHUC","Nhận chức / nhậm chức","上官赴任",frozenset({"KIEN","KHAI"}),frozenset({"PHA","BINH","THU","MAN","BE"}),"VERIFIED","卷十一 · 上官赴任"),
    "CAU_TAI": EventRule("CAU_TAI","Thu / nhận tiền","納財",frozenset({"MAN","THU"}),frozenset({"PHA","BINH"}),"VERIFIED","卷十一 · 納財"),
    "AN_TANG": EventRule("AN_TANG","Tang lễ / an táng","安葬",frozenset(),frozenset({"KIEN","PHA","BINH","THU"}),"VERIFIED","卷十一 · 安葬","Các cát thần chuyên biệt cho an táng chưa tính trong V1."),
}

ALIASES = {"DAU_TU":"CAU_TAI", "XAY_DUNG":"DONG_THO"}


def chuan_hoa_chi(code: str) -> str:
    c = CHI_ALIAS.get(str(code or "").strip().upper(), str(code or "").strip().upper())
    if c not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {code}")
    return c


def chuan_hoa_event(code: str | None) -> str | None:
    if not code:
        return None
    c = str(code).strip().upper()
    if c in BACKLOG_EVENT_CODES or c == "HOC_TAP":
        return c
    return ALIASES.get(c, c)


def tinh_truc(chi_thang: str, chi_ngay: str) -> str:
    chi_thang = chuan_hoa_chi(chi_thang)
    chi_ngay = chuan_hoa_chi(chi_ngay)
    return TRUC[(CHI.index(chi_ngay) - CHI.index(chi_thang)) % 12]


def quan_he_chi(a: str, b: str) -> QuanHeChi:
    a, b = chuan_hoa_chi(a), chuan_hoa_chi(b)
    pair = frozenset((a,b))
    if a == b and a in TU_HINH:
        return QuanHeChi("TU_HINH","Tự hình","CAUTION",f"{CHI_VI[a]} gặp cùng {CHI_VI[b]} thuộc nhóm tự hình; nên thận trọng hơn.","BT-REL-0004",SRC_REL)
    if pair in LUC_HOP:
        return QuanHeChi("LUC_HOP","Lục hợp","POSITIVE",f"{CHI_VI[a]} và {CHI_VI[b]} thuộc Lục hợp, biểu thị quan hệ hòa hợp trực tiếp.","BT-REL-0001",SRC_REL)
    if pair in LUC_XUNG:
        return QuanHeChi("LUC_XUNG","Lục xung","CAUTION",f"{CHI_VI[a]} và {CHI_VI[b]} trực xung; đây là dấu hiệu xung động cần được lưu ý, không tự đồng nghĩa với kết quả xấu tuyệt đối.","BT-REL-0002",SRC_REL)
    if pair in LUC_HAI:
        return QuanHeChi("LUC_HAI","Lục hại","CAUTION",f"{CHI_VI[a]} và {CHI_VI[b]} thuộc Lục hại; V1 coi đây là tín hiệu cần thận trọng.","BT-REL-0003",SRC_REL)
    if pair in HINH_CAP:
        return QuanHeChi("HINH","Hình","CAUTION",f"{CHI_VI[a]} và {CHI_VI[b]} nằm trong quan hệ Hình; V1 chỉ ghi nhận là điểm va chạm.","BT-REL-0004",SRC_REL)
    return QuanHeChi("NONE","Không có quan hệ trực tiếp","NEUTRAL",f"Không thấy Lục hợp, Lục xung, Lục hại hoặc Hình trực tiếp giữa {CHI_VI[a]} và {CHI_VI[b]} ở lớp V1.","FUS-V1-REL-0001",SRC_PRODUCT)


def danh_gia_giai_doan(chi_menh_ngay: str, chi_hien_tai: str, scope: str) -> dict:
    qh = quan_he_chi(chi_menh_ngay, chi_hien_tai)
    horizon = "tháng" if scope == "month" else "ngày" if scope == "day" else "giai đoạn"
    headline = (f"{horizon.capitalize()} chưa có quan hệ Địa Chi trực tiếp trong nhóm quy tắc hiện đã cài" if qh.ma == "NONE" else f"{horizon.capitalize()} có quan hệ {qh.nhan} với Chi ngày sinh")
    return {
        "scope":scope, "state":"DESCRIPTIVE_ONLY", "label":"Chỉ ghi nhận cấu trúc",
        "relation":{**qh.__dict__, "muc":"STRUCTURAL_ONLY"}, "recommended":[], "caution":[],
        "confidence":"MEDIUM" if qh.ma != "NONE" else "LOW", "basis":headline,
        "dien_giai":{
            "interpretation_status":"ZPZQ_DESCRIPTIVE_ONLY_0_5", "evidence_scope":"BRANCH_RELATION_NOT_DECISION",
            "headline":headline, "trigger":qh.mo_ta,
            "cong_viec":"Chưa dùng quan hệ Chi đơn lẻ để kết luận thuận/nghịch công việc.",
            "tai_chinh":"Chưa dùng quan hệ Chi đơn lẻ để kết luận thuận/nghịch tài chính.",
            "quan_he":"Quan hệ này chỉ mô tả kiểu tương tác cấu trúc; chưa đồng nghĩa tốt/xấu.",
            "viec_lon":"Không dùng quan hệ Chi đơn lẻ để quyết định việc lớn.",
            "focus":[], "khong_suy_dien":"Chờ Cách cục + hỷ/kỵ mệnh gốc trước khi cho quan hệ thời gian tác động vào quyết định cá nhân.",
            "technical_trigger":qh.mo_ta,
        },
    }


def danh_gia_event(chi_thang: str, chi_ngay: str, chi_menh_ngay: str, event_code: str) -> dict:
    code = chuan_hoa_event(event_code)
    rule = EVENT_RULES.get(code or "")
    if not rule:
        status = "BACKLOG_NOT_V1" if code in BACKLOG_EVENT_CODES or code == "HOC_TAP" else "NO_RULE"
        return {"support_level":status,"event_code":code,"label":"Chưa hỗ trợ trong V1","rank_group":9,"score":None,"scoring_status":"NO_NUMERIC_SCORE"}
    truc = tinh_truc(chi_thang, chi_ngay)
    event_state = "JI" if truc in rule.ji_truc else "YI" if truc in rule.yi_truc else "NEUTRAL"
    qh = quan_he_chi(chi_menh_ngay, chi_ngay)
    if event_state == "JI":
        group, label = 5, "Không ưu tiên theo việc"
    elif event_state == "YI" and rule.mapping_status == "VERIFIED":
        group, label = 1, "Phù hợp theo Hiệp Kỷ"
    elif event_state == "YI":
        group, label = 2, "Có thể cân nhắc theo Hiệp Kỷ"
    else:
        group, label = 3, "Chưa có tín hiệu theo việc"
    reasons = [f"Ngày thuộc Trực {TRUC_VI[truc]} trong tháng hiện tại."]
    if event_state == "YI": reasons.append(f"Trực {TRUC_VI[truc]} nằm trong nhóm được nêu là phù hợp cho {rule.ten} ở lớp quy tắc V1.")
    if event_state == "JI": reasons.append(f"Trực {TRUC_VI[truc]} nằm trong nhóm cần tránh cho {rule.ten} ở lớp quy tắc V1.")
    if qh.ma != "NONE": reasons.append(qh.mo_ta + " Quan hệ này hiện chỉ là evidence cấu trúc, không đổi thứ hạng ngày.")
    if rule.mapping_status == "PROVISIONAL": reasons.append("Ánh xạ hiện đại đang ở trạng thái PROVISIONAL; nhãn được hạ mức tin cậy.")
    return {
        "support_level":"ACTIVE_BASIC", "event_code":code, "event_name":rule.ten,
        "classical_event":rule.classical, "mapping_status":rule.mapping_status,
        "truc":truc, "truc_vi":TRUC_VI[truc], "event_state":event_state,
        "personal_relation":{**qh.__dict__, "decision_effect":"NONE_UNTIL_NATAL_USE_READY"},
        "label":label, "rank_group":group, "score":None,
        "scoring_status":"NO_NUMERIC_SCORE", "numeric_score_status":NUMERIC_SCORE_STATUS,
        "reasons":reasons, "source_id":SRC_HK11, "source_location":rule.source_location,
        "event_note":rule.note or None, "coverage":HIEP_KY_COVERAGE,
        "v1_event_coverage":V1_EVENT_COVERAGE,
        "confidence":"MEDIUM" if rule.mapping_status == "VERIFIED" else "LOW",
        "coverage_note":"V1 dùng phần 12 Trực được nêu trực tiếp trong mục 宜/忌; không tuyên bố Hiệp Kỷ đầy đủ.",
        "rule_ids":["HK-GENERAL-0001", f"HK-EVENT-{list(EVENT_RULES).index(code)+1:04d}", qh.rule_id, "FUS-V1-0001"],
    }


def xep_hang(ds: Iterable[dict]) -> list[dict]:
    return sorted(ds, key=lambda x: (x.get("rank_group",9), x.get("ngay","")))
