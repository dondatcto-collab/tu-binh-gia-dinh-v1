# 0.3.0 — PERSONAL BAZI DECISION ENGINE V1.1

## Mục tiêu
Tăng giá trị thực tế của app mà không đổi UI và không bịa Dụng/Hỷ/Kỵ hay điểm số.

## Thay đổi chính
- Tháng/Hôm nay dùng Thập Thần của Can hiện tại, không chỉ quan hệ một Chi.
- Chi hiện tại được đối chiếu với cả bốn trụ Năm/Tháng/Ngày/Giờ của Mệnh gốc.
- Bối cảnh Đại vận → Năm → Tháng được đưa vào phần "Điểm tạo khác biệt".
- Mỗi kết quả sinh bốn phân tích riêng: Công việc, Tài chính, Quan hệ, Việc lớn.
- Tìm ngày giữ Hiệp Kỷ là lớp chính nhưng kiểm tra va chạm/hòa hợp với cả bốn trụ.
- Một ngày Hiệp Kỷ thuận nhưng va chạm cá nhân sẽ hạ thành "Phù hợp nhưng cần cân nhắc cá nhân".
- Ngày thuộc lớp Kỵ không thể được tín hiệu cá nhân cứu ngược.

## Ví dụ cấu trúc với hồ sơ Mậu Thìn – Quý Hợi – Mậu Dần – Bính Thìn
Tháng Bính Thân:
- Can Bính đối với Nhật chủ Mậu = Thiên Ấn.
- Chi Thân xung Dần ở trụ ngày.
- Chi Thân hại Hợi ở trụ tháng.
=> Engine phải mô tả đồng thời chủ đề học hỏi/hỗ trợ/thông tin và hai điểm va chạm cấu trúc, thay vì chỉ nói chung "cần lưu ý".

Ngày Kỷ Tị:
- Can Kỷ đối với Nhật chủ Mậu = Kiếp Tài.
- Tị xung Hợi và có quan hệ trực tiếp với Dần.
=> Kết luận phải khác tháng Bính Thân và khác người có cấu trúc gốc khác.

## Giới hạn được giữ
- Không điểm 0–10.
- Không tự kết luận tài lộc tuyệt đối.
- Không sức khỏe dự báo.
- Không Dụng/Hỷ/Kỵ giả.
- Diễn giải lĩnh vực là PRODUCT_INTERPRETATION và giữ technical facts để truy nguồn.
