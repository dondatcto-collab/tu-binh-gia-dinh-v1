# QUYẾT ĐỊNH ĐÃ KHÓA — 0.4.0 / ĐÚNG PHƯƠNG PHÁP TỬ BÌNH

Mục đích: ngăn dự án quay lại vòng lặp bàn lại / xây lại những phần đã chốt.
Chỉ mở một mục LOCKED khi: (1) test chứng minh lỗi; (2) nguồn gốc trực tiếp mâu thuẫn; hoặc (3) chủ dự án yêu cầu đổi.

## A. Sản phẩm và kiến trúc — LOCKED
- Giữ nguyên phạm vi V1, 13 nhóm việc, PWA/local-data, 7 bố cục và hai tầng giải thích.
- Hai hệ độc lập: **Tử Bình cá nhân** và **Hiệp Kỷ theo việc**; hợp lưu ở cuối.
- Dòng thời gian: **Mệnh gốc → Đại vận → Năm → Tháng → Ngày → Giờ**.
- Tầng trên đặt bối cảnh/giới hạn; tầng dưới tối ưu trong phạm vi còn cho phép.
- Không bịa điểm 0–10, không tự đặt trọng số, không để AI thay Engine.

## B. Trường phái Tử Bình cá nhân V1 — LOCKED
Phương pháp lõi: **Tử Bình Chân Thuyên — nguyệt lệnh/cách cục** (`ZPZQ-GEJU-V1`).

Trình tự phương pháp:
1. Tứ Trụ gốc + Nhật chủ + Nguyệt lệnh + Tàng Can + Thập Thần + quan hệ Can/Chi.
2. Xét toàn cục mạnh/yếu như một điều kiện cấu trúc; **không** lấy đắc lệnh/thất lệnh đơn độc làm phán quyết.
3. Lấy Nguyệt lệnh làm đề cương để xác định **Cách cục / Dụng thần của cách**.
4. Xét **thành-bại, cứu-ứng, biến hóa, tương thần** để khóa hỷ/kỵ của mệnh gốc.
5. Sau khi mệnh gốc đã khóa, mới đưa **Đại vận → Năm → Tháng → Ngày → Giờ** vào đối chiếu với hỷ/kỵ đó.
6. Khi người dùng chọn việc, hợp lưu thêm lớp **Hiệp Kỷ theo việc**.

## C. Ý nghĩa các dữ liệu trung gian — LOCKED
- **Thập Thần**: cho biết vai trò/quan hệ của Can đối với Nhật chủ; KHÔNG tự thân là tốt/xấu.
- **Hợp/Xung/Hình/Hại...**: cho biết kiểu tương tác; KHÔNG tự thân là cát/hung.
- **Vượng suy**: là đánh giá cấu trúc quan trọng nhưng KHÔNG được giản hóa thành “thân yếu thì bổ, thân mạnh thì tiết” để tự động chọn Dụng thần cho phương pháp lõi này.
- **Dụng thần** trong lõi 0.4 là dụng thần theo Nguyệt lệnh/Cách cục của Tử Bình Chân Thuyên; không tự đồng nhất với khái niệm “ngũ hành cân bằng” của các hệ hiện đại khác.

## D. Cổng quyết định cá nhân — LOCKED
Cho tới khi Cách cục + hỷ/kỵ mệnh gốc được cài đủ và nghiệm thu:
- `decision_mode = DESCRIPTIVE_ONLY`.
- Thập Thần / Can Chi chỉ được mô tả cấu trúc.
- Không sinh nhãn thuận/nghịch cá nhân.
- Không sinh NÊN/TRÁNH cá nhân.
- Không nâng/hạ ngày Hiệp Kỷ bằng Lục hợp/Lục xung/Thập Thần.
- Giờ chỉ được mô tả quan hệ cấu trúc; không gọi “giờ tốt cá nhân”.

## E. Xử lý phần 0.3.x — LOCKED
Các diễn giải hành động từng được sinh chỉ từ Thập Thần + quan hệ Chi ở 0.3.0/0.3.1:
- **DEPRECATED AS DECISION EFFECT** — không còn quyền ảnh hưởng kết luận.
- Có thể giữ dữ liệu kỹ thuật để giải thích “đang có cấu trúc gì”.
- Không dùng lại làm đường tắt thay Cách cục/hỷ-kỵ.

## F. Hiệp Kỷ — LOCKED
- Hiệp Kỷ là lớp **sự kiện**, không phải lớp mệnh cá nhân.
- 12 Trực hiện là coverage một phần; VERIFIED/PROVISIONAL phải giữ đúng.
- Khi lớp cá nhân chưa sẵn sàng, thứ hạng tìm ngày chỉ được mô tả là **theo Hiệp Kỷ**, không quảng bá là “ngày tốt nhất cho người này”.
- Một ngày thuộc lớp Kỵ sự kiện không được “cứu” chỉ bằng quan hệ cá nhân.

## G. Việc tiếp theo — KHÔNG PHẢI MỞ THÊM KIẾN TRÚC
Chỉ hoàn thiện các rule còn thiếu trong kiến trúc đã chốt, theo thứ tự nguồn:
**Luận dụng thần → thành bại cứu ứng → biến hóa → tương thần/hỷ-kỵ → hành vận → hợp lưu giờ**.

Không tạo thêm “layer” mới chỉ vì câu chữ chưa hay.
