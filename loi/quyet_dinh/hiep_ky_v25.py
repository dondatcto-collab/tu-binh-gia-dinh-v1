"""V2.5 — kiểm kê quy tắc Hiệp Kỷ cho đúng 12 sự kiện hiện hành.

Giai đoạn này chỉ khóa dữ liệu nguồn, ánh xạ và thứ bậc. Các thần sát ngoài
12 Trực CHƯA được phép tác động vào quyết định cho tới khi có bộ tính tương
ứng và golden conflict tests.
"""
from __future__ import annotations

from dataclasses import dataclass

HK_V25_SOURCE_ID = "SRC-HK-QD-V11-WIKISOURCE"
HK_V25_SOURCE_TITLE = "欽定協紀辨方書（四庫全書本）卷十一 · 用事"
HK_V25_SOURCE_URL = "https://zh.wikisource.org/zh-hant/欽定協紀辨方書_(四庫全書本)/卷11"
HK_V25_COVERAGE = "SOURCE_INVENTORY_12_12_DECISION_ACTIVE_12_TRUC_ONLY"
HK_V25_NUMERIC_SCORE_STATUS = "LOCKED_OFF"
HK_V25_DECISION_HIERARCHY = "HARD_BLOCK > EVENT > PERSONAL"


@dataclass(frozen=True)
class HiepKyEventInventory:
    code: str
    classical: str
    mapping_status: str
    source_location: str
    yi_tokens: tuple[str, ...]
    ji_tokens: tuple[str, ...]
    decision_status: str = "INVENTORY_ONLY"
    source_id: str = HK_V25_SOURCE_ID
    numeric_score: None = None
    note: str = ""


HK_V25_EVENT_RULES: dict[str, HiepKyEventInventory] = {
    "KHAI_TRUONG": HiepKyEventInventory(
        "KHAI_TRUONG", "開市", "VERIFIED", "卷十一 · 開市",
        ("天願", "民日", "滿日", "成日", "開日", "五富"),
        ("月破", "大耗", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "大時", "天吏", "小耗", "四耗", "四廢", "四窮", "五墓", "九空"),
    ),
    "KY_HOP_DONG": HiepKyEventInventory(
        "KY_HOP_DONG", "立券交易", "VERIFIED", "卷十一 · 立券交易",
        ("天願", "民日", "三合", "滿日", "六合", "五富", "五合"),
        ("月破", "大耗", "平日", "收日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "大時", "天吏", "小耗", "四耗", "四廢", "四窮", "五墓", "九空", "五離"),
    ),
    "MUA_TAI_SAN": HiepKyEventInventory(
        "MUA_TAI_SAN", "修置產室 / 納財", "PROVISIONAL", "卷十一 · 修置產室; 納財",
        ("開日",),
        ("月建", "土府", "月破", "平日", "死神", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "大時", "天吏", "死氣", "四廢", "五墓", "土符", "地囊", "土王用事後"),
        note="Mua tài sản lớn là khái niệm hiện đại rộng; V2.5 chưa đồng nhất bất động sản, tài sản tài chính và nạp tài.",
    ),
    "DONG_THO": HiepKyEventInventory(
        "DONG_THO", "興造動土〈修造同〉", "VERIFIED", "卷十一 · 興造動土〈修造同〉",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "月恩", "四相", "時徳", "三合", "開日"),
        ("月建", "土府", "月破", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月厭", "大時", "天吏", "四廢", "五墓", "土符", "地囊", "土王用事後"),
    ),
    "NHAP_TRACH": HiepKyEventInventory(
        "NHAP_TRACH", "般移〈移徙同〉", "VERIFIED", "卷十一 · 般移〈移徙同〉",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "月恩", "四相", "時徳", "民日", "驛馬", "天馬", "成日", "開日"),
        ("月破", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月厭", "大時", "天吏", "四廢", "五墓", "歸忌", "往亡"),
    ),
    "CUOI_HOI": HiepKyEventInventory(
        "CUOI_HOI", "嫁娶", "VERIFIED", "卷十一 · 嫁娶",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "三合", "天喜", "六合", "不將"),
        ("月破", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "厭對", "大時", "天吏", "四廢", "四忌", "四窮", "五墓", "往亡", "八專", "亥日"),
    ),
    "XUAT_HANH": HiepKyEventInventory(
        "XUAT_HANH", "行幸遣使〈出行同〉", "VERIFIED", "卷十一 · 行幸遣使〈出行同〉",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "月恩", "四相", "時徳", "王日", "驛馬", "天馬", "建日", "吉期", "天喜", "開日"),
        ("月破", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月厭", "大時", "天吏", "天賊", "四廢", "五墓", "往亡", "巳日"),
    ),
    "DIEU_TRI": HiepKyEventInventory(
        "DIEU_TRI", "求醫療病", "VERIFIED", "卷十一 · 求醫療病",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "月恩", "四相", "時徳", "天后", "除日", "破日", "天醫", "開日", "解神", "除神"),
        ("月建", "平日", "死神", "收日", "滿日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "大時", "遊禍", "天吏", "死氣", "四廢", "五墓", "往亡", "未日", "每月十五日", "朔弦望日"),
        note="Chỉ dùng chọn ngày khi thời điểm y khoa linh hoạt; không trì hoãn cấp cứu hoặc điều trị cần thiết.",
    ),
    "DAM_PHAN": HiepKyEventInventory(
        "DAM_PHAN", "宴會〈會親友同〉", "PROVISIONAL", "卷十一 · 宴會〈會親友同〉",
        ("天徳", "月徳", "天徳合", "月徳合", "天恩", "天赦", "天願", "月恩", "四相", "時徳", "王日", "民日", "三合", "福徳", "天喜", "開日", "六合", "五合"),
        ("月破", "平日", "收日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "四廢", "五離", "酉日"),
        note="Đàm phán/họp là ánh xạ hiện đại từ hội thân hữu/yến hội; chưa coi là tương đương tuyệt đối.",
    ),
    "NHAM_CHUC": HiepKyEventInventory(
        "NHAM_CHUC", "上官赴任", "VERIFIED", "卷十一 · 上官赴任",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "月恩", "四相", "時徳", "王日", "官日", "守日", "相日", "臨日", "建日", "吉期", "天喜", "開日"),
        ("月破", "平日", "收日", "滿日", "閉日", "劫煞", "災煞", "月煞", "月刑", "月厭", "大時", "天吏", "四廢", "五墓", "往亡"),
    ),
    "CAU_TAI": HiepKyEventInventory(
        "CAU_TAI", "納財", "VERIFIED", "卷十一 · 納財",
        ("母倉", "天願", "月恩", "四相", "時徳", "民日", "三合", "滿日", "收日", "六合", "五富", "天倉"),
        ("月破", "大耗", "平日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "大時", "天吏", "小耗", "四耗", "四廢", "四窮", "九空"),
    ),
    "AN_TANG": HiepKyEventInventory(
        "AN_TANG", "安葬", "VERIFIED", "卷十一 · 安葬",
        ("天徳", "月徳", "天徳合", "月徳合", "天赦", "天願", "六合", "鳴吠"),
        ("月建", "月破", "平日", "收日", "劫煞", "災煞", "月煞", "月刑", "月害", "月厭", "四廢", "四忌", "四窮", "五墓", "復日", "重日"),
    ),
}


def inventory_status() -> dict:
    verified = sum(1 for r in HK_V25_EVENT_RULES.values() if r.mapping_status == "VERIFIED")
    provisional = sum(1 for r in HK_V25_EVENT_RULES.values() if r.mapping_status == "PROVISIONAL")
    return {
        "coverage": HK_V25_COVERAGE,
        "event_count": len(HK_V25_EVENT_RULES),
        "verified_mapping_count": verified,
        "provisional_mapping_count": provisional,
        "decision_status": "INVENTORY_ONLY",
        "numeric_score": None,
        "numeric_score_status": HK_V25_NUMERIC_SCORE_STATUS,
        "hierarchy": HK_V25_DECISION_HIERARCHY,
        "source_id": HK_V25_SOURCE_ID,
    }
