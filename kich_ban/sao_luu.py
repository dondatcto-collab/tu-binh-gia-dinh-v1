"""Sao lưu và khôi phục dữ liệu gia đình.

    python3 -m kich_ban.sao_luu luu   [thư mục đích]
    python3 -m kich_ban.sao_luu phuc  <tệp sao lưu>
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

from loi.nen.phien_ban import DB_MAC_DINH


def luu(dich: Path) -> Path:
    if not DB_MAC_DINH.exists():
        raise SystemExit("Chưa có dữ liệu để sao lưu.")
    dich.mkdir(parents=True, exist_ok=True)
    ten = f"xemngay-{datetime.now():%Y%m%d-%H%M}.sqlite3"
    tep = dich / ten
    # Dùng backup của sqlite để an toàn kể cả khi app đang chạy.
    import sqlite3
    nguon = sqlite3.connect(str(DB_MAC_DINH))
    dich_db = sqlite3.connect(str(tep))
    with dich_db:
        nguon.backup(dich_db)
    nguon.close()
    dich_db.close()
    return tep


def phuc(tep: Path) -> Path:
    if not tep.exists():
        raise SystemExit(f"Không thấy tệp: {tep}")
    if DB_MAC_DINH.exists():
        cu = DB_MAC_DINH.with_suffix(".truoc-khi-phuc-hoi.sqlite3")
        shutil.copy2(DB_MAC_DINH, cu)
        print(f"Đã giữ bản cũ tại: {cu}")
    DB_MAC_DINH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tep, DB_MAC_DINH)
    return DB_MAC_DINH


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("luu", "phuc"):
        print(__doc__)
        return 1
    if sys.argv[1] == "luu":
        dich = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("sao-luu")
        print(f"Đã sao lưu vào: {luu(dich)}")
    else:
        if len(sys.argv) < 3:
            print(__doc__)
            return 1
        print(f"Đã khôi phục vào: {phuc(Path(sys.argv[2]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
