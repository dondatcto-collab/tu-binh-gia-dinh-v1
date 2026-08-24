"""Vercel entrypoint.

Release 0.5.0 deliberately rebuilds the small public rule database in /tmp on
cold start instead of trusting the packaged binary seed. This prevents an old
seed (for example the former 13-event V1 scope) from blocking a newer release.
User profiles are still device-only and are never written to this database.
"""
from __future__ import annotations

import os

if os.environ.get("VERCEL"):
    os.environ.setdefault("XEMNGAY_DB_PATH", "/tmp/xemngay-rules-050.sqlite3")
    # cong.api interprets a truthy VERCEL flag as "copy packaged seed".
    # For 0.5.0 the committed binary seed can lag text migrations/rules, so the
    # serverless entrypoint forces the safe rebuild path on ephemeral /tmp.
    os.environ["VERCEL"] = ""

from cong.api import app
