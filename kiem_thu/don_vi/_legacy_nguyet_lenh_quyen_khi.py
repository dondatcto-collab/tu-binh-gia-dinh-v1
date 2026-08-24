"""Kiểm thử Giai đoạn 3C.

Hai lớp TÁCH RỜI:
  3C-1  BT-ML            nguyệt lệnh — xác định được
  3C-2  BT-SEASON-POWER  quyền khí — chỉ ghi nguồn nói gì

Không lớp nào được chứa tỷ lệ, điểm số, hay kết luận vượng suy.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from loi.bat_tu.nguyet_lenh import (
    MUA_THEO_CHI,
    NguyetLenhError,
    so_ngay_da_qua_trong_tiet,
    tu_ket_qua_lich,
)
from loi.bat_tu.quyen_khi import lay_quyen_khi, thong_ke, tinh_dong_thuan
from loi.kho_du_lieu.nap_quyen_khi import CAM_TU, doc_cau_hinh, kiem_cau_hinh
from loi.lich.bo_quy_uoc import tai_tat_ca as tai_bo_lich
from loi.lich.engine import CalendarEngine
from loi.lich.quy_uoc_can_chi import CAN, CHI, quy_uoc_mac_dinh

TZ = "Asia/Ho_Chi_Minh"


@pytest.fixture(scope="module")
def engine():
    return CalendarEngine(tai_bo_lich()["CAL-V1"])


def _nl(conn, engine, y, m, d, h=12, mi=0):
    kq = engine.tinh(y, m, d, h, mi, timezone_name=TZ, gioi_tinh="NAM")
    return tu_ket_qua_lich(conn, kq), kq


# ============ 3C-1: đủ 12 tháng =====================================

@pytest.mark.parametrize("chi", CHI)
def test_month_branch_coverage_12_tren_12(db_da_nap, chi):
    r = db_da_nap.execute(
        "SELECT season, opening_jie, closing_jie, rule_id FROM month_commands "
        "WHERE month_branch = ?", (chi,)).fetchone()
    assert r is not None, f"thiếu nguyệt lệnh cho {chi}"
    assert r["season"] == MUA_THEO_CHI[chi]
    assert r["opening_jie"] != r["closing_jie"]
    assert r["rule_id"] == f"BT-ML-{CHI.index(chi) + 1:03d}"


def test_moi_mua_co_dung_ba_chi(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT season, COUNT(*) AS n FROM month_commands GROUP BY season").fetchall()
    assert {r["season"]: r["n"] for r in rows} == {
        "XUAN": 3, "HA": 3, "THU": 3, "DONG": 3}


def test_tiet_mo_thang_khop_bang_tiet_khi(db_da_nap):
    q = quy_uoc_mac_dinh()
    theo_chi = {t.month_branch: t.code for t in q.cac_jie}
    for chi in CHI:
        r = db_da_nap.execute(
            "SELECT opening_jie FROM month_commands WHERE month_branch = ?",
            (chi,)).fetchone()
        assert r["opening_jie"] == theo_chi[chi]


def test_tiet_dong_thang_la_tiet_mo_cua_thang_ke(db_da_nap):
    for i, chi in enumerate(CHI):
        a = db_da_nap.execute(
            "SELECT closing_jie FROM month_commands WHERE month_branch = ?",
            (chi,)).fetchone()
        b = db_da_nap.execute(
            "SELECT opening_jie FROM month_commands WHERE month_branch = ?",
            (CHI[(i + 1) % 12],)).fetchone()
        assert a["closing_jie"] == b["opening_jie"]


# ============ 3C-1: mốc trước và sau Jie ============================

JIE_KIEM = [("MANG_CHUNG", 2024, "NGO"), ("LAP_THU", 2024, "THAN"),
            ("LAP_XUAN", 2024, "DAN"), ("LAP_DONG", 2024, "HOI")]


@pytest.mark.parametrize("code,nam,chi_sau", JIE_KIEM)
def test_jie_boundary_truoc_va_sau(db_da_nap, engine, code, nam, chi_sau):
    moc = engine.bo_tiet.thoi_diem(nam, code)
    for lech, mong_bang in ((-timedelta(hours=3), False), (timedelta(hours=3), True)):
        t = (moc + lech).astimezone(
            __import__("zoneinfo").ZoneInfo(TZ))
        nl, _ = _nl(db_da_nap, engine, t.year, t.month, t.day, t.hour, t.minute)
        assert (nl.month_branch == chi_sau) is mong_bang, (
            f"{code} lệch {lech}: ra {nl.month_branch}")


@pytest.mark.parametrize("code,nam,chi_sau", JIE_KIEM)
def test_sau_jie_thi_current_jie_chinh_la_no(db_da_nap, engine, code, nam, chi_sau):
    moc = engine.bo_tiet.thoi_diem(nam, code)
    t = (moc + timedelta(hours=3)).astimezone(__import__("zoneinfo").ZoneInfo(TZ))
    nl, _ = _nl(db_da_nap, engine, t.year, t.month, t.day, t.hour, t.minute)
    assert nl.current_jie == code
    assert nl.next_jie != code
    assert nl.next_jie_utc > nl.current_jie_utc


def test_so_ngay_da_qua_chi_la_so_do(db_da_nap, engine):
    """Số ngày kể từ Tiết là một PHÉP ĐO, không phải một đánh giá."""
    moc = engine.bo_tiet.thoi_diem(2024, "MANG_CHUNG")
    t = (moc + timedelta(days=5)).astimezone(__import__("zoneinfo").ZoneInfo(TZ))
    _, kq = _nl(db_da_nap, engine, t.year, t.month, t.day, t.hour, t.minute)
    n = so_ngay_da_qua_trong_tiet(kq)
    assert 4.9 < n < 5.1
    assert isinstance(n, float)


# ============ 3C-1: payload không có mạnh yếu ========================

def test_payload_nguyet_lenh_khong_co_diem_so(db_da_nap, engine):
    nl, _ = _nl(db_da_nap, engine, 2024, 6, 15)
    d = nl.to_dict()
    cam = {"strength", "score", "vuong", "suy", "manh", "yeu",
           "ty_le", "percent", "governing_stem"}
    assert not (set(d) & cam), set(d) & cam
    assert set(d) == {"month_branch", "month_branch_vi", "season", "season_vi",
                      "current_jie", "current_jie_utc", "next_jie", "next_jie_utc",
                      "rule_ids", "source_ids"}


def test_quy_tac_nguyet_lenh_khong_cham_diem(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT rule_version_id, effect_class, max_effect, logic FROM rule_versions "
        "WHERE rule_id LIKE 'BT-ML-%'").fetchall()
    assert len(rows) == 12
    for r in rows:
        assert r["effect_class"] == "EXPLANATORY"
        assert r["max_effect"] is None
        logic = json.loads(r["logic"])
        assert "vuong_suy" in logic["khong_co"]


def test_chi_thang_la_thi_bao_loi(db_da_nap, engine):
    from unittest.mock import patch
    kq = engine.tinh(2024, 6, 15, 12, 0, timezone_name=TZ, gioi_tinh="NAM")
    with patch.object(type(kq.tru_thang), "chi", "XYZ", create=True):
        pass
    db_da_nap.execute("DELETE FROM month_commands WHERE month_branch = 'NGO'")
    db_da_nap.commit()
    with pytest.raises(NguyetLenhError, match="CHUA_NAP_NGUYET_LENH"):
        tu_ket_qua_lich(db_da_nap, kq)


# ============ 3C-2: chỉ ghi nguồn nói gì ============================

def test_chi_moi_co_mot_truyen_thong(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT DISTINCT tradition FROM seasonal_governing_qi").fetchall()
    assert [r["tradition"] for r in rows] == ["UYEN_HAI_TU_BINH"]


def test_tam_menh_thong_hoi_ghi_ro_la_chua_chep_duoc():
    raw = doc_cau_hinh()
    tmth = next(t for t in raw["truyen_thong"] if t["tradition"] == "TAM_MENH_THONG_HOI")
    assert tmth["status"] == "NOT_TRANSCRIBED"
    assert tmth["cac_doan"] == []
    assert "CHƯA LẤY ĐƯỢC" in tmth["ghi_chu_chung"]


def test_mot_nguon_thi_khong_duoc_goi_la_dong_thuan(db_da_nap):
    """Chỉ một truyền thống thì KHÔNG kết luận đồng thuận hay mâu thuẫn."""
    tk = thong_ke(db_da_nap)
    assert set(tk) == {"INSUFFICIENT_SOURCES"}, tk
    assert tk["INSUFFICIENT_SOURCES"] >= 20
    assert "AGREED" not in tk, "một nguồn không đủ để nói đồng thuận"


@pytest.mark.parametrize("tiet", ["THANH_MINH", "TIEU_THU", "BACH_LO", "TIEU_HAN"])
def test_bien_the_giu_nguyen_van_va_trang_thai_doc(db_da_nap, tiet):
    r = lay_quyen_khi(db_da_nap, tiet)
    assert r.governing_qi_variants
    assert r.agreement_status == "INSUFFICIENT_SOURCES"
    for v in r.governing_qi_variants:
        assert v.original_text.strip()
        assert v.parse_status in ("PARSED", "PARTIAL", "NO_DAY_COUNT", "SUSPECT_TEXT")
        assert v.status == "PROVISIONAL"


def test_giu_nguyen_cho_chu_hong_khong_va(db_da_nap):
    """Câu Tiểu Tuyết có chữ 甲水 hỏng. Không được tự sửa thành 癸水."""
    r = lay_quyen_khi(db_da_nap, "TIEU_TUYET")
    doan2 = [v for v in r.governing_qi_variants if v.segment_order == 2][0]
    assert doan2.parse_status == "SUSPECT_TEXT"
    assert doan2.governing_stem is None, "chữ hỏng thì để trống, không đoán"
    assert "甲水" in doan2.original_text


def test_giu_nguyen_cho_khong_co_so_ngay(db_da_nap):
    """Kinh Trập không cho số ngày. Không được bịa ra."""
    r = lay_quyen_khi(db_da_nap, "KINH_TRAP")
    assert all(v.day_count is None for v in r.governing_qi_variants)
    assert all(v.parse_status == "NO_DAY_COUNT" for v in r.governing_qi_variants)


def test_payload_quyen_khi_dung_dang_yeu_cau(db_da_nap):
    d = lay_quyen_khi(db_da_nap, "THANH_MINH").to_dict()
    assert set(d) == {"solar_term", "governing_qi_variants", "agreement_status",
                      "conflicts", "rule_ids", "source_ids"}
    v = d["governing_qi_variants"][0]
    assert set(v) == {"tradition", "source", "stem", "interval", "textual_order",
                      "original_text", "parse_status", "status"}


# ============ 3C-2: điều cấm =========================================

def test_cau_hinh_khong_chua_tu_cam():
    assert kiem_cau_hinh(doc_cau_hinh()) == []


def test_khoi_cam_neu_du_dieu():
    cam = doc_cau_hinh()["cam"]
    assert len(cam) >= 5
    van = json.dumps(cam, ensure_ascii=False)
    for tu in ("60/30/10", "70/20/10", "strength", "MAIN_QI", "trung bình"):
        assert tu in van


def test_bo_kiem_bat_duoc_ty_le_gia():
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["cac_doan"][0]["ty_le"] = "60/30/10"
    loi = kiem_cau_hinh(raw)
    assert any("60/30/10" in x for x in loi)


def test_bo_kiem_bat_duoc_gan_vai_tro():
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["cac_doan"][0]["doan"][0]["vai_tro"] = "MAIN_QI"
    loi = kiem_cau_hinh(raw)
    assert any("MAIN_QI" in x for x in loi)


def test_khong_dung_source_order_tang_can_lam_quyen_khi(db_da_nap):
    """Quyền khí phải đến từ bài phú riêng, KHÔNG suy từ thứ tự Tàng Can.

    Bằng chứng: Tiểu Thử trong bài quyền khí có Ất mộc, nhưng bảng Tàng Can
    không cho Chi nào của mùa hạ chứa Ất ở chỗ tương ứng. Hai bảng khác hệ.
    """
    r = lay_quyen_khi(db_da_nap, "TIEU_THU")
    can_quyen_khi = [v.governing_stem for v in r.governing_qi_variants]
    assert "AT" in can_quyen_khi

    from loi.bat_tu.tang_can import lay_tang_can
    tc_mui = lay_tang_can(db_da_nap, "MUI").hidden_stems
    tc_ngo = lay_tang_can(db_da_nap, "NGO").hidden_stems
    # Thứ tự hai bảng KHÔNG khớp nhau — chứng tỏ không suy cái này từ cái kia.
    assert list(tc_ngo) != [c for c in can_quyen_khi if c][:len(tc_ngo)]
    assert tc_mui != tuple(c for c in can_quyen_khi if c)


def test_khong_bang_nao_chua_ty_le_trong_co_so_du_lieu(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT notes FROM seasonal_governing_qi WHERE notes IS NOT NULL").fetchall()
    for r in rows:
        for tu in ("60/30/10", "70/20/10", "strength", "score"):
            assert tu not in r["notes"]


def test_bay_chan_ty_le_o_tang_co_so_du_lieu(db_da_nap):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError, match="KHONG_DUOC_CHUA_TY_LE"):
        db_da_nap.execute(
            """INSERT INTO seasonal_governing_qi (entry_id, tradition, solar_term,
                   segment_order, governing_stem, day_count, textual_order,
                   original_text, parse_status, source_id, rule_id, notes)
               VALUES ('X','T','LAP_XUAN',9,'GIAP',3,1,'x','PARSED',
                       'SRC-UHTB-CHEP','BT-SEASON-POWER-UYEN_HAI_TU_BINH',
                       'ty le 60/30/10')""")


def test_quy_tac_quyen_khi_khong_duoc_bat(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT rule_id, is_active FROM rule_registry "
        "WHERE namespace = 'BT-SEASON-POWER'").fetchall()
    assert rows, "phải có quy tắc ghi nguồn"
    for r in rows:
        assert r["is_active"] == 0, f"{r['rule_id']} không được bật để tính"


def test_khong_ket_luan_vuong_suy_o_dau_ca(db_da_nap):
    """Không quy tắc nào của 3C được KẾT LUẬN mạnh yếu.

    Chú ý: khoá `khong_co` là bản KHAI BÁO những thứ quy tắc KHÔNG chứa.
    Nó cố ý nhắc tên các thứ bị cấm, nên phải loại nó ra khỏi vùng quét.
    Quét cả nó thì test tự bắt chính lời cam kết của mình.
    """
    rows = db_da_nap.execute(
        "SELECT rule_version_id, logic FROM rule_versions "
        "WHERE rule_id LIKE 'BT-SEASON-POWER%' OR rule_id LIKE 'BT-ML-%'").fetchall()
    assert len(rows) >= 13
    for r in rows:
        logic = json.loads(r["logic"])
        # Mọi quy tắc phải TỰ KHAI rằng nó không chứa mạnh yếu.
        khai_bao = logic.get("khong_co") or logic.get("khong_ket_luan")
        assert khai_bao, f"{r['rule_version_id']} chưa khai báo phạm vi"

        phan_du_lieu = {k: v for k, v in logic.items()
                        if k not in ("khong_co", "khong_ket_luan")}
        van = json.dumps(phan_du_lieu, ensure_ascii=False).upper()
        for tu in ("STRENGTH", "SCORE", "TY_LE", "PERCENT", "MANH", "YEU"):
            assert tu not in van, f"{r['rule_version_id']} có {tu}"


def test_moi_quy_tac_3c_tu_khai_khong_chua_manh_yeu(db_da_nap):
    """Lời khai đó phải nhắc đúng những thứ bị cấm, không được khai suông."""
    r = db_da_nap.execute(
        "SELECT logic FROM rule_versions WHERE rule_version_id = 'BT-ML-001@1'"
    ).fetchone()
    khong_co = json.loads(r["logic"])["khong_co"]
    assert {"strength", "score", "ty_le", "vuong_suy"} <= set(khong_co)


# ============ Phạm vi: chưa làm gì thêm =============================

def test_cach_cuc_dung_than_chua_co_nhung_bt_rel_da_co(db_da_nap):
    """Regression FIX4: không mở BT-PAT/BT-USE; BT-REL đã được nạp có nguồn."""
    rows = db_da_nap.execute(
        "SELECT rule_id FROM rule_registry WHERE namespace IN ('BT-PAT','BT-USE')"
    ).fetchall()
    assert rows == [], "Cách cục và Dụng-Hỷ-Kỵ vẫn chưa được phép suy"

    rel = db_da_nap.execute(
        "SELECT COUNT(*) AS n FROM rule_registry rr JOIN rule_versions rv "
        "ON rv.rule_id=rr.rule_id AND rv.version=rr.active_version "
        "WHERE rr.namespace='BT-REL' AND rv.status='VERIFIED' AND rr.is_active=1"
    ).fetchone()
    assert rel["n"] == 4


# ============ Chốt CHÍNH XÁC từng đoạn của bài phú ==================
# Bảng này chép thẳng từ nguyên văn. Đổi một chữ trong cấu hình là trượt.
# (tiết, [(số ngày, Can), ...]) — None nghĩa là nguồn không nói rõ.

DOAN_TU_NGUYEN_VAN = {
    "LAP_XUAN":    [(3, "BINH"), (None, "GIAP")],
    "KINH_TRAP":   [],
    "XUAN_PHAN":   [(None, "AT")],
    "THANH_MINH":  [(10, "AT"), (8, "QUY")],
    "COC_VU":      [(3, "MAU")],
    "LAP_HA":      [(None, "MAU")],
    "TIEU_MAN":    [(None, "BINH")],
    "MANG_CHUNG":  [(None, "KY"), (7, None)],
    "HA_CHI":      [(None, "BINH"), (None, "DINH")],
    "TIEU_THU":    [(10, "DINH"), (3, "AT"), (3, "KY")],
    "DAI_THU":     [(10, "KY")],
    "LAP_THU":     [(10, "NHAM")],
    "XU_THU":      [(15, "CANH")],
    "BACH_LO":     [(7, "CANH"), (8, "TAN")],
    "HAN_LO":      [(7, "TAN"), (8, "DINH")],
    "SUONG_GIANG": [(15, "KY")],
    "LAP_DONG":    [(7, "QUY"), (8, "NHAM")],
    "TIEU_TUYET":  [(7, "NHAM"), (8, None)],
    "DAI_TUYET":   [(7, "NHAM")],
    "DONG_CHI":    [(None, "QUY")],
    "TIEU_HAN":    [(7, "QUY"), (8, "TAN")],
    "DAI_HAN":     [(10, "KY")],
}


@pytest.mark.parametrize("tiet,mong_doi", sorted(DOAN_TU_NGUYEN_VAN.items()))
def test_tung_doan_khop_nguyen_van(db_da_nap, tiet, mong_doi):
    r = lay_quyen_khi(db_da_nap, tiet)
    bien = [v for v in r.governing_qi_variants if v.tradition == "UYEN_HAI_TU_BINH"]
    if not mong_doi:
        # Tiết không có đoạn nào: vẫn phải có một bản ghi giữ nguyên văn.
        assert len(bien) == 1 and bien[0].segment_order == 0
        assert bien[0].governing_stem is None and bien[0].day_count is None
        return
    thuc_te = [(v.day_count, v.governing_stem)
               for v in sorted(bien, key=lambda x: x.segment_order)]
    assert thuc_te == mong_doi, f"{tiet}: nguyên văn {bien[0].original_text}"


def test_phu_du_22_tiet_ma_bai_phu_co(db_da_nap):
    tiet = {r["solar_term"] for r in db_da_nap.execute(
        "SELECT DISTINCT solar_term FROM seasonal_governing_qi")}
    assert tiet == set(DOAN_TU_NGUYEN_VAN)
    assert len(tiet) == 22, "bài phú chép 22 tiết, thiếu Vũ Thủy và Thu Phân"


def test_hai_tiet_bai_phu_khong_chep(db_da_nap):
    """Bài phú KHÔNG nhắc Vũ Thủy và Thu Phân. Không được bịa vào."""
    for tiet in ("VU_THUY", "THU_PHAN"):
        r = lay_quyen_khi(db_da_nap, tiet)
        assert r.governing_qi_variants == []
        assert r.agreement_status == "INSUFFICIENT_SOURCES"


def test_tong_so_doan_dung(db_da_nap):
    n = db_da_nap.execute(
        "SELECT COUNT(*) AS n FROM seasonal_governing_qi "
        "WHERE tradition = 'UYEN_HAI_TU_BINH'").fetchone()["n"]
    mong = sum(max(len(v), 1) for v in DOAN_TU_NGUYEN_VAN.values())
    assert n == mong, f"mong đợi {mong} bản ghi, có {n}"


# ============ Ba lỗ hổng đã bịt =====================================

def test_bat_duoc_ty_le_gan_bang_TEN_KHOA():
    """Đột biến `ty_le: 60` không chứa chuỗi cấm nào. Phải bắt bằng tên khoá."""
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["cac_doan"][0]["doan"][0]["ty_le"] = 60
    loi = kiem_cau_hinh(raw)
    assert any("CO_KHOA_CAM" in x and "ty_le" in x for x in loi), loi


@pytest.mark.parametrize("khoa", ["trong_so", "weight", "strength", "vai_tro",
                                  "semantic_role", "vuong_suy", "priority"])
def test_bat_duoc_moi_khoa_cam(khoa):
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["cac_doan"][0][khoa] = "x"
    assert any("CO_KHOA_CAM" in x and khoa in x for x in kiem_cau_hinh(raw))


def test_khong_truyen_thong_nao_duoc_tu_nang_len_verified():
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["status"] = "VERIFIED"
    loi = kiem_cau_hinh(raw)
    assert any("TRANG_THAI_LA" in x for x in loi), loi


def test_trang_thai_thuc_te_van_la_chua_xac_minh():
    for tt in doc_cau_hinh()["truyen_thong"]:
        assert tt["status"] in ("PROVISIONAL", "CONFLICTED", "NOT_TRANSCRIBED")


def test_khong_duoc_dung_cho_trong_lam_nguon_quyen_khi():
    raw = doc_cau_hinh()
    raw["truyen_thong"][0]["source_id"] = "SRC-CHUA-CO-NGUON"
    loi = kiem_cau_hinh(raw)
    assert any("NGUON_CAM" in x for x in loi), loi


def test_nguon_thuc_te_dung_sach_co(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT DISTINCT source_id FROM seasonal_governing_qi").fetchall()
    assert [r["source_id"] for r in rows] == ["SRC-UHTB-CHEP"]
    r = db_da_nap.execute(
        """SELECT rvs.source_id FROM rule_version_sources rvs
            WHERE rvs.rule_version_id LIKE 'BT-SEASON-POWER%'
              AND rvs.source_level = 'PRIMARY'""").fetchall()
    assert all(x["source_id"] != "SRC-CHUA-CO-NGUON" for x in r)
