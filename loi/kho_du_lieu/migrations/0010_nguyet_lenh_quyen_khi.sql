-- 0010_nguyet_lenh_quyen_khi.sql
-- Hai lớp TÁCH RỜI:
--   BT-ML-*            nguyệt lệnh — xác định được, không tranh cãi
--   BT-SEASON-POWER-*  quyền khí theo tiết — các nguồn nói khác nhau
-- Không lớp nào chứa điểm số hay mạnh yếu.

PRAGMA foreign_keys = ON;

-- Mùa của từng Chi tháng. Suy từ Tiết mở tháng, không tranh cãi.
CREATE TABLE month_commands (
    month_branch    TEXT PRIMARY KEY REFERENCES branches(code),
    season          TEXT NOT NULL CHECK (season IN ('XUAN','HA','THU','DONG')),
    opening_jie     TEXT NOT NULL,
    closing_jie     TEXT NOT NULL,
    rule_id         TEXT NOT NULL REFERENCES rule_registry(rule_id),
    source_id       TEXT REFERENCES sources(source_id)
);

-- Bảng quyền khí, ghi theo TỪNG TRUYỀN THỐNG. Không hợp nhất.
CREATE TABLE seasonal_governing_qi (
    entry_id        TEXT PRIMARY KEY,
    tradition       TEXT NOT NULL,
    solar_term      TEXT NOT NULL,
    segment_order   INTEGER NOT NULL,
    governing_stem  TEXT REFERENCES stems(code),   -- NULL khi nguồn không nói rõ
    day_count       INTEGER,                        -- NULL khi nguồn không cho số ngày
    textual_order   INTEGER NOT NULL,
    original_text   TEXT NOT NULL,
    parse_status    TEXT NOT NULL
                    CHECK (parse_status IN ('PARSED','PARTIAL','NO_DAY_COUNT',
                                            'SUSPECT_TEXT','NOT_TRANSCRIBED')),
    status          TEXT NOT NULL DEFAULT 'PROVISIONAL'
                    CHECK (status IN ('VERIFIED','PROVISIONAL','CONFLICTED','NOT_TRANSCRIBED')),
    source_id       TEXT NOT NULL REFERENCES sources(source_id),
    rule_id         TEXT NOT NULL REFERENCES rule_registry(rule_id),
    notes           TEXT,
    UNIQUE (tradition, solar_term, segment_order)
);

-- Chặn mọi thứ có mùi tỷ lệ hay điểm số lọt vào bảng quyền khí.
CREATE TRIGGER trg_quyen_khi_khong_ty_le
BEFORE INSERT ON seasonal_governing_qi
FOR EACH ROW
WHEN NEW.notes LIKE '%60/30/10%' OR NEW.notes LIKE '%70/20/10%'
  OR NEW.notes LIKE '%strength%' OR NEW.notes LIKE '%score%'
BEGIN
    SELECT RAISE(ABORT, 'QUYEN_KHI_KHONG_DUOC_CHUA_TY_LE_HAY_DIEM_SO');
END;

-- Ghi nhận mức đồng thuận giữa các truyền thống cho từng tiết.
CREATE TABLE seasonal_qi_agreement (
    solar_term       TEXT PRIMARY KEY,
    agreement_status TEXT NOT NULL
                     CHECK (agreement_status IN ('AGREED','CONFLICTED',
                                                 'INSUFFICIENT_SOURCES','PROVISIONAL')),
    tradition_count  INTEGER NOT NULL,
    notes            TEXT
);
