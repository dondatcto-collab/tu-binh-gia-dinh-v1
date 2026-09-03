# UI V1.2.2 — Home Decision

Mục tiêu: Trang chủ để nắm nhanh, không phải đọc báo cáo.

## Thay đổi
- Giữ nguyên engine và API.
- Giữ các module Công việc / Tiền bạc / Quan hệ để mở chi tiết.
- Ẩn ba card dài của các module này trên Trang chủ.
- Gom thành một bảng `HÔM NAY THEO TỪNG LĨNH VỰC` gồm 3 dòng: Công việc, Tiền bạc, Quan hệ.
- Mỗi dòng chỉ hiển thị kết luận ngắn + mức căn cứ; bấm mới mở màn chi tiết cũ.
- Không tính điểm, không suy lại kết luận, không đổi decision hierarchy.
- PWA cache: `tubinh-ui-v3.2.2-home-decision`.

## Gate
- Source/public mirror.
- Bootstrap nạp home overlay cuối cùng.
- Regression test xác nhận overlay không gọi API và không có numeric score.
