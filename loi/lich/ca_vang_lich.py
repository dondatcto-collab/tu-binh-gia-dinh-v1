"""Bộ tính cho ca vàng nhóm lịch pháp.

Nhận đầu vào của một ca, trả về bảng khoá–giá trị để khung ca vàng đối chiếu.
Bộ tính KHÔNG biết đáp án mong đợi là gì. Nó chỉ chạy Engine và nộp kết quả.

Quy ước đặt tên khoá:
    tiet_khi:<MA_TIET>:<NAM>   thời điểm tiết khí, dạng ISO, giờ UTC
    utc_offset:<NHAN>          độ lệch múi giờ tính bằng phút
    <MA_BO_LICH>:<NHAN>        bốn trụ tại một thời điểm
    canh_bao:<MA_BO_LICH>:<NHAN>  danh sách mã cảnh báo, đã sắp xếp
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loi.kho_du_lieu import ca_vang
from loi.lich.bo_quy_uoc import tai_tat_ca
from loi.lich.engine import CalendarEngine


def _doc_thoi_diem(chuoi: str) -> tuple[int, int, int, int, int, int]:
    dt = datetime.fromisoformat(chuoi)
    return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second


def tinh_ca_lich(dau_vao: dict[str, Any]) -> dict[str, Any]:
    bo_lich_tat_ca = tai_tat_ca()

    ma_bo = dau_vao.get("so_sanh_bo_lich")
    if not ma_bo:
        mot = dau_vao.get("calendar_ruleset_id")
        ma_bo = [mot] if mot else ["CAL-V1"]

    engines = {m: CalendarEngine(bo_lich_tat_ca[m]) for m in ma_bo}
    tz = dau_vao.get("timezone_name")
    gioi_tinh = dau_vao.get("gioi_tinh", "NAM")

    ket: dict[str, Any] = {}

    # Thời điểm tiết khí, nếu ca có yêu cầu.
    bat_ky = next(iter(engines.values()))
    for yc in dau_vao.get("tiet_khi_can_tinh", []) or []:
        moc = bat_ky.bo_tiet.thoi_diem(int(yc["nam"]), yc["code"])
        ket[f"tiet_khi:{yc['code']}:{yc['nam']}"] = moc.isoformat().replace("+00:00", "Z")

    for td in dau_vao.get("cac_thoi_diem", []) or []:
        nhan = td["nhan"]
        y, mo, d, h, mi, s = _doc_thoi_diem(td["dia_phuong"])
        for ma, e in engines.items():
            r = e.tinh(y, mo, d, h, mi, s, timezone_name=tz, gioi_tinh=gioi_tinh)
            tt = r.tom_tat()
            ket[f"{ma}:{nhan}"] = {
                "year_pillar": tt["year_pillar"],
                "month_pillar": tt["month_pillar"],
                "day_pillar": tt["day_pillar"],
                "hour_pillar": tt["hour_pillar"],
            }
            ket[f"tru_ngay:{ma}:{nhan}"] = tt["day_pillar"]
            ket[f"chi_gio:{ma}:{nhan}"] = r.tru_gio.chi
            ket[f"canh_bao:{ma}:{nhan}"] = sorted(c.ma for c in r.canh_bao)
            ket[f"utc_offset:{nhan}"] = r.thoi_diem.utc_offset_phut

    return ket


def dang_ky() -> None:
    ca_vang.dang_ky_bo_tinh("GOLD-CAL", tinh_ca_lich)
