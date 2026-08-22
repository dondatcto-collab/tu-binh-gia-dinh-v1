-- 0008_thap_than.sql
-- Mười Thập Thần: bảng tham chiếu và bảng dị biệt tên gọi.
-- Chỉ là dữ liệu quan hệ. Không điểm số, không tốt xấu.

PRAGMA foreign_keys = ON;

CREATE TABLE ten_gods (
    ten_god_code    TEXT PRIMARY KEY,
    rule_id         TEXT NOT NULL UNIQUE,
    name_vi         TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    -- Hai chiều tạo nên mười ô.
    relation_direction TEXT NOT NULL
        CHECK (relation_direction IN ('DONG_HANH','TA_SINH','SINH_TA','TA_KHAC','KHAC_TA')),
    polarity_relation  TEXT NOT NULL
        CHECK (polarity_relation IN ('DONG_TINH','KHAC_TINH')),
    source_id       TEXT REFERENCES sources(source_id),
    status          TEXT NOT NULL DEFAULT 'VERIFIED'
                    CHECK (status IN ('VERIFIED','PROVISIONAL','CONFLICTED')),
    UNIQUE (relation_direction, polarity_relation)
);

-- Tên gọi khác cho cùng một ô, theo từng nguồn. Không hợp nhất.
CREATE TABLE ten_god_naming_variants (
    variant_id          TEXT PRIMARY KEY,
    relation_direction  TEXT NOT NULL,
    polarity_relation   TEXT NOT NULL,
    variant_name        TEXT NOT NULL,
    name_original       TEXT,
    source_id           TEXT REFERENCES sources(source_id),
    source_quote        TEXT,
    is_active_convention INTEGER NOT NULL DEFAULT 0 CHECK (is_active_convention IN (0,1)),
    notes               TEXT
);

-- Ví dụ trích thẳng từ nguyên văn, dùng để kiểm lại quy tắc.
CREATE TABLE ten_god_source_examples (
    example_id      TEXT PRIMARY KEY,
    day_master      TEXT NOT NULL REFERENCES stems(code),
    target_stem     TEXT NOT NULL REFERENCES stems(code),
    ten_god_code    TEXT NOT NULL REFERENCES ten_gods(ten_god_code),
    source_id       TEXT NOT NULL REFERENCES sources(source_id),
    original_text   TEXT NOT NULL,
    translation_vi  TEXT NOT NULL
);

INSERT INTO rule_namespaces (namespace, name_vi, description) VALUES
 ('BT-TG-CONFLICT', 'Dị biệt tên gọi Thập Thần',
  'Chỗ các nguồn gọi tên khác nhau cho cùng một quan hệ.')
ON CONFLICT DO NOTHING;

-- Mười ô phải đủ mười, không thừa không thiếu.
CREATE TRIGGER trg_thap_than_khong_cham_diem
BEFORE INSERT ON ten_gods
FOR EACH ROW
WHEN NEW.ten_god_code IN ('SCORE','STRENGTH','FAVORABLE')
BEGIN
    SELECT RAISE(ABORT, 'THAP_THAN_KHONG_CHAM_DIEM');
END;
