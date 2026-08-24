> **SUPERSEDED VỀ PHƯƠNG PHÁP CÁ NHÂN:** từ 0.4.0, xem `QUYET-DINH-DA-KHOA-0.4.0.md`. Các quyết định sản phẩm/UI vẫn kế thừa; mọi hiệu lực quyết định dựa riêng trên Thập Thần + quan hệ Chi của 0.3.x đã bị vô hiệu hóa.

# QUYẾT ĐỊNH ĐÃ KHÓA — TỬ BÌNH GIA ĐÌNH V1 / 0.3.0

Tệp này ngăn dự án quay lại bàn hoặc sửa lặp các nội dung đã chốt.
Chỉ mở lại một mục LOCKED khi: (1) test chứng minh có lỗi; hoặc (2) chủ dự án yêu cầu đổi.

## 1. Sản phẩm — LOCKED
- Mục tiêu V1: người nhà không biết Tử Bình vẫn hiểu giai đoạn hiện tại, hôm nay, tháng này và chọn ngày cho một việc.
- Một màn hình = một câu hỏi.
- 13 nhóm việc V1 đã khóa; không mở rộng trước khi nghiệm thu V1.
- Không thêm Tử Vi/Kỳ Môn/phong thủy/nhân tướng/chatbot/cộng đồng vào V1.

## 2. Triển khai & dữ liệu — LOCKED
- Một link PWA dùng Android/iOS/laptop.
- Hồ sơ lưu cục bộ trên thiết bị; server không lưu hồ sơ gia đình.
- Có xuất/khôi phục bản sao dữ liệu.
- Vercel/FastAPI chỉ tính toán và trả kết quả.

## 3. Giao diện — LOCKED
1. Trang chủ: bố cục B.
2. Hôm nay thế nào?: bố cục A.
3. Tháng này của tôi: bố cục B.
4. Lịch: bố cục B.
5. Tìm ngày cho một việc: bố cục B.
6. Hồ sơ: bố cục A.
7. Cài đặt: bố cục A.
- 5 phong cách hiển thị giữ nguyên.
- Không đổi bố cục trừ khi có lỗi usability thật.

## 4. Nguyên tắc Engine — LOCKED
- Không bịa điểm 0–10.
- Không tự đặt trọng số.
- Không tự suy Vượng suy/Cách cục/Dụng-Hỷ-Kỵ khi chưa đủ nguồn/rule.
- UNKNOWN/PROVISIONAL/CONFLICTED phải được giữ đúng trạng thái.
- Hiệp Kỷ theo việc là lớp sự kiện chính; quan hệ cá nhân không được cứu một ngày nằm trong lớp Kỵ.
- Result → Rule → Version → Source → Passage → Verification status.

## 5. Personal Bazi Decision Engine V1.1 — ACTIVE
Từ 0.3.0, kết luận tháng/ngày không còn chỉ so Chi ngày sinh.
Engine hợp lưu:
- Thập Thần của Can đang xét so với Nhật chủ;
- quan hệ Chi đang xét với CẢ BỐN trụ gốc;
- bối cảnh Đại vận → Năm → Tháng → Ngày;
- 4 lĩnh vực: Công việc / Tài chính / Quan hệ / Việc lớn;
- Tìm ngày: Hiệp Kỷ + quan hệ cá nhân toàn 4 trụ.

Diễn giải lĩnh vực là PRODUCT_INTERPRETATION, không giả làm nguyên văn cổ thư.

## 6. Chưa khóa / backlog có chủ đích
- Vượng suy.
- Cách cục.
- Dụng/Hỷ/Kỵ.
- Hợp/xung/hình/hại/phá nâng cao ngoài lớp hiện có.
- Hiệp Kỷ đầy đủ các cát/hung thần ngoài 12 Trực.
- Giờ đã hợp lưu riêng với ngày và việc.
- Scoring 0–10 đã hiệu chỉnh.

Các mục này KHÔNG được biến thành blocker cho việc dùng V1 hiện tại; nhưng cũng KHÔNG được giả lập như đã hoàn thành.
