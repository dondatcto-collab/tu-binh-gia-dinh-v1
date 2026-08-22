-- 0009_tach_duong_nhan.sql
-- Dương Nhận KHÔNG phải tên khác của Tỷ Kiên.
-- Bổ sung cột để nói rõ điều đó, thay vì để người sau đoán.

PRAGMA foreign_keys = ON;

ALTER TABLE ten_god_naming_variants ADD COLUMN alias_relation TEXT
    NOT NULL DEFAULT 'NOT_A_DIRECT_ALIAS'
    CHECK (alias_relation IN ('DIRECT_ALIAS','NOT_A_DIRECT_ALIAS'));
ALTER TABLE ten_god_naming_variants ADD COLUMN concept_group TEXT;
ALTER TABLE ten_god_naming_variants ADD COLUMN concept_kind TEXT;
ALTER TABLE ten_god_naming_variants ADD COLUMN determined_by TEXT;

-- LƯU Ý VỀ TÊN NHÓM:
-- Đặc tả yêu cầu đặt Dương Nhận vào nhóm "BT-YR". Nhưng "BT-YR" ĐÃ ĐƯỢC DÙNG
-- từ mục 6 của đặc tả gốc với nghĩa "Lưu niên" (luận năm).
-- Nếu chèn đè, tên nhóm sẽ mang hai nghĩa mà không ai biết.
-- Vì vậy dùng "BT-DN" cho Dương Nhận, và ghi lại va chạm này.
INSERT INTO rule_namespaces (namespace, name_vi, description) VALUES
 ('BT-DN', 'Dương Nhận',
  'Khái niệm cổ riêng, xét theo vị trí Địa Chi so với Lộc của Nhật chủ (祿前一位). '
  || 'KHÔNG phải một Thập Thần, KHÔNG phải tên khác của Tỷ Kiên. Chưa làm. '
  || 'Đặt tên BT-DN chứ không phải BT-YR vì BT-YR đã mang nghĩa Lưu niên.')
ON CONFLICT DO NOTHING;
