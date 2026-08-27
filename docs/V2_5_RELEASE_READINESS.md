# V2.5 — Hiệp Kỷ mở rộng có kiểm soát

## Phạm vi release

V2.5 mở rộng riêng luồng **Tìm ngày theo việc** cho đúng 12 loại việc hiện hành. Đây **không phải** triển khai toàn bộ 《欽定協紀辨方書》 và không được mô tả là Hiệp Kỷ đầy đủ.

Nguồn inventory chính: 《欽定協紀辨方書（四庫全書本）》, trọng tâm 卷十一 · 用事; công thức quan hệ tháng-ngày đối chiếu các quyển định nghĩa tương ứng.

## Đã kích hoạt

1. Lớp 12 Trực đã nghiệm thu từ V1.
2. Năm token quan hệ Chi tháng-ngày có bộ tính riêng:
   - 月建 — Nguyệt Kiến;
   - 月破 — Nguyệt Phá;
   - 三合 — Tam Hợp;
   - 六合 — Lục Hợp;
   - 月害 — Nguyệt Hại.
3. Mỗi evidence đang dùng cho quyết định phải có Rule ID, source ID và vị trí nguồn.
4. Thứ bậc quyết định giữ nguyên: `HARD_BLOCK > EVENT > PERSONAL`.
5. `numeric_score = LOCKED_OFF`.

## Giới hạn bắt buộc

- Các token cổ thư chưa có bộ tính như 天徳, 月徳, 天願, 劫煞, 災煞, 月煞, 月刑... tiếp tục `PENDING_CALCULATOR` và không được tác động vào kết luận.
- Tín hiệu `JI` mới từ lớp 5 token chỉ tạo **CAUTION/Không ưu tiên**, chưa tự tạo HARD_BLOCK. HARD_BLOCK vẫn thuộc lớp V1 đã nghiệm thu.
- Hai ánh xạ hiện đại `MUA_TAI_SAN` và `DAM_PHAN` vẫn `PROVISIONAL`; tín hiệu mới không được tự nâng chúng thành `Ưu tiên`.
- `DIEU_TRI` chỉ dùng chọn ngày khi thời điểm y khoa có thể linh hoạt; không trì hoãn cấp cứu hay điều trị cần thiết.
- V2.4 giờ cá nhân vẫn chỉ `DESCRIPTIVE_ONLY`; giờ không cứu ngày bị chặn.

## Kiến trúc

- `/api/stateless/tim-ngay`: giữ V1, không thay hành vi.
- `/api/v2/tim-ngay`: dùng pipeline V2.5 riêng.
- `/api/v2/schema-status`: `2.5-alpha.1 / V2_5_HIEP_KY_PARTIAL_ACTIVE`.
- Coverage công khai: `V2_5_PARTIAL_12_TRUC_PLUS_MONTH_BRANCH_5`.
- `full_classical_claim = false`.

## Quy trình deploy

Các commit trung gian trên branch được Vercel bỏ build. Chỉ commit cuối/PR-ready có marker `[vercel-preview]` mới tạo preview. Chỉ merge sau khi GitHub Actions và preview đều PASS. Sau merge phải chạy live smoke production rồi mới đóng release.
