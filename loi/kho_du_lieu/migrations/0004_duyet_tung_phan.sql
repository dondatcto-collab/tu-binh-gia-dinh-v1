-- 0004_duyet_tung_phan.sql
-- Cho phép duyệt ca vàng theo từng lớp.
-- Một lớp còn tranh luận không được làm cả ca thành vô dụng.

PRAGMA foreign_keys = ON;

-- Thêm trạng thái CONFLICTED cho từng lớp đáp án, và ghi nguồn theo lớp.
CREATE TABLE golden_case_expected_moi (
    expected_id      TEXT PRIMARY KEY,
    case_id          TEXT NOT NULL REFERENCES golden_cases(case_id) ON DELETE CASCADE,
    stage            TEXT NOT NULL CHECK (stage IN ('INTERMEDIATE','FINAL')),
    stage_key        TEXT NOT NULL,
    expected_payload TEXT NOT NULL,
    tolerance_seconds REAL,
    source_id        TEXT REFERENCES sources(source_id),
    source_note      TEXT,
    review_status    TEXT NOT NULL DEFAULT 'PENDING'
                     CHECK (review_status IN ('PENDING','APPROVED','REJECTED','CONFLICTED')),
    reviewed_by      TEXT,
    reviewed_at      TEXT,
    notes            TEXT,
    UNIQUE (case_id, stage, stage_key)
);

INSERT INTO golden_case_expected_moi
    (expected_id, case_id, stage, stage_key, expected_payload,
     review_status, reviewed_by, reviewed_at, notes)
SELECT expected_id, case_id, stage, stage_key, expected_payload,
       review_status, reviewed_by, reviewed_at, notes
  FROM golden_case_expected;

DROP TABLE golden_case_expected;
ALTER TABLE golden_case_expected_moi RENAME TO golden_case_expected;

-- Lớp đáp án đã duyệt bắt buộc phải có nguồn riêng.
CREATE TRIGGER trg_expected_duyet_phai_co_nguon
BEFORE INSERT ON golden_case_expected
FOR EACH ROW
WHEN NEW.review_status = 'APPROVED' AND NEW.source_id IS NULL
BEGIN
    SELECT RAISE(ABORT, 'THIEU_NGUON_THEO_LOP: lop dap an da duyet phai ghi nguon rieng');
END;

-- Bảng ghi các tranh luận mang sang giai đoạn sau.
CREATE TABLE known_conflicts (
    conflict_id     TEXT PRIMARY KEY,
    rule_id         TEXT REFERENCES rule_registry(rule_id),
    title_vi        TEXT NOT NULL,
    mo_ta           TEXT NOT NULL,
    cac_cach_hieu   TEXT NOT NULL,
    dang_dung       TEXT,
    trang_thai      TEXT NOT NULL DEFAULT 'OPEN'
                    CHECK (trang_thai IN ('OPEN','RESOLVED','DEFERRED')),
    anh_huong_toi   TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Dữ liệu tranh luận được nạp ở bước nạp mầm, sau khi có quy tắc TIME-0007.
