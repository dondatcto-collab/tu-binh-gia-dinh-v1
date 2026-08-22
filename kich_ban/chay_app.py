"""Chạy ứng dụng cho gia đình dùng.

    python3 -m kich_ban.chay_app

Rồi mở trình duyệt vào http://127.0.0.1:8000
"""

from __future__ import annotations

import sys

from loi.kho_du_lieu.ket_noi import chay_migration, danh_sach_bang, mo_ket_noi
from loi.nen.phien_ban import DB_MAC_DINH


def main() -> int:
    if not DB_MAC_DINH.exists():
        print("Chưa có kho dữ liệu. Đang dựng lần đầu…")
        conn = mo_ket_noi()
        chay_migration(conn)
        from loi.kho_du_lieu.nap_mam import nap_mam
        nap_mam(conn)
        conn.close()
        print("Xong.")
    else:
        conn = mo_ket_noi()
        chay_migration(conn)
        print(f"Kho dữ liệu sẵn sàng, {len(danh_sach_bang(conn))} bảng.")
        conn.close()

    import uvicorn
    print("\n" + "=" * 58)
    print("  Mở trình duyệt vào:  http://127.0.0.1:8000")
    print("  Hướng dẫn:           http://127.0.0.1:8000/huong-dan")
    print("  Dừng: bấm Ctrl và C")
    print("=" * 58 + "\n")
    uvicorn.run("cong.api:app", host="127.0.0.1", port=8000, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
