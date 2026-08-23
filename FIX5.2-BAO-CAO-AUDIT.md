# FIX5.2 — BÁO CÁO AUDIT ỔN ĐỊNH

## Lỗi gốc đã tìm thấy

Calendar Engine dùng mã Địa Chi chuẩn nội bộ:
`TY, SUU, DAN, MAO, THIN, TI, NGO, MUI, THAN, DAU, TUAT, HOI`.

Lớp quyết định V1 mới lại dùng:
`ZI, CHOU, YIN, MAO, CHEN, SI, WU, WEI, SHEN, YOU, XU, HAI`.

Khi dữ liệu thật đi từ Engine sang lớp quyết định, `quan_he_chi()` truy `CHI_VI['DAN']`
trong bảng chỉ có `YIN` và phát sinh `KeyError`. FastAPI bắt lỗi và trả HTTP 500,
đúng với hiện tượng Trang chủ/Lịch báo lỗi trên Vercel.

## Sửa chính

1. Thống nhất lớp quyết định dùng mã Địa Chi native của Calendar Engine.
2. Giữ alias pinyin cũ để không gãy test/dữ liệu thử nghiệm cũ.
3. Thêm regression test quét toàn bộ 12×12 quan hệ native và 13 loại việc × 12 Chi.
4. Tối ưu định vị tiết khí: từ 72 phép dò thiên văn cho một lần định vị xuống tối đa
   10 ứng viên gần nhất, có fallback toàn bộ nếu thiếu mốc; thêm cache dùng chung worker.
5. Trang chủ dùng một endpoint `/api/stateless/dashboard` thay vì ba request riêng.
6. Lịch tháng và Tìm ngày dùng đường tính nhẹ, không dựng lại toàn bộ lá số 31–93 lần.
7. Vercel rule DB được copy atomic mỗi worker; không còn nhận phiên bản DB bằng file size.
8. `/api/health` kiểm cả rule DB, 13 nhóm việc và dependency astronomy.
9. HTTP 500 trả thêm `error_stage` để phân biệt dependency / rule DB / thiên văn / mã dữ liệu / runtime.
10. PWA nâng 0.2.5, cache mới ép loại cache giao diện cũ.
11. Cập nhật test cũ còn khóa phạm vi trước FIX4/FIX5: 13 nhóm việc, BT-REL, HK-EVENT và FUS hiện là phạm vi hợp lệ.
12. Seed DB kiểm `integrity_check=ok`, `profiles=0`, `events=13`, chuyển journal về DELETE trước đóng gói.

## Kiểm tra đã chạy

- Python compile: PASS cho toàn bộ 80 file Python.
- JavaScript syntax: PASS cho `public/static/app.js` và `giao_dien/app.js`.
- TOML/manifest: PASS.
- Rule DB integrity: PASS; không chứa hồ sơ cá nhân.
- Bộ test quyết định + deploy + hiệu năng mới: PASS.
- Bộ test dữ liệu/kho quy tắc/phạm vi V1 hiện tại: PASS.
- Smoke API giả lập Vercel: PASS HTTP 200 cho:
  - `/api/stateless/dashboard`
  - `/api/stateless/lich-thang`
  - `/api/stateless/tim-ngay`
  - `/api/stateless/toi-dang-o-dau`
  - `/api/health`

## Giới hạn kiểm thử môi trường hiện tại

Container hiện không có package `astronomy-engine` và không có internet để cài.
Do đó các Golden test thiên văn tuyệt đối không thể chạy bằng nền thật tại đây.
Gói Vercel vẫn khai báo `astronomy-engine>=2.1`; smoke runtime được chạy bằng nền giả lập
chỉ để kiểm đường API/cấu trúc/mã dữ liệu, không dùng để xác nhận thời điểm tiết khí.
