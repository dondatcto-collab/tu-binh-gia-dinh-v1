-- 0006_nhom_doc_lap.sql
-- Thêm nhóm độc lập cho nguồn.
--
-- Lý do phải có: đếm SỐ TÊN NGUỒN không phải đếm SỐ BẰNG CHỨNG ĐỘC LẬP.
-- Hai thư viện cùng truyền thống là một bằng chứng, không phải hai.
-- Hai phép tính cùng dùng một bộ tinh lịch cũng là một bằng chứng.

PRAGMA foreign_keys = OFF;

DROP VIEW rule_sources;

ALTER TABLE sources ADD COLUMN independence_group TEXT NOT NULL DEFAULT 'UNASSIGNED';

CREATE VIEW rule_sources AS
SELECT rvs.rule_version_id, rv.rule_id, rv.version,
       s.source_id, s.title, s.author, s.edition, s.language,
       s.primary_or_secondary, s.edition_certainty, s.independence_group,
       rvs.source_level, rvs.source_location,
       rvs.original_text, rvs.translation_vi, rvs.logic_note
  FROM rule_version_sources rvs
  JOIN rule_versions rv ON rv.rule_version_id = rvs.rule_version_id
  JOIN sources s        ON s.source_id = rvs.source_id;

PRAGMA foreign_keys = ON;

-- Nhóm độc lập phải nằm trong tập đã định. Không cho gõ bừa.
CREATE TABLE independence_groups (
    independence_group TEXT PRIMARY KEY,
    name_vi            TEXT NOT NULL,
    mo_ta              TEXT NOT NULL
);

INSERT INTO independence_groups (independence_group, name_vi, mo_ta) VALUES
 ('CLASSICAL_TEXT', 'Cổ thư',
  'Văn bản cổ. Hai bản chép của cùng một sách vẫn chỉ là một bằng chứng.'),
 ('ASTRONOMICAL_EPHEMERIS', 'Tinh lịch thiên văn',
  'Mọi phép tính cùng dựa trên VSOP87 và ELP2000 đều thuộc nhóm này, kể cả NASA.'),
 ('ACADEMIC_CALENDAR_RESEARCH', 'Nghiên cứu lịch pháp học thuật',
  'Công trình có nêu rõ thuật toán và mốc neo, kiểm lại được.'),
 ('MODERN_CALENDAR_IMPLEMENTATION', 'Cài đặt lịch pháp hiện đại',
  'Thư viện phần mềm. sxtwl và lunar-python cùng truyền thống nên cùng nhóm.'),
 ('GOLDEN_CASE', 'Ca vàng đã được người duyệt',
  'Chỉ độc lập ở mức người duyệt đã xem xét, không độc lập về nguồn gốc dữ liệu.'),
 ('NONE', 'Chưa có bằng chứng',
  'Chỗ trống. Không được tính vào số nhóm bằng chứng.');

CREATE TRIGGER trg_nhom_doc_lap_hop_le
BEFORE INSERT ON sources
FOR EACH ROW
WHEN NEW.independence_group NOT IN
     (SELECT independence_group FROM independence_groups)
BEGIN
    SELECT RAISE(ABORT, 'NHOM_DOC_LAP_LA: phai nam trong bang independence_groups');
END;
