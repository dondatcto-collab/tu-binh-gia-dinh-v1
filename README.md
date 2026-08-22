# Tử Bình Gia Đình - V1 (bản đã rà soát)

Ứng dụng gia đình để lưu hồ sơ sinh, dựng Tứ Trụ, xem Đại vận/Năm/Tháng/Ngày và truy ngược quy tắc về nguồn.

## Trạng thái thật của V1

**Đã chạy được:** hồ sơ gia đình, lịch pháp, Tứ Trụ, Tàng Can, Thập Thần, Nguyệt lệnh, dòng thời gian, xem cấu trúc một ngày, truy nguồn.

**Chưa được phép kết luận:** vượng suy, cách cục, Dụng/Hỷ/Kỵ, chấm điểm tốt-xấu, xếp hạng ngày theo việc, chọn giờ tốt cá nhân, Hiệp Kỷ và Thần sát. Các phần này chưa đủ Rule/Source nên app cố ý hiển thị `chưa đủ căn cứ`.

> Test PASS chỉ chứng minh phần mềm làm đúng các quy tắc đang có; không có nghĩa mọi quy tắc cổ thư đã được xác minh.

## Cách chạy trên Windows

1. Cài **Python 3.11 trở lên** từ python.org và tick **Add Python to PATH**.
2. Có Internet ở lần chạy đầu để cài thư viện.
3. Bấm đúp `CAI-DAT-VA-CHAY.bat`.
4. Trình duyệt mở `http://127.0.0.1:8000`.

Script tự tạo `.venv` riêng, cài đúng phụ thuộc và kiểm tra `astronomy-engine`, `pymeeus`, FastAPI trước khi mở app.

## Cách chạy trên macOS/Linux

```bash
./CAI-DAT-VA-CHAY.sh
```

## Sao lưu dữ liệu

```bash
.venv/Scripts/python -m kich_ban.sao_luu luu sao-luu   # Windows
.venv/bin/python -m kich_ban.sao_luu luu sao-luu       # macOS/Linux
```

File dữ liệu chính: `du_lieu/kho/xemngay.sqlite3`.

## Kiểm thử

```bash
.venv/Scripts/python -m pytest     # Windows
.venv/bin/python -m pytest         # macOS/Linux
```

## Lưu ý dữ liệu sinh

- Nên nhập đúng ngày/giờ sinh; V1 không tự đoán giờ sinh.
- Hồ sơ sinh tại Việt Nam dùng `Asia/Ho_Chi_Minh` mặc định.
- Nếu sinh ở nước khác, chọn đúng múi giờ nơi sinh trong màn hình Hồ sơ.

## Y tế

Ứng dụng không thay bác sĩ và không dùng để trì hoãn cấp cứu hoặc thay chỉ định chuyên môn.
