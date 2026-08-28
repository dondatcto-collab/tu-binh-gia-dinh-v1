# V2.9A Release Candidate

Scope: event-day gate trước lớp giờ cá nhân.

Đã khóa:
- HARD_BLOCK của ngày không thể được giờ cứu.
- Không có loại việc => giờ chỉ DESCRIPTIVE_ONLY.
- Ngày không bị chặn => chỉ PASS_TO_HOUR_RULES; chưa gọi giờ tốt/xấu.
- personal_hour_decision_ready = false.
- numeric_score = null / LOCKED_OFF.
- UI chọn đúng 12 loại việc hiện hành và chỉ gọi `/api/v2/gio-ca-nhan`.

V2.9B chỉ được mở sau khi có inventory rule giờ + nguồn + trạng thái VERIFIED + ca vàng xung đột.
