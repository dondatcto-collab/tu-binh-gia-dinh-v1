# V2.4 controlled production retry

Mục đích: kích hoạt đúng một lượt production deployment sau khi Vercel từng chặn build do rate limit.

Không thay đổi engine, schema, rule, API hoặc UI.

Điều kiện đóng V2.4:
- full regression PASS;
- live smoke production PASS;
- production `/api/v2/schema-status` = `2.4-alpha.1`;
- `/api/v2/gio-ca-nhan` trả 12 giờ `DESCRIPTIVE_ONLY`;
- runtime không có lỗi mới.

Nếu Vercel tiếp tục chặn build, dừng retry để tránh vòng lặp.
