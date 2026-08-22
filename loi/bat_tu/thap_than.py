"""Thập Thần.

Việc duy nhất: cho Nhật chủ và một Thiên Can, trả về tên quan hệ.

Cách làm: TÍNH RA từ hai chiều, không tra bảng mười nhân mười.
    chiều ngũ hành  — đồng hành, ta sinh, sinh ta, ta khắc, khắc ta
    chiều âm dương  — đồng tính, khác tính
Năm nhân hai bằng mười.

Quan hệ sinh khắc đọc từ bảng element_relations trong cơ sở dữ liệu,
âm dương đọc từ bảng stems. Không chép cứng cái nào.

KHÔNG có mạnh yếu, điểm số, hỷ kỵ, cát hung, hay lời luận giải.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from loi.lich.quy_uoc_can_chi import CAN, CAN_VI
from loi.nen.phien_ban import GOC_DU_AN

DUONG_DAN_CAU_HINH = GOC_DU_AN / "cau_hinh" / "can_chi" / "thap_than.yaml"

CHIEU_QUAN_HE = ("DONG_HANH", "TA_SINH", "SINH_TA", "TA_KHAC", "KHAC_TA")
QUAN_HE_AM_DUONG = ("DONG_TINH", "KHAC_TINH")


class ThapThanError(Exception):
    pass


@dataclass(frozen=True)
class OThapThan:
    rule_id: str
    code: str
    name_vi: str
    name_original: str
    chieu: str
    tinh: str


@dataclass(frozen=True)
class KetQuaThapThan:
    day_master: str
    target_stem: str
    day_master_element: str
    target_element: str
    day_master_yinyang: str
    target_yinyang: str
    relation_direction: str
    polarity_relation: str
    ten_god: str
    ten_god_vi: str
    rule_id: str
    source_id: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "day_master": self.day_master,
            "target_stem": self.target_stem,
            "day_master_element": self.day_master_element,
            "target_element": self.target_element,
            "day_master_yinyang": self.day_master_yinyang,
            "target_yinyang": self.target_yinyang,
            "relation_direction": self.relation_direction,
            "polarity_relation": self.polarity_relation,
            "ten_god": self.ten_god,
            # Tên tiếng Việt đi kèm luôn. Tầng hiển thị không phải tự dịch mã.
            "ten_god_vi": self.ten_god_vi,
            "rule_id": self.rule_id,
            "source_id": self.source_id,
            "status": self.status,
        }


# ---------------------------------------------------------------
# Nạp lưới mười ô từ cấu hình
# ---------------------------------------------------------------

def doc_cau_hinh(duong_dan: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load((duong_dan or DUONG_DAN_CAU_HINH).read_text(encoding="utf-8"))


@lru_cache(maxsize=2)
def luoi_thap_than() -> dict[tuple[str, str], OThapThan]:
    raw = doc_cau_hinh()
    luoi: dict[tuple[str, str], OThapThan] = {}
    for x in raw["thap_than"]:
        khoa = (x["chieu"], x["tinh"])
        if khoa in luoi:
            raise ThapThanError(f"TRUNG_O: {khoa}")
        if x["chieu"] not in CHIEU_QUAN_HE:
            raise ThapThanError(f"CHIEU_LA: {x['chieu']}")
        if x["tinh"] not in QUAN_HE_AM_DUONG:
            raise ThapThanError(f"TINH_LA: {x['tinh']}")
        luoi[khoa] = OThapThan(x["rule_id"], x["code"], x["name_vi"],
                               x["name_original"], x["chieu"], x["tinh"])
    thieu = [(c, t) for c in CHIEU_QUAN_HE for t in QUAN_HE_AM_DUONG if (c, t) not in luoi]
    if thieu:
        raise ThapThanError(f"THIEU_O: {thieu}")
    if len(luoi) != 10:
        raise ThapThanError(f"SO_O_SAI: {len(luoi)}")
    return luoi


# ---------------------------------------------------------------
# Tính chiều quan hệ từ bảng sinh khắc trong cơ sở dữ liệu
# ---------------------------------------------------------------

def _quan_he_ngu_hanh(conn: sqlite3.Connection, hanh_nhat_chu: str,
                      hanh_doi_tuong: str) -> str:
    if hanh_nhat_chu == hanh_doi_tuong:
        return "DONG_HANH"

    def co(a: str, b: str, quan_he: str) -> bool:
        return conn.execute(
            "SELECT 1 FROM element_relations "
            "WHERE from_element=? AND to_element=? AND relation=?",
            (a, b, quan_he)).fetchone() is not None

    if co(hanh_nhat_chu, hanh_doi_tuong, "SINH"):
        return "TA_SINH"
    if co(hanh_doi_tuong, hanh_nhat_chu, "SINH"):
        return "SINH_TA"
    if co(hanh_nhat_chu, hanh_doi_tuong, "KHAC"):
        return "TA_KHAC"
    if co(hanh_doi_tuong, hanh_nhat_chu, "KHAC"):
        return "KHAC_TA"
    raise ThapThanError(
        f"KHONG_XAC_DINH_DUOC_QUAN_HE: {hanh_nhat_chu} với {hanh_doi_tuong}")


def _thong_tin_can(conn: sqlite3.Connection, can: str) -> tuple[str, str]:
    r = conn.execute(
        "SELECT element_code, polarity FROM stems WHERE code = ?", (can,)).fetchone()
    if r is None:
        raise ThapThanError(f"CHUA_NAP_CAN: {can}")
    return r["element_code"], r["polarity"]


def tinh_thap_than(conn: sqlite3.Connection, day_master: str,
                   target_stem: str) -> KetQuaThapThan:
    """Nhật chủ gặp một Thiên Can thì gọi là gì."""
    for ten, gt in (("day_master", day_master), ("target_stem", target_stem)):
        if gt not in CAN:
            raise ThapThanError(
                f"CAN_KHONG_HOP_LE: {ten}={gt!r}. Chỉ nhận {', '.join(CAN)}")

    hanh_nc, am_duong_nc = _thong_tin_can(conn, day_master)
    hanh_dt, am_duong_dt = _thong_tin_can(conn, target_stem)

    chieu = _quan_he_ngu_hanh(conn, hanh_nc, hanh_dt)
    tinh = "DONG_TINH" if am_duong_nc == am_duong_dt else "KHAC_TINH"

    o = luoi_thap_than()[(chieu, tinh)]
    trang_thai = conn.execute(
        "SELECT status, source_id FROM ten_gods WHERE ten_god_code = ?",
        (o.code,)).fetchone()
    if trang_thai is None:
        raise ThapThanError(f"CHUA_NAP_THAP_THAN: {o.code}")

    return KetQuaThapThan(
        day_master=day_master, target_stem=target_stem,
        day_master_element=hanh_nc, target_element=hanh_dt,
        day_master_yinyang=am_duong_nc, target_yinyang=am_duong_dt,
        relation_direction=chieu, polarity_relation=tinh,
        ten_god=o.code, ten_god_vi=o.name_vi,
        rule_id=o.rule_id, source_id=trang_thai["source_id"],
        status=trang_thai["status"],
    )


# ---------------------------------------------------------------
# Tầng áp dụng vào Tứ Trụ
# ---------------------------------------------------------------

@dataclass(frozen=True)
class ViTriThapThan:
    position: str                 # YEAR_STEM, MONTH_HIDDEN_2, ...
    stem: str
    ket_qua: KetQuaThapThan | None
    la_nhat_chu: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"position": self.position, "stem": self.stem,
                             "la_nhat_chu": self.la_nhat_chu}
        d["ten_god"] = None if self.ket_qua is None else self.ket_qua.ten_god
        d["ten_god_vi"] = None if self.ket_qua is None else self.ket_qua.ten_god_vi
        if self.ket_qua is not None:
            d["rule_id"] = self.ket_qua.rule_id
        return d


TRU = ("YEAR", "MONTH", "DAY", "HOUR")


def ap_dung_tu_tru(conn: sqlite3.Connection, day_master: str,
                   can_theo_tru: dict[str, str],
                   chi_theo_tru: dict[str, str] | None = None) -> list[ViTriThapThan]:
    """Gán Thập Thần cho từng Can trong Tứ Trụ, kể cả Can tàng.

    Can ngày CHÍNH LÀ Nhật chủ. Nó không có Thập Thần với chính nó,
    và được đánh dấu riêng thay vì gán bừa một tên.
    """
    from loi.bat_tu.tang_can import lay_tang_can

    ket: list[ViTriThapThan] = []
    for tru in TRU:
        can = can_theo_tru.get(tru)
        if can is None:
            continue
        vi_tri = f"{tru}_STEM"
        if tru == "DAY":
            if can != day_master:
                raise ThapThanError(
                    f"NHAT_CHU_KHONG_KHOP: Can ngày là {can} nhưng Nhật chủ khai {day_master}")
            ket.append(ViTriThapThan(vi_tri, can, None, la_nhat_chu=True))
        else:
            ket.append(ViTriThapThan(vi_tri, can, tinh_thap_than(conn, day_master, can)))

    for tru in TRU:
        chi = (chi_theo_tru or {}).get(tru)
        if chi is None:
            continue
        tc = lay_tang_can(conn, chi)
        for thu_tu, can in zip(tc.source_order, tc.hidden_stems):
            ket.append(ViTriThapThan(
                f"{tru}_HIDDEN_{thu_tu}", can,
                tinh_thap_than(conn, day_master, can)))
    return ket


def viet_hoa_can(can: str) -> str:
    return CAN_VI[CAN.index(can)]
