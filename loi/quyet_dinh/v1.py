"""Quyết định V1 tối thiểu, có căn cứ nguồn và không dùng trọng số bịa.

Mục tiêu của lớp này là trả lời ba câu hỏi sản phẩm V1 bằng các quy tắc đã
có thể xác minh trực tiếp:
  1) tháng này đang có nhịp hòa hợp / va chạm trực tiếp nào với lá số;
  2) hôm nay có quan hệ trực tiếp nào đáng chú ý;
  3) ngày nào phù hợp hơn cho MỘT VIỆC theo Hiệp Kỷ, dùng 12 Trực làm lớp
     sự kiện tối thiểu và quan hệ Địa Chi cá nhân làm lớp phụ.

Không chấm điểm 0-10. Không suy Dụng/Hỷ/Kỵ. Không coi Thập Thần tự thân là
cát/hung. Xếp hạng dùng thứ tự quyết định rời rạc, không dùng trọng số số học.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from loi.lich.quy_uoc_can_chi import CHI as CHI_NATIVE, CHI_VI as CHI_VI_NATIVE

# Dùng cùng mã Địa Chi với Calendar Engine. Vẫn nhận pinyin cũ để tương thích dữ liệu/test cũ.
CHI = list(CHI_NATIVE)
CHI_VI = dict(zip(CHI, CHI_VI_NATIVE))
CHI_ALIAS = {
    "ZI":"TY", "CHOU":"SUU", "YIN":"DAN", "MAO":"MAO",
    "CHEN":"THIN", "SI":"TI", "WU":"NGO", "WEI":"MUI",
    "SHEN":"THAN", "YOU":"DAU", "XU":"TUAT", "HAI":"HOI",
}

def chuan_hoa_chi(code: str) -> str:
    c = str(code or "").strip().upper()
    c = CHI_ALIAS.get(c, c)
    if c not in CHI:
        raise ValueError(f"CHI_KHONG_HOP_LE: {code}")
    return c
TRUC = ["KIEN","TRU","MAN","BINH","DINH","CHAP","PHA","NGUY","THANH","THU","KHAI","BE"]
TRUC_VI = {
    "KIEN":"Kiến","TRU":"Trừ","MAN":"Mãn","BINH":"Bình","DINH":"Định","CHAP":"Chấp",
    "PHA":"Phá","NGUY":"Nguy","THANH":"Thành","THU":"Thu","KHAI":"Khai","BE":"Bế",
}

# 三命通會, quyển 2: 支元六合 / 冲击 / 六害 / 三刑.
LUC_HOP = {frozenset(x) for x in [("TY","SUU"),("DAN","HOI"),("MAO","TUAT"),("THIN","DAU"),("TI","THAN"),("NGO","MUI")]}
LUC_XUNG = {frozenset(x) for x in [("TY","NGO"),("SUU","MUI"),("DAN","THAN"),("MAO","DAU"),("THIN","TUAT"),("TI","HOI")]}
LUC_HAI = {frozenset(x) for x in [("TY","MUI"),("SUU","NGO"),("DAN","TI"),("MAO","THIN"),("THAN","HOI"),("DAU","TUAT")]}
HINH_CAP = {frozenset(x) for x in [("TY","MAO"),("DAN","TI"),("TI","THAN"),("DAN","THAN"),("SUU","TUAT"),("TUAT","MUI"),("SUU","MUI")]}
TU_HINH = {"THIN","NGO","DAU","HOI"}

SRC_REL = "SRC-TMTH-V02-WIKISOURCE"
SRC_HK11 = "SRC-HK-QD-V11-WIKISOURCE"
SRC_HK04 = "SRC-HK-QD-V04-KANRIPO"
SRC_PRODUCT = "SRC-PRODUCT-V1-SPEC"

@dataclass(frozen=True)
class QuanHeChi:
    ma: str
    nhan: str
    muc: str   # POSITIVE | CAUTION | NEUTRAL
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

# Chỉ dùng các Trực được nêu trực tiếp trong mục 宜/忌 của 協紀辨方書卷十一.
# Các thần khác chưa được tính ở V1-basic, vì vậy kết quả ghi rõ coverage PARTIAL.
EVENT_RULES = {
    "KHAI_TRUONG": EventRule("KHAI_TRUONG","Khai trương","開市",frozenset({"MAN","THANH","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 開市"),
    "KY_HOP_DONG": EventRule("KY_HOP_DONG","Ký hợp đồng / giao dịch quan trọng","立券交易",frozenset({"MAN"}),frozenset({"PHA","BINH","THU"}),"VERIFIED","卷十一 · 立券交易"),
    "MUA_TAI_SAN": EventRule("MUA_TAI_SAN","Mua tài sản lớn","納財",frozenset({"MAN","THU"}),frozenset({"PHA","BINH"}),"PROVISIONAL","卷十一 · 納財","Nhóm hiện đại rộng; V1 dùng 納財 làm đại diện."),
    "DONG_THO": EventRule("DONG_THO","Động thổ / sửa nhà","興造動土/修造",frozenset({"KHAI"}),frozenset({"KIEN","PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 興造動土"),
    "NHAP_TRACH": EventRule("NHAP_TRACH","Nhập trạch / chuyển nhà","般移/移徙",frozenset({"THANH","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 般移〈移徙同〉"),
    "CUOI_HOI": EventRule("CUOI_HOI","Cưới hỏi","嫁娶",frozenset(),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 嫁娶","Các cát thần cưới hỏi khác chưa tính trong V1-basic."),
    "XUAT_HANH": EventRule("XUAT_HANH","Đi xa / xuất hành","出行",frozenset({"KIEN","KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"VERIFIED","卷十一 · 行幸遣使〈出行同〉"),
    "DIEU_TRI": EventRule("DIEU_TRI","Khám / điều trị / thủ thuật linh hoạt","求醫療病",frozenset({"TRU","PHA","KHAI"}),frozenset({"KIEN","BINH","THU","MAN","BE"}),"VERIFIED","卷十一 · 求醫療病","Chỉ dùng trong các lựa chọn thời gian đã được bác sĩ cho phép; không trì hoãn cấp cứu."),
    "DAM_PHAN": EventRule("DAM_PHAN","Gặp gỡ / đàm phán quan trọng","會親友",frozenset({"KHAI"}),frozenset({"PHA","BINH","THU","BE"}),"PROVISIONAL","卷十一 · 宴會〈會親友同〉","Đàm phán hiện đại được ánh xạ gần nhất sang 會親友."),
    "NHAM_CHUC": EventRule("NHAM_CHUC","Bắt đầu công việc mới / nhận chức","上官赴任",frozenset({"KIEN","KHAI"}),frozenset({"PHA","BINH","THU","MAN","BE"}),"VERIFIED","卷十一 · 上官赴任"),
    "THI_CU": EventRule("THI_CU","Thi cử / phỏng vấn","入學",frozenset({"THANH","KHAI"}),frozenset(),"PROVISIONAL","卷十一 · 入學","Thi cử/phỏng vấn là nhóm hiện đại; 入學 là ánh xạ gần nhất cho lớp học hành."),
    "CAU_TAI": EventRule("CAU_TAI","Cầu tài / thu hồi tiền / giao dịch","納財",frozenset({"MAN","THU"}),frozenset({"PHA","BINH"}),"VERIFIED","卷十一 · 納財"),
    "AN_TANG": EventRule("AN_TANG","Tang lễ / an táng","安葬",frozenset(),frozenset({"KIEN","PHA","BINH","THU"}),"VERIFIED","卷十一 · 安葬","Các cát thần chuyên biệt cho an táng chưa tính trong V1-basic."),
}

# Alias để không làm gãy hồ sơ/URL cũ.
ALIASES = {
    "DAU_TU":"CAU_TAI", "XAY_DUNG":"DONG_THO", "HOC_TAP":"THI_CU",
}


def chuan_hoa_event(code: str | None) -> str | None:
    if not code:
        return None
    return ALIASES.get(code, code)


def tinh_truc(chi_thang: str, chi_ngay: str) -> str:
    """建 đặt tại chi tháng, sau đó thuận 12 chi: 建除滿平定執破危成收開閉."""
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


def _dien_giai_ung_dung(qh: QuanHeChi, scope: str) -> dict:
    """Diễn giải sản phẩm từ QUAN HỆ CẤU TRÚC đã xác minh.

    Đây KHÔNG phải câu nguyên văn cổ thư và KHÔNG được quảng bá như dự báo chắc chắn.
    Mỗi câu đều giữ giới hạn: quan hệ Chi chỉ là một tín hiệu cấu trúc, không thay
    Dụng/Hỷ/Kỵ và không tự suy ra tiền bạc/sức khỏe tốt xấu.
    """
    is_month = scope == "month"
    horizon = "tháng" if is_month else "ngày"
    base = {
        "interpretation_status": "PRODUCT_INTERPRETATION",
        "evidence_scope": "VERIFIED_BRANCH_RELATION_ONLY",
        "khong_suy_dien": "Không dùng riêng quan hệ này để kết luận tài chính, sức khỏe hay thành bại của việc lớn.",
        "technical_trigger": qh.mo_ta,
    }
    if qh.ma == "LUC_HOP":
        return {**base,
            "headline": f"{horizon.capitalize()} có nhịp phối hợp thuận hơn",
            "trigger": "Nhịp hiện tại tạo một quan hệ phối hợp trực tiếp với cấu trúc ngày sinh.",
            "cong_viec": "Thuận hơn cho việc cần phối hợp, trao đổi hoặc nối lại công việc đang dang dở; việc quan trọng vẫn nên xét đúng loại việc trước khi chốt.",
            "tai_chinh": "Chưa có căn cứ riêng để gọi là tháng/ngày tài lộc; nếu có giao dịch lớn, dùng mục Tìm ngày và kiểm tra điều kiện thực tế.",
            "quan_he": "Dễ tìm điểm chung hơn trong trao đổi; phù hợp để nói rõ nhu cầu, thống nhất cách làm hoặc hàn gắn một bất đồng nhỏ.",
            "viec_lon": "Có thể chủ động chuẩn bị, nhưng không dùng Lục hợp một mình để quyết định thời điểm cuối cùng.",
            "focus": ["Ưu tiên việc cần phối hợp và thống nhất", "Chốt rõ trách nhiệm, mốc thời gian và điều kiện thực tế"],
        }
    if qh.ma == "LUC_XUNG":
        return {**base,
            "headline": f"{horizon.capitalize()} có nhịp thay đổi và va chạm trực tiếp",
            "trigger": "Nhịp hiện tại va chạm trực tiếp với cấu trúc ngày sinh, nên khả năng phải điều chỉnh cao hơn bình thường.",
            "cong_viec": "Dễ phát sinh đổi lịch, đổi cách làm hoặc việc chen ngang; nên chừa khoảng trống và có phương án B cho việc cần chốt.",
            "tai_chinh": "Không tự suy ra hao tài. Với khoản lớn, tránh quyết định chỉ vì cảm giác gấp; kiểm tra lại điều kiện, dòng tiền và thời điểm cụ thể.",
            "quan_he": "Dễ khó đồng bộ quan điểm hoặc nhịp hành động; nên xử lý từng việc cụ thể, tránh đẩy bất đồng nhỏ thành tranh luận lớn.",
            "viec_lon": "Không đồng nghĩa phải hoãn mọi việc lớn; nếu buộc làm, nên chuẩn bị phương án dự phòng và chọn ngày/giờ theo đúng loại việc.",
            "focus": ["Rà lại lịch và điểm dễ thay đổi", "Giữ phương án dự phòng cho việc khó đảo ngược"],
        }
    if qh.ma == "LUC_HAI":
        return {**base,
            "headline": f"{horizon.capitalize()} có điểm vướng cần kiểm tra kỹ",
            "trigger": "Nhịp hiện tại tạo một điểm vướng trực tiếp với cấu trúc ngày sinh; nên kiểm tra kỹ phần dễ bị hiểu lệch hoặc bỏ sót.",
            "cong_viec": "Nên làm rõ điều kiện, đầu mối và phần việc dễ bị hiểu khác nhau; tránh dựa vào thỏa thuận miệng ở việc quan trọng.",
            "tai_chinh": "Chưa có căn cứ để kết luận tiền bạc xấu; ưu tiên kiểm tra phí, điều khoản và phần nghĩa vụ dễ bị bỏ sót.",
            "quan_he": "Dễ có cảm giác không hiểu nhau hoặc kỳ vọng lệch nhau; nói rõ việc cụ thể và xác nhận lại điều đã thống nhất.",
            "viec_lon": "Có thể tiến hành khi điều kiện đủ rõ; nên tăng bước kiểm tra trước khi ký, chuyển tiền hoặc cam kết dài hạn.",
            "focus": ["Làm rõ điều kiện và trách nhiệm", "Kiểm tra phần dễ bị bỏ sót trước khi chốt"],
        }
    if qh.ma in {"HINH", "TU_HINH"}:
        return {**base,
            "headline": f"{horizon.capitalize()} dễ phát sinh ma sát hoặc tự gây áp lực",
            "trigger": "Nhịp hiện tại tạo một dạng ma sát trực tiếp với cấu trúc ngày sinh; nên giảm áp lực và xử lý từng điểm nghẽn.",
            "cong_viec": "Nên giảm việc làm song song quá nhiều, rà quy trình và xử lý một điểm nghẽn mỗi lần.",
            "tai_chinh": "Không có căn cứ riêng để gọi là xấu về tiền; tránh quyết định khi đang căng thẳng hoặc muốn xử lý quá nhanh.",
            "quan_he": "Dễ căng vì cách làm hoặc cách nói hơn là vì bản chất vấn đề; nên hạ nhịp và tách người khỏi việc khi trao đổi.",
            "viec_lon": "Nếu có nhiều ràng buộc chưa rõ, nên hoàn tất checklist trước khi đưa ra cam kết khó đảo ngược.",
            "focus": ["Giảm quá tải và xử lý từng điểm nghẽn", "Hoàn tất checklist trước quyết định quan trọng"],
        }
    return {**base,
        "headline": f"{horizon.capitalize()} chưa có tín hiệu quan hệ nổi bật",
        "trigger": "Ở lớp quan hệ trực tiếp hiện dùng, chưa thấy tín hiệu đủ nổi bật để ưu tiên hay cảnh báo riêng.",
        "cong_viec": "Có thể xử lý theo kế hoạch bình thường; nếu là việc quan trọng, nên xét riêng theo loại việc thay vì dựa vào nhịp chung.",
        "tai_chinh": "Chưa có tín hiệu riêng để kết luận thuận/nghịch về tài chính.",
        "quan_he": "Chưa thấy quan hệ Địa Chi trực tiếp đủ mạnh để đưa ra cảnh báo hoặc ưu tiên riêng.",
        "viec_lon": "Không dùng trạng thái này như một xác nhận rằng mọi việc đều tốt; hãy chọn ngày theo đúng loại việc nếu cần chốt thời điểm.",
        "focus": ["Giữ kế hoạch bình thường", "Việc lớn: xét riêng theo đúng loại việc"],
    }


def danh_gia_giai_doan(chi_menh_ngay: str, chi_hien_tai: str, scope: str) -> dict:
    qh = quan_he_chi(chi_menh_ngay, chi_hien_tai)
    dg = _dien_giai_ung_dung(qh, scope)
    if qh.muc == "POSITIVE":
        label, state = "Khá thuận", "THUAN"
    elif qh.muc == "CAUTION":
        label, state = "Có điểm cần lưu ý", "CAN_NHAC"
    else:
        label, state = "Chưa có tín hiệu nổi bật", "TRUNG_TINH"
    return {
        "scope": scope, "state": state, "label": label, "relation": qh.__dict__,
        "recommended": list(dg["focus"]),
        "caution": [dg["khong_suy_dien"]],
        "confidence": "MEDIUM" if qh.ma != "NONE" else "LOW",
        "basis": dg["headline"],
        "dien_giai": dg,
    }

def danh_gia_event(chi_thang: str, chi_ngay: str, chi_menh_ngay: str, event_code: str) -> dict:
    code = chuan_hoa_event(event_code)
    rule = EVENT_RULES.get(code or "")
    if not rule:
        return {"support_level":"NO_RULE","label":"Chưa hỗ trợ","rank_group":9,"score":None}
    truc = tinh_truc(chi_thang, chi_ngay)
    if truc in rule.ji_truc:
        event_state = "JI"
    elif truc in rule.yi_truc:
        event_state = "YI"
    else:
        event_state = "NEUTRAL"
    qh = quan_he_chi(chi_menh_ngay, chi_ngay)

    # Chính sách hợp lưu rời rạc: kỵ theo việc có ưu tiên cao nhất; sau đó mới đến
    # ngày được sách nêu là宜; quan hệ cá nhân chỉ dùng để phân hạng trong cùng lớp.
    if event_state == "JI":
        group, label = 5, "Không ưu tiên"
    elif event_state == "YI" and qh.muc == "POSITIVE" and rule.mapping_status == "VERIFIED":
        group, label = 0, "Ưu tiên"
    elif event_state == "YI" and rule.mapping_status == "VERIFIED":
        group, label = 1, "Phù hợp"
    elif event_state == "YI":
        # Ánh xạ hiện đại còn PROVISIONAL: không được nâng thành “Phù hợp” mạnh.
        group, label = 2, "Có thể cân nhắc"
    elif qh.muc == "POSITIVE":
        # Quan hệ cá nhân chỉ phá hòa trong lớp sự kiện trung tính; không được
        # nâng thành “ngày tốt cho việc” khi Hiệp Kỷ chưa nêu Trực này là 宜.
        group, label = 2, "Có thể cân nhắc"
    elif qh.muc == "CAUTION":
        group, label = 4, "Cân nhắc"
    else:
        group, label = 3, "Chưa có tín hiệu nổi bật"

    reasons = [f"Ngày thuộc Trực {TRUC_VI[truc]} trong tháng hiện tại."]
    if event_state == "YI": reasons.append(f"Trực {TRUC_VI[truc]} nằm trong nhóm được nêu là phù hợp cho {rule.ten} ở lớp quy tắc V1-basic.")
    if event_state == "JI": reasons.append(f"Trực {TRUC_VI[truc]} nằm trong nhóm cần tránh cho {rule.ten} ở lớp quy tắc V1-basic.")
    if qh.ma != "NONE": reasons.append(qh.mo_ta)
    if rule.mapping_status == "PROVISIONAL":
        reasons.append("Ánh xạ từ việc hiện đại sang mục cổ thư đang ở trạng thái PROVISIONAL; nhãn được hạ mức tin cậy.")
    return {
        "support_level":"ACTIVE_BASIC", "event_code":code, "event_name":rule.ten,
        "classical_event":rule.classical, "mapping_status":rule.mapping_status,
        "truc":truc, "truc_vi":TRUC_VI[truc], "event_state":event_state,
        "personal_relation":qh.__dict__, "label":label, "rank_group":group,
        "score":None, "scoring_status":"ORDINAL_RULESET_V1",
        "reasons":reasons,
        "source_id":SRC_HK11, "source_location":rule.source_location,
        "event_note":rule.note or None,
        "coverage":"PARTIAL_12_TRUC_ONLY",
        "confidence":"MEDIUM" if rule.mapping_status == "VERIFIED" else "LOW",
        "coverage_note":"Đã dùng phần 12 Trực được nêu trực tiếp trong mục 宜/忌; các cát/hung thần khác của Hiệp Kỷ chưa được đưa vào lớp xếp hạng này.",
        "rule_ids":["HK-GENERAL-0001", f"HK-EVENT-{list(EVENT_RULES).index(code)+1:04d}", qh.rule_id, "FUS-V1-0001"],
    }


def xep_hang(ds: Iterable[dict]) -> list[dict]:
    return sorted(ds, key=lambda x: (x.get("rank_group",9), x.get("ngay","")))
