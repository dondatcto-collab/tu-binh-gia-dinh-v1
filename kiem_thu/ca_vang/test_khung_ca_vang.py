"""Kiểm thử khung ca vàng.

Điểm quan trọng nhất: ca chưa được người duyệt thì tuyệt đối không được tính là đạt.
"""

from __future__ import annotations

import pytest
import yaml

from loi.kho_du_lieu import ca_vang
from loi.kho_du_lieu.ca_vang import (
    ExpectedEntry,
    GoldenCase,
    GoldenCaseError,
    tai_ca_tu_tep,
    tai_tat_ca,
)
from loi.nen.phien_ban import DUONG_DAN


@pytest.fixture(autouse=True)
def bang_bo_tinh_sach():
    """Mỗi bài test bắt đầu với bảng bộ tính rỗng, kết thúc thì trả lại như cũ."""
    cu = dict(ca_vang.BANG_BO_TINH)
    ca_vang.BANG_BO_TINH.clear()
    yield
    ca_vang.BANG_BO_TINH.clear()
    ca_vang.BANG_BO_TINH.update(cu)


def _ca_cho_duyet(case_id="X-0001", category="GOLD-CAL") -> GoldenCase:
    return GoldenCase(
        case_id=case_id, category=category, title_vi="Ca chờ duyệt",
        ruleset_version="RS-T", input_payload={"a": 1},
    )


def _ca_da_duyet(case_id="X-0002", category="GOLD-CAL") -> GoldenCase:
    return GoldenCase(
        case_id=case_id, category=category, title_vi="Ca đã duyệt",
        ruleset_version="RS-T", input_payload={"a": 1},
        source_id="SRC-T", review_status="APPROVED", reviewed_by="nguoi_duyet",
        expected=[ExpectedEntry("FINAL", "ket_qua", 42, review_status="APPROVED",
                                source_id="SRC-T")],
    )


# --- Bộ tải và bộ kiểm định ------------------------------------------

def test_tai_duoc_ca_tren_dia():
    cac_ca = tai_tat_ca()
    assert len(cac_ca) >= 6
    nhom = {c.category for c in cac_ca}
    assert nhom == {"GOLD-CAL", "GOLD-BT", "GOLD-HK", "GOLD-SS", "GOLD-FUS", "GOLD-END"}


def test_ca_da_duyet_phai_co_dau_vet_nguoi_duyet():
    """Máy được ĐỀ XUẤT đáp án. Máy không được TỰ DUYỆT đáp án của chính nó.

    Dấu vết bắt buộc của một ca đã duyệt: có tên người duyệt, và mỗi lớp
    đáp án đã duyệt phải tự ghi nguồn riêng.
    """
    for ca in tai_tat_ca():
        if ca.review_status != "APPROVED":
            assert not ca.san_sang_cham, f"{ca.case_id} chưa duyệt mà đang được chấm"
            continue
        assert ca.reviewed_by, f"{ca.case_id} đã duyệt nhưng không ghi ai duyệt"
        for e in ca.dap_an_duoc_cham:
            assert e.source_id, f"{ca.case_id}.{e.stage_key} đã duyệt nhưng thiếu nguồn riêng"


def test_ca_chua_duyet_van_khong_duoc_tinh_diem(db_da_nap):
    """Ca chưa duyệt bị bộ chạy loại khỏi tỷ lệ đạt, dù đã soạn sẵn đáp án."""
    cac_ca = [c for c in tai_tat_ca() if c.review_status != "APPROVED"]
    assert cac_ca, "cần ít nhất một ca chưa duyệt để kiểm điều này"
    for ca in cac_ca:
        ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, cac_ca, test_run_id="R-CHUADUYET")
    assert kq.dat == 0 and kq.truot == 0
    assert kq.cho_duyet == len(cac_ca)
    assert kq.ty_le_dat is None


def test_lop_conflicted_bi_loai_khoi_cham_diem(db_da_nap):
    """Lớp CONFLICTED không được chấm, nhưng không làm cả ca thành vô dụng."""
    cac = [c for c in tai_tat_ca() if c.duyet_tung_phan]
    assert cac, "cần ít nhất một ca duyệt từng phần"
    for ca in cac:
        assert ca.san_sang_cham, f"{ca.case_id} phải vẫn chấm được phần đã duyệt"
        assert any(e.review_status == "CONFLICTED" for e in ca.dap_an_chua_duyet)
        for e in ca.dap_an_chua_duyet:
            assert not e.duoc_cham


def _viet_ca(tmp_path, raw: dict):
    tep = tmp_path / "ca.yaml"
    tep.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    return tep


def test_ca_da_duyet_ma_thieu_nguon_thi_bao_loi(tmp_path):
    tep = _viet_ca(tmp_path, {
        "case_id": "T-1", "category": "GOLD-CAL", "title_vi": "t",
        "ruleset_version": "RS-T", "input": {"a": 1},
        "review_status": "APPROVED", "reviewed_by": "ai_do",
        "expected": [{"stage": "FINAL", "stage_key": "k", "payload": 1}],
    })
    with pytest.raises(GoldenCaseError, match="THIEU_SOURCE"):
        tai_ca_tu_tep(tep)


def test_ca_thieu_ruleset_version_thi_bao_loi(tmp_path):
    tep = _viet_ca(tmp_path, {
        "case_id": "T-2", "category": "GOLD-CAL", "title_vi": "t",
        "ruleset_version": "", "input": {"a": 1},
    })
    with pytest.raises(GoldenCaseError, match="THIEU_RULESET_VERSION"):
        tai_ca_tu_tep(tep)


def test_ca_nhom_la_thi_bao_loi(tmp_path):
    tep = _viet_ca(tmp_path, {
        "case_id": "T-3", "category": "GOLD-TUVI", "title_vi": "t",
        "ruleset_version": "RS-T", "input": {"a": 1},
    })
    with pytest.raises(GoldenCaseError, match="NHOM_LA"):
        tai_ca_tu_tep(tep)


def test_dap_an_duyet_truoc_ca_thi_bao_loi(tmp_path):
    tep = _viet_ca(tmp_path, {
        "case_id": "T-4", "category": "GOLD-CAL", "title_vi": "t",
        "ruleset_version": "RS-T", "input": {"a": 1},
        "review_status": "PENDING",
        "expected": [{"stage": "FINAL", "stage_key": "k", "payload": 1,
                      "review_status": "APPROVED"}],
    })
    with pytest.raises(GoldenCaseError, match="DAP_AN_DUYET_TRUOC_CA"):
        tai_ca_tu_tep(tep)


def test_ca_da_duyet_ma_khong_co_dap_an_thi_bao_loi(tmp_path):
    tep = _viet_ca(tmp_path, {
        "case_id": "T-5", "category": "GOLD-CAL", "title_vi": "t",
        "ruleset_version": "RS-T", "input": {"a": 1},
        "review_status": "APPROVED", "reviewed_by": "ai_do", "source_id": "S",
        "expected": [],
    })
    with pytest.raises(GoldenCaseError, match="THIEU_EXPECTED"):
        tai_ca_tu_tep(tep)


# --- Bộ chạy ---------------------------------------------------------

def test_ca_cho_duyet_khong_duoc_tinh_dat(db_da_nap):
    ca = _ca_cho_duyet()
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    ca_vang.dang_ky_bo_tinh("GOLD-CAL", lambda inp: {"ket_qua": 42})

    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R1")
    assert kq.dat == 0
    assert kq.truot == 0
    assert kq.cho_duyet == 1
    assert kq.so_ca_duoc_cham == 0
    assert kq.ty_le_dat is None, "không được bịa ra tỷ lệ đạt khi chưa có ca nào được chấm"
    assert kq.chi_tiet[0][1] == "PENDING_EXCLUDED"


def test_ca_da_duyet_duoc_runner_nhan(db_da_nap):
    ca = _ca_da_duyet()
    db_da_nap.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
                                primary_or_secondary, status, independence_group)
           VALUES ('SRC-T','Nguồn thử','vi','OTHER','PRIMARY','ACTIVE','GOLDEN_CASE')""")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    ca_vang.dang_ky_bo_tinh("GOLD-CAL", lambda inp: {"ket_qua": 42})

    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R2")
    assert kq.dat == 1 and kq.truot == 0 and kq.cho_duyet == 0
    assert kq.ty_le_dat == 1.0


def test_ca_da_duyet_ma_sai_thi_truot(db_da_nap):
    ca = _ca_da_duyet()
    db_da_nap.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
                                primary_or_secondary, status, independence_group)
           VALUES ('SRC-T','Nguồn thử','vi','OTHER','PRIMARY','ACTIVE','GOLDEN_CASE')""")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)
    ca_vang.dang_ky_bo_tinh("GOLD-CAL", lambda inp: {"ket_qua": 7})

    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R3")
    assert kq.dat == 0 and kq.truot == 1
    assert kq.ty_le_dat == 0.0
    assert "mong doi 42" in kq.chi_tiet[0][2]


def test_bo_tinh_nem_loi_thi_ghi_truot_khong_ghi_dat(db_da_nap):
    ca = _ca_da_duyet()
    db_da_nap.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
                                primary_or_secondary, status, independence_group)
           VALUES ('SRC-T','Nguồn thử','vi','OTHER','PRIMARY','ACTIVE','GOLDEN_CASE')""")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)

    def bo_tinh_hong(inp):
        raise RuntimeError("chưa cài đặt")

    ca_vang.dang_ky_bo_tinh("GOLD-CAL", bo_tinh_hong)
    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R4")
    assert kq.truot == 1 and kq.dat == 0


def test_thieu_bo_tinh_thi_ghi_bi_chan_khong_ghi_truot(db_da_nap):
    ca = _ca_da_duyet()
    db_da_nap.execute(
        """INSERT INTO sources (source_id, title, language, source_type,
                                primary_or_secondary, status, independence_group)
           VALUES ('SRC-T','Nguồn thử','vi','OTHER','PRIMARY','ACTIVE','GOLDEN_CASE')""")
    ca_vang.dong_bo_vao_db(db_da_nap, ca)

    kq = ca_vang.chay(db_da_nap, [ca], test_run_id="R5")
    assert kq.bi_chan == 1 and kq.truot == 0 and kq.dat == 0
    assert kq.ty_le_dat is None


def test_ghi_lai_lan_chay_vao_co_so_du_lieu(db_da_nap):
    cac_ca = [c for c in tai_tat_ca() if c.review_status != "APPROVED"]
    for ca in cac_ca:
        ca_vang.dong_bo_vao_db(db_da_nap, ca)
    kq = ca_vang.chay(db_da_nap, cac_ca, test_run_id="R6")

    row = db_da_nap.execute(
        "SELECT * FROM test_runs WHERE test_run_id='R6'").fetchone()
    assert row["total_cases"] == len(cac_ca)
    assert row["pending_excluded"] == len(cac_ca)
    assert row["passed"] == 0 and row["failed"] == 0
    assert row["finished_at"] is not None

    n = db_da_nap.execute(
        "SELECT COUNT(*) AS n FROM test_run_results WHERE test_run_id='R6' "
        "AND status='PENDING_EXCLUDED'").fetchone()["n"]
    assert n == len(cac_ca)


def test_thong_ke_theo_nhom_du_sau_nhom():
    bang = ca_vang.thong_ke_theo_nhom(tai_tat_ca())
    assert set(bang) == {"GOLD-CAL", "GOLD-BT", "GOLD-HK", "GOLD-SS", "GOLD-FUS", "GOLD-END"}
    # Lịch pháp và Tàng Can đã có ca duyệt. Bốn nhóm còn lại vẫn trắng.
    assert bang["GOLD-CAL"]["da_duyet"] == 6
    assert bang["GOLD-BT"]["da_duyet"] == 6
    for nhom in ("GOLD-HK", "GOLD-SS", "GOLD-FUS", "GOLD-END"):
        assert bang[nhom]["da_duyet"] == 0


def test_trung_case_id_thi_bao_loi(tmp_path):
    for ten in ("a.yaml", "b.yaml"):
        (tmp_path / ten).write_text(yaml.safe_dump({
            "case_id": "DUP-1", "category": "GOLD-CAL", "title_vi": "t",
            "ruleset_version": "RS-T", "input": {"a": 1},
        }, allow_unicode=True), encoding="utf-8")
    with pytest.raises(GoldenCaseError, match="TRUNG_CASE_ID"):
        tai_tat_ca(tmp_path)


def test_thu_muc_ca_vang_dung_duong_dan():
    assert DUONG_DAN["ca_vang"].is_dir()
