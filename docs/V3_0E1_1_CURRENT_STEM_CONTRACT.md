# V3.0E1.1 — Chuẩn hóa hợp đồng Can ngày

## Mục tiêu

Loại bỏ phụ thuộc của runtime Hiệp Kỷ vào chuỗi diễn giải `technical_facts` khi cần Can ngày cho calculator `MONTH_BRANCH_DAY_STEM_V30E1`.

## Hợp đồng mới

Lớp cá nhân phát trực tiếp hai trường máy đọc:

- `current_stem`: mã Can hiện hành, một trong `GIAP, AT, BINH, DINH, MAU, KY, CANH, TAN, NHAM, QUY`.
- `current_branch`: mã Chi hiện hành.

Runtime Hiệp Kỷ đọc `current_stem` trực tiếp. Tham số `can_ngay` của `evaluate_event_v25()` vẫn được giữ để tương thích và có ưu tiên cao hơn khi được truyền hợp lệ.

## Fail-closed

- Không parse `technical_facts` để suy Can.
- `current_stem` ngoài bộ 10 Can không kích hoạt rule Can-ngày.
- Thiếu `current_stem` và không có `can_ngay` hợp lệ thì `月徳` không được kích hoạt.

## Bất biến quyết định

V3.0E1.1 không thêm rule và không đổi semantics:

- `月徳` vẫn `FAVORABLE_SUPPORT_ONLY`.
- `JI` vẫn thắng `YI`.
- `HARD_BLOCK > EVENT > PERSONAL` giữ nguyên.
- Numeric score vẫn `LOCKED_OFF`.
- Capability vẫn 21 active / 60 pending.
- Coverage vẫn `V3_0E1_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_1`.

## Regression bắt buộc

1. `current_stem=BINH` + tháng Dần kích hoạt `月徳` đúng trường hợp.
2. Chuỗi `technical_facts` chứa chữ “Can Bính” nhưng không có `current_stem` thì không được kích hoạt `月徳`.
3. `current_stem=INVALID` phải fail-closed.
4. `can_ngay=BINH` truyền trực tiếp vẫn tương thích và ưu tiên hơn payload cá nhân.
5. Các gate V3.0E1 cũ: thuận, `月徳 + 災煞`, HARD_BLOCK và score-off vẫn giữ nguyên.

## Phạm vi không làm

- Không kích hoạt token mới.
- Không thay inventory Hiệp Kỷ.
- Không mở UI.
- Không đổi source rule.
- Không review/approve golden mới trong release kỹ thuật này.
