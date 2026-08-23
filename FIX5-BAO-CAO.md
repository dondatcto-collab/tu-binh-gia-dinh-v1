# FIX5 — ỔN ĐỊNH BETA GIA ĐÌNH

## Mục tiêu
Đưa V1 từ bản thử kỹ thuật sang beta gia đình ổn định, không mở rộng phạm vi sản phẩm.

## Đã sửa
1. Cache PWA version hóa `0.2.2`; API luôn `no-store`; service worker mới xóa cache cũ và nhận bản mới.
2. Client API timeout 25 giây, retry một lần cho lỗi mạng/5xx; lỗi có thông báo cụ thể và mã tham chiếu khi server gặp exception.
3. API có exception handler thống nhất; không còn UI chỉ nói `Không thể thực hiện.`.
4. Vercel copy DB rule seed theo phiên bản sang `/tmp` và KHÔNG migration/seed ở mỗi cold start; giảm ghi SQLite và rủi ro cold-start.
5. SQLite có `busy_timeout=15000`.
6. IndexedDB lên schema 2; hồ sơ cũ được normalize khi tải. Payload gửi API chỉ chứa các trường schema chuẩn.
7. Lịch mobile dùng 7 cột `minmax(0,1fr)`; trên màn nhỏ chỉ hiện số ngày + chấm trạng thái, chi tiết mở khi chạm.
8. Mốc Đại vận PROVISIONAL chuyển xuống tầng chi tiết. Tầng gia đình chỉ nói mốc dự kiến có thể lệch vài tháng.
9. Hồ sơ đổi `Dụng / Hỷ / Kỵ` ở tầng thường thành `Yếu tố cân bằng cá nhân — đang hoàn thiện ở tầng chuyên sâu`.
10. Có nút `Thử lại` ở kết quả, lịch, hồ sơ và tìm ngày khi mạng/server tạm lỗi.
11. Cài đặt hiển thị version và trạng thái kết nối Engine.

## Không thay đổi
- Không tạo điểm 0–10 giả.
- Không tự suy Dụng/Hỷ/Kỵ khi chưa đủ nguồn.
- Giữ 13 nhóm việc V1 và lớp quyết định V1-basic.
- Hồ sơ cá nhân chỉ lưu trên thiết bị; server không lưu hồ sơ.

## Kiểm thử trong môi trường hiện tại
- `test_quyet_dinh_v1 + test_co_so_du_lieu + test_kho_quy_tac`: 38 PASS.
- Python compile: PASS.
- JavaScript syntax: PASS.
- TOML version: PASS (`0.2.2`).
- Event types active/non-deprecated trong seed: 13.
- Bảng `profiles` trong seed: 0 bản ghi.
- Kiểm tra chuỗi lỗi mơ hồ `Không thể thực hiện.` trong client: không còn.
- Full E2E/Calendar chưa chạy được trong container này vì thiếu package `astronomy`; dependency vẫn có trong `pyproject.toml` và `requirements.txt` để Vercel cài khi build.

## Nghiệm thu sau deploy Vercel
1. `/api/health` trả `ok=true`.
2. Hồ sơ cũ mở được; nếu schema cũ, app tự normalize.
3. Vận dài hạn mở 5 lần liên tiếp không lỗi.
4. Hôm nay/Tháng này mở 5 lần liên tiếp không lỗi.
5. Tìm ngày quét 14 ngày cho ít nhất 3 loại việc.
6. Lịch trên Android/iPhone hiển thị đủ 7 cột không tràn ngang.
7. Đổi 5 theme và reload vẫn giữ theme.
8. Xuất backup → xóa local → khôi phục backup thành công.
