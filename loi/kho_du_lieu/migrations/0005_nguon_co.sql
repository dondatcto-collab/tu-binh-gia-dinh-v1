-- 0005_nguon_co.sql
-- Bổ sung kiểu nguồn cho bản chép số hóa cổ thư, và hai cột nói rõ
-- mức chắc chắn về bản in cùng đường đi của văn bản tới tay mình.

PRAGMA foreign_keys = OFF;

-- Khung nhìn phụ thuộc bảng sources, phải bỏ trước rồi dựng lại sau.
DROP VIEW rule_sources;

CREATE TABLE sources_moi (
    source_id               TEXT PRIMARY KEY,
    title                   TEXT NOT NULL,
    author                  TEXT,
    dynasty_or_year         TEXT,
    edition                 TEXT,
    language                TEXT NOT NULL,
    source_type             TEXT NOT NULL
                            CHECK (source_type IN ('CLASSIC','CLASSICAL_TEXT_TRANSCRIPTION',
                                                   'COMMENTARY','TRANSLATION',
                                                   'MODERN_BOOK','ARTICLE','DATASET','OTHER')),
    url_or_file_reference   TEXT,
    primary_or_secondary    TEXT NOT NULL
                            CHECK (primary_or_secondary IN ('PRIMARY','SECONDARY')),
    -- Chắc chắn tới đâu về BẢN IN cụ thể. Không được để trống khi là cổ thư.
    edition_certainty       TEXT NOT NULL DEFAULT 'UNKNOWN'
                            CHECK (edition_certainty IN ('PINNED_PRINT','PINNED_SCAN',
                                                         'TRANSCRIPTION_ONLY','UNKNOWN',
                                                         'NOT_APPLICABLE')),
    -- Văn bản này tới tay mình bằng đường nào.
    provenance_note         TEXT,
    status                  TEXT NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('ACTIVE','PENDING','DEPRECATED','REJECTED')),
    notes                   TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO sources_moi
    (source_id, title, author, dynasty_or_year, edition, language, source_type,
     url_or_file_reference, primary_or_secondary, edition_certainty, status, notes,
     created_at, updated_at)
SELECT source_id, title, author, dynasty_or_year, edition, language, source_type,
       url_or_file_reference, primary_or_secondary,
       CASE WHEN source_type IN ('DATASET','MODERN_BOOK') THEN 'NOT_APPLICABLE'
            ELSE 'UNKNOWN' END,
       status, notes, created_at, updated_at
  FROM sources;

DROP TABLE sources;
ALTER TABLE sources_moi RENAME TO sources;
CREATE INDEX idx_sources_status ON sources(status);

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
       s.edition_certainty,
       rvs.source_level,
       rvs.source_location,
       rvs.original_text,
       rvs.translation_vi,
       rvs.logic_note
  FROM rule_version_sources rvs
  JOIN rule_versions rv ON rv.rule_version_id = rvs.rule_version_id
  JOIN sources s        ON s.source_id = rvs.source_id;

PRAGMA foreign_keys = ON;

-- Cổ thư mà không nói rõ mức chắc chắn về bản in thì chặn ngay.
CREATE TRIGGER trg_co_thu_phai_ghi_edition_certainty
BEFORE INSERT ON sources
FOR EACH ROW
WHEN NEW.source_type IN ('CLASSIC', 'CLASSICAL_TEXT_TRANSCRIPTION')
     AND NEW.edition_certainty = 'NOT_APPLICABLE'
BEGIN
    SELECT RAISE(ABORT, 'THIEU_EDITION_CERTAINTY: co thu phai ghi ro muc chac chan ve ban in');
END;

-- Bảng nguyên văn: mỗi đoạn cổ thư gắn với quy tắc nào.
CREATE TABLE source_passages (
    passage_id      TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL REFERENCES sources(source_id) ON DELETE RESTRICT,
    chapter         TEXT,
    original_text   TEXT NOT NULL,
    translation_vi  TEXT NOT NULL,
    derivation_note TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE rule_version_passages (
    rule_version_id TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE CASCADE,
    passage_id      TEXT NOT NULL REFERENCES source_passages(passage_id) ON DELETE RESTRICT,
    PRIMARY KEY (rule_version_id, passage_id)
);
