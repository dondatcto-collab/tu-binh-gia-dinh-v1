# TÌNH TRẠNG THẬT — 0.4.0

Cập nhật: 2026-08-24  
`ENGINE_VERSION = 0.4.0-zpzq-method-gate`  
`RULESET_VERSION = RS-2026.08-ZPZQ.1`

## 1. Điều đã sửa ở 0.4.0
0.3.x đã dùng Thập Thần + quan hệ Địa Chi để tạo lời khuyên cá nhân trong khi Cách cục/hỷ-kỵ chưa hoàn chỉnh. 0.4.0 khóa lại phương pháp:
- Thập Thần và quan hệ Can/Chi vẫn tính và truy nguồn.
- Chúng chỉ là **evidence cấu trúc**, không thay Dụng/Hỷ/Kỵ.
- Lớp cá nhân tạm ở `DESCRIPTIVE_ONLY`.
- Tìm ngày vẫn chạy lớp Hiệp Kỷ, nhưng cá nhân chưa được phép nâng/hạ hạng.

## 2. Phương pháp cá nhân đã khóa
**Tử Bình Chân Thuyên — Nguyệt lệnh/Cách cục (`ZPZQ-GEJU-V1`)**.

Ba nguyên tắc phương pháp đã đưa vào rule registry:
- `BT-BASE-0401`: không lấy đắc/thất thời một mình để kết luận mạnh/yếu; các trụ khác có quyền tăng giảm.
- `BT-USE-0401`: Dụng thần chuyên cầu từ Nguyệt lệnh, phối Nhật can để phân Cách cục.
- `BT-DY-0401`: luận vận phải phối Can Chi vận với hỷ/kỵ đã xác lập từ mệnh gốc.

Nguồn chính được ghim bằng bản scan; bản chép số hóa chỉ dùng đối chiếu.

## 3. Đã có và được phép dùng
- Lập Tứ Trụ / lịch pháp nền.
- Nguyệt lệnh.
- Tàng Can.
- Thập Thần.
- Quan hệ Địa Chi đang có nguồn.
- Đại vận / Năm / Tháng / Ngày ở tầng dữ liệu thời gian.
- Hiệp Kỷ V1-basic theo 12 Trực cho 13 nhóm việc, giữ trạng thái VERIFIED/PROVISIONAL.
- Trace Rule → Version → Source → Passage → status.

## 4. Chưa có quyền kết luận cá nhân
- Cách cục engine đầy đủ.
- Thành/bại/cứu/ứng và biến hóa cách cục.
- Hỷ/Kỵ mệnh gốc theo phương pháp đã khóa.
- Hợp lưu Đại vận→Năm→Tháng→Ngày→Giờ với hỷ/kỵ.
- Giờ tốt/xấu cá nhân theo chính ngày đang xét.

Vì vậy: **chưa được gọi một thời điểm là thuận/nghịch cá nhân chỉ từ Thập Thần hoặc xung/hợp.**

## 5. Kiểm thử 0.4.0
- Static Python compile: PASS.
- JavaScript syntax: PASS.
- YAML parse: PASS.
- Rule/seed audit: 0 lỗi, 0 cảnh báo.
- Bộ hồi quy phương pháp 0.4: PASS.
- Full Calendar/Golden trong container: chưa chạy hết vì thiếu package `astronomy`; đây là giới hạn môi trường, không được ghi PASS.

## 6. Việc ưu tiên duy nhất
Trích và mã hóa có nguồn phần **Luận Dụng Thần / Cách cục** của Tử Bình Chân Thuyên trong kiến trúc hiện có. Không xây thêm lớp mới.
