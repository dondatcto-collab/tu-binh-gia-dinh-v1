"""Kiểm thử Thập Thần.

Mục tiêu: PAIR_COVERAGE = 100/100, TEN_GOD_CLASS_COVERAGE = 10/10.

Bảng mong đợi dựng từ QUY TẮC ngũ hành và âm dương, không chép bảng
mười nhân mười, và không lấy từ Engine.
"""

from __future__ import annotations

import itertools

import pytest

from loi.bat_tu.thap_than import (
    CHIEU_QUAN_HE,
    QUAN_HE_AM_DUONG,
    ThapThanError,
    ap_dung_tu_tru,
    luoi_thap_than,
    tinh_thap_than,
)
from loi.lich.quy_uoc_can_chi import CAN

# --- Dữ liệu nền dựng độc lập với Engine -----------------------------
HANH_CUA_CAN = {
    "GIAP": "MOC", "AT": "MOC", "BINH": "HOA", "DINH": "HOA",
    "MAU": "THO", "KY": "THO", "CANH": "KIM", "TAN": "KIM",
    "NHAM": "THUY", "QUY": "THUY",
}
DUONG = {"GIAP", "BINH", "MAU", "CANH", "NHAM"}

SINH = {"MOC": "HOA", "HOA": "THO", "THO": "KIM", "KIM": "THUY", "THUY": "MOC"}
KHAC = {"MOC": "THO", "THO": "THUY", "THUY": "HOA", "HOA": "KIM", "KIM": "MOC"}

# Lưới mong đợi, viết thẳng từ đoạn 五曰… của Uyên Hải Tử Bình.
LUOI_MONG_DOI = {
    ("DONG_HANH", "DONG_TINH"): "TY_KIEN",
    ("DONG_HANH", "KHAC_TINH"): "KIEP_TAI",
    ("TA_SINH", "DONG_TINH"): "THUC_THAN",
    ("TA_SINH", "KHAC_TINH"): "THUONG_QUAN",
    ("TA_KHAC", "DONG_TINH"): "THIEN_TAI",
    ("TA_KHAC", "KHAC_TINH"): "CHINH_TAI",
    ("KHAC_TA", "DONG_TINH"): "THAT_SAT",
    ("KHAC_TA", "KHAC_TINH"): "CHINH_QUAN",
    ("SINH_TA", "DONG_TINH"): "THIEN_AN",
    ("SINH_TA", "KHAC_TINH"): "CHINH_AN",
}


def _chieu(nc: str, dt: str) -> str:
    a, b = HANH_CUA_CAN[nc], HANH_CUA_CAN[dt]
    if a == b:
        return "DONG_HANH"
    if SINH[a] == b:
        return "TA_SINH"
    if SINH[b] == a:
        return "SINH_TA"
    if KHAC[a] == b:
        return "TA_KHAC"
    if KHAC[b] == a:
        return "KHAC_TA"
    raise AssertionError(f"{nc} {dt}")


def _tinh(nc: str, dt: str) -> str:
    return "DONG_TINH" if (nc in DUONG) == (dt in DUONG) else "KHAC_TINH"


def _mong_doi(nc: str, dt: str) -> str:
    return LUOI_MONG_DOI[(_chieu(nc, dt), _tinh(nc, dt))]


CAC_CAP = list(itertools.product(CAN, CAN))


# ============ 100 tổ hợp ============================================

@pytest.mark.parametrize("nc,dt", CAC_CAP, ids=[f"{a}-{b}" for a, b in CAC_CAP])
def test_du_100_to_hop(db_da_nap, nc, dt):
    r = tinh_thap_than(db_da_nap, nc, dt)
    assert r.ten_god == _mong_doi(nc, dt)
    assert r.relation_direction == _chieu(nc, dt)
    assert r.polarity_relation == _tinh(nc, dt)


def test_pair_coverage_100_tren_100():
    assert len(CAC_CAP) == 100
    assert len({a for a, _ in CAC_CAP}) == 10      # DAY_MASTER_COVERAGE
    assert len({b for _, b in CAC_CAP}) == 10      # TARGET_STEM_COVERAGE


def test_ten_god_class_coverage_10_tren_10(db_da_nap):
    thay = {tinh_thap_than(db_da_nap, a, b).ten_god for a, b in CAC_CAP}
    assert len(thay) == 10
    assert thay == set(LUOI_MONG_DOI.values())


def test_moi_o_xuat_hien_dung_10_lan(db_da_nap):
    """Lưới cân: mỗi Thập Thần ứng đúng 10 trong 100 tổ hợp."""
    from collections import Counter
    dem = Counter(tinh_thap_than(db_da_nap, a, b).ten_god for a, b in CAC_CAP)
    assert set(dem.values()) == {10}, dem


# ============ Đối chiếu thẳng với nguyên văn ========================

def test_khop_moi_vi_du_trong_nguyen_van(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT day_master, target_stem, ten_god_code, original_text "
        "FROM ten_god_source_examples").fetchall()
    assert len(rows) == 12, "phải có đủ 12 ví dụ trích thẳng"
    for r in rows:
        kq = tinh_thap_than(db_da_nap, r["day_master"], r["target_stem"])
        assert kq.ten_god == r["ten_god_code"], (
            f"{r['day_master']} gặp {r['target_stem']}: nguyên văn "
            f"{r['original_text']} nói {r['ten_god_code']}, Engine ra {kq.ten_god}")


def test_nguyen_van_phu_du_bon_chieu_quan_he(db_da_nap):
    """12 ví dụ trong sách phủ được bốn trên năm chiều."""
    rows = db_da_nap.execute(
        "SELECT day_master, target_stem FROM ten_god_source_examples").fetchall()
    chieu = {tinh_thap_than(db_da_nap, r["day_master"], r["target_stem"]).relation_direction
             for r in rows}
    assert chieu == {"TA_SINH", "SINH_TA", "KHAC_TA"} | {"TA_SINH"}
    # Chiều DONG_HANH và TA_KHAC không có ví dụ cụ thể trong đoạn trích.
    assert "DONG_HANH" not in chieu
    assert "TA_KHAC" not in chieu


# ============ Lưới 5 nhân 2 ==========================================

def test_luoi_du_10_o_khong_thua_khong_thieu():
    luoi = luoi_thap_than()
    assert len(luoi) == 10
    assert set(luoi) == set(itertools.product(CHIEU_QUAN_HE, QUAN_HE_AM_DUONG))


def test_luoi_khop_ma_quy_tac_da_giao():
    luoi = luoi_thap_than()
    ma = {o.code: o.rule_id for o in luoi.values()}
    assert ma == {
        "TY_KIEN": "BT-TG-001", "KIEP_TAI": "BT-TG-002",
        "THUC_THAN": "BT-TG-003", "THUONG_QUAN": "BT-TG-004",
        "THIEN_TAI": "BT-TG-005", "CHINH_TAI": "BT-TG-006",
        "THAT_SAT": "BT-TG-007", "CHINH_QUAN": "BT-TG-008",
        "THIEN_AN": "BT-TG-009", "CHINH_AN": "BT-TG-010",
    }


@pytest.mark.parametrize("chieu", CHIEU_QUAN_HE)
def test_moi_chieu_co_dung_hai_o(chieu):
    o = [k for k in luoi_thap_than() if k[0] == chieu]
    assert len(o) == 2


def test_quy_uoc_chinh_thien_dung_chieu(db_da_nap):
    """Chính là KHÁC tính, Thiên là ĐỒNG tính — trừ cặp Thực Thương.

    Thực Thần đồng tính, Thương Quan khác tính. Đây là chỗ dễ nhớ nhầm,
    và nguyên văn nói thẳng: 甲見丙為食神 (dương gặp dương).
    """
    for ten, tinh_mong in (("CHINH_QUAN", "KHAC_TINH"), ("THAT_SAT", "DONG_TINH"),
                           ("CHINH_TAI", "KHAC_TINH"), ("THIEN_TAI", "DONG_TINH"),
                           ("CHINH_AN", "KHAC_TINH"), ("THIEN_AN", "DONG_TINH"),
                           ("THUC_THAN", "DONG_TINH"), ("THUONG_QUAN", "KHAC_TINH"),
                           ("TY_KIEN", "DONG_TINH"), ("KIEP_TAI", "KHAC_TINH")):
        r = db_da_nap.execute(
            "SELECT polarity_relation FROM ten_gods WHERE ten_god_code = ?",
            (ten,)).fetchone()
        assert r["polarity_relation"] == tinh_mong, ten


# ============ Không có điểm số hay tốt xấu ==========================

@pytest.mark.parametrize("nc,dt", [("GIAP", "CANH"), ("QUY", "QUY"), ("MAU", "AT")])
def test_payload_khong_co_diem_so(db_da_nap, nc, dt):
    d = tinh_thap_than(db_da_nap, nc, dt).to_dict()
    cam = {"strength", "score", "favorable", "unfavorable", "hy", "ky",
           "cat", "hung", "weight", "priority", "luan_giai"}
    assert not (set(d) & cam), set(d) & cam


def test_payload_du_truong_bat_buoc(db_da_nap):
    d = tinh_thap_than(db_da_nap, "GIAP", "TAN").to_dict()
    assert set(d) == {
        "day_master", "target_stem", "day_master_element", "target_element",
        "day_master_yinyang", "target_yinyang", "relation_direction",
        "polarity_relation", "ten_god", "ten_god_vi", "rule_id", "source_id", "status"}


@pytest.mark.parametrize("nc,dt", CAC_CAP[::7])
def test_nam_truong_di_xuyen_payload(db_da_nap, nc, dt):
    """Năm trường này không được rơi rụng ở bất kỳ tổ hợp nào."""
    r = tinh_thap_than(db_da_nap, nc, dt)
    d = r.to_dict()
    for truong in ("ten_god", "ten_god_vi", "rule_id", "source_id", "status"):
        assert truong in d, f"payload thiếu {truong}"
        assert d[truong], f"{truong} rỗng"
    assert d["ten_god_vi"] == r.ten_god_vi
    assert d["ten_god_vi"] != d["ten_god"], "phải là tên tiếng Việt, không phải mã"


def test_ten_god_vi_dung_cho_ca_muoi_o(db_da_nap):
    thay = {tinh_thap_than(db_da_nap, a, b).to_dict()["ten_god_vi"]
            for a, b in CAC_CAP}
    assert thay == {"Tỷ Kiên", "Kiếp Tài", "Thực Thần", "Thương Quan",
                    "Thiên Tài", "Chính Tài", "Thất Sát", "Chính Quan",
                    "Thiên Ấn", "Chính Ấn"}


def test_tang_tu_tru_cung_xuat_ten_viet(db_da_nap):
    kq = ap_dung_tu_tru(db_da_nap, "GIAP", {"DAY": "GIAP", "YEAR": "CANH"})
    theo_vt = {x.position: x.to_dict() for x in kq}
    assert theo_vt["YEAR_STEM"]["ten_god_vi"] == "Thất Sát"
    assert theo_vt["DAY_STEM"]["ten_god_vi"] is None


def test_khong_quy_tac_thap_than_nao_cham_diem(db_da_nap):
    rows = db_da_nap.execute(
        "SELECT effect_class, max_effect FROM rule_versions "
        "WHERE rule_id LIKE 'BT-TG-%'").fetchall()
    assert len(rows) == 11, "mười ô cộng một quy tắc dị biệt"
    for r in rows:
        assert r["effect_class"] == "EXPLANATORY"
        assert r["max_effect"] is None


# ============ Đầu vào hỏng ==========================================

@pytest.mark.parametrize("xau", ["", "XYZ", "giap", "TY", None, 3])
def test_can_khong_hop_le_bi_bao_loi(db_da_nap, xau):
    with pytest.raises(ThapThanError, match="CAN_KHONG_HOP_LE"):
        tinh_thap_than(db_da_nap, "GIAP", xau)
    with pytest.raises(ThapThanError, match="CAN_KHONG_HOP_LE"):
        tinh_thap_than(db_da_nap, xau, "GIAP")


def test_ket_qua_lap_lai_giong_nhau(db_da_nap):
    for nc, dt in CAC_CAP[:20]:
        assert (tinh_thap_than(db_da_nap, nc, dt).to_dict()
                == tinh_thap_than(db_da_nap, nc, dt).to_dict())


# ============ Dị biệt tên gọi cặp đồng hành =========================

def test_di_biet_ten_goi_duoc_ghi_conflicted(db_da_nap):
    r = db_da_nap.execute(
        "SELECT status FROM rule_versions "
        "WHERE rule_version_id = 'BT-TG-CONFLICT-001@1'").fetchone()
    assert r["status"] == "CONFLICTED"
    a = db_da_nap.execute(
        "SELECT is_active FROM rule_registry "
        "WHERE rule_id = 'BT-TG-CONFLICT-001'").fetchone()
    assert a["is_active"] == 0


def test_duong_nhan_khong_phai_alias_cua_ty_kien(db_da_nap):
    """NOT_A_DIRECT_ALIAS. Hai khái niệm khác nhau, xác định bằng thứ khác nhau."""
    rows = db_da_nap.execute(
        """SELECT variant_name, is_active_convention, source_quote,
                  alias_relation, concept_group, concept_kind, determined_by
             FROM ten_god_naming_variants
            WHERE relation_direction='DONG_HANH' AND polarity_relation='DONG_TINH'
         ORDER BY variant_name""").fetchall()
    assert len(rows) == 2
    theo_ten = {r["variant_name"]: r for r in rows}
    assert set(theo_ten) == {"TY_KIEN", "DUONG_NHAN"}

    for r in rows:
        assert r["alias_relation"] == "NOT_A_DIRECT_ALIAS"
        assert r["source_quote"].strip(), "mỗi cách dùng phải có nguyên văn"

    ty = theo_ten["TY_KIEN"]
    assert ty["concept_group"] == "BT-TG"
    assert ty["concept_kind"] == "TEN_GOD_RELATION"
    assert ty["is_active_convention"] == 1

    yr = theo_ten["DUONG_NHAN"]
    assert yr["concept_group"] == "BT-DN", "Dương Nhận thuộc nhóm khác"
    assert yr["concept_kind"] == "SEPARATE_CLASSICAL_CONCEPT"
    assert yr["is_active_convention"] == 0
    assert "Chi" in yr["determined_by"], "xác định bằng Địa Chi, không phải Thiên Can"


def test_nhom_duong_nhan_da_co_cho_nhung_con_trong(db_da_nap):
    ns = db_da_nap.execute(
        "SELECT namespace, name_vi FROM rule_namespaces WHERE namespace='BT-DN'").fetchone()
    assert ns is not None, "phải có chỗ dành sẵn"
    assert "Dương Nhận" in ns["name_vi"]
    rows = db_da_nap.execute(
        "SELECT rule_id FROM rule_registry WHERE namespace='BT-DN'").fetchall()
    assert rows == [], "chưa làm Dương Nhận"


def test_khong_ghi_de_nhom_luu_nien(db_da_nap):
    """BT-YR đã mang nghĩa Lưu niên từ đặc tả gốc. Không được đổi nghĩa nó."""
    r = db_da_nap.execute(
        "SELECT name_vi FROM rule_namespaces WHERE namespace='BT-YR'").fetchone()
    assert r is not None
    assert r["name_vi"] == "Lưu niên", (
        f"BT-YR bị đổi nghĩa thành {r['name_vi']!r} — đây là ghi đè âm thầm")


def test_quy_tac_lich_su_thuat_ngu_co_canh_bao(db_da_nap):
    import json
    r = db_da_nap.execute(
        "SELECT logic, notes FROM rule_versions "
        "WHERE rule_version_id='BT-TG-CONFLICT-001@1'").fetchone()
    logic = json.loads(r["logic"])
    assert logic["quan_he"] == "NOT_A_DIRECT_ALIAS"
    assert logic["canh_bao"] == "NOT_A_DIRECT_ALIAS"
    nhom = {c["thuoc_nhom"] for c in logic["cac_khai_niem"]}
    assert nhom == {"BT-TG", "BT-DN"}, "hai khái niệm phải thuộc hai nhóm"


def test_engine_dung_quy_uoc_hien_dai(db_da_nap):
    """Chọn Tỷ Kiên vì nó phủ đủ mười Nhật chủ. Dương Nhận chỉ phủ năm dương."""
    assert tinh_thap_than(db_da_nap, "GIAP", "GIAP").ten_god == "TY_KIEN"
    assert tinh_thap_than(db_da_nap, "AT", "AT").ten_god == "TY_KIEN"
    assert tinh_thap_than(db_da_nap, "GIAP", "AT").ten_god == "KIEP_TAI"


# ============ Áp dụng vào Tứ Trụ ====================================

def test_ap_dung_tu_tru_can_ngay_la_nhat_chu(db_da_nap):
    kq = ap_dung_tu_tru(
        db_da_nap, "GIAP",
        {"YEAR": "CANH", "MONTH": "MAU", "DAY": "GIAP", "HOUR": "BINH"})
    theo_vt = {x.position: x for x in kq}
    assert theo_vt["DAY_STEM"].la_nhat_chu is True
    assert theo_vt["DAY_STEM"].ket_qua is None, "Nhật chủ không có Thập Thần với chính nó"
    assert theo_vt["YEAR_STEM"].ket_qua.ten_god == "THAT_SAT"
    assert theo_vt["MONTH_STEM"].ket_qua.ten_god == "THIEN_TAI"
    assert theo_vt["HOUR_STEM"].ket_qua.ten_god == "THUC_THAN"


def test_ap_dung_tu_tru_bao_loi_khi_nhat_chu_khong_khop(db_da_nap):
    with pytest.raises(ThapThanError, match="NHAT_CHU_KHONG_KHOP"):
        ap_dung_tu_tru(db_da_nap, "GIAP", {"DAY": "AT"})


def test_ap_dung_ca_can_tang(db_da_nap):
    kq = ap_dung_tu_tru(
        db_da_nap, "GIAP", {"DAY": "GIAP"}, {"MONTH": "DAN"})
    an = [x for x in kq if x.position.startswith("MONTH_HIDDEN")]
    assert [x.position for x in an] == [
        "MONTH_HIDDEN_1", "MONTH_HIDDEN_2", "MONTH_HIDDEN_3"]
    assert [x.stem for x in an] == ["GIAP", "BINH", "MAU"]
    assert [x.ket_qua.ten_god for x in an] == ["TY_KIEN", "THUC_THAN", "THIEN_TAI"]


def test_ap_dung_tu_tru_khong_luan_giai(db_da_nap):
    kq = ap_dung_tu_tru(db_da_nap, "GIAP", {"DAY": "GIAP", "YEAR": "CANH"})
    for x in kq:
        d = x.to_dict()
        assert set(d) <= {"position", "stem", "la_nhat_chu", "ten_god", "ten_god_vi", "rule_id"}


# ============ Phạm vi: chưa làm quyền khí ===========================

def test_chua_lam_vuong_suy_cach_cuc_nhung_bt_rel_da_mo(db_da_nap):
    """FIX4 không được lấn sang Vượng suy/Cách cục/Dụng thần; BT-REL là ngoại lệ đã mở có nguồn."""
    rows = db_da_nap.execute(
        "SELECT rule_id FROM rule_registry "
        "WHERE namespace IN ('BT-PAT','BT-USE')").fetchall()
    assert rows == [], "V1 chưa được phép tự tạo Cách cục/Dụng-Hỷ-Kỵ"

    rel = db_da_nap.execute(
        "SELECT COUNT(*) AS n FROM rule_registry rr JOIN rule_versions rv "
        "ON rv.rule_id=rr.rule_id AND rv.version=rr.active_version "
        "WHERE rr.namespace='BT-REL' AND rv.status='VERIFIED' AND rr.is_active=1"
    ).fetchone()
    assert rel["n"] == 4

    # Quyền khí có tồn tại nhưng vẫn không được bật để suy vượng suy.
    qk = db_da_nap.execute(
        "SELECT is_active FROM rule_registry WHERE namespace='BT-SEASON-POWER'"
    ).fetchall()
    assert all(r["is_active"] == 0 for r in qk)


# ============ Đổi Nhật chủ thì kết quả phải đổi ======================

@pytest.mark.parametrize("dt", CAN)
def test_doi_nhat_chu_giu_target_thi_doi_ket_qua(db_da_nap, dt):
    """Giáp và Ất cùng hành nhưng khác âm dương.

    Với mọi Can đối tượng, hai Nhật chủ này phải cho CÙNG chiều quan hệ
    nhưng KHÁC quan hệ âm dương, do đó khác Thập Thần.
    """
    a = tinh_thap_than(db_da_nap, "GIAP", dt)
    b = tinh_thap_than(db_da_nap, "AT", dt)
    assert a.relation_direction == b.relation_direction
    assert a.polarity_relation != b.polarity_relation
    assert a.ten_god != b.ten_god


def test_doi_nhat_chu_sang_hanh_khac_thi_doi_chieu(db_da_nap):
    """Nhật chủ đổi hành thì chiều quan hệ phải đổi theo."""
    canh = tinh_thap_than(db_da_nap, "GIAP", "CANH")
    canh_nc_hoa = tinh_thap_than(db_da_nap, "BINH", "CANH")
    assert canh.relation_direction == "KHAC_TA"
    assert canh_nc_hoa.relation_direction == "TA_KHAC"
    assert canh.ten_god != canh_nc_hoa.ten_god


def test_kho_quy_tac_sach_sau_khi_nap_thap_than(db_da_nap):
    """Nguồn của Thập Thần không được là chỗ trống chờ nguồn."""
    from loi.kho_quy_tac.kiem_dinh import kiem_toan_kho
    loi = [x for x in kiem_toan_kho(db_da_nap) if x.muc == "LOI"]
    assert loi == [], [str(x) for x in loi]
    rows = db_da_nap.execute(
        """SELECT rv.rule_id, rvs.source_id FROM rule_versions rv
             JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
            WHERE rv.rule_id LIKE 'BT-TG-0%' AND rvs.source_level = 'PRIMARY'""").fetchall()
    assert len(rows) == 10
    for r in rows:
        assert r["source_id"] == "SRC-UHTB-CHEP", f"{r['rule_id']} sai nguồn"


def test_thap_than_tua_vao_nguon_co(db_da_nap):
    from loi.lich.do_phu import dem_bang_chung
    d = dem_bang_chung(db_da_nap, "BT-TG-007")
    assert d["groups"] == ("CLASSICAL_TEXT",)
