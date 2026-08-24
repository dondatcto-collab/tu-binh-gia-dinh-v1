"""Public seed-loader facade for release 0.5.0.

Implementation remains in _nap_mam_impl; only locked row-count expectations changed
when THI_CU moved out of active V1 event rules.
"""
from __future__ import annotations
from . import _nap_mam_impl as _impl

_impl.SO_LUONG_MONG_DOI.update({
    "rule_registry":70,
    "rule_versions":70,
    "rule_version_sources":95,
    "source_passages":29,
    "rule_version_passages":49,
})

BANG_NEN=_impl.BANG_NEN
SO_LUONG_MONG_DOI=_impl.SO_LUONG_MONG_DOI
dem_ban_ghi_nen=_impl.dem_ban_ghi_nen
kiem_so_luong=_impl.kiem_so_luong
nap_mam=_impl.nap_mam
