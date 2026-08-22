-- 0002_rule_registry.sql
-- Kho quy tắc, phiên bản quy tắc, liên kết nguồn, ca kiểm cho từng quy tắc,
-- bộ quy tắc sự kiện, và nhật ký kiểm toán.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------
-- 1. RULE REGISTRY (danh tính quy tắc — không chứa nội dung)
-- ---------------------------------------------------------------
-- Nội dung quy tắc nằm hết ở rule_versions.
-- Sửa quy tắc = tạo version mới, không sửa version cũ.

CREATE TABLE rule_registry (
    rule_id             TEXT PRIMARY KEY,      -- vd: HK-EVENT-0001
    rule_group          TEXT NOT NULL,
    namespace           TEXT NOT NULL REFERENCES rule_namespaces(namespace),
    name_vi             TEXT NOT NULL,
    name_original       TEXT,
    active_version      INTEGER,               -- trỏ tới rule_versions.version
    is_active           INTEGER NOT NULL DEFAULT 0 CHECK (is_active IN (0,1)),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_rule_registry_ns ON rule_registry(namespace);
CREATE INDEX idx_rule_registry_active ON rule_registry(is_active);

-- ---------------------------------------------------------------
-- 2. RULE VERSIONS (nội dung quy tắc — bất biến sau khi bị khoá)
-- ---------------------------------------------------------------

CREATE TABLE rule_versions (
    rule_version_id     TEXT PRIMARY KEY,      -- vd: HK-EVENT-0001@3
    rule_id             TEXT NOT NULL REFERENCES rule_registry(rule_id) ON DELETE RESTRICT,
    version             INTEGER NOT NULL CHECK (version >= 1),

    status              TEXT NOT NULL
                        CHECK (status IN ('VERIFIED','PROVISIONAL','CONFLICTED','REJECTED')),
    confidence          TEXT NOT NULL DEFAULT 'LOW'
                        CHECK (confidence IN ('HIGH','MEDIUM','LOW')),

    -- Đầu vào / điều kiện / logic / đầu ra: hình dạng thay đổi theo loại quy tắc
    -- nên dùng JSON có kiểm tra hợp lệ ở tầng Python.
    inputs              TEXT NOT NULL DEFAULT '[]',
    preconditions       TEXT NOT NULL DEFAULT '[]',
    logic               TEXT,
    outputs             TEXT NOT NULL DEFAULT '[]',

    effect_class        TEXT NOT NULL
                        CHECK (effect_class IN ('SCORING','HARD_BLOCK','MITIGATION',
                                                'EXPLANATORY','EXPERIMENTAL','DISABLED')),
    priority            INTEGER NOT NULL DEFAULT 100,

    block_type          TEXT NOT NULL DEFAULT 'NONE'
                        CHECK (block_type IN ('ABSOLUTE','EVENT_SPECIFIC','CONDITIONAL','NONE')),
    severity            TEXT NOT NULL DEFAULT 'MINOR'
                        CHECK (severity IN ('MAJOR','MEDIUM','MINOR')),
    mitigatable         INTEGER NOT NULL DEFAULT 0 CHECK (mitigatable IN (0,1)),
    max_effect          REAL,

    conflict_group      TEXT,
    duplication_group   TEXT,
    causal_family       TEXT,
    effect_domain       TEXT,

    notes               TEXT,
    locked              INTEGER NOT NULL DEFAULT 0 CHECK (locked IN (0,1)),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE (rule_id, version)
);

CREATE INDEX idx_rule_versions_rule ON rule_versions(rule_id);
CREATE INDEX idx_rule_versions_status ON rule_versions(status);
CREATE INDEX idx_rule_versions_effect ON rule_versions(effect_class);

-- Liên kết quy tắc với nguồn. Đây là mắt xích truy ngược bắt buộc.
CREATE TABLE rule_version_sources (
    rule_version_id     TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE CASCADE,
    source_id           TEXT NOT NULL REFERENCES sources(source_id) ON DELETE RESTRICT,
    source_location     TEXT,                  -- quyển / chương / trang
    source_level        TEXT NOT NULL
                        CHECK (source_level IN ('PRIMARY','SUPPORTING','CROSS_REFERENCE')),
    original_text       TEXT,                  -- nguyên văn hoặc trích yếu
    translation_vi      TEXT,                  -- bản dịch nghĩa
    logic_note          TEXT,                  -- cách chuyển thành logic máy
    PRIMARY KEY (rule_version_id, source_id, source_level)
);

CREATE INDEX idx_rvs_source ON rule_version_sources(source_id);

-- Ca kiểm gắn với một phiên bản quy tắc cụ thể.
CREATE TABLE rule_test_cases (
    rule_test_case_id   TEXT PRIMARY KEY,
    rule_version_id     TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE CASCADE,
    description         TEXT NOT NULL,
    input_payload       TEXT NOT NULL,
    expected_payload    TEXT,
    review_status       TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (review_status IN ('PENDING','APPROVED','REJECTED')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Danh sách quy tắc chờ anh duyệt vì nghĩa chưa rõ hoặc có nhiều cách hiểu.
CREATE TABLE rule_review_queue (
    review_id           TEXT PRIMARY KEY,
    rule_version_id     TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE CASCADE,
    reason              TEXT NOT NULL
                        CHECK (reason IN ('AMBIGUOUS_MEANING','MULTIPLE_READINGS',
                                          'SOURCE_CONFLICT','MISSING_SOURCE','OTHER')),
    question_vi         TEXT NOT NULL,
    options_payload     TEXT,
    resolution          TEXT,
    resolved_at         TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------
-- 3. BỘ QUY TẮC SỰ KIỆN (HIỆP KỶ)
-- ---------------------------------------------------------------

CREATE TABLE event_rule_packs (
    event_rule_pack_id  TEXT PRIMARY KEY,
    code                TEXT NOT NULL UNIQUE,
    name_vi             TEXT NOT NULL,
    name_original       TEXT,
    version             INTEGER NOT NULL DEFAULT 1,
    status              TEXT NOT NULL DEFAULT 'PLACEHOLDER'
                        CHECK (status IN ('ACTIVE','PLACEHOLDER','DEPRECATED')),
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE event_rule_pack_rules (
    event_rule_pack_id  TEXT NOT NULL REFERENCES event_rule_packs(event_rule_pack_id) ON DELETE CASCADE,
    rule_version_id     TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE RESTRICT,
    role                TEXT NOT NULL CHECK (role IN ('REQUIRED','OPTIONAL','EXCLUSION')),
    PRIMARY KEY (event_rule_pack_id, rule_version_id)
);

-- Ánh xạ: việc đời nay -> việc trong sách cổ -> bộ quy tắc.
CREATE TABLE event_mappings (
    event_mapping_id    TEXT PRIMARY KEY,
    event_type_id       TEXT NOT NULL REFERENCES event_types(event_type_id) ON DELETE RESTRICT,
    classical_event     TEXT NOT NULL,
    event_rule_pack_id  TEXT REFERENCES event_rule_packs(event_rule_pack_id) ON DELETE RESTRICT,
    source_id           TEXT REFERENCES sources(source_id),
    source_location     TEXT,
    status              TEXT NOT NULL DEFAULT 'PROVISIONAL'
                        CHECK (status IN ('VERIFIED','PROVISIONAL','CONFLICTED','REJECTED')),
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (event_type_id, classical_event)
);

-- ---------------------------------------------------------------
-- 4. NHẬT KÝ KIỂM TOÁN
-- ---------------------------------------------------------------

CREATE TABLE audit_logs (
    audit_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,             -- rule_registry, rule_versions, sources...
    entity_id       TEXT NOT NULL,
    action          TEXT NOT NULL
                    CHECK (action IN ('CREATE','UPDATE','DELETE','STATUS_CHANGE',
                                      'VERSION_CHANGE','SOURCE_CHANGE','LOCK')),
    actor           TEXT NOT NULL DEFAULT 'system',
    before_payload  TEXT,
    after_payload   TEXT,
    reason          TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at);

-- ---------------------------------------------------------------
-- 5. HÀNG RÀO Ở TẦNG CƠ SỞ DỮ LIỆU
-- ---------------------------------------------------------------

-- Phiên bản đã khoá thì không sửa được nội dung, kể cả sửa nhầm.
CREATE TRIGGER trg_rule_version_locked
BEFORE UPDATE ON rule_versions
FOR EACH ROW
WHEN OLD.locked = 1 AND (
       NEW.logic IS NOT OLD.logic
    OR NEW.inputs IS NOT OLD.inputs
    OR NEW.preconditions IS NOT OLD.preconditions
    OR NEW.outputs IS NOT OLD.outputs
    OR NEW.status IS NOT OLD.status
    OR NEW.effect_class IS NOT OLD.effect_class
    OR NEW.block_type IS NOT OLD.block_type
    OR NEW.severity IS NOT OLD.severity
    OR NEW.mitigatable IS NOT OLD.mitigatable
    OR NEW.max_effect IS NOT OLD.max_effect
)
BEGIN
    SELECT RAISE(ABORT, 'RULE_VERSION_LOCKED: phien ban da khoa, phai tao version moi');
END;

-- Không cho xoá phiên bản quy tắc đã khoá.
CREATE TRIGGER trg_rule_version_no_delete
BEFORE DELETE ON rule_versions
FOR EACH ROW
WHEN OLD.locked = 1
BEGIN
    SELECT RAISE(ABORT, 'RULE_VERSION_LOCKED: khong duoc xoa phien ban da dung');
END;

-- Ghi nhật ký mỗi khi thêm phiên bản quy tắc.
CREATE TRIGGER trg_audit_rule_version_insert
AFTER INSERT ON rule_versions
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (entity_type, entity_id, action, after_payload, reason)
    VALUES ('rule_versions', NEW.rule_version_id, 'CREATE',
            json_object('status', NEW.status, 'effect_class', NEW.effect_class,
                        'version', NEW.version),
            'tao phien ban quy tac');
END;

-- Ghi nhật ký mỗi khi đổi trạng thái phiên bản quy tắc.
CREATE TRIGGER trg_audit_rule_version_status
AFTER UPDATE OF status ON rule_versions
FOR EACH ROW
WHEN NEW.status IS NOT OLD.status
BEGIN
    INSERT INTO audit_logs (entity_type, entity_id, action, before_payload, after_payload, reason)
    VALUES ('rule_versions', NEW.rule_version_id, 'STATUS_CHANGE',
            json_object('status', OLD.status), json_object('status', NEW.status),
            'doi trang thai');
END;

-- Ghi nhật ký khi đổi nguồn.
CREATE TRIGGER trg_audit_rule_source_insert
AFTER INSERT ON rule_version_sources
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (entity_type, entity_id, action, after_payload, reason)
    VALUES ('rule_version_sources', NEW.rule_version_id, 'SOURCE_CHANGE',
            json_object('source_id', NEW.source_id, 'level', NEW.source_level),
            'gan nguon cho quy tac');
END;

-- ---------------------------------------------------------------
-- 6. KHUNG NHÌN TƯƠNG THÍCH TÊN BẢNG THEO ĐẶC TẢ
-- ---------------------------------------------------------------
-- Đặc tả gọi là `rule_sources`. Thiết kế thực tế tách làm hai:
--   sources              = Source Registry, mô tả sách.
--   rule_version_sources = quy tắc nào lấy từ sách nào, chỗ nào.
-- Khung nhìn dưới đây giữ đúng tên trong đặc tả để truy vấn cho tiện.
CREATE VIEW rule_sources AS
SELECT rvs.rule_version_id,
       rv.rule_id,
       rv.version,
       s.source_id,
       s.title,
       s.author,
       s.edition,
       s.language,
       s.primary_or_secondary,
       rvs.source_level,
       rvs.source_location,
       rvs.original_text,
       rvs.translation_vi,
       rvs.logic_note
  FROM rule_version_sources rvs
  JOIN rule_versions rv ON rv.rule_version_id = rvs.rule_version_id
  JOIN sources s        ON s.source_id = rvs.source_id;
