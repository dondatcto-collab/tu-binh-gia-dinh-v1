# TỬ BÌNH GIA ĐÌNH V1 — CHUYỂN SANG VERCEL

## Kiến trúc đã khóa

GitHub Private → Vercel Hobby → 1 link PWA.

- Hồ sơ: IndexedDB trên từng thiết bị.
- Giao diện/cài đặt: trên từng thiết bị.
- Sao lưu: file JSON do người dùng chủ động xuất/khôi phục.
- FastAPI: chỉ tính toán, không lưu hồ sơ.
- SQLite phía Vercel: chỉ chứa rule/source/seed công khai.

## Tại màn hình Configure Project hiện tại

1. Application Preset: **FastAPI**.
2. Root Directory: `./`.
3. Build and Output Settings: để mặc định.
4. Environment Variables: **để trống**.
5. Chưa bấm Deploy cho đến khi commit mới đã có trên GitHub.

## Cập nhật GitHub

Giải nén gói Vercel mới và chép toàn bộ nội dung vào thư mục repo `tu-binh-gia-dinh-v1` trên laptop, cho phép ghi đè file cũ nhưng giữ nguyên thư mục `.git` của repo.

Mở PowerShell tại repo và chạy:

```powershell
git add -A
git commit -m "Chuyen V1 sang Vercel PWA local-data stateless"
git push origin main
```

Hoặc chạy `CAP-NHAT-GITHUB-VERCEL.ps1`.

## Deploy

Quay lại Vercel → bấm **Deploy**.

Sau khi thành công kiểm tra lần lượt:

- `/` mở được giao diện.
- `/api/health` trả `ok: true` và `profile_storage: DEVICE_ONLY`.
- Tạo một hồ sơ thử trên điện thoại.
- Reload app: hồ sơ vẫn còn.
- Mở cùng link trên máy khác: hồ sơ không tự xuất hiện.
- Cài PWA lên màn hình chính.
- Cài đặt → Xuất bản sao lưu → tạo file `.json`.
- Cài đặt → Khôi phục → chọn file đó và xác nhận.

## Cài lên iPhone

Safari → mở link Vercel → Chia sẻ → Thêm vào Màn hình chính → Mở dưới dạng ứng dụng web (nếu hiện) → Thêm.

## Cài lên Android

Chrome → mở link → menu ⋮ → Cài ứng dụng / Thêm vào màn hình chính.

## Laptop

Mở cùng link bằng Chrome/Edge. Có thể dùng trực tiếp hoặc chọn Cài ứng dụng.

## Lưu ý sao lưu

Dữ liệu cục bộ có thể mất nếu người dùng xóa dữ liệu trình duyệt, reset máy hoặc xóa dữ liệu website. Nên sao lưu sau khi sửa hồ sơ và ít nhất mỗi 30 ngày.

Không đưa file backup lên GitHub vì có dữ liệu sinh của gia đình.
