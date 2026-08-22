-- 0003_ket_qua_va_kiem_thu.sql
-- Bảng lá số, các tầng phân tích, kết quả hợp lưu, ca vàng, lần chạy kiểm thử.
-- Mọi bảng kết quả đều có ruleset_version, engine_version, calculation_timestamp.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------
-- 1. LÁ SỐ
-- ---------------------------------------------------------------

CREATE TABLE bazi_charts (
    chart_id                TEXT PRIMARY KEY,
    profile_id              TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    calendar_ruleset_id     TEXT NOT NULL REFERENCES calendar_rulesets(calendar_ruleset_id),

    year_stem_index         INTEGER NOT NULL REFERENCES stems(stem_index),
    year_branch_index       INTEGER NOT NULL REFERENCES branches(branch_index),
    month_stem_index        INTEGER NOT NULL REFERENCES stems(stem_index),
    month_branch_index      INTEGER NOT NULL REFERENCES branches(branch_index),
    day_stem_index          INTEGER NOT NULL REFERENCES stems(stem_index),
    day_branch_index        INTEGER NOT NULL REFERENCES branches(branch_index),
    hour_stem_index         INTEGER REFERENCES stems(stem_index),
    hour_branch_index       INTEGER REFERENCES branches(branch_index),

    day_master_stem_index   INTEGER NOT NULL REFERENCES stems(stem_index),
    month_command_element   TEXT REFERENCES elements(element_code),

    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (profile_id, calendar_ruleset_id, engine_version)
);

CREATE TABLE chart_hidden_stems (
    chart_id        TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    pillar          TEXT NOT NULL CHECK (pillar IN ('YEAR','MONTH','DAY','HOUR')),
    stem_index      INTEGER NOT NULL REFERENCES stems(stem_index),
    rank            INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 3),
    PRIMARY KEY (chart_id, pillar, stem_index)
);

CREATE TABLE chart_ten_gods (
    chart_id        TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    position        TEXT NOT NULL,             -- YEAR_STEM, MONTH_HIDDEN_1, ...
    ten_god_code    TEXT NOT NULL,
    rule_version_id TEXT REFERENCES rule_versions(rule_version_id),
    PRIMARY KEY (chart_id, position, ten_god_code)
);

CREATE TABLE chart_relations (
    chart_relation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id            TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    relation_type       TEXT NOT NULL
                        CHECK (relation_type IN ('HOP','XUNG','HINH','HAI','PHA','HOI','TAM_HOP')),
    positions           TEXT NOT NULL,
    transformation      TEXT NOT NULL DEFAULT 'COMBINATION_ONLY'
                        CHECK (transformation IN ('COMBINATION_ONLY',
                                                  'QUALIFIED_FOR_TRANSFORMATION','TRANSFORMED')),
    rule_version_id     TEXT REFERENCES rule_versions(rule_version_id)
);

-- ---------------------------------------------------------------
-- 2. CÁC TẦNG PHÂN TÍCH
-- ---------------------------------------------------------------

CREATE TABLE natal_analysis (
    natal_analysis_id       TEXT PRIMARY KEY,
    chart_id                TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    pattern_code            TEXT,
    pattern_status          TEXT
                            CHECK (pattern_status IN ('CANDIDATE','FORMED','FORMED_WITH_DEFECT',
                                                      'DAMAGED','RESCUED','TRANSFORMED','UNRESOLVED')),
    pattern_use_element     TEXT REFERENCES elements(element_code),
    natal_usefulness        TEXT,
    strength_assessment     TEXT,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE natal_factors (
    natal_analysis_id   TEXT NOT NULL REFERENCES natal_analysis(natal_analysis_id) ON DELETE CASCADE,
    factor_kind         TEXT NOT NULL
                        CHECK (factor_kind IN ('SUPPORTIVE','ADVERSE','CONDITIONAL')),
    element_code        TEXT NOT NULL REFERENCES elements(element_code),
    condition_note      TEXT,
    rule_version_id     TEXT REFERENCES rule_versions(rule_version_id),
    PRIMARY KEY (natal_analysis_id, factor_kind, element_code)
);

CREATE TABLE da_yun_periods (
    da_yun_period_id        TEXT PRIMARY KEY,
    chart_id                TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    sequence_no             INTEGER NOT NULL CHECK (sequence_no >= 1),
    stem_index              INTEGER NOT NULL REFERENCES stems(stem_index),
    branch_index            INTEGER NOT NULL REFERENCES branches(branch_index),
    direction               TEXT NOT NULL CHECK (direction IN ('THUAN','NGHICH')),
    start_date              TEXT NOT NULL,
    end_date                TEXT NOT NULL,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (chart_id, sequence_no)
);

CREATE TABLE year_analysis (
    year_analysis_id        TEXT PRIMARY KEY,
    chart_id                TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    da_yun_period_id        TEXT NOT NULL REFERENCES da_yun_periods(da_yun_period_id),
    solar_year              INTEGER NOT NULL,
    stem_index              INTEGER NOT NULL REFERENCES stems(stem_index),
    branch_index            INTEGER NOT NULL REFERENCES branches(branch_index),
    context_state           TEXT,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (chart_id, solar_year, engine_version)
);

CREATE TABLE month_analysis (
    month_analysis_id       TEXT PRIMARY KEY,
    year_analysis_id        TEXT NOT NULL REFERENCES year_analysis(year_analysis_id) ON DELETE CASCADE,
    month_ordinal           INTEGER NOT NULL CHECK (month_ordinal BETWEEN 1 AND 12),
    stem_index              INTEGER NOT NULL REFERENCES stems(stem_index),
    branch_index            INTEGER NOT NULL REFERENCES branches(branch_index),
    context_state           TEXT,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (year_analysis_id, month_ordinal)
);

-- Tác động theo lĩnh vực, dùng chung cho tầng năm và tầng tháng.
CREATE TABLE period_domain_effects (
    period_domain_effect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_kind             TEXT NOT NULL CHECK (period_kind IN ('YEAR','MONTH')),
    period_id               TEXT NOT NULL,
    domain_code             TEXT NOT NULL,     -- CONG_VIEC, TAI_CHINH, QUAN_HE...
    effect_class            TEXT NOT NULL
                            CHECK (effect_class IN ('UU_TIEN','CO_THE_LAM','HAN_CHE',
                                                    'KHONG_UU_TIEN','CO_HOI','RUI_RO')),
    rule_version_id         TEXT REFERENCES rule_versions(rule_version_id),
    note_vi                 TEXT
);

CREATE INDEX idx_pde_period ON period_domain_effects(period_kind, period_id);

CREATE TABLE day_analysis (
    day_analysis_id         TEXT PRIMARY KEY,
    chart_id                TEXT NOT NULL REFERENCES bazi_charts(chart_id) ON DELETE CASCADE,
    month_analysis_id       TEXT REFERENCES month_analysis(month_analysis_id),
    solar_date              TEXT NOT NULL,
    stem_index              INTEGER NOT NULL REFERENCES stems(stem_index),
    branch_index            INTEGER NOT NULL REFERENCES branches(branch_index),
    person_day_state        TEXT,
    person_score            REAL,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (chart_id, solar_date, engine_version)
);

CREATE INDEX idx_day_analysis_date ON day_analysis(solar_date);

CREATE TABLE hour_analysis (
    hour_analysis_id        TEXT PRIMARY KEY,
    day_analysis_id         TEXT NOT NULL REFERENCES day_analysis(day_analysis_id) ON DELETE CASCADE,
    branch_index            INTEGER NOT NULL REFERENCES branches(branch_index),
    stem_index              INTEGER REFERENCES stems(stem_index),
    hour_state              TEXT,
    hour_score              REAL,
    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (day_analysis_id, branch_index)
);

-- ---------------------------------------------------------------
-- 3. KẾT QUẢ HỢP LƯU
-- ---------------------------------------------------------------

CREATE TABLE fusion_results (
    fusion_result_id        TEXT PRIMARY KEY,
    profile_id              TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    day_analysis_id         TEXT NOT NULL REFERENCES day_analysis(day_analysis_id),
    hour_analysis_id        TEXT REFERENCES hour_analysis(hour_analysis_id),
    event_type_id           TEXT REFERENCES event_types(event_type_id),
    event_rule_pack_id      TEXT REFERENCES event_rule_packs(event_rule_pack_id),

    person_score            REAL,
    event_score             REAL,
    final_score             REAL,
    final_label             TEXT,
    final_status            TEXT,
    confidence              TEXT CHECK (confidence IN ('HIGH','MEDIUM','LOW')),
    relative_rank           INTEGER,

    ruleset_version         TEXT NOT NULL,
    engine_version          TEXT NOT NULL,
    calculation_timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_fusion_profile ON fusion_results(profile_id);

-- Mọi phát hiện của Fusion đều gắn với một phiên bản quy tắc.
-- Đây là mắt xích: fusion_results -> rule_version -> rule_id -> source.
CREATE TABLE fusion_findings (
    fusion_finding_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    fusion_result_id    TEXT NOT NULL REFERENCES fusion_results(fusion_result_id) ON DELETE CASCADE,
    finding_kind        TEXT NOT NULL
                        CHECK (finding_kind IN ('HARD_BLOCK','CONFLICT','MITIGATION',
                                                'POSITIVE','NEGATIVE','WARNING')),
    rule_version_id     TEXT NOT NULL REFERENCES rule_versions(rule_version_id) ON DELETE RESTRICT,
    severity            TEXT CHECK (severity IN ('MAJOR','MEDIUM','MINOR')),
    mitigation_state    TEXT CHECK (mitigation_state IN ('FULLY_MITIGATED','PARTIALLY_MITIGATED',
                                                         'NOT_MITIGATED','NON_MITIGATABLE')),
    conflict_type       TEXT,
    detail_vi           TEXT,
    ordering            INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_ff_result ON fusion_findings(fusion_result_id);
CREATE INDEX idx_ff_rule ON fusion_findings(rule_version_id);

-- Quy tắc đã được dùng trong một kết quả thì bị khoá ngay.
CREATE TRIGGER trg_lock_rule_on_use
AFTER INSERT ON fusion_findings
FOR EACH ROW
BEGIN
    UPDATE rule_versions SET locked = 1
     WHERE rule_version_id = NEW.rule_version_id AND locked = 0;
    INSERT INTO audit_logs (entity_type, entity_id, action, reason)
    SELECT 'rule_versions', NEW.rule_version_id, 'LOCK', 'da dung trong ket qua'
     WHERE changes() > 0;
END;

-- ---------------------------------------------------------------
-- 4. CA VÀNG VÀ LẦN CHẠY KIỂM THỬ
-- ---------------------------------------------------------------

CREATE TABLE golden_cases (
    case_id             TEXT PRIMARY KEY,
    category            TEXT NOT NULL
                        CHECK (category IN ('GOLD-CAL','GOLD-BT','GOLD-HK',
                                            'GOLD-SS','GOLD-FUS','GOLD-END')),
    title_vi            TEXT NOT NULL,
    source_id           TEXT REFERENCES sources(source_id),
    source_location     TEXT,
    ruleset_version     TEXT NOT NULL,
    calendar_ruleset_id TEXT REFERENCES calendar_rulesets(calendar_ruleset_id),
    input_payload       TEXT NOT NULL,
    review_status       TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (review_status IN ('PENDING','APPROVED','REJECTED','NEEDS_REWORK')),
    reviewed_by         TEXT,
    reviewed_at         TEXT,
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_golden_category ON golden_cases(category);
CREATE INDEX idx_golden_review ON golden_cases(review_status);

CREATE TABLE golden_case_expected (
    expected_id     TEXT PRIMARY KEY,
    case_id         TEXT NOT NULL REFERENCES golden_cases(case_id) ON DELETE CASCADE,
    stage           TEXT NOT NULL CHECK (stage IN ('INTERMEDIATE','FINAL')),
    stage_key       TEXT NOT NULL,             -- vd: year_pillar, final_label
    expected_payload TEXT NOT NULL,
    review_status   TEXT NOT NULL DEFAULT 'PENDING'
                    CHECK (review_status IN ('PENDING','APPROVED','REJECTED')),
    reviewed_by     TEXT,
    reviewed_at     TEXT,
    notes           TEXT,
    UNIQUE (case_id, stage, stage_key)
);

CREATE TABLE test_runs (
    test_run_id         TEXT PRIMARY KEY,
    started_at          TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at         TEXT,
    engine_version      TEXT NOT NULL,
    ruleset_version     TEXT NOT NULL,
    total_cases         INTEGER NOT NULL DEFAULT 0,
    passed              INTEGER NOT NULL DEFAULT 0,
    failed              INTEGER NOT NULL DEFAULT 0,
    blocked             INTEGER NOT NULL DEFAULT 0,
    pending_excluded    INTEGER NOT NULL DEFAULT 0,
    notes               TEXT
);

CREATE TABLE test_run_results (
    test_run_id     TEXT NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    case_id         TEXT NOT NULL REFERENCES golden_cases(case_id) ON DELETE CASCADE,
    status          TEXT NOT NULL
                    CHECK (status IN ('PASS','FAIL','BLOCKED','PENDING_EXCLUDED')),
    detail          TEXT,
    PRIMARY KEY (test_run_id, case_id)
);
