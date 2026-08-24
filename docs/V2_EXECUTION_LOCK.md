# V2 EXECUTION LOCK

Mục tiêu: tránh phá kế hoạch V2 và tránh vòng lặp chỉnh UI/logic nhiều lần.

## Thứ tự bắt buộc

1. Core flows: Trang chủ → Hôm nay → Tháng → Đại vận → Tìm ngày.
2. Mỗi core flow phải đọc Result Schema V2; UI không tự suy quyết định từ dữ liệu kỹ thuật.
3. Chỉ khi 5 core flows PASS mới mở domain mới.
4. Thứ tự domain: Công việc → Tiền bạc → Quan hệ → Giờ cá nhân → Hiệp Kỷ mở rộng.

## Điều kiện đóng một giai đoạn

Một giai đoạn chỉ được đánh dấu DONE khi:
- schema/API tương ứng đã có test;
- UI consumer không gọi lại route V1 cho luồng đã chuyển;
- full regression PASS;
- Vercel preview PASS;
- live smoke V1 PASS;
- production health PASS sau merge.

## Chống vòng lặp

- Không quay lại sửa câu chữ của giai đoạn đã PASS nếu không có lỗi thực tế hoặc phản hồi người dùng cụ thể.
- Không thêm rule/domain mới trong PR chỉ nhằm hoàn thiện core flow.
- Không để UI tự tái tạo logic mà server/schema đã quyết định.
- Không đổi engine 0.5.0 khi đang hoàn thiện lớp sản phẩm V2, trừ khi có lỗi engine được chứng minh bằng test.
- Không mở rộng Hiệp Kỷ hoặc giờ cá nhân trước khi các domain theo lộ trình được hoàn thành.

## Phạm vi PR core-flow-completion

IN SCOPE:
- Trang chủ V2
- Hôm nay V2
- Tháng V2
- Đại vận V2
- Tìm ngày V2
- Result Schema/API cần thiết cho 5 luồng trên
- test chống regression và chống quay lại route V1

OUT OF SCOPE:
- engine Công việc
- engine Tiền bạc
- engine Quan hệ
- giờ tốt/xấu cá nhân
- mở rộng Hiệp Kỷ ngoài phạm vi hiện tại
- thêm thần sát hoặc điểm số
