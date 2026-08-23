# TỬ BÌNH GIA ĐÌNH 0.3.0 — PERSONAL BAZI DECISION ENGINE V1.1

## Mục tiêu của vòng này
Không đổi bố cục/UI. Tăng giá trị thật của kết luận và khóa các quyết định cũ để tránh lặp.

## Đã thay đổi
### 1. Tháng/Hôm nay
Trước 0.3.0: chủ yếu so một Chi hiện tại với Chi ngày sinh.

Từ 0.3.0:
- tính Thập Thần của Can đang xét đối với Nhật chủ;
- so Chi đang xét với cả 4 trụ gốc Năm/Tháng/Ngày/Giờ;
- ghi nhận đồng thời nhiều quan hệ nếu có;
- đưa bối cảnh Đại vận → Năm → Tháng → Ngày vào diễn giải;
- sinh 4 kết luận riêng: Công việc, Tài chính, Quan hệ, Việc lớn;
- giữ technical facts để tầng chuyên sâu truy nguồn.

### 2. Đại vận và Năm
Đại vận/Năm không còn chỉ là nhãn bối cảnh. Mỗi tầng có `danh_gia` riêng từ cùng Personal Engine.

### 3. Lịch
Lịch tháng dùng Personal Engine cho từng ngày:
- chủ đề Thập Thần của Can ngày;
- quan hệ Chi ngày với cả bốn trụ gốc;
- nếu chọn việc, kết hợp thêm Hiệp Kỷ.

### 4. Tìm ngày
Hiệp Kỷ vẫn là lớp quyết định sự kiện chính.
- Ngày thuộc Kỵ: cá nhân không được cứu ngược.
- Ngày thuộc 宜 nhưng có va chạm với một/nhiều trụ gốc: hạ thành “Phù hợp nhưng cần cân nhắc cá nhân”.
- Quan hệ phối hợp cá nhân chỉ dùng phá hòa trong cùng lớp, không biến ngày sự kiện trung tính thành “đại cát”.
- Top ngày có thêm chủ đề Thập Thần và các tương tác toàn 4 trụ để giải thích.

## Ví dụ kiểm tra cấu trúc
Với Mậu Thìn – Quý Hợi – Mậu Dần – Bính Thìn:
- Tháng Bính Thân: Bính = Thiên Ấn đối với Mậu; Thân xung Dần và hại Hợi.
- Ngày Kỷ Tị: Kỷ = Kiếp Tài; Tị xung Hợi và có quan hệ trực tiếp với Dần.
Hai thời điểm phải tạo kết luận khác nhau, không thể dùng cùng một lời khuyên mẫu.

## Những gì KHÔNG làm
- Không tự suy Vượng suy.
- Không tự chốt Cách cục.
- Không bịa Dụng/Hỷ/Kỵ.
- Không tạo điểm 0–10.
- Không coi diễn giải sản phẩm là nguyên văn cổ thư.

## Trạng thái diễn giải
`PRODUCT_INTERPRETATION_V1_1`

Cấu trúc tính toán Thập Thần/quan hệ Địa Chi có rule/source riêng. Việc dịch các tín hiệu đó thành ngôn ngữ Công việc/Tài chính/Quan hệ/Việc lớn là lớp ứng dụng sản phẩm và được đánh dấu riêng.

## Kiểm thử đã chạy
- 34 test trọng tâm Personal Engine / quyết định / deploy: PASS.
- Python compile toàn bộ `loi`, `cong`, `api`, `kich_ban`: PASS.
- JavaScript giao diện + public: PASS.
- SQLite integrity: OK.
- seed: 0 hồ sơ cá nhân; 13 event types; 68 rules/versions.
- version/cache PWA: 0.3.0 đồng bộ.

Bộ test Thập Thần rất lớn đã chạy qua phần lớn case không thấy fail nhưng vượt giới hạn thời gian của một lượt chạy trong môi trường này. Golden/Calendar phụ thuộc `astronomy` vẫn cần chạy lại ở môi trường có dependency đầy đủ/Vercel.

## File khóa quyết định
Xem `tai_lieu/QUYET-DINH-DA-KHOA-0.3.0.md`.
Các mục LOCKED không được mở lại nếu không có test lỗi hoặc yêu cầu đổi trực tiếp từ chủ dự án.

## Backlog tiếp theo — không làm lại phần đã xong
1. Vượng suy có nguồn đủ chắc.
2. Cách cục.
3. Dụng/Hỷ/Kỵ.
4. Hiệp Kỷ đầy đủ ngoài 12 Trực.
5. Giờ hợp lưu thật theo ngày + việc + cá nhân.
6. Scoring sau khi có ca vàng để hiệu chỉnh.
