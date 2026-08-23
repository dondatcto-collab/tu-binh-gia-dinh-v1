# TỬ BÌNH GIA ĐÌNH V1 — BETA GIA ĐÌNH 0.2.6

## Mục tiêu vòng sửa
Không đổi bố cục đã chốt. Chỉ sửa logic kết luận, cách diễn đạt và kiểm thử Lịch / Tìm ngày / Giờ.

## Các điểm đã sửa

1. Nhãn tầng gia đình
- `Có xung động cần lưu ý` -> `Có điểm cần lưu ý`.
- `Có nhịp hòa hợp` -> `Khá thuận`.
- Trường hợp không thấy quan hệ trực tiếp -> `Chưa có tín hiệu nổi bật`, tránh làm người dùng hiểu là đã xác minh trung tính tuyệt đối.
- Thuật ngữ Lục hợp/Lục xung/Lục hại/Hình vẫn giữ ở tầng Tại sao?/chuyên sâu.

2. Xếp hạng ngày theo việc
- Mức mạnh nhất: `Ưu tiên` chỉ khi Trực thuộc nhóm 宜, quan hệ cá nhân thuận và mapping sự kiện VERIFIED.
- `Phù hợp`: Trực thuộc nhóm 宜 và mapping VERIFIED.
- Mapping PROVISIONAL dù Trực thuận chỉ được `Có thể cân nhắc`.
- `Không ưu tiên`: Trực thuộc nhóm 忌, không bị quan hệ cá nhân đảo ngược.
- Trường hợp không có tín hiệu trực tiếp -> `Chưa có tín hiệu nổi bật`.
- Tang lễ / an táng hiện chưa có `yi_truc` trong lớp V1-basic nên không được tự gắn `Ưu tiên/Phù hợp`.

3. Giờ
- Xác nhận nguyên nhân các ngày thường cùng hiện giờ Hợi: V1 chỉ đang so `Chi ngày sinh ↔ Chi giờ`, không dùng riêng ngày đang chọn.
- Do đó đổi toàn bộ cách trình bày thành `Giờ tham khảo theo hồ sơ`.
- API trả `gio_status=PROFILE_REFERENCE_ONLY` và `scope=PROFILE_BRANCH_RELATION_ONLY`.
- Không còn gọi sai đây là `giờ phù hợp trong ngày` hay `giờ tốt của ngày`.

4. Lịch
- Màu xám đổi chú giải từ `Trung tính` -> `Chưa có tín hiệu`.
- Khi không chọn việc: màu dựa trên quan hệ cá nhân ngày đang xét.
- Khi chọn việc: API gọi `danh_gia_event(..., v.viec)` nên kết quả thực sự đổi theo loại việc.
- Thêm test cùng một ngày nhưng đổi KHAI_TRUONG ↔ CAU_TAI phải cho kết quả khác.

5. Hồ sơ / wording
- `Yếu tố cân bằng`: `Chưa dùng trong kết luận V1`.
- `Xem rule & nguồn` -> `Xem cách tính & nguồn` ở tầng gia đình.
- Tên `An táng / tang sự` -> `Tang lễ / an táng`.

6. Phiên bản/cache
- App/PWA: 0.2.6.
- Service worker cache đồng bộ 0.2.6.
- Rebuild rule seed SQLite từ source hiện tại.

## Kiểm thử
- 19 test logic/deploy trọng tâm: PASS.
- Python compile: PASS.
- JavaScript syntax: PASS.
- TOML/manifest: PASS.
- SQLite integrity_check: ok.
- Hồ sơ trong seed: 0.
- Nhóm việc active: 13/13.
- public/giao_dien JS, HTML và service worker: đồng bộ.

## Giới hạn kiểm thử môi trường
Full Golden/Calendar suite không chạy được trong container hiện tại vì package `astronomy` không được cài. Lỗi đầu tiên của full suite là `No module named 'astronomy'`. Vercel vẫn cài dependency này từ pyproject/requirements khi deploy.

## Trạng thái sản phẩm
Đây là bản beta gia đình để nghiệm thu thực tế. Không tự tạo điểm 0–10. Giờ vẫn là tham khảo theo hồ sơ, chưa phải hợp lưu giờ riêng theo từng ngày.
