"""Nạp các nguồn/quy tắc tối thiểu cho lớp quyết định V1-basic.

Các quy tắc cổ thư ở đây chỉ gồm những gì đã có thể xác minh trực tiếp từ
bản chép công khai của Khâm Định Hiệp Kỷ Biện Phương Thư và Tam Mệnh Thông Hội.
Chính sách hợp lưu là quy tắc sản phẩm riêng, không giả là cổ thư.
"""
from __future__ import annotations

import json
import sqlite3

from loi.quyet_dinh.v1 import EVENT_RULES

SOURCES = [
    {
        "source_id":"SRC-HK-QD-V11-WIKISOURCE",
        "title":"Khâm Định Hiệp Kỷ Biện Phương Thư — quyển 11 (dụng sự)",
        "author":"Doãn Lộc, Mai Giác Thành và nhóm biên soạn",
        "dynasty_or_year":"Thanh",
        "edition":"Tứ Khố Toàn Thư bản — bản chép số hóa Wikisource",
        "language":"zh-Hans",
        "source_type":"CLASSICAL_TEXT_TRANSCRIPTION",
        "url_or_file_reference":"https://zh.wikisource.org/zh-hans/欽定協紀辨方書_(四庫全書本)/卷11",
        "primary_or_secondary":"PRIMARY",
        "edition_certainty":"TRANSCRIPTION_ONLY",
        "provenance_note":"Bản chép số hóa công khai; đã trực tiếp đối chiếu mục dụng sự và các dòng 宜/忌.",
        "independence_group":"CLASSICAL_TEXT",
        "status":"ACTIVE",
        "notes":"Dùng cho event mapping và tập Trực được nêu trực tiếp trong từng mục. Không suy thêm các thần chưa cài công thức.",
    },
    {
        "source_id":"SRC-HK-QD-V04-KANRIPO",
        "title":"Khâm Định Hiệp Kỷ Biện Phương Thư — quyển 4 (Kiến Trừ)",
        "author":"Doãn Lộc, Mai Giác Thành và nhóm biên soạn",
        "dynasty_or_year":"Thanh",
        "edition":"Bản chép Kanripo",
        "language":"zh-Hant",
        "source_type":"CLASSICAL_TEXT_TRANSCRIPTION",
        "url_or_file_reference":"https://www.kanripo.org/text/KR3g0051/004",
        "primary_or_secondary":"PRIMARY",
        "edition_certainty":"TRANSCRIPTION_ONLY",
        "provenance_note":"Bản chép số hóa; đã đối chiếu đoạn nêu thứ tự 建除滿平定執破危成收開閉 và cách khởi từ月建.",
        "independence_group":"CLASSICAL_TEXT",
        "status":"ACTIVE",
        "notes":"Dùng cho công thức 12 Trực.",
    },
    {
        "source_id":"SRC-TMTH-V02-WIKISOURCE",
        "title":"Tam Mệnh Thông Hội — quyển 2",
        "author":"Vạn Dân Anh",
        "dynasty_or_year":"Minh",
        "edition":"Tứ Khố Toàn Thư bản — bản chép số hóa",
        "language":"zh-Hant",
        "source_type":"CLASSICAL_TEXT_TRANSCRIPTION",
        "url_or_file_reference":"https://zh.wikisource.org/wiki/三命通會/卷二",
        "primary_or_secondary":"PRIMARY",
        "edition_certainty":"TRANSCRIPTION_ONLY",
        "provenance_note":"Đã đối chiếu các mục 支元六合, 冲击, 六害, 三刑.",
        "independence_group":"CLASSICAL_TEXT",
        "status":"ACTIVE",
        "notes":"Dùng để nhận diện quan hệ Địa Chi; không dùng để khẳng định cát/hung tuyệt đối.",
    },
    {
        "source_id":"SRC-PRODUCT-V1-SPEC",
        "title":"Đặc tả sản phẩm Tử Bình Gia Đình V1",
        "author":"Product specification",
        "dynasty_or_year":"2026",
        "edition":"V1 decision policy",
        "language":"vi",
        "source_type":"OTHER",
        "url_or_file_reference":"tai_lieu/PHAM-VI-V1-DA-CHOT.md",
        "primary_or_secondary":"PRIMARY",
        "edition_certainty":"NOT_APPLICABLE",
        "provenance_note":"Quy tắc sản phẩm nội bộ, không phải cổ thư.",
        "independence_group":"NONE",
        "status":"ACTIVE",
        "notes":"Ưu tiên rule theo việc trước, quan hệ cá nhân sau; xếp hạng rời rạc, không trọng số.",
    },
]



PASSAGES = {
    "BT-REL-0001": ("SRC-TMTH-V02-WIKISOURCE", "Quyển 2 · 論支元六合",
        "夫合者和也……子合丑，寅合亥……卯與戌合，辰與酉合，巳與申合，午與未合。",
        "Hợp là hòa; các cặp Lục hợp gồm Tý–Sửu, Dần–Hợi, Mão–Tuất, Thìn–Dậu, Tị–Thân, Ngọ–Mùi."),
    "BT-REL-0002": ("SRC-TMTH-V02-WIKISOURCE", "Quyển 2 · 論沖擊",
        "地支取七位為沖……如子午對沖……可見沖破有吉有凶，不可概論。",
        "Địa Chi cách bảy vị thành xung, như Tý–Ngọ; xung có thể có cát hoặc hung, không được luận tuyệt đối."),
    "BT-REL-0003": ("SRC-TMTH-V02-WIKISOURCE", "Quyển 2 · 論六害",
        "六害者，十二支凌戰之辰也。子未相害，丑午相害，寅巳相害，卯辰相害，申亥相害，酉戌相害。",
        "Lục hại là sáu cặp Địa Chi tương hại: Tý–Mùi, Sửu–Ngọ, Dần–Tị, Mão–Thìn, Thân–Hợi, Dậu–Tuất."),
    "BT-REL-0004": ("SRC-TMTH-V02-WIKISOURCE", "Quyển 2 · 論三刑",
        "子卯一刑也，寅巳申一刑也，丑未戌一刑也……辰午酉亥……自刑。",
        "Ghi nhận các nhóm Hình Tý–Mão, Dần–Tị–Thân, Sửu–Mùi–Tuất và tự hình Thìn/Ngọ/Dậu/Hợi."),
    "HK-GENERAL-0001": ("SRC-HK-QD-V04-KANRIPO", "Quyển 4 · 建除",
        "建除滿平定執破危成收開閉凡十二日周而復始……正月建寅則寅日起建順行十二辰。",
        "Mười hai Trực tuần hoàn; lấy chi tháng làm Trực Kiến rồi thuận theo mười hai chi."),
}

EVENT_PASSAGE_TEXT = {
    "KHAI_TRUONG": ("開市：宜……滿日成日開日……忌月破……平日收日閉日。", "Khai thị: trong lớp Trực, Mãn/Thành/Khai được nêu ở mục nên; Nguyệt phá/Bình/Thu/Bế ở mục kỵ."),
    "KY_HOP_DONG": ("立券交易：宜……滿日……忌月破……平日收日。", "Lập khế/giao dịch: Mãn được nêu ở mục nên; Nguyệt phá/Bình/Thu ở mục kỵ."),
    "MUA_TAI_SAN": ("納財：宜……滿日收日……忌月破……平日。", "Nạp tài: Mãn/Thu được nêu ở mục nên; Nguyệt phá/Bình ở mục kỵ."),
    "DONG_THO": ("興造動土：宜……開日；忌月建……月破平日收日閉日。", "Động thổ/tu tạo: Khai được nêu ở mục nên; Kiến/Nguyệt phá/Bình/Thu/Bế ở mục kỵ."),
    "NHAP_TRACH": ("般移〈移徙同〉：宜……成日開日；忌月破平日收日閉日。", "Dời/chuyển nhà: Thành/Khai được nêu ở mục nên; Nguyệt phá/Bình/Thu/Bế ở mục kỵ."),
    "CUOI_HOI": ("嫁娶：宜……三合天喜六合不將；忌月破平日收日閉日……", "Giá thú: mục nên dựa nhiều cát thần; ở lớp Trực, Phá/Bình/Thu/Bế nằm trong mục kỵ."),
    "XUAT_HANH": ("行幸遣使〈出行同〉：宜……建日……開日；忌月破平日收日閉日。", "Xuất hành: Kiến/Khai được nêu ở mục nên; Nguyệt phá/Bình/Thu/Bế ở mục kỵ."),
    "DIEU_TRI": ("求醫療病：宜……除日破日……開日；忌月建平日收日滿日閉日。", "Cầu y trị bệnh: Trừ/Phá/Khai được nêu ở mục nên; Kiến/Bình/Thu/Mãn/Bế ở mục kỵ."),
    "DAM_PHAN": ("宴會〈會親友同〉：宜……開日……；忌月破平日收日閉日。", "Hội thân hữu: Khai được nêu ở mục nên; Nguyệt phá/Bình/Thu/Bế ở mục kỵ."),
    "NHAM_CHUC": ("上官赴任：宜……建日……開日；忌月破平日收日滿日閉日。", "Nhậm chức: Kiến/Khai được nêu ở mục nên; Nguyệt phá/Bình/Thu/Mãn/Bế ở mục kỵ."),
    "THI_CU": ("入學：宜成日開日；忌無。", "Nhập học: Thành/Khai được nêu ở mục nên; không ghi mục kỵ."),
    "CAU_TAI": ("納財：宜……滿日收日……忌月破……平日。", "Cầu tài/nạp tài: Mãn/Thu được nêu ở mục nên; Nguyệt phá/Bình ở mục kỵ."),
    "AN_TANG": ("安葬：宜……六合鳴吠；忌月建月破平日收日……", "An táng: lớp V1-basic chỉ lấy các Trực được ghi ở mục kỵ; cát thần chuyên biệt chưa được tính."),
}

REL_RULES = [
    ("BT-REL-0001","BT-REL","Lục hợp Địa Chi","VERIFIED","MEDIUM","SRC-TMTH-V02-WIKISOURCE","Quyển 2 · Luận Chi nguyên Lục hợp"),
    ("BT-REL-0002","BT-REL","Lục xung Địa Chi","VERIFIED","MEDIUM","SRC-TMTH-V02-WIKISOURCE","Quyển 2 · Luận xung kích"),
    ("BT-REL-0003","BT-REL","Lục hại Địa Chi","VERIFIED","MEDIUM","SRC-TMTH-V02-WIKISOURCE","Quyển 2 · Luận Lục hại"),
    ("BT-REL-0004","BT-REL","Hình Địa Chi","VERIFIED","MEDIUM","SRC-TMTH-V02-WIKISOURCE","Quyển 2 · Luận Tam hình"),
]


def _source(conn: sqlite3.Connection, s: dict) -> None:
    conn.execute(
        """INSERT INTO sources (source_id,title,author,dynasty_or_year,edition,language,source_type,
               url_or_file_reference,primary_or_secondary,edition_certainty,provenance_note,
               independence_group,status,notes)
           VALUES (:source_id,:title,:author,:dynasty_or_year,:edition,:language,:source_type,
               :url_or_file_reference,:primary_or_secondary,:edition_certainty,:provenance_note,
               :independence_group,:status,:notes)
           ON CONFLICT(source_id) DO UPDATE SET title=excluded.title, url_or_file_reference=excluded.url_or_file_reference,
               status=excluded.status, notes=excluded.notes, provenance_note=excluded.provenance_note""", s)




def _passage(conn: sqlite3.Connection, passage_id: str, source_id: str, chapter: str, original: str, translation: str, rule_version_id: str) -> None:
    conn.execute(
        """INSERT INTO source_passages(passage_id,source_id,chapter,original_text,translation_vi,derivation_note)
           VALUES(?,?,?,?,?,?)
           ON CONFLICT(passage_id) DO UPDATE SET original_text=excluded.original_text,translation_vi=excluded.translation_vi,derivation_note=excluded.derivation_note""",
        (passage_id, source_id, chapter, original, translation,
         "Trích đoạn ngắn dùng để truy nguyên đúng phần logic V1-basic; không đại diện toàn bộ quy tắc của mục cổ thư."))
    conn.execute(
        """INSERT INTO rule_version_passages(rule_version_id,passage_id) VALUES(?,?) ON CONFLICT DO NOTHING""",
        (rule_version_id, passage_id))

def _rule(conn, rid, ns, name, status, confidence, source_id, location, logic, effect="EXPLANATORY", priority=100):
    conn.execute("""INSERT INTO rule_registry(rule_id,rule_group,namespace,name_vi,name_original,active_version,is_active)
                    VALUES(?,?,?,?,NULL,1,1)
                    ON CONFLICT(rule_id) DO UPDATE SET name_vi=excluded.name_vi,is_active=1,updated_at=datetime('now')""",
                 (rid,ns,ns,name))
    rvid=f"{rid}@1"
    conn.execute("""INSERT INTO rule_versions(rule_version_id,rule_id,version,status,confidence,inputs,preconditions,logic,outputs,
                    effect_class,priority,block_type,severity,mitigatable,notes)
                    VALUES(?,?,1,?,?,'[]','[]',?,'[]',?,?, 'NONE','MINOR',0,?)
                    ON CONFLICT(rule_version_id) DO UPDATE SET status=excluded.status,confidence=excluded.confidence,
                    logic=excluded.logic,effect_class=excluded.effect_class,priority=excluded.priority,notes=excluded.notes""",
                 (rvid,rid,status,confidence,json.dumps(logic,ensure_ascii=False),effect,priority,
                  "Quy tắc V1-basic; không được diễn giải vượt phạm vi logic đã ghi."))
    conn.execute("""INSERT INTO rule_version_sources(rule_version_id,source_id,source_location,source_level,logic_note)
                    VALUES(?,?,?,'PRIMARY',?)
                    ON CONFLICT(rule_version_id,source_id,source_level) DO UPDATE SET source_location=excluded.source_location,
                    logic_note=excluded.logic_note""",
                 (rvid,source_id,location,"Chuyển trực tiếp sang logic nhận diện/xếp lớp; không thêm trọng số."))


def nap(conn: sqlite3.Connection) -> None:
    for s in SOURCES:
        _source(conn,s)
    for rid,ns,name,status,conf,sid,loc in REL_RULES:
        _rule(conn,rid,ns,name,status,conf,sid,loc,{"type":"BRANCH_RELATION_RECOGNITION"})
        psid, chapter, original, trans = PASSAGES[rid]
        _passage(conn, f"P-{rid}", psid, chapter, original, trans, f"{rid}@1")
    _rule(conn,"HK-GENERAL-0001","HK-GENERAL","Khởi 12 Trực từ chi tháng","VERIFIED","HIGH",
          "SRC-HK-QD-V04-KANRIPO","Quyển 4 · Kiến Trừ",
          {"sequence":["KIEN","TRU","MAN","BINH","DINH","CHAP","PHA","NGUY","THANH","THU","KHAI","BE"],"anchor":"month_branch=KIEN"})
    psid, chapter, original, trans = PASSAGES["HK-GENERAL-0001"]
    _passage(conn, "P-HK-GENERAL-0001", psid, chapter, original, trans, "HK-GENERAL-0001@1")

    for idx,(code,ev) in enumerate(EVENT_RULES.items(), start=1):
        rid=f"HK-EVENT-{idx:04d}"
        status="VERIFIED" if ev.mapping_status=="VERIFIED" else "PROVISIONAL"
        _rule(conn,rid,"HK-EVENT",f"Hiệp Kỷ V1-basic · {ev.ten}",status,"MEDIUM",
              "SRC-HK-QD-V11-WIKISOURCE",ev.source_location,
              {"event_code":code,"classical_event":ev.classical,"yi_truc":sorted(ev.yi_truc),"ji_truc":sorted(ev.ji_truc),"coverage":"12_TRUC_SUBSET"},
              effect="EXPLANATORY",priority=40)
        original, trans = EVENT_PASSAGE_TEXT[code]
        _passage(conn, f"P-{rid}", "SRC-HK-QD-V11-WIKISOURCE", ev.source_location, original, trans, f"{rid}@1")
        pack_id=f"ERP-{code}"
        conn.execute("""INSERT INTO event_rule_packs(event_rule_pack_id,code,name_vi,name_original,version,status,notes)
                        VALUES(?,?,?,?,1,'ACTIVE',?)
                        ON CONFLICT(event_rule_pack_id) DO UPDATE SET status='ACTIVE',notes=excluded.notes,updated_at=datetime('now')""",
                     (pack_id,code,ev.ten,ev.classical,"V1-basic: chỉ các Trực được nêu trực tiếp trong mục 宜/忌; coverage PARTIAL."))
        conn.execute("""INSERT INTO event_rule_pack_rules(event_rule_pack_id,rule_version_id,role)
                        VALUES(?,?, 'REQUIRED') ON CONFLICT DO NOTHING""",(pack_id,f"{rid}@1"))
        # event_types đã được nạp từ namespace yaml.
        row=conn.execute("SELECT event_type_id FROM event_types WHERE code=?",(code,)).fetchone()
        if row:
            conn.execute("UPDATE event_types SET status='ACTIVE',notes=? WHERE code=?",
                         ("V1-basic có xếp hạng theo 12 Trực; chưa bao phủ toàn bộ thần Hiệp Kỷ.",code))
            conn.execute("""INSERT INTO event_mappings(event_mapping_id,event_type_id,classical_event,event_rule_pack_id,
                            source_id,source_location,status,notes)
                            VALUES(?,?,?,?,?,?,?,?)
                            ON CONFLICT(event_type_id,classical_event) DO UPDATE SET event_rule_pack_id=excluded.event_rule_pack_id,
                            status=excluded.status,notes=excluded.notes""",
                         (f"MAP-{code}",row["event_type_id"],ev.classical,pack_id,"SRC-HK-QD-V11-WIKISOURCE",
                          ev.source_location,ev.mapping_status,ev.note or "Ánh xạ trực tiếp."))
    _rule(conn,"FUS-V1-0001","FUS","Chính sách hợp lưu rời rạc V1-basic","PROVISIONAL","HIGH",
          "SRC-PRODUCT-V1-SPEC","V1 decision policy",
          {"order":["EVENT_JI","EVENT_YI","PERSONAL_RELATION"],"numeric_weight":False,"hard_rule":"event JI cannot be overturned by personal positive relation"},
          effect="EXPLANATORY",priority=10)
    _rule(conn,"FUS-V1-REL-0001","FUS","Không có quan hệ trực tiếp trong lớp V1","PROVISIONAL","HIGH",
          "SRC-PRODUCT-V1-SPEC","V1 decision policy",{"type":"NEUTRAL_FALLBACK"})
    conn.commit()
