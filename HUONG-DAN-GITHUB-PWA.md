# TỬ BÌNH GIA ĐÌNH V1 — GITHUB + PWA

## Kiến trúc đã chốt

- GitHub: lưu mã nguồn, phiên bản và test.
- Render: chạy Python/FastAPI + Engine và cung cấp HTTPS.
- PWA: cùng một đường link dùng trên iPhone, Android và laptop.
- SQLite: phải đặt trên ổ đĩa lưu trữ bền vững của máy chủ.

> GitHub Pages không chạy Python/FastAPI. Không bật Pages cho toàn app này.

## A. Đưa mã nguồn lên GitHub

1. Vào GitHub → **New repository**.
2. Đặt tên ví dụ: `tu-binh-gia-dinh-v1`.
3. Chọn **Private**.
4. Không thêm README/.gitignore khi tạo repo nếu đang dùng gói này.
5. Giải nén gói PWA trên laptop, mở PowerShell trong thư mục đó và chạy:

```powershell
git init
git add .
git commit -m "PWA V1 gia dinh"
git branch -M main
git remote add origin https://github.com/TEN-CUA-BAN/tu-binh-gia-dinh-v1.git
git push -u origin main
```

Nếu GitHub yêu cầu đăng nhập, đăng nhập bằng Git Credential Manager/trình duyệt.

## B. Đưa app lên HTTPS bằng Render

1. Vào Render và đăng nhập.
2. Chọn **New → Web Service**.
3. Kết nối GitHub và chọn repo `tu-binh-gia-dinh-v1`.
4. Render có thể đọc `render.yaml`; nếu nhập tay:
   - Language: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `python -m kich_ban.chay_cloud`
5. Tạo biến bí mật `FAMILY_PIN` = mã PIN chỉ gia đình biết, tối thiểu 6 số/ký tự.
6. Bắt buộc dùng **persistent disk** và mount tại `/var/data`; biến `XEMNGAY_DB_PATH=/var/data/xemngay.sqlite3`.
7. Deploy. Khi xong Render cho URL dạng `https://...onrender.com`.

### Vì sao cần persistent disk?
SQLite chứa hồ sơ gia đình. Hệ thống file mặc định của dịch vụ cloud có thể bị thay thế khi deploy; không có disk thì dữ liệu có thể mất sau một lần triển khai mới.

## C. Cài trên iPhone/iPad

1. Mở URL HTTPS bằng **Safari**.
2. Bấm **Chia sẻ**.
3. Chọn **Thêm vào Màn hình chính**.
4. Bật **Mở dưới dạng ứng dụng web** nếu máy hiển thị lựa chọn này.
5. Bấm **Thêm**.
6. Mở icon **Tử Bình Gia Đình** ngoài màn hình chính.
7. Lần đầu nhập `FAMILY_PIN`.

## D. Cài trên Android

1. Mở URL HTTPS bằng Chrome.
2. Bấm menu **⋮**.
3. Chọn **Cài ứng dụng** hoặc **Thêm vào màn hình chính**.
4. Xác nhận cài.
5. Mở icon **Tử Bình Gia Đình**.
6. Lần đầu nhập `FAMILY_PIN`.

## E. Dùng trên laptop

Mở cùng URL bằng Chrome/Edge. Nếu trình duyệt hiện biểu tượng cài app trên thanh địa chỉ, bấm **Cài đặt** để mở như app riêng.

## F. Cập nhật app sau này

Sau khi sửa code:

```powershell
git add .
git commit -m "Mo ta noi dung cap nhat"
git push
```

Render sẽ tự lấy nhánh GitHub đã liên kết và triển khai bản mới. Không cần cài lại app trên từng điện thoại; PWA tự nhận phần giao diện mới khi mở lại.

## G. Bảo mật tối thiểu

- Repo nên để **Private**.
- Tuyệt đối không commit file `.sqlite3`, bản sao lưu hay `.env`.
- Không viết `FAMILY_PIN` trong source/GitHub. Đặt nó trong Environment/Secret của Render.
- Đổi PIN ngay nếu đã gửi cho người ngoài.
- Sao lưu SQLite định kỳ.

## H. Giới hạn V1 vẫn giữ nguyên

PWA chỉ thay cách phân phối ứng dụng. Nó **không** thay Engine hay mức xác minh. Các phần chưa có đủ rule/source vẫn phải trả “chưa đủ căn cứ”, không tự sinh điểm hay ngày tốt giả.
