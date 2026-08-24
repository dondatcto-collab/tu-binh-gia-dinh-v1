# Tử Bình Gia Đình — V1 0.5.0

Ứng dụng gia đình để lưu hồ sơ sinh trên thiết bị, dựng Tứ Trụ, theo dõi Đại vận/Năm/Tháng/Ngày, chọn ngày cho việc quan trọng và truy ngược quy tắc về nguồn.

## Phiên bản hiện tại

- Engine: `0.5.0-zpzq-fusion`
- Ruleset: `RS-2026.08-ZPZQ.2`
- Hồ sơ cá nhân: lưu trên thiết bị (`DEVICE_ONLY`), không lưu hồ sơ sinh trên máy chủ.
- Quyết định: nhãn thứ bậc, **không dùng điểm số 0–10** (`numeric_score = LOCKED_OFF`).

## V1 hiện đã hỗ trợ

- Lịch pháp, tiết khí, Tứ Trụ, Tàng Can, Thập Thần và Nguyệt lệnh.
- Đại vận, năm, tháng và ngày theo hồ sơ cá nhân.
- Bộ chọn Cách cục theo Nguyệt lệnh đã khóa; không dùng thứ tự Tàng Can làm chủ khí ngầm.
- Lớp Hỷ/Kỵ theo Cách cục cho các trường hợp đủ căn cứ.
- Hợp lưu cá nhân với lớp chọn ngày theo sự kiện.
- 12 nhóm việc V1:
  - An táng
  - Cầu tài / thu nhận tiền
  - Cưới hỏi
  - Đàm phán / gặp gỡ
  - Điều trị
  - Động thổ / sửa nhà
  - Khai trương
  - Ký hợp đồng
  - Mua tài sản
  - Nhậm chức / bắt đầu công việc mới
  - Nhập trạch / chuyển nhà
  - Xuất hành
- Truy nguồn Rule / Source / Version ở lớp giải thích chuyên sâu.

## Nguyên tắc quyết định V1

Thứ tự ưu tiên đã khóa:

`HARD_BLOCK > lớp sự kiện > lớp cá nhân`

- Nếu ngày bị `HARD_BLOCK` theo việc đang chọn, tín hiệu cá nhân thuận **không được đảo ngược** kết quả.
- Lớp cá nhân chỉ nâng/hạ ưu tiên khi lớp sự kiện không bị chặn.
- Không trung bình hóa các lớp bằng điểm số.
- Các nhãn chính: `Ưu tiên`, `Có thể cân nhắc`, `Không ưu tiên`, `Bị chặn`.

## Giới hạn phải nói rõ

- Phần Hiệp Kỷ của V1 hiện mới bao phủ **tập 12 Trực đã nghiệm thu cho 12 nhóm việc**, chưa phải toàn bộ hệ quy tắc của *Hiệp Kỷ Biện Phương Thư*.
- Thần sát chưa được dùng để lật quyết định V1.
- Giờ trong ngày hiện là **tham khảo cấu trúc**; chưa được tuyên bố là giờ tốt/xấu cá nhân hoàn chỉnh.
- Trường hợp Cách cục chưa đủ rõ sẽ tự hạ về `DESCRIPTIVE_ONLY`; app không tự lấp phần còn thiếu.
- Test PASS chỉ chứng minh phần mềm thực hiện đúng bộ quy tắc đang cài và đã nghiệm thu; không có nghĩa toàn bộ cổ thư đã được xác minh.

## Production health

Các endpoint kiểm trạng thái:

- `/api/health`
- `/api/tinh-trang`
- `/api/loai-viec`

Production phải có `rule_db=true`, `astronomy=true`, `events=12` trước khi coi là sẵn sàng.

## Kiểm thử

Kiểm thử cục bộ:

```bash
.venv/Scripts/python -m pytest     # Windows
.venv/bin/python -m pytest         # macOS/Linux
```

GitHub Actions chạy full regression khi mở PR. Production còn có live-smoke riêng để gọi trực tiếp các POST chính: Dashboard, Hôm nay, Tháng, Lịch tháng và Tìm ngày.

## Cách chạy trên Windows

1. Cài Python theo phiên bản được khai báo trong `pyproject.toml`.
2. Có Internet ở lần chạy đầu để cài thư viện.
3. Bấm đúp `CAI-DAT-VA-CHAY.bat`.
4. Trình duyệt mở `http://127.0.0.1:8000`.

Script tự tạo `.venv`, cài phụ thuộc và kiểm tra `astronomy-engine`, `pymeeus`, FastAPI trước khi mở app.

## Cách chạy trên macOS/Linux

```bash
./CAI-DAT-VA-CHAY.sh
```

## Dữ liệu hồ sơ và sao lưu

Hồ sơ của PWA production được lưu trên thiết bị. Chức năng Sao lưu / Khôi phục trong giao diện dùng file JSON để chuyển hoặc lưu dữ liệu gia đình.

Bản chạy cục bộ có thể dùng kho SQLite theo cấu hình của ứng dụng; SQLite phía production chỉ chứa rule/source công khai, không chứa hồ sơ sinh người dùng.

## Lưu ý dữ liệu sinh

- Nên nhập đúng ngày và giờ sinh; V1 không tự đoán giờ sinh.
- Hồ sơ sinh tại Việt Nam dùng `Asia/Ho_Chi_Minh` mặc định.
- Nếu sinh ở nước khác, chọn đúng múi giờ nơi sinh trong màn hình Hồ sơ.

## Y tế

Ứng dụng không thay bác sĩ và không dùng để trì hoãn cấp cứu hoặc thay chỉ định chuyên môn.
