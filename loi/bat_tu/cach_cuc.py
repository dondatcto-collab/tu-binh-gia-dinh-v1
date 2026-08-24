"""Engine Cách cục/Dụng-Hỷ-Kỵ V1 theo nền ZPZQ đã khóa.

Không dùng thứ tự Tàng Can như một proxy cho chủ khí. Với tháng không tạp khí,
chủ khí được khóa tường minh theo chi tháng; tháng tạp khí vẫn xét thấu/hội.
Không dùng điểm số.
"""
from __future__ import annotations
from typing import Any
from loi.bat_tu.tang_can import lay_tang_can
from loi.bat_tu.thap_than import tinh_thap_than

TAQI = {"THIN","TUAT","SUU","MUI"}
YANG_REN = {"GIAP":"MAO","BINH":"NGO","MAU":"NGO","CANH":"DAU","NHAM":"TY"}
JIAN_LU = {"GIAP":"DAN","AT":"MAO","BINH":"TI","DINH":"NGO","MAU":"TI","KY":"NGO","CANH":"THAN","TAN":"DAU","NHAM":"HOI","QUY":"TY"}
# Chủ khí khóa tường minh; tuyệt đối không suy từ hidden_stems[0].
MONTH_MAIN_QI = {
    "TY":"QUY", "DAN":"GIAP", "MAO":"AT", "TI":"BINH",
    "NGO":"DINH", "THAN":"CANH", "DAU":"TAN", "HOI":"NHAM",
}
TG_TO_PATTERN = {
    "CHINH_QUAN":"ZHENG_GUAN", "THIEN_TAI":"CAI", "CHINH_TAI":"CAI",
    "CHINH_AN":"YIN", "THIEN_AN":"YIN", "THUC_THAN":"SHI_SHEN",
    "THAT_SAT":"QI_SHA", "THUONG_QUAN":"SHANG_GUAN",
}
PATTERN_VI = {
    "ZHENG_GUAN":"Chính Quan", "CAI":"Tài", "YIN":"Ấn", "SHI_SHEN":"Thực Thần",
    "QI_SHA":"Thất Sát", "SHANG_GUAN":"Thương Quan", "YANG_REN":"Dương Nhận",
    "JIAN_LU_YUE_JIE":"Kiến Lộc/Nguyệt Kiếp", "AMBIGUOUS":"Chưa khóa được Cách cục",
}
FAVOR = {
    "ZHENG_GUAN":{"CHINH_TAI","THIEN_TAI","CHINH_AN","THIEN_AN"},
    "CAI":{"CHINH_QUAN","THUC_THAN"},
    "YIN":{"THUC_THAN","THUONG_QUAN","THAT_SAT","CHINH_QUAN"},
    "SHI_SHEN":{"CHINH_TAI","THIEN_TAI","THAT_SAT"},
    "QI_SHA":{"CHINH_AN","THIEN_AN","THUC_THAN"},
    "SHANG_GUAN":{"CHINH_TAI","THIEN_TAI","CHINH_AN","THIEN_AN"},
    "YANG_REN":{"CHINH_QUAN","THAT_SAT","CHINH_TAI","THIEN_TAI"},
    "JIAN_LU_YUE_JIE":{"CHINH_QUAN","THAT_SAT","CHINH_TAI","THIEN_TAI","THUC_THAN","THUONG_QUAN"},
}
AVOID = {
    "ZHENG_GUAN":{"THUONG_QUAN"}, "CAI":{"TY_KIEN","KIEP_TAI"},
    "YIN":{"CHINH_TAI","THIEN_TAI"}, "SHI_SHEN":{"THIEN_AN"},
    "QI_SHA":{"CHINH_TAI","THIEN_TAI"}, "SHANG_GUAN":{"CHINH_QUAN"},
    "YANG_REN":{"THUONG_QUAN"}, "JIAN_LU_YUE_JIE":set(),
}

def _visible_stems(tu_tru: dict) -> list[str]:
    return [tu_tru[k].can for k in ("nam","thang","ngay","gio")]

def _select_pattern(conn, tu_tru: dict, nhat_chu: str) -> tuple[str, list[str], str]:
    month = tu_tru["thang"]
    chi = month.chi
    if nhat_chu in YANG_REN and YANG_REN[nhat_chu] == chi:
        return "YANG_REN", ["GEJU-040"], "Chi tháng đúng vị trí Dương Nhận của Nhật chủ."
    if JIAN_LU.get(nhat_chu) == chi:
        return "JIAN_LU_YUE_JIE", ["GEJU-040"], "Chi tháng đúng vị trí Kiến Lộc/Nguyệt Kiếp của Nhật chủ."
    hidden = list(lay_tang_can(conn, chi).hidden_stems)
    if chi in TAQI:
        if month.can in hidden:
            tg = tinh_thap_than(conn, nhat_chu, month.can).ten_god
            return TG_TO_PATTERN.get(tg, "AMBIGUOUS"), ["GEJU-030"], "Tháng tạp khí: can tháng thấu trực tiếp từ tàng can của Nguyệt lệnh."
        vis = [s for s in _visible_stems(tu_tru) if s in hidden and s != nhat_chu]
        kinds = []
        for s in dict.fromkeys(vis):
            p = TG_TO_PATTERN.get(tinh_thap_than(conn, nhat_chu, s).ten_god)
            if p and p not in kinds:
                kinds.append(p)
        if len(kinds) == 1:
            return kinds[0], ["GEJU-030"], "Tháng tạp khí: một loại tàng can thấu rõ."
        return "AMBIGUOUS", ["GEJU-030"], "Tháng tạp khí chưa có một dụng rõ đủ để khóa Cách cục."
    main_qi = MONTH_MAIN_QI.get(chi)
    if not main_qi:
        return "AMBIGUOUS", ["GEJU-001"], "Chưa khóa chủ khí cho chi tháng này."
    if main_qi not in hidden:
        return "AMBIGUOUS", ["GEJU-001"], "Dữ liệu Tàng Can mâu thuẫn bảng chủ khí đã khóa."
    p = TG_TO_PATTERN.get(tinh_thap_than(conn, nhat_chu, main_qi).ten_god)
    if p:
        return p, ["GEJU-001","GEJU-020"], "Tháng không tạp khí: lấy chủ khí đã khóa tường minh của Nguyệt lệnh, không dựa thứ tự Tàng Can."
    return "AMBIGUOUS", ["GEJU-001"], "Chủ khí không rơi vào nhóm Cách cục lõi đã cài."

def _formation(conn, tu_tru: dict, nhat_chu: str, pattern: str) -> dict[str, Any]:
    if pattern=="AMBIGUOUS":
        return {"pattern_state":"AMBIGUOUS","key_structure":"Chưa đủ căn cứ để khóa thành/bại.","xiang_shen":[],"favorable_factors":[],"avoid_factors":[],"rescue_factors":[],"unresolved_conditions":["Cần thấu/hội rõ hơn ở Nguyệt lệnh."]}
    gods=[tinh_thap_than(conn, nhat_chu, tu_tru[k].can).ten_god for k in ("nam","thang","gio")]
    godset=set(gods); state="FORMED"; key=PATTERN_VI[pattern]; xiang=[]
    if pattern=="ZHENG_GUAN":
        key="Chính Quan đương lệnh; xét Tài/Ấn phối hợp toàn cục"; xiang=[x for x in ("CHINH_TAI","THIEN_TAI","CHINH_AN","THIEN_AN") if x in godset]
        if "THUONG_QUAN" in godset and not ({"CHINH_AN","THIEN_AN"}&godset): state="MIXED"
    elif pattern=="CAI":
        key="Tài cách; ưu tiên xét Tài sinh Quan hoặc được Thực sinh"; xiang=[x for x in ("CHINH_QUAN","THUC_THAN") if x in godset]
    elif pattern=="YIN":
        if {"THUC_THAN","THUONG_QUAN"}&godset: key="Ấn cách có Thực/Thương phát dụng để tiết tú khí"; xiang=list({"THUC_THAN","THUONG_QUAN"}&godset)
        else: key="Ấn cách; phải xét Quan/Sát hoặc tiết khí theo toàn cục"
    elif pattern=="SHI_SHEN":
        if {"CHINH_TAI","THIEN_TAI"}&godset: key="Thực Thần sinh Tài"; xiang=list({"CHINH_TAI","THIEN_TAI"}&godset)
        else: key="Thực Thần cách; chưa thấy Tài thấu rõ"; state="MIXED"
    elif pattern=="QI_SHA":
        if {"CHINH_AN","THIEN_AN"}&godset: key="Thất Sát dùng Ấn; Sát–Ấn phối hợp"; xiang=list({"CHINH_AN","THIEN_AN"}&godset)
        elif "THUC_THAN" in godset: key="Thất Sát có chế"; xiang=["THUC_THAN"]
        else: key="Thất Sát chưa thấy cơ chế chế/hóa rõ"; state="MIXED"
    elif pattern=="SHANG_GUAN":
        if {"CHINH_TAI","THIEN_TAI"}&godset: key="Thương Quan dụng Tài"; xiang=list({"CHINH_TAI","THIEN_TAI"}&godset)
        elif {"CHINH_AN","THIEN_AN"}&godset: key="Thương Quan phối Ấn"; xiang=list({"CHINH_AN","THIEN_AN"}&godset)
        else: key="Thương Quan cách; chưa khóa phối dụng"; state="MIXED"
    elif pattern=="YANG_REN":
        if {"CHINH_QUAN","THAT_SAT"}&godset: key="Dương Nhận dùng Quan/Sát chế Nhận"; xiang=list({"CHINH_QUAN","THAT_SAT"}&godset)
        else: key="Dương Nhận chưa thấy Quan/Sát chế"; state="FAILED"
    elif pattern=="JIAN_LU_YUE_JIE":
        choices={"CHINH_QUAN","THAT_SAT","CHINH_TAI","THIEN_TAI","THUC_THAN","THUONG_QUAN"}&godset
        if choices: key="Kiến Lộc/Nguyệt Kiếp tìm Tài/Quan/Sát/Thực làm dụng"; xiang=list(choices)
        else: key="Kiến Lộc/Nguyệt Kiếp chưa thấy dụng ngoài Lộc/Kiếp"; state="MIXED"
    return {"pattern_state":state,"key_structure":key,"xiang_shen":sorted(xiang),"favorable_factors":sorted(FAVOR.get(pattern,set())),"avoid_factors":sorted(AVOID.get(pattern,set())),"rescue_factors":[],"unresolved_conditions":[]}

def phan_tich_menh_goc(conn, *, tu_tru: dict, nhat_chu: str) -> dict[str, Any]:
    pattern, rule_ids, reason = _select_pattern(conn, tu_tru, nhat_chu)
    f = _formation(conn,tu_tru,nhat_chu,pattern)
    return {"method_id":"ZPZQ-GEJU-V1","status":"READY" if pattern!="AMBIGUOUS" else "AMBIGUOUS","pattern":pattern,"pattern_vi":PATTERN_VI[pattern],"month_command":tu_tru["thang"].chi,"yong_shen_of_pattern":pattern if pattern!="AMBIGUOUS" else None,"selection_reason":reason,**f,"rule_ids":sorted(set(rule_ids+["XIJI-001","XIJI-002"])),"source_ids":["SRC-ZPZQ-NLC-SCAN","SRC-ZPZQ-DONGLI"],"no_numeric_score":True}

def phan_tich_hanh_van(conn, natal: dict[str,Any], nhat_chu: str, can: str, chi: str, scope: str) -> dict[str,Any]:
    if natal.get("status")!="READY":
        return {"scope":scope,"state":"AMBIGUOUS","stem_effect":"UNDETERMINED","branch_effect":"UNDETERMINED","label":"Chưa đủ căn cứ cá nhân","rule_ids":["TRANSIT-001"]}
    tg=tinh_thap_than(conn,nhat_chu,can).ten_god
    fav=set(natal.get("favorable_factors",[])); avoid=set(natal.get("avoid_factors",[]))
    stem="FAVORABLE" if tg in fav else "UNFAVORABLE" if tg in avoid else "NEUTRAL"
    hidden=lay_tang_can(conn,chi).hidden_stems
    bg=[tinh_thap_than(conn,nhat_chu,s).ten_god for s in hidden]
    bf=any(x in fav for x in bg); ba=any(x in avoid for x in bg)
    branch="MIXED" if bf and ba else "FAVORABLE" if bf else "UNFAVORABLE" if ba else "NEUTRAL"
    if stem=="UNFAVORABLE" or branch=="UNFAVORABLE": state="CAUTION"
    elif stem=="FAVORABLE" or branch=="FAVORABLE": state="SUPPORT"
    else: state="NEUTRAL"
    return {"scope":scope,"state":state,"label":{"SUPPORT":"Thuận nền mệnh","CAUTION":"Cần thận trọng","NEUTRAL":"Trung tính"}[state],"stem_ten_god":tg,"stem_effect":stem,"branch_hidden_ten_gods":bg,"branch_effect":branch,"rule_ids":["BT-DY-0401","TRANSIT-001"],"no_numeric_score":True}
