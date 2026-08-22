"""Bộ tính cho ca vàng nhóm Bát Tự.

Giai đoạn 3A chỉ phục vụ Tàng Can cấu trúc.
Nhận đầu vào là danh sách Địa Chi, trả về Tàng Can của từng Chi.
"""

from __future__ import annotations

from typing import Any

from loi.bat_tu.tang_can import lay_tang_can
from loi.kho_du_lieu import ca_vang
from loi.kho_du_lieu.ket_noi import mo_ket_noi


def tinh_ca_bat_tu(dau_vao: dict[str, Any]) -> dict[str, Any]:
    conn = mo_ket_noi()
    try:
        ket: dict[str, Any] = {}
        for chi in dau_vao.get("cac_chi", []) or []:
            r = lay_tang_can(conn, chi)
            ket[f"tang_can:{chi}"] = list(r.hidden_stems)
            ket[f"so_can:{chi}"] = len(r.hidden_stems)
            ket[f"vai_tro:{chi}"] = r.semantic_role_status
            ket[f"rule_id:{chi}"] = list(r.rule_ids)
        return ket
    finally:
        conn.close()


def _bo_tinh_chung(dau_vao):
    """Một bộ tính cho cả nhóm. Chọn nhánh theo hình dạng đầu vào."""
    if "day_master" in dau_vao:
        return tinh_ca_thap_than(dau_vao)
    return tinh_ca_bat_tu(dau_vao)


def dang_ky() -> None:
    ca_vang.dang_ky_bo_tinh("GOLD-BT", _bo_tinh_chung)


def tinh_ca_thap_than(dau_vao: dict[str, Any]) -> dict[str, Any]:
    """Bộ tính cho ca vàng Thập Thần."""
    from loi.bat_tu.thap_than import ap_dung_tu_tru, tinh_thap_than
    conn = mo_ket_noi()
    try:
        ket: dict[str, Any] = {}
        nc = dau_vao.get("day_master")
        for dt in dau_vao.get("cac_can_doi_tuong", []) or []:
            r = tinh_thap_than(conn, nc, dt)
            ket[f"thap_than:{nc}:{dt}"] = r.ten_god
            ket[f"chieu:{nc}:{dt}"] = r.relation_direction
            ket[f"tinh:{nc}:{dt}"] = r.polarity_relation
        if dau_vao.get("tu_tru"):
            tt = dau_vao["tu_tru"]
            for x in ap_dung_tu_tru(conn, nc, tt.get("can", {}), tt.get("chi", {})):
                ket[f"vi_tri:{x.position}"] = (
                    "NHAT_CHU" if x.la_nhat_chu else x.ket_qua.ten_god)
        return ket
    finally:
        conn.close()
