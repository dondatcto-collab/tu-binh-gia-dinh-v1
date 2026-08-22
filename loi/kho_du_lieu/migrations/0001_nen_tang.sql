-- 0001_nen_tang.sql
-- Bảng nền: tham chiếu bất biến, người dùng, hồ sơ, dữ liệu sinh,
-- bộ quy ước lịch, và Source Registry.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------
-- 1. BẢNG THAM CHIẾU BẤT BIẾN
-- ---------------------------------------------------------------

CREATE TABLE elements (
    element_code    TEXT PRIMARY KEY,          -- MOC, HOA, THO, KIM, THUY
    name_vi         TEXT NOT NULL,
    name_original   TEXT NOT NULL
);

CREATE TABLE element_relations (
    from_element    TEXT NOT NULL REFERENCES elements(element_code),
    to_element      TEXT NOT NULL REFERENCES elements(element_code),
    relation        TEXT NOT NULL CHECK (relation IN ('SINH', 'KHAC')),
    PRIMARY KEY (from_element, to_element, relation)
);

CREATE TABLE stems (
    stem_index      INTEGER PRIMARY KEY CHECK (stem_index BETWEEN 1 AND 10),
    code            TEXT NOT NULL UNIQUE,
    name_vi         TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    polarity        TEXT NOT NULL CHECK (polarity IN ('DUONG', 'AM')),
    element_code    TEXT NOT NULL REFERENCES elements(element_code)
);

CREATE TABLE branches (
    branch_index    INTEGER PRIMARY KEY CHECK (branch_index BETWEEN 1 AND 12),
    code            TEXT NOT NULL UNIQUE,
    name_vi         TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    polarity        TEXT NOT NULL CHECK (polarity IN ('DUONG', 'AM')),
    element_code    TEXT NOT NULL REFERENCES elements(element_code)
);

-- Tàng Can: nguồn phải xác minh trước khi seed, nên bảng để trống ở V1.
CREATE TABLE branch_hidden_stems (
    branch_index    INTEGER NOT NULL REFERENCES branches(branch_index),
    stem_index      INTEGER NOT NULL REFERENCES stems(stem_index),
    rank            INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 3),
    source_id       TEXT NOT NULL REFERENCES sources(source_id),
    status          TEXT NOT NULL DEFAULT 'PROVISIONAL'
                    CHECK (status IN ('VERIFIED','PROVISIONAL','CONFLICTED','REJECTED')),
    PRIMARY KEY (branch_index, stem_index)
);

CREATE TABLE rule_namespaces (
    namespace       TEXT PRIMARY KEY,          -- vd: BT-PAT, HK-EVENT, FUS
    name_vi         TEXT NOT NULL,
    description     TEXT
);

-- ---------------------------------------------------------------
-- 2. SOURCE REGISTRY
-- ---------------------------------------------------------------

CREATE TABLE sources (
    source_id               TEXT PRIMARY KEY,
    title                   TEXT NOT NULL,
    author                  TEXT,
    dynasty_or_year         TEXT,
    edition                 TEXT,
    language                TEXT NOT NULL,     -- vd: zh-Hant, vi, en
    source_type             TEXT NOT NULL
                            CHECK (source_type IN ('CLASSIC','COMMENTARY','TRANSLATION',
                                                   'MODERN_BOOK','ARTICLE','DATASET','OTHER')),
    url_or_file_reference   TEXT,
    primary_or_secondary    TEXT NOT NULL
                            CHECK (primary_or_secondary IN ('PRIMARY','SECONDARY')),
    status                  TEXT NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('ACTIVE','PENDING','DEPRECATED','REJECTED')),
    notes                   TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_sources_status ON sources(status);

-- ---------------------------------------------------------------
-- 3. NGƯỜI DÙNG VÀ HỒ SƠ
-- ---------------------------------------------------------------

CREATE TABLE users (
    user_id         TEXT PRIMARY KEY,
    display_name    TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE profiles (
    profile_id      TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name       TEXT NOT NULL,
    gender          TEXT NOT NULL CHECK (gender IN ('NAM','NU')),
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_profiles_user ON profiles(user_id);

-- Dữ liệu sinh giữ nguyên dạng người dùng nhập.
-- Mọi quy đổi lịch pháp là việc của Calendar Engine, không lưu đè lên đây.
CREATE TABLE birth_data (
    birth_data_id       TEXT PRIMARY KEY,
    profile_id          TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    birth_year          INTEGER NOT NULL,
    birth_month         INTEGER NOT NULL CHECK (birth_month BETWEEN 1 AND 12),
    birth_day           INTEGER NOT NULL CHECK (birth_day BETWEEN 1 AND 31),
    birth_hour          INTEGER NOT NULL CHECK (birth_hour BETWEEN 0 AND 23),
    birth_minute        INTEGER NOT NULL CHECK (birth_minute BETWEEN 0 AND 59),
    birth_place_text    TEXT NOT NULL,
    latitude            REAL,
    longitude           REAL,
    timezone_name       TEXT,
    utc_offset_minutes  INTEGER,
    time_certainty      TEXT NOT NULL DEFAULT 'KNOWN'
                        CHECK (time_certainty IN ('KNOWN','APPROXIMATE','UNKNOWN')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (profile_id)
);

-- ---------------------------------------------------------------
-- 4. BỘ QUY ƯỚC LỊCH
-- ---------------------------------------------------------------

CREATE TABLE calendar_rulesets (
    calendar_ruleset_id TEXT PRIMARY KEY,      -- vd: CAL-V1
    version             TEXT NOT NULL,
    name_vi             TEXT NOT NULL,
    source_id           TEXT REFERENCES sources(source_id),
    status              TEXT NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE','EXPERIMENTAL','DEPRECATED')),
    is_default          INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0,1)),
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (calendar_ruleset_id, version)
);

-- Từng thiết lập là một dòng. Engine đọc bảng này, không đọc hằng số trong mã.
CREATE TABLE calendar_ruleset_settings (
    calendar_ruleset_id TEXT NOT NULL REFERENCES calendar_rulesets(calendar_ruleset_id)
                        ON DELETE CASCADE,
    setting_key         TEXT NOT NULL,
    setting_value       TEXT NOT NULL,
    value_type          TEXT NOT NULL CHECK (value_type IN ('STRING','BOOL','INT','TIME')),
    source_id           TEXT REFERENCES sources(source_id),
    notes               TEXT,
    PRIMARY KEY (calendar_ruleset_id, setting_key)
);

-- Chỉ được một bộ lịch mặc định.
CREATE UNIQUE INDEX idx_calendar_default
    ON calendar_rulesets(is_default) WHERE is_default = 1;

-- ---------------------------------------------------------------
-- 5. LOẠI SỰ KIỆN
-- ---------------------------------------------------------------

CREATE TABLE event_types (
    event_type_id   TEXT PRIMARY KEY,          -- vd: EVT-KHAI-TRUONG
    code            TEXT NOT NULL UNIQUE,
    name_vi         TEXT NOT NULL,
    name_original   TEXT,
    status          TEXT NOT NULL DEFAULT 'PLACEHOLDER'
                    CHECK (status IN ('ACTIVE','PLACEHOLDER','DEPRECATED')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
