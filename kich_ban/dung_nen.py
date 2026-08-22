"""Dựng nền từ đầu: chuyển đổi lược đồ, nạp mầm, đồng bộ ca vàng, kiểm định.

Chạy:  python3 -m kich_ban.dung_nen [--sach]
"""

from __future__ import annotations

import argparse
import sys

from loi.kho_du_lieu import ca_vang
from loi.bat_tu.ca_vang_bat_tu import dang_ky as dang_ky_bo_tinh_bat_tu
from loi.lich.ca_vang_lich import dang_ky as dang_ky_bo_tinh_lich
from loi.kho_du_lieu.ket_noi import chay_migration, danh_sach_bang, mo_ket_noi
from loi.kho_du_lieu.nap_mam import kiem_so_luong, nap_mam
from loi.kho_quy_tac.kiem_dinh import kiem_toan_kho
from loi.lich.bo_quy_uoc import bo_mac_dinh, kiem_khong_hard_code, tai_tu_db
from loi.lich.do_phu import bao_cao as bao_cao_do_phu
from loi.nen.phien_ban import DB_MAC_DINH, ENGINE_VERSION, RULESET_VERSION


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sach", action="store_true", help="xoá cơ sở dữ liệu cũ trước khi dựng")
    args = parser.parse_args()

    if args.sach and DB_MAC_DINH.exists():
        for hau_to in ("", "-wal", "-shm"):
            p = DB_MAC_DINH.with_name(DB_MAC_DINH.name + hau_to)
            if p.exists():
                p.unlink()
        print("[1] Đã xoá cơ sở dữ liệu cũ")

    conn = mo_ket_noi()

    vua_chay = chay_migration(conn)
    bang = danh_sach_bang(conn)
    print(f"[2] Chuyển đổi: chạy {len(vua_chay)} tệp, tổng {len(bang)} bảng")

    dem = nap_mam(conn)
    lech = kiem_so_luong(conn)
    print("[3] Nạp mầm:")
    for k, v in dem.items():
        print(f"      {k:<28} {v}")
    if lech:
        print("    LỆCH SỐ LƯỢNG:")
        for l in lech:
            print(f"      {l}")
        return 1

    dang_ky_bo_tinh_lich()
    dang_ky_bo_tinh_bat_tu()
    cac_ca = ca_vang.tai_tat_ca()
    for ca in cac_ca:
        ca_vang.dong_bo_vao_db(conn, ca)
    conn.commit()
    print(f"[4] Ca vàng: nạp {len(cac_ca)} ca")
    for nhom, so in ca_vang.thong_ke_theo_nhom(cac_ca).items():
        print(f"      {nhom:<10} tổng {so['tong']}, đã duyệt {so['da_duyet']}, chờ duyệt {so['cho_duyet']}")

    van_de = kiem_toan_kho(conn)
    loi_kho = [x for x in van_de if x.muc == "LOI"]
    canh_bao = [x for x in van_de if x.muc != "LOI"]
    print(f"[5] Kiểm định kho quy tắc: {len(loi_kho)} lỗi, {len(canh_bao)} cảnh báo")
    for l in van_de:
        print(f"      {l}")

    mac_dinh = bo_mac_dinh(conn)
    h23 = tai_tu_db(conn, "CAL-V1-23H")
    print(f"[6] Bộ lịch mặc định: {mac_dinh.calendar_ruleset_id}, "
          f"mốc đổi ngày {mac_dinh.moc_doi_ngay} ({mac_dinh.moc_doi_ngay_phut} phút)")
    print(f"    Bộ lịch thử nghiệm: {h23.calendar_ruleset_id}, "
          f"mốc đổi ngày {h23.moc_doi_ngay} ({h23.moc_doi_ngay_phut} phút)")

    vi_pham = kiem_khong_hard_code()
    print(f"[7] Quét mốc lịch nhét cứng trong mã: {len(vi_pham)} vi phạm")
    for v in vi_pham:
        print(f"      {v}")

    kq = ca_vang.chay(conn, cac_ca, test_run_id="RUN-DUNG-NEN")
    print(f"[8] Chạy ca vàng: tổng {kq.tong_so}, đạt {kq.dat}, trượt {kq.truot}, "
          f"bị chặn {kq.bi_chan}, chờ duyệt {kq.cho_duyet}, "
          f"tỷ lệ đạt {kq.ty_le_dat if kq.ty_le_dat is not None else 'chưa tính được'}")
    print(f"    Lớp đáp án: đã chấm {kq.lop_da_cham}, chưa duyệt nên bỏ qua {kq.lop_chua_duyet}")
    for cid, tt, ct in kq.chi_tiet:
        print(f"      {cid:<10} {tt:<18} {ct[:64]}")

    from loi.bat_tu.tang_can import do_phu_chi
    print(f"\n[9] BRANCH_COVERAGE (Tàng Can): {do_phu_chi(conn)}")
    print("\n[10] Độ phủ hai bảng độn:")
    for d in bao_cao_do_phu().splitlines():
        print(f"      {d}")

    print(f"\nENGINE_VERSION={ENGINE_VERSION}  RULESET_VERSION={RULESET_VERSION}")
    conn.close()
    return 0 if not loi_kho and not vi_pham else 1


if __name__ == "__main__":
    sys.exit(main())
