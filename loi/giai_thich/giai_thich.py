"""Giải thích hai tầng cho release 0.5.0.

Tầng 1 chỉ dùng lời thường. Tầng 2 giữ thuật ngữ và truy nguồn.
"""
from __future__ import annotations
from typing import Any
from loi.hop_luu.hop_luu import UNKNOWN, KetQuaHopLuu

NHAN_VI={UNKNOWN:"Chưa đủ căn cứ để kết luận"}


def tang_1(kq:KetQuaHopLuu,scope:str="day")->dict[str,Any]:
    d=kq.to_dict()
    if scope=="month":
        dg=d["month_state"].get("danh_gia",{}); cau=f"Tháng hiện tại của {d['person']}: {dg.get('label',d['label'])}."
    elif scope=="day":
        dg=d["day_state"].get("danh_gia",{}); cau=f"Ngày {d['period']} của {d['person']}: {dg.get('label',d['label'])}."
    else:
        dg={}; cau=d["label"] if d["label"]!=UNKNOWN else "Chưa đủ căn cứ để kết luận."
    quan_sat=["Bốn trụ của bạn: "+", ".join(v["vi"] for v in d["base_state"]["tu_tru"].values())+"."]
    if d["decade_state"].get("tru"):
        dv=d["decade_state"]; quan_sat.append(f"Bạn đang ở giai đoạn mười năm {dv['tru']}, năm thứ {dv['nam_thu_may']} trên {dv['tong_so_nam']}, mốc đang dùng khoảng {dv.get('ngay_bat_dau',dv['nam_bat_dau'])} đến {dv.get('ngay_ket_thuc',dv['nam_ket_thuc'])}.")
    quan_sat.append(f"Năm hiện tại là {d['year_state']['tru']['vi']}, tháng hiện tại là {d['month_state']['tru']['vi']}.")
    if scope=="day" and d["day_state"].get("tru_ngay"): quan_sat.append(f"Ngày đang xem là {d['day_state']['tru_ngay']}.")
    nen=list(dg.get("recommended",d["recommended"]) or d["recommended"]); can=list(dg.get("caution",d["caution"]) or d["caution"]); khong=list(d["avoid"])
    descriptive=dg.get("state")=="DESCRIPTIVE_ONLY"
    if descriptive: nen,can=[],[]
    chua=["Điểm số 0–10 chưa dùng vì chưa có bộ hiệu chỉnh được duyệt."]
    chua.append("Trường hợp này chưa đủ căn cứ để kết luận thuận hay nghịch cho cá nhân." if descriptive else "Một số lớp phụ vẫn chưa được dùng; kết quả hiện chỉ dựa trên các quy tắc đã nghiệm thu.")
    # Cố ý không nhúng object methodology/technical trigger vào tầng 1.
    return {"tieu_de":cau,"tom_tat":dg.get("label",d["label"]),"co_ket_luan_co_ban":not descriptive,"co_ket_luan_ca_nhan_thuan_nghich":not descriptive,"vi_sao":"Kết quả được hợp lưu từ các lớp đã nghiệm thu; xem Chuyên sâu để truy nguồn.","dien_giai":{"headline":cau,"ghi_chu":"Chi tiết kỹ thuật được tách sang mục Chuyên sâu."},"vi_sao_chua_cham_diem":"Điểm số 0–10 chưa hiệu chỉnh; app dùng nhãn thứ bậc có truy nguồn.","he_thong_biet_gi":quan_sat,"he_thong_chua_biet_gi":chua,"diem_thuan_loi":[x["mo_ta"] for x in d["positive_factors"]],"diem_can_luu_y":[x["mo_ta"] for x in d["negative_factors"]],"nen_lam":nen,"can_nhac":can,"khong_uu_tien":khong,"confidence":d["confidence"],"scoring_status":d["scoring_status"],"canh_bao_trung_thuc":("Chưa đủ căn cứ để kết luận cá nhân ở trường hợp này; app không tự lấp chỗ trống." if descriptive else "Kết luận chỉ dùng các lớp đã có căn cứ; phần chưa đủ nguồn không được suy rộng thành dự báo chắc chắn.")}


def tang_2(kq:KetQuaHopLuu)->dict[str,Any]:
    d=kq.to_dict()
    return {"menh":d["base_state"],"dai_van":d["decade_state"],"nam":d["year_state"],"thang":d["month_state"],"ngay":d["day_state"],"gio":d["hour_state"],"hiep_ky":d["event_state"],"than_sat":{"status":UNKNOWN,"ly_do":"Nhóm Thần sát chưa được dùng trong quyết định V1."},"hop_luu":{"score":d["score"],"label":d["label"],"confidence":d["confidence"],"scoring_status":d["scoring_status"]},"yeu_to":{"positive":d["positive_factors"],"negative":d["negative_factors"],"conflicts":d["conflicts"]},"chua_du_can_cu":d["uncertainties"],"rule_trace":d["rule_trace"],"source_trace":d["source_trace"]}


def truy_nguoc_day_du(conn,kq:KetQuaHopLuu)->list[dict[str,Any]]:
    chuoi=[]
    for rid in sorted(set(kq.rule_trace)):
        rows=conn.execute("""SELECT r.rule_id,r.name_vi,rv.version,rv.status,rv.confidence,s.source_id,s.title,s.edition_certainty,s.independence_group,rvs.source_level,rvs.source_location,p.passage_id,p.original_text FROM rule_registry r JOIN rule_versions rv ON rv.rule_id=r.rule_id LEFT JOIN rule_version_sources rvs ON rvs.rule_version_id=rv.rule_version_id LEFT JOIN sources s ON s.source_id=rvs.source_id LEFT JOIN rule_version_passages rvp ON rvp.rule_version_id=rv.rule_version_id LEFT JOIN source_passages p ON p.passage_id=rvp.passage_id WHERE r.rule_id=? AND (rvs.source_level='PRIMARY' OR rvs.source_level IS NULL) ORDER BY rv.version DESC LIMIT 1""",(rid,)).fetchall()
        for r in rows:
            chuoi.append({"rule_id":r["rule_id"],"name_vi":r["name_vi"],"rule_version":f"{r['rule_id']}@{r['version']}","verification_status":r["status"],"confidence":r["confidence"],"source_id":r["source_id"],"source_title":r["title"],"edition_certainty":r["edition_certainty"],"independence_group":r["independence_group"],"source_location":r["source_location"],"passage_id":r["passage_id"],"passage_excerpt":((r["original_text"] or "")[:80] or None)})
    return chuoi
