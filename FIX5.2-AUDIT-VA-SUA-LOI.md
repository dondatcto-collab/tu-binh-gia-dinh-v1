# FIX5.2 — AUDIT ỔN ĐỊNH

- Sửa lỗi liên tầng Địa Chi: Calendar dùng TY/SUU/DAN..., lớp quyết định dùng ZI/CHOU/YIN... gây HTTP 500.
- Thống nhất mã native, vẫn tương thích pinyin cũ.
- Giảm tính tiết khí từ 72 phép dò/lần định vị xuống tối đa 10 ứng viên, có fallback toàn bộ; thêm cache dùng chung worker.
- Trang chủ dùng một endpoint dashboard thay vì 3 request rời.
- Lịch tháng/Tìm ngày dùng đường tính nhẹ, không dựng toàn bộ lá số 31–93 lần.
- DB Vercel copy atomic mỗi worker, không nhận diện phiên bản bằng file size.
- Health check kiểm DB rule + astronomy.
- Lỗi 500 có error_stage để truy đúng lớp lỗi.
- Cập nhật regression test cũ sang phạm vi V1-basic hiện tại.
- Version PWA 0.2.5; Engine 0.2.5-fix52-stable.
