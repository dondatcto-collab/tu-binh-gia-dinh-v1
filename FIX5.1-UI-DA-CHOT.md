# FIX5.1 UI — BỐ CỤC ĐÃ CHỐT

Phiên bản giao diện: 0.2.4

## 7 bố cục chính thức
1. Trang chủ — Bố cục B
2. Hôm nay thế nào? — Bố cục A
3. Tháng này của tôi — Bố cục B
4. Lịch — Bố cục B
5. Tìm ngày cho một việc — Bố cục B
6. Hồ sơ — Bố cục A
7. Cài đặt — Bố cục A

## Nguyên tắc giữ nguyên
- Không thay Engine bằng thiết kế.
- Không sinh điểm 0–10 giả khi scoring chưa hiệu chỉnh.
- Kết quả V1-basic dùng nhãn thứ bậc và lý do có truy nguồn.
- Hồ sơ vẫn lưu cục bộ trên từng thiết bị.
- FIX5.1 sửa lỗi rule seed Vercel vẫn được giữ nguyên.
- 5 phong cách hiển thị tiếp tục hoạt động.

## Kiểm tra trước đóng gói
- JavaScript syntax: PASS
- Python compile: PASS
- pyproject TOML: PASS
- deploy + quyết định + kho quy tắc: 33 test PASS
- cache PWA: 0.2.4
