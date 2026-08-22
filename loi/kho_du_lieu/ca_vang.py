"""Khung ca vàng.

Nguyên tắc cứng nhất của tệp này:

  Máy KHÔNG được tự sinh đáp án mong đợi rồi tự chấm mình đúng.

Cho nên:
  - ca chưa có người duyệt thì REVIEW_STATUS = PENDING;
  - bộ chạy bỏ ca PENDING ra khỏi tỷ lệ đạt, và báo riêng số lượng;
  - ca có nhóm chưa có bộ tính tương ứng thì ghi BLOCKED, không ghi FAIL.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from loi.nen.phien_ban import DUONG_DAN, ENGINE_VERSION, RULESET_VERSION
from loi.nen.trang_thai import CaseResult, GoldenCategory

NHOM_HOP_LE = {c.value for c in GoldenCategory}
TRANG_THAI_HOP_LE = {"PENDING", "APPROVED", "REJECTED", "NEEDS_REWORK"}
TRANG_THAI_DAP_AN = {"PENDING", "APPROVED", "REJECTED", "CONFLICTED"}


class GoldenCaseError(Exception):
    pass


@dataclass
class ExpectedEntry:
    stage: str          # INTERMEDIATE hoặc FINAL
    stage_key: str
    payload: Any
    review_status: str = "PENDING"
    source_id: str | None = None      # nguồn cho ĐÚNG lớp này, không phải cho cả ca
    source_note: str | None = None
    tolerance_seconds: float | None = None   # dùng khi đáp án là một mốc thời gian

    @property
    def duoc_cham(self) -> bool:
        return self.review_status == "APPROVED"


@dataclass
class GoldenCase:
    case_id: str
    category: str
    title_vi: str
    ruleset_version: str
    input_payload: dict[str, Any]
    source_id: str | None = None
    source_location: str | None = None
    calendar_ruleset_id: str | None = None
    review_status: str = "PENDING"
    reviewed_by: str | None = None
    notes: str | None = None
    expected: list[ExpectedEntry] = field(default_factory=list)

    @property
    def dap_an_duoc_cham(self) -> list[ExpectedEntry]:
        return [e for e in self.expected if e.duoc_cham]

    @property
    def dap_an_chua_duyet(self) -> list[ExpectedEntry]:
        return [e for e in self.expected if not e.duoc_cham]

    @property
    def duyet_tung_phan(self) -> bool:
        """Ca đã duyệt nhưng còn lớp chưa chốt."""
        return bool(self.dap_an_duoc_cham) and bool(self.dap_an_chua_duyet)

    @property
    def san_sang_cham(self) -> bool:
        """Ca được chấm khi đã duyệt và có ÍT NHẤT MỘT lớp đáp án đã duyệt.

        Một lớp còn tranh luận không được phép làm cả ca thành vô dụng.
        Lớp chưa duyệt bị bỏ qua khi chấm và được đếm riêng.
        """
        return self.review_status == "APPROVED" and bool(self.dap_an_duoc_cham)


# ---------------------------------------------------------------
# Bộ tải
# ---------------------------------------------------------------

def tai_ca_tu_tep(duong_dan: Path) -> GoldenCase:
    raw = yaml.safe_load(duong_dan.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GoldenCaseError(f"CA_HONG: {duong_dan.name}")

    expected = []
    for e in raw.get("expected", []) or []:
        expected.append(
            ExpectedEntry(
                stage=str(e["stage"]).upper(),
                stage_key=str(e["stage_key"]),
                payload=e["payload"],
                review_status=str(e.get("review_status", "PENDING")).upper(),
                source_id=e.get("source_id"),
                source_note=e.get("source_note"),
                tolerance_seconds=e.get("tolerance_seconds"),
            )
        )

    ca = GoldenCase(
        case_id=raw["case_id"],
        category=str(raw["category"]).upper(),
        title_vi=raw["title_vi"],
        ruleset_version=str(raw["ruleset_version"]),
        input_payload=raw.get("input") or {},
        source_id=raw.get("source_id"),
        source_location=raw.get("source_location"),
        calendar_ruleset_id=raw.get("calendar_ruleset_id"),
        review_status=str(raw.get("review_status", "PENDING")).upper(),
        reviewed_by=raw.get("reviewed_by"),
        notes=raw.get("notes"),
        expected=expected,
    )
    kiem_ca(ca)
    return ca


def tai_tat_ca(thu_muc: Path | None = None) -> list[GoldenCase]:
    thu_muc = thu_muc or DUONG_DAN["ca_vang"]
    ket_qua: list[GoldenCase] = []
    da_thay: set[str] = set()
    for tep in sorted(thu_muc.rglob("*.yaml")):
        ca = tai_ca_tu_tep(tep)
        if ca.case_id in da_thay:
            raise GoldenCaseError(f"TRUNG_CASE_ID: {ca.case_id}")
        da_thay.add(ca.case_id)
        ket_qua.append(ca)
    return ket_qua


# ---------------------------------------------------------------
# Bộ kiểm định
# ---------------------------------------------------------------

def kiem_ca(ca: GoldenCase) -> None:
    if ca.category not in NHOM_HOP_LE:
        raise GoldenCaseError(f"NHOM_LA: {ca.case_id} có nhóm {ca.category}")
    if ca.review_status not in TRANG_THAI_HOP_LE:
        raise GoldenCaseError(f"TRANG_THAI_LA: {ca.case_id} = {ca.review_status}")
    if not ca.ruleset_version:
        raise GoldenCaseError(f"THIEU_RULESET_VERSION: {ca.case_id}")
    if not ca.input_payload:
        raise GoldenCaseError(f"THIEU_INPUT: {ca.case_id}")

    # Ca đã duyệt thì bắt buộc phải truy được về nguồn và phải có người duyệt.
    if ca.review_status == "APPROVED":
        if not ca.source_id:
            raise GoldenCaseError(f"THIEU_SOURCE: {ca.case_id} đã duyệt nhưng không ghi nguồn")
        if not ca.reviewed_by:
            raise GoldenCaseError(f"THIEU_NGUOI_DUYET: {ca.case_id}")
        if not ca.expected:
            raise GoldenCaseError(f"THIEU_EXPECTED: {ca.case_id} đã duyệt nhưng không có đáp án")

    for e in ca.expected:
        if e.stage not in {"INTERMEDIATE", "FINAL"}:
            raise GoldenCaseError(f"STAGE_LA: {ca.case_id}.{e.stage_key} = {e.stage}")
        if e.review_status not in TRANG_THAI_DAP_AN:
            raise GoldenCaseError(
                f"TRANG_THAI_DAP_AN_LA: {ca.case_id}.{e.stage_key} = {e.review_status}")
        # Đáp án được đánh dấu đã duyệt thì ca cũng phải đã duyệt.
        if e.review_status == "APPROVED" and ca.review_status != "APPROVED":
            raise GoldenCaseError(
                f"DAP_AN_DUYET_TRUOC_CA: {ca.case_id}.{e.stage_key}"
            )
        # Mỗi lớp đáp án đã duyệt phải tự ghi nguồn của riêng nó.
        if e.review_status == "APPROVED" and not e.source_id:
            raise GoldenCaseError(
                f"THIEU_NGUON_THEO_LOP: {ca.case_id}.{e.stage_key} đã duyệt "
                "nhưng không ghi nguồn riêng cho lớp này")


# ---------------------------------------------------------------
# Ghi vào cơ sở dữ liệu
# ---------------------------------------------------------------

def dong_bo_vao_db(conn: sqlite3.Connection, ca: GoldenCase) -> None:
    conn.execute(
        """
        INSERT INTO golden_cases
            (case_id, category, title_vi, source_id, source_location, ruleset_version,
             calendar_ruleset_id, input_payload, review_status, reviewed_by, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(case_id) DO UPDATE SET
            category = excluded.category,
            title_vi = excluded.title_vi,
            source_id = excluded.source_id,
            source_location = excluded.source_location,
            ruleset_version = excluded.ruleset_version,
            calendar_ruleset_id = excluded.calendar_ruleset_id,
            input_payload = excluded.input_payload,
            review_status = excluded.review_status,
            reviewed_by = excluded.reviewed_by,
            notes = excluded.notes,
            updated_at = datetime('now')
        """,
        (ca.case_id, ca.category, ca.title_vi, ca.source_id, ca.source_location,
         ca.ruleset_version, ca.calendar_ruleset_id,
         json.dumps(ca.input_payload, ensure_ascii=False),
         ca.review_status, ca.reviewed_by, ca.notes),
    )
    for e in ca.expected:
        conn.execute(
            """
            INSERT INTO golden_case_expected
                (expected_id, case_id, stage, stage_key, expected_payload,
                 tolerance_seconds, source_id, source_note, review_status, reviewed_by)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(case_id, stage, stage_key) DO UPDATE SET
                expected_payload = excluded.expected_payload,
                tolerance_seconds = excluded.tolerance_seconds,
                source_id = excluded.source_id,
                source_note = excluded.source_note,
                review_status = excluded.review_status,
                reviewed_by = excluded.reviewed_by
            """,
            (f"{ca.case_id}:{e.stage}:{e.stage_key}", ca.case_id, e.stage, e.stage_key,
             json.dumps(e.payload, ensure_ascii=False), e.tolerance_seconds,
             e.source_id, e.source_note, e.review_status, ca.reviewed_by),
        )


# ---------------------------------------------------------------
# Bộ chạy
# ---------------------------------------------------------------

# Mỗi nhóm cần một bộ tính. Bộ tính nhận input, trả về bảng khoá-giá trị.
# Giai đoạn này chưa có bộ tính nào, nên bảng để trống một cách cố ý.
BoTinh = Callable[[dict[str, Any]], dict[str, Any]]
BANG_BO_TINH: dict[str, BoTinh] = {}


def dang_ky_bo_tinh(nhom: str, ham: BoTinh) -> None:
    if nhom not in NHOM_HOP_LE:
        raise GoldenCaseError(f"NHOM_LA: {nhom}")
    BANG_BO_TINH[nhom] = ham


@dataclass
class KetQuaChay:
    test_run_id: str
    tong_so: int = 0
    dat: int = 0
    truot: int = 0
    bi_chan: int = 0
    cho_duyet: int = 0
    lop_da_cham: int = 0
    lop_chua_duyet: int = 0
    chi_tiet: list[tuple[str, str, str]] = field(default_factory=list)

    @property
    def so_ca_duoc_cham(self) -> int:
        return self.dat + self.truot

    @property
    def ty_le_dat(self) -> float | None:
        """Tỷ lệ đạt chính thức. Ca chờ duyệt và ca bị chặn không nằm trong mẫu số."""
        if self.so_ca_duoc_cham == 0:
            return None
        return self.dat / self.so_ca_duoc_cham


def chay(conn: sqlite3.Connection,
         cac_ca: list[GoldenCase] | None = None,
         test_run_id: str | None = None) -> KetQuaChay:
    cac_ca = cac_ca if cac_ca is not None else tai_tat_ca()
    run_id = test_run_id or f"RUN-{ENGINE_VERSION}-{len(cac_ca)}"

    conn.execute(
        """INSERT INTO test_runs (test_run_id, engine_version, ruleset_version)
           VALUES (?,?,?)
           ON CONFLICT(test_run_id) DO NOTHING""",
        (run_id, ENGINE_VERSION, RULESET_VERSION),
    )

    kq = KetQuaChay(test_run_id=run_id)
    for ca in cac_ca:
        kq.tong_so += 1

        if not ca.san_sang_cham:
            trang_thai = CaseResult.PENDING_EXCLUDED
            chi_tiet = f"review_status={ca.review_status}, chua co lop dap an nao duoc duyet"
            kq.cho_duyet += 1
            kq.lop_chua_duyet += len(ca.expected)
        elif ca.category not in BANG_BO_TINH:
            trang_thai = CaseResult.BLOCKED
            chi_tiet = f"chua co bo tinh cho nhom {ca.category}"
            kq.bi_chan += 1
        else:
            try:
                thuc_te = BANG_BO_TINH[ca.category](ca.input_payload)
                kq.lop_da_cham += len(ca.dap_an_duoc_cham)
                kq.lop_chua_duyet += len(ca.dap_an_chua_duyet)
                lech = _so_sanh(ca, thuc_te)
                if lech:
                    trang_thai = CaseResult.FAIL
                    chi_tiet = "; ".join(lech)
                    kq.truot += 1
                else:
                    trang_thai = CaseResult.PASS
                    chi_tiet = (f"khop {len(ca.dap_an_duoc_cham)} lop da duyet"
                                + (f"; bo qua {len(ca.dap_an_chua_duyet)} lop chua duyet"
                                   if ca.dap_an_chua_duyet else ""))
                    kq.dat += 1
            except Exception as loi:  # bộ tính hỏng thì ghi FAIL, không ghi PASS
                trang_thai = CaseResult.FAIL
                chi_tiet = f"bo tinh nem loi: {loi}"
                kq.truot += 1

        kq.chi_tiet.append((ca.case_id, trang_thai.value, chi_tiet))
        conn.execute(
            """INSERT INTO test_run_results (test_run_id, case_id, status, detail)
               VALUES (?,?,?,?)
               ON CONFLICT(test_run_id, case_id) DO UPDATE SET
                   status = excluded.status, detail = excluded.detail""",
            (run_id, ca.case_id, trang_thai.value, chi_tiet),
        )

    conn.execute(
        """UPDATE test_runs SET finished_at = datetime('now'),
               total_cases = ?, passed = ?, failed = ?, blocked = ?, pending_excluded = ?
           WHERE test_run_id = ?""",
        (kq.tong_so, kq.dat, kq.truot, kq.bi_chan, kq.cho_duyet, run_id),
    )
    conn.commit()
    return kq


def _so_sanh(ca: GoldenCase, thuc_te: dict[str, Any]) -> list[str]:
    lech: list[str] = []
    for e in ca.dap_an_duoc_cham:
        if e.stage_key not in thuc_te:
            lech.append(f"thieu khoa {e.stage_key}")
            continue
        co = thuc_te[e.stage_key]
        if e.tolerance_seconds is not None:
            sai = _lech_giay(e.payload, co)
            if sai is None:
                lech.append(f"{e.stage_key}: khong doc duoc moc thoi gian {co!r}")
            elif sai > e.tolerance_seconds:
                lech.append(f"{e.stage_key}: lech {sai:.1f} giay, cho phep "
                            f"{e.tolerance_seconds} giay (mong doi {e.payload}, thuc te {co})")
        elif co != e.payload:
            lech.append(f"{e.stage_key}: mong doi {e.payload!r}, thuc te {co!r}")
    return lech


def _lech_giay(a: Any, b: Any) -> float | None:
    from datetime import datetime
    try:
        da = datetime.fromisoformat(str(a).replace("Z", "+00:00"))
        db = datetime.fromisoformat(str(b).replace("Z", "+00:00"))
    except ValueError:
        return None
    return abs((da - db).total_seconds())


def thong_ke_theo_nhom(cac_ca: list[GoldenCase]) -> dict[str, dict[str, int]]:
    bang: dict[str, dict[str, int]] = {n: {"tong": 0, "da_duyet": 0, "cho_duyet": 0}
                                       for n in sorted(NHOM_HOP_LE)}
    for ca in cac_ca:
        bang[ca.category]["tong"] += 1
        if ca.san_sang_cham:
            bang[ca.category]["da_duyet"] += 1
        else:
            bang[ca.category]["cho_duyet"] += 1
    return bang
