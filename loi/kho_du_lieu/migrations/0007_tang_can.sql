-- 0007_tang_can.sql
-- Dựng lại bảng Tàng Can theo mô hình dữ liệu của Giai đoạn 3A.
--
-- Tách rõ hai việc:
--   TẬP CAN   — Chi này chứa những Can nào. Mọi nguồn thống nhất.
--   THỨ TỰ    — liệt kê theo trình tự nào. Các nguồn KHÁC NHAU.
-- Cột semantic_role để trống, vì chưa chứng minh được thứ tự mang nghĩa gì.

PRAGMA foreign_keys = OFF;

DROP TABLE branch_hidden_stems;

CREATE TABLE branch_hidden_stems (
    branch_index          INTEGER NOT NULL REFERENCES branches(branch_index),
    stem_index            INTEGER NOT NULL REFERENCES stems(stem_index),
    source_order          INTEGER NOT NULL CHECK (source_order BETWEEN 1 AND 3),
    -- Vai trò ngữ nghĩa: bản khí, trung khí, dư khí. CHƯA GÁN ở giai đoạn này.
    semantic_role         TEXT CHECK (semantic_role IN ('MAIN_QI','MIDDLE_QI','RESIDUAL_QI')),
    semantic_role_status  TEXT NOT NULL DEFAULT 'NOT_ASSIGNED'
                          CHECK (semantic_role_status IN ('NOT_ASSIGNED','PROVISIONAL',
                                                          'VERIFIED','CONFLICTED')),
    source_rule_id        TEXT NOT NULL REFERENCES rule_registry(rule_id),
    PRIMARY KEY (branch_index, stem_index),
    UNIQUE (branch_index, source_order)
);

-- Chưa gán vai trò thì không được điền vai trò. Và ngược lại.
CREATE TRIGGER trg_semantic_role_nhat_quan
BEFORE INSERT ON branch_hidden_stems
FOR EACH ROW
WHEN (NEW.semantic_role_status = 'NOT_ASSIGNED' AND NEW.semantic_role IS NOT NULL)
  OR (NEW.semantic_role_status <> 'NOT_ASSIGNED' AND NEW.semantic_role IS NULL)
BEGIN
    SELECT RAISE(ABORT, 'SEMANTIC_ROLE_KHONG_NHAT_QUAN: trang thai va gia tri phai di doi');
END;

-- Ghi lại thứ tự của các truyền thống khác, để không hợp nhất âm thầm.
CREATE TABLE hidden_stem_order_variants (
    variant_id      TEXT PRIMARY KEY,
    branch_index    INTEGER NOT NULL REFERENCES branches(branch_index),
    tradition       TEXT NOT NULL,
    stem_order      TEXT NOT NULL,        -- danh sách mã Can, đúng thứ tự nguồn đó
    source_id       TEXT REFERENCES sources(source_id),
    notes           TEXT
);

PRAGMA foreign_keys = ON;

-- Bổ sung nhóm độc lập cho sách vở đời sau.
INSERT INTO independence_groups (independence_group, name_vi, mo_ta) VALUES
 ('MODERN_PRACTITIONER_LITERATURE', 'Sách vở giới hành nghề đời sau',
  'Bảng và khẩu quyết lưu hành trong giới hành nghề. Nhiều bản cùng một dòng truyền, không tính là nhiều bằng chứng.');

-- Bổ sung không gian tên cho Tàng Can và cho quyền khí theo mùa.
INSERT INTO rule_namespaces (namespace, name_vi, description) VALUES
 ('BT-HIDDEN', 'Tàng Can cấu trúc',
  'Chi chứa những Can nào. Chỉ là dữ liệu cấu trúc, không chấm điểm.'),
 ('BT-SEASON-POWER', 'Quyền khí theo tiết',
  'Can nào đương quyền trong từng đoạn tiết khí. CHƯA làm ở Giai đoạn 3A.');
