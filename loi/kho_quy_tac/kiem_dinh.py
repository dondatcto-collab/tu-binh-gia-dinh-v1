"""Bộ kiểm định Rule Registry.

Đây là hàng rào chính. Không quy tắc nào vào được kho nếu không qua đây.

Sáu điều bắt buộc theo yêu cầu:
  V01 quy tắc VERIFIED phải có nguồn;
  V02 quy tắc dùng để chấm điểm phải có logic;
  V03 quy tắc chặn cứng phải có block_type khác NONE;
  V04 quy tắc không được vừa REJECTED vừa đang hoạt động;
  V05 phiên bản phải được khoá khi đã đưa vào sử dụng;
  V06 quy tắc đã dùng trong kết quả cũ không được sửa âm thầm.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from loi.kho_quy_tac.mo_hinh import RuleVersion
from loi.nen.trang_thai import (
    HANG_TAC_DUNG_CHAM_DIEM,
    BlockType,
    EffectClass,
    RuleStatus,
    SourceLevel,
)


@dataclass(frozen=True)
class LoiKiemDinh:
    ma: str
    muc: str          # LOI = chặn, CANH_BAO = cho qua nhưng ghi lại
    doi_tuong: str
    thong_diep: str

    def __str__(self) -> str:  # pragma: no cover - chỉ để đọc cho dễ
        return f"[{self.muc}] {self.ma} {self.doi_tuong}: {self.thong_diep}"


class RegistryValidationError(Exception):
    def __init__(self, loi: list[LoiKiemDinh]):
        self.loi = loi
        super().__init__("; ".join(str(x) for x in loi))


# ---------------------------------------------------------------
# Kiểm một phiên bản quy tắc trước khi ghi vào kho
# ---------------------------------------------------------------

def kiem_phien_ban(rv: RuleVersion) -> list[LoiKiemDinh]:
    loi: list[LoiKiemDinh] = []
    ten = rv.rule_version_id

    # V01 — VERIFIED phải có ít nhất một nguồn cấp PRIMARY.
    if rv.status is RuleStatus.VERIFIED:
        co_primary = any(s.source_level is SourceLevel.PRIMARY for s in rv.sources)
        if not rv.sources:
            loi.append(LoiKiemDinh("V01", "LOI", ten,
                                   "trạng thái VERIFIED nhưng không gắn nguồn nào"))
        elif not co_primary:
            loi.append(LoiKiemDinh("V01", "LOI", ten,
                                   "trạng thái VERIFIED nhưng chưa có nguồn cấp PRIMARY"))

    # V02 — quy tắc tham gia chấm điểm phải có logic.
    if rv.effect_class in HANG_TAC_DUNG_CHAM_DIEM:
        if not rv.logic:
            loi.append(LoiKiemDinh("V02", "LOI", ten,
                                   f"hạng tác dụng {rv.effect_class.value} nhưng chưa có logic"))
        if not rv.outputs:
            loi.append(LoiKiemDinh("V02", "LOI", ten,
                                   "quy tắc chấm điểm phải khai báo outputs"))

    # V03 — chặn cứng phải nói rõ chặn kiểu gì.
    if rv.effect_class is EffectClass.HARD_BLOCK and rv.block_type is BlockType.NONE:
        loi.append(LoiKiemDinh("V03", "LOI", ten,
                               "HARD_BLOCK nhưng block_type để NONE"))
    if rv.effect_class is not EffectClass.HARD_BLOCK and rv.block_type is BlockType.ABSOLUTE:
        loi.append(LoiKiemDinh("V03", "LOI", ten,
                               "block_type ABSOLUTE chỉ được dùng cho HARD_BLOCK"))

    # Thần Sát không được tự lật kết luận: chỉ giải thích hoặc thử nghiệm.
    if rv.rule_id.startswith("SS-") and rv.effect_class is EffectClass.HARD_BLOCK:
        loi.append(LoiKiemDinh("V03", "LOI", ten,
                               "quy tắc Thần Sát không được đặt là HARD_BLOCK"))

    # Trần tác dụng: quy tắc chấm điểm phải có mức trần để không bị cộng dồn vô hạn.
    if rv.effect_class is EffectClass.SCORING and rv.max_effect is None:
        loi.append(LoiKiemDinh("V07", "CANH_BAO", ten,
                               "quy tắc chấm điểm chưa đặt max_effect"))

    if rv.version < 1:
        loi.append(LoiKiemDinh("V08", "LOI", ten, "số phiên bản phải từ 1 trở lên"))

    if rv.status is RuleStatus.CONFLICTED and not rv.notes:
        loi.append(LoiKiemDinh("V09", "CANH_BAO", ten,
                               "CONFLICTED nhưng chưa ghi rõ khác biệt giữa các nguồn"))

    return loi


def bat_buoc_hop_le(rv: RuleVersion) -> None:
    """Ném lỗi nếu có bất kỳ mục LOI nào."""
    loi = [x for x in kiem_phien_ban(rv) if x.muc == "LOI"]
    if loi:
        raise RegistryValidationError(loi)


# ---------------------------------------------------------------
# Kiểm toàn kho
# ---------------------------------------------------------------

def kiem_toan_kho(conn: sqlite3.Connection) -> list[LoiKiemDinh]:
    loi: list[LoiKiemDinh] = []

    # V01 — mọi phiên bản VERIFIED trong kho phải có nguồn PRIMARY.
    thieu_nguon = conn.execute(
        """
        SELECT rv.rule_version_id
          FROM rule_versions rv
         WHERE rv.status = 'VERIFIED'
           AND NOT EXISTS (
               SELECT 1 FROM rule_version_sources s
                WHERE s.rule_version_id = rv.rule_version_id
                  AND s.source_level = 'PRIMARY')
        """
    ).fetchall()
    for r in thieu_nguon:
        loi.append(LoiKiemDinh("V01", "LOI", r["rule_version_id"],
                               "VERIFIED nhưng thiếu nguồn PRIMARY"))

    # V02 — quy tắc chấm điểm phải có logic.
    thieu_logic = conn.execute(
        """
        SELECT rule_version_id, effect_class FROM rule_versions
         WHERE effect_class IN ('SCORING','HARD_BLOCK','MITIGATION')
           AND (logic IS NULL OR trim(logic) = '')
        """
    ).fetchall()
    for r in thieu_logic:
        loi.append(LoiKiemDinh("V02", "LOI", r["rule_version_id"],
                               f"{r['effect_class']} nhưng chưa có logic"))

    # V03 — chặn cứng phải có block_type.
    thieu_block = conn.execute(
        """
        SELECT rule_version_id FROM rule_versions
         WHERE effect_class = 'HARD_BLOCK' AND block_type = 'NONE'
        """
    ).fetchall()
    for r in thieu_block:
        loi.append(LoiKiemDinh("V03", "LOI", r["rule_version_id"],
                               "HARD_BLOCK nhưng block_type là NONE"))

    # V04 — không được vừa REJECTED vừa đang hoạt động.
    vua_reject_vua_active = conn.execute(
        """
        SELECT r.rule_id, rv.rule_version_id
          FROM rule_registry r
          JOIN rule_versions rv
            ON rv.rule_id = r.rule_id AND rv.version = r.active_version
         WHERE r.is_active = 1 AND rv.status = 'REJECTED'
        """
    ).fetchall()
    for r in vua_reject_vua_active:
        loi.append(LoiKiemDinh("V04", "LOI", r["rule_id"],
                               "đang hoạt động nhưng phiên bản hiện hành là REJECTED"))

    # V04b — đang hoạt động thì phải trỏ tới một phiên bản có thật.
    tro_hong = conn.execute(
        """
        SELECT r.rule_id FROM rule_registry r
         WHERE r.is_active = 1
           AND (r.active_version IS NULL
                OR NOT EXISTS (SELECT 1 FROM rule_versions rv
                                WHERE rv.rule_id = r.rule_id
                                  AND rv.version = r.active_version))
        """
    ).fetchall()
    for r in tro_hong:
        loi.append(LoiKiemDinh("V04", "LOI", r["rule_id"],
                               "đang hoạt động nhưng active_version không tồn tại"))

    # V05 — phiên bản đã dùng trong kết quả phải ở trạng thái khoá.
    chua_khoa = conn.execute(
        """
        SELECT DISTINCT rv.rule_version_id
          FROM rule_versions rv
          JOIN fusion_findings f ON f.rule_version_id = rv.rule_version_id
         WHERE rv.locked = 0
        """
    ).fetchall()
    for r in chua_khoa:
        loi.append(LoiKiemDinh("V05", "LOI", r["rule_version_id"],
                               "đã dùng trong kết quả nhưng chưa bị khoá"))

    # V06 — phiên bản đã khoá phải có dấu vết trong nhật ký kiểm toán.
    thieu_nhat_ky = conn.execute(
        """
        SELECT rv.rule_version_id
          FROM rule_versions rv
         WHERE rv.locked = 1
           AND NOT EXISTS (SELECT 1 FROM audit_logs a
                            WHERE a.entity_type = 'rule_versions'
                              AND a.entity_id = rv.rule_version_id)
        """
    ).fetchall()
    for r in thieu_nhat_ky:
        loi.append(LoiKiemDinh("V06", "LOI", r["rule_version_id"],
                               "đã khoá nhưng không có dấu vết trong nhật ký"))

    # V10 — chỉ VERIFIED mới được dùng để chấm điểm chính thức.
    khong_verified_ma_cham_diem = conn.execute(
        """
        SELECT rv.rule_version_id, rv.status
          FROM rule_registry r
          JOIN rule_versions rv
            ON rv.rule_id = r.rule_id AND rv.version = r.active_version
         WHERE r.is_active = 1
           AND rv.effect_class IN ('SCORING','HARD_BLOCK','MITIGATION')
           AND rv.status <> 'VERIFIED'
        """
    ).fetchall()
    for r in khong_verified_ma_cham_diem:
        loi.append(LoiKiemDinh("V10", "LOI", r["rule_version_id"],
                               f"trạng thái {r['status']} nhưng đang được bật để chấm điểm"))

    # V11 — không được lấy chỗ trống làm nguồn rồi tuyên bố đã xác minh.
    gia_verified = conn.execute(
        """
        SELECT rv.rule_version_id, s.source_id
          FROM rule_versions rv
          JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
          JOIN sources s ON s.source_id = rvs.source_id
         WHERE rv.status = 'VERIFIED'
           AND rvs.source_level = 'PRIMARY'
           AND s.status = 'PENDING'
        """
    ).fetchall()
    for r in gia_verified:
        loi.append(LoiKiemDinh("V11", "LOI", r["rule_version_id"],
                               f"đánh dấu VERIFIED nhưng nguồn chính {r['source_id']} "
                               "vẫn là chỗ trống chờ nguồn"))

    # V12 — cổ thư phải nói rõ mức chắc chắn về bản in.
    mo_ho = conn.execute(
        """
        SELECT source_id FROM sources
         WHERE source_type IN ('CLASSIC','CLASSICAL_TEXT_TRANSCRIPTION')
           AND edition_certainty = 'UNKNOWN'
        """
    ).fetchall()
    for r in mo_ho:
        loi.append(LoiKiemDinh("V12", "CANH_BAO", r["source_id"],
                               "cổ thư chưa ghi mức chắc chắn về bản in"))

    return loi


def truy_nguoc_quy_tac(conn: sqlite3.Connection, fusion_result_id: str) -> list[dict]:
    """Đi ngược từ một kết quả về tới nguồn sách.

    kết quả -> phát hiện -> phiên bản quy tắc -> quy tắc -> nguồn
    """
    rows = conn.execute(
        """
        SELECT f.finding_kind,
               rv.rule_version_id,
               rv.version,
               rv.status,
               r.rule_id,
               r.name_vi         AS ten_quy_tac,
               s.source_id,
               s.title           AS ten_nguon,
               s.edition,
               rvs.source_level,
               rvs.source_location
          FROM fusion_findings f
          JOIN rule_versions rv ON rv.rule_version_id = f.rule_version_id
          JOIN rule_registry r  ON r.rule_id = rv.rule_id
     LEFT JOIN rule_version_sources rvs ON rvs.rule_version_id = rv.rule_version_id
     LEFT JOIN sources s ON s.source_id = rvs.source_id
         WHERE f.fusion_result_id = ?
      ORDER BY f.ordering, rvs.source_level
        """,
        (fusion_result_id,),
    ).fetchall()
    return [dict(r) for r in rows]
