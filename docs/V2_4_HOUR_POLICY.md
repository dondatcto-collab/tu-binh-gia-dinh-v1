# V2.4 — Giờ cá nhân

## Phạm vi đã khóa

V2.4 không được gọi một giờ là “giờ tốt/xấu cá nhân” chỉ vì đã có Can Chi giờ hoặc một quan hệ Thập Thần đơn lẻ.

Trạng thái phương pháp phải phân biệt rõ:

- `hour_structure_ready`: đã có thể tính/hiển thị cấu trúc giờ;
- `hour_fusion_ready`: chỉ `true` khi đã có hợp lưu giờ + ngày + nền mệnh được nghiệm thu;
- `personal_hour_decision_ready`: chỉ `true` khi được phép sinh kết luận giờ cá nhân.

Ở V2.4 alpha, `hour_structure_ready = true`, còn `hour_fusion_ready = false` và `personal_hour_decision_ready = false`.

UI chỉ được hiển thị giờ ở mức tham khảo cấu trúc và phải nói rõ chưa đủ căn cứ để gọi là giờ tốt/xấu cá nhân. Không numeric score. Không cho giờ cứu ngày `HARD_BLOCK`.
