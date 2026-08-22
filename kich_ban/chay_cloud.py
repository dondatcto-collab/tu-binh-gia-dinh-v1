"""Khởi động bản PWA/Cloud.

Dùng cho Render/Railway/Docker. Tự dựng DB lần đầu, sau đó bind 0.0.0.0:$PORT.
"""
from __future__ import annotations

import os

from loi.kho_du_lieu.ket_noi import chay_migration, mo_ket_noi
from loi.nen.phien_ban import DB_MAC_DINH


def chuan_bi_du_lieu() -> None:
    moi = not DB_MAC_DINH.exists()
    conn = mo_ket_noi()
    chay_migration(conn)
    if moi:
        from loi.kho_du_lieu.nap_mam import nap_mam
        nap_mam(conn)
    conn.close()


def main() -> None:
    chuan_bi_du_lieu()
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("cong.api:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
