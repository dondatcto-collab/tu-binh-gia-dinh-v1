"""Kiểm thử Tàng Can — tầng cấu trúc.

Mục tiêu: BRANCH_COVERAGE = 12/12.

Bảng mong đợi dưới đây suy thẳng từ bài phú 又地支藏遁歌, không suy từ Engine.
"""

from __future__ import annotations

import pytest

from loi.bat_tu.tang_can import (
    TangCanError,
    do_phu_chi,
    lay_tang_can,
    lay_tat_ca,
    thu_tu_cac_truyen_thong,
)
from loi.kho_du_lieu.nap_tang_can import MA_QUY_TAC, MA_QUY_TAC_THU_TU
from loi.lich.quy_uoc_can_chi import CAN, CHI

# --- Suy thẳng từ nguyên văn 又地支藏遁歌 ---------------------------
TANG_CAN_TU_NGUYEN_VAN = {
    "TY":   ["QUY"],                    # 子宮癸水在其中
    "SUU":  ["QUY", "TAN", "KY"],       # 丑癸辛金己土同
    "DAN":  ["GIAP", "BINH", "MAU"],    # 寅宮甲木兼丙戊
    "MAO":  ["AT"],                     # 卯宮乙木獨相逢
    "THIN": ["AT", "MAU", "QUY"],       # 辰藏乙戊三分癸
    "TI":   ["CANH", "BINH", "MAU"],    # 巳中庚金丙戊叢
    "NGO":  ["DINH", "KY"],             # 午宮丁火并己土
    "MUI":  ["AT", "KY", "DINH"],       # 未宮乙己丁共宗
    "THAN": ["CANH", "NHAM", "MAU"],    # 申位庚金壬水戊
    "DAU":  ["TAN"],                    # 酉宮辛金獨豐隆
    "TUAT": ["TAN", "DINH", "MAU"],     # 戌宮辛金及丁戊
    "HOI":  ["NHAM", "GIAP"],           # 亥藏壬甲是真蹤
}

# Năm Chi mà các truyền thống ghi THỨ TỰ khác nhau.
CHI_DI_BIET_THU_TU = {"SUU", "THIN", "TI", "MUI", "TUAT"}


# ============ Đủ 12 Chi =============================================

@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_dung_tap_can(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert list(r.hidden_stems) == TANG_CAN_TU_NGUYEN_VAN[chi]


@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_dung_thu_tu_nguon(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert r.source_order == tuple(range(1, len(r.hidden_stems) + 1))


@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_khong_trung_can(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert len(set(r.hidden_stems)) == len(r.hidden_stems)


@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_chi_dung_can_hop_le(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert all(c in CAN for c in r.hidden_stems)
    assert 1 <= len(r.hidden_stems) <= 3


@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_ket_qua_lap_lai_giong_nhau(db_da_nap, chi):
    a = lay_tang_can(db_da_nap, chi)
    b = lay_tang_can(db_da_nap, chi)
    assert a == b
    assert a.to_dict() == b.to_dict()


@pytest.mark.parametrize("chi", CHI)
def test_du_12_chi_gan_dung_quy_tac(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert r.rule_ids == (MA_QUY_TAC[chi],)
    assert r.source_status == "VERIFIED"


def test_branch_coverage_du_12_tren_12(db_da_nap):
    assert do_phu_chi(db_da_nap) == "12/12"
    assert len(lay_tat_ca(db_da_nap)) == 12


# ============ Không được có trọng số hay vai trò =====================

@pytest.mark.parametrize("chi", CHI)
def test_khong_co_trong_so_trong_ket_qua(db_da_nap, chi):
    d = lay_tang_can(db_da_nap, chi).to_dict()
    cam = {"ty_le", "trong_so", "weight", "ratio", "percent", "score",
           "strength", "so_ngay", "priority"}
    assert not (set(d) & cam), f"kết quả có trường trọng số: {set(d) & cam}"


@pytest.mark.parametrize("chi", CHI)
def test_chua_gan_vai_tro_ngu_nghia(db_da_nap, chi):
    r = lay_tang_can(db_da_nap, chi)
    assert r.semantic_role_status == "NOT_ASSIGNED"
    assert r.to_dict()["semantic_role_status"] == "NOT_ASSIGNED"
    rows = db_da_nap.execute(
        """SELECT h.semantic_role FROM branch_hidden_stems h
             JOIN branches b ON b.branch_index = h.branch_index
            WHERE b.code = ?""", (chi,)).fetchall()
    assert all(r0["semantic_role"] is None for r0 in rows)


def test_khong_quy_tac_tang_can_nao_cham_diem(db_da_nap):
    rows = db_da_nap.execute(
        """SELECT rule_version_id, effect_class, max_effect FROM rule_versions
            WHERE rule_id LIKE 'BT-HIDDEN-%'""").fetchall()
    assert len(rows) == 13, "12 Chi cộng một quy tắc thứ tự"
    for r in rows:
        assert r["effect_class"] == "EXPLANATORY"
        assert r["max_effect"] is None


def test_khong_lot_ty_le_vao_du_lieu(db_da_nap):
    """Chữ 三分 trong câu Thìn không được biến thành con số."""
    import json
    r = db_da_nap.execute(
        "SELECT logic FROM rule_versions WHERE rule_version_id='BT-HIDDEN-005@1'"
    ).fetchone()
    logic = json.loads(r["logic"])
    assert logic["hidden_stems"] == ["AT", "MAU", "QUY"]
    assert "ty_le" in logic["khong_co"]
    assert not any(isinstance(v, (int, float)) for v in logic.values())


# ============ Đầu vào không hợp lệ ==================================

@pytest.mark.parametrize("xau", ["", "XYZ", "ty", "TÝ", "GIAP", None, 5])
def test_chi_khong_hop_le_bi_bao_loi(db_da_nap, xau):
    with pytest.raises(TangCanError, match="CHI_KHONG_HOP_LE"):
        lay_tang_can(db_da_nap, xau)


def test_chua_nap_thi_bao_loi_rieng(db_trong):
    from loi.kho_du_lieu.nap_mam import nap_mam
    nap_mam(db_trong)
    db_trong.execute("DELETE FROM branch_hidden_stems WHERE branch_index = 1")
    db_trong.commit()
    with pytest.raises(TangCanError, match="CHUA_NAP_TANG_CAN"):
        lay_tang_can(db_trong, "TY")
    assert do_phu_chi(db_trong) == "11/12"


# ============ Thứ tự: giữ nguyên trạng, không hợp nhất ==============

def test_quy_tac_thu_tu_dang_conflicted(db_da_nap):
    r = db_da_nap.execute(
        "SELECT status, confidence FROM rule_versions WHERE rule_version_id = ?",
        (f"{MA_QUY_TAC_THU_TU}@1",)).fetchone()
    assert r["status"] == "CONFLICTED"


def test_quy_tac_thu_tu_khong_duoc_bat(db_da_nap):
    r = db_da_nap.execute(
        "SELECT is_active FROM rule_registry WHERE rule_id = ?",
        (MA_QUY_TAC_THU_TU,)).fetchone()
    assert r["is_active"] == 0


@pytest.mark.parametrize("chi", sorted(CHI_DI_BIET_THU_TU))
def test_nam_chi_di_biet_giu_ca_hai_thu_tu(db_da_nap, chi):
    bien = thu_tu_cac_truyen_thong(db_da_nap, chi)
    assert len(bien) == 2, f"{chi} phải giữ cả hai thứ tự"
    ds = {b["tradition"]: b["stem_order"] for b in bien}
    assert set(ds) == {"UYEN_HAI_TU_BINH", "BANG_DOI_SAU"}
    # Khác thứ tự nhưng CÙNG tập Can.
    assert ds["UYEN_HAI_TU_BINH"] != ds["BANG_DOI_SAU"]
    assert sorted(ds["UYEN_HAI_TU_BINH"]) == sorted(ds["BANG_DOI_SAU"])
    # Engine dùng thứ tự của nguồn chính.
    assert list(lay_tang_can(db_da_nap, chi).hidden_stems) == ds["UYEN_HAI_TU_BINH"]


@pytest.mark.parametrize("chi", sorted(set(CHI) - CHI_DI_BIET_THU_TU))
def test_bay_chi_con_lai_khong_di_biet(db_da_nap, chi):
    assert thu_tu_cac_truyen_thong(db_da_nap, chi) == []


def test_moi_nguon_deu_thong_nhat_tap_can(db_da_nap):
    """Điểm mấu chốt: TẬP Can thống nhất, chỉ THỨ TỰ khác."""
    import json
    rows = db_da_nap.execute(
        "SELECT branch_index, tradition, stem_order FROM hidden_stem_order_variants"
    ).fetchall()
    theo_chi: dict[int, list[list[str]]] = {}
    for r in rows:
        theo_chi.setdefault(r["branch_index"], []).append(json.loads(r["stem_order"]))
    assert len(theo_chi) == 5
    for chi_i, cac_thu_tu in theo_chi.items():
        tap = {tuple(sorted(t)) for t in cac_thu_tu}
        assert len(tap) == 1, f"Chi {chi_i} khác cả tập Can, không chỉ khác thứ tự"


# ============ Phạm vi: chưa làm quyền khí ===========================

def test_quyen_khi_lam_o_giai_doan_khac_va_khong_duoc_bat(db_da_nap):
    """Quyền khí nay làm ở 3C, nhưng KHÔNG được bật để tính.

    Tàng Can là dữ liệu cấu trúc và đã VERIFIED.
    Quyền khí chỉ ghi nguồn nói gì, chưa đủ căn cứ, nên is_active phải là 0.
    """
    rows = db_da_nap.execute(
        "SELECT rule_id, is_active FROM rule_registry "
        "WHERE namespace = 'BT-SEASON-POWER'").fetchall()
    assert rows, "3C đã tạo quy tắc ghi nguồn"
    for r in rows:
        assert r["is_active"] == 0, f"{r['rule_id']} không được bật"


def test_chua_lam_cach_cuc_dung_than(db_da_nap):
    """Thập Thần làm ở 3B, nguyệt lệnh ở 3C. Cách cục và dụng thần thì chưa."""
    rows = db_da_nap.execute(
        "SELECT rule_id FROM rule_registry WHERE namespace IN ('BT-PAT','BT-USE','BT-REL')"
    ).fetchall()
    assert rows == [], "chưa tới phạm vi này"


def test_tang_can_khong_lan_sang_thap_than(db_da_nap):
    """Quy tắc Tàng Can không được chứa gì về Thập Thần."""
    import json
    for i in range(1, 13):
        r = db_da_nap.execute(
            "SELECT logic FROM rule_versions WHERE rule_version_id = ?",
            (f"BT-HIDDEN-{i:03d}@1",)).fetchone()
        logic = json.dumps(json.loads(r["logic"]), ensure_ascii=False)
        for tu in ("ten_god", "THAP_THAN", "TY_KIEN", "CHINH_QUAN"):
            assert tu not in logic


# ============ Kho quy tắc phải sạch sau khi nạp Tàng Can =============

def test_kiem_toan_kho_khong_loi_sau_khi_nap_tang_can(db_da_nap):
    """Nạp Tàng Can xong, toàn kho vẫn phải qua được bộ kiểm định."""
    from loi.kho_quy_tac.kiem_dinh import kiem_toan_kho
    loi = [x for x in kiem_toan_kho(db_da_nap) if x.muc == "LOI"]
    assert loi == [], [str(x) for x in loi]


def test_quy_tac_tang_can_khong_tua_vao_cho_trong(db_da_nap):
    """VERIFIED thì nguồn chính không được là chỗ trống chờ nguồn."""
    rows = db_da_nap.execute(
        """SELECT rv.rule_id, rvs.source_id
             FROM rule_versions rv
             JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
            WHERE rv.rule_id LIKE 'BT-HIDDEN-0%'
              AND rvs.source_level = 'PRIMARY'""").fetchall()
    assert len(rows) == 12
    for r in rows:
        assert r["source_id"] == "SRC-UHTB-CHEP", f"{r['rule_id']} sai nguồn chính"


def test_moi_quy_tac_tang_can_deu_gan_nguyen_van(db_da_nap):
    n = db_da_nap.execute(
        """SELECT COUNT(*) AS n FROM rule_version_passages
            WHERE rule_version_id LIKE 'BT-HIDDEN-0%'
              AND passage_id = 'PSG-UHTB-TANGCAN'""").fetchone()["n"]
    assert n == 12


def test_bang_tang_can_tua_vao_hai_nhom_bang_chung(db_da_nap):
    from loi.lich.do_phu import dem_bang_chung
    d = dem_bang_chung(db_da_nap, "BT-HIDDEN-003")
    assert d["SOURCE_COUNT"] == 2
    assert set(d["groups"]) == {"CLASSICAL_TEXT", "MODERN_PRACTITIONER_LITERATURE"}


# ============ Provenance không được rơi rụng ========================

@pytest.mark.parametrize("chi", CHI)
def test_payload_giu_source_order(db_da_nap, chi):
    """to_dict phải giữ source_order. Mất nó là mất dấu vết nguồn."""
    r = lay_tang_can(db_da_nap, chi)
    d = r.to_dict()
    assert "source_order" in d, "payload làm rơi source_order"
    assert d["source_order"] == list(r.source_order)
    assert d["source_order"] == list(range(1, len(d["hidden_stems"]) + 1))
    assert len(d["source_order"]) == len(d["hidden_stems"])


@pytest.mark.parametrize("chi", CHI)
def test_payload_du_sau_truong_bat_buoc(db_da_nap, chi):
    d = lay_tang_can(db_da_nap, chi).to_dict()
    assert set(d) == {"branch", "hidden_stems", "source_order",
                      "rule_ids", "source_status", "semantic_role_status"}


def test_tam_menh_thong_hoi_khong_lam_nguon_cho_tang_can_tinh(db_da_nap):
    """TMTH nói về quyền khí theo mùa, KHÔNG phải tập Tàng Can tĩnh.

    Hai khái niệm liên quan nhưng không đồng nhất. Không được lấy TMTH
    để tuyên bố mọi nguồn thống nhất tập Tàng Can.
    """
    rows = db_da_nap.execute(
        """SELECT rule_version_id, source_id FROM rule_version_sources
            WHERE rule_version_id LIKE 'BT-HIDDEN-%'
              AND source_id = 'SRC-TMTH-CHEP'""").fetchall()
    assert rows == [], (
        "Tam Mệnh Thông Hội đang được dùng làm nguồn cho Tàng Can tĩnh: "
        f"{[r['rule_version_id'] for r in rows]}")


def test_gia_thuyet_thu_tu_duoc_danh_dau_la_gia_thuyet():
    """Hai nhận định về lý do khác thứ tự phải mang nhãn HYPOTHESIS."""
    from loi.kho_du_lieu.nap_tang_can import doc_bang
    gt = doc_bang().get("gia_thuyet_thu_tu")
    assert gt is not None, "phải ghi lại giả thuyết, nhưng dán nhãn rõ"
    assert gt["status"] == "HYPOTHESIS"
    assert gt["source_id"] is None
    for x in gt["cac_gia_thuyet"]:
        assert "KHÔNG CÓ" in x["bang_chung"]


def test_bay_chi_khong_di_biet_dung_so_bay():
    from loi.kho_du_lieu.nap_tang_can import doc_bang
    raw = doc_bang()
    di_biet = {d["branch"] for d in raw["thu_tu_di_biet"]}
    assert len(di_biet) == 5
    assert len(set(CHI) - di_biet) == 7
