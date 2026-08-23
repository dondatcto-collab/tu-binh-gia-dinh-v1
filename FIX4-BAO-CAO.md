# FIX4 — V1 BASIC DECISION LAYER

## Mục tiêu
V1 bắt đầu trả lời ba câu hỏi lõi mà không bịa điểm số:
1. Tháng này thế nào?
2. Hôm nay thế nào?
3. Ngày nào phù hợp hơn cho một việc?

## Đã mở
- BT-REL: Lục hợp, Lục xung, Lục hại, Hình; 4 rule VERIFIED.
- Hiệp Kỷ V1-basic: 12 Trực + 13 nhóm việc; mapping hiện đại có thể PROVISIONAL.
- Hợp lưu rời rạc: kỵ theo việc không bị quan hệ cá nhân thuận đảo ngược.
- Không dùng điểm 0–10; score=None; scoring_status=ORDINAL_V1_BASIC.
- Dữ liệu hồ sơ lưu cục bộ trên thiết bị; API stateless.

## Vẫn không dùng để kết luận
- Vượng suy, Cách cục, Dụng/Hỷ/Kỵ khi chưa đủ rule nguồn.
- Thần sát chưa hoàn thiện.
- Điểm số tuyệt đối chưa hiệu chỉnh.

## Giao diện
- 5 phong cách đã chốt.
- 6 avatar cố định: nam/nữ lớn tuổi, trung niên, thiếu niên.
- Lịch cá nhân, Hôm nay/Tháng này, Tìm ngày, Hồ sơ, Cài đặt theo bố cục đã khóa.

## Kiểm thử
- Regression phạm vi BT-REL cũ đã cập nhật theo FIX4.
- Decision/database/rule tests PASS trong môi trường hiện tại.
- Full Calendar/Golden suite cần package `astronomy-engine`; môi trường ChatGPT hiện tại không có module `astronomy`, nên các test phụ thuộc thiên văn không thể tái chạy tại đây.
