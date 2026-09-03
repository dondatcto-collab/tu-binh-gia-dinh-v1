# UI V1.2 — TRUST FIRST PROTOTYPE

## Mục tiêu
Biến kết quả kỹ thuật thành nội dung người dùng có thể hiểu, so sánh và kiểm chứng.

## Luồng chuẩn
1. Nêu rõ đang xem cho ai, việc gì, khoảng ngày nào.
2. Hiển thị lựa chọn #1 trước với lý do ngắn.
3. Hiển thị tín hiệu hỗ trợ/cần tránh bằng ngôn ngữ người dùng.
4. Nêu riêng lớp cá nhân; nếu chưa đủ căn cứ phải nói thẳng.
5. So sánh trực tiếp Top 3 bằng các khác biệt thực tế có trong payload.
6. Chi tiết ngày chia thành Tổng quan · Riêng với tôi · Giờ · Căn cứ.
7. Căn cứ hiển thị trạng thái xác minh và vị trí nguồn trước; Rule ID/Source ID để trong phần kỹ thuật.

## Nguyên tắc khóa
- Không thay engine 43-rule.
- Không tự tính lại ranking.
- Không dùng số lượng tín hiệu như công thức điểm.
- HARD_BLOCK > EVENT > PERSONAL giữ nguyên.
- Numeric score không hiển thị.
- Giờ chỉ gọi là “Giờ tham khảo có căn cứ hiện tại”, chưa gọi là giờ tốt/xấu cá nhân hoàn chỉnh.
- Không giả vờ cá nhân hóa khi engine chưa trả dữ liệu đủ rõ.

## Tiêu chí nghiệm thu prototype
- Người dùng trả lời được: ngày nào nên chọn, vì sao, vì sao hơn ngày kế tiếp, riêng với mình ra sao, nguồn nào hỗ trợ kết luận.
- Màn chính không trở thành bức tường chữ.
- Nội dung nguồn/kỹ thuật vẫn truy vết được nhưng không chiếm màn chính.
- Source và public renderer phải giống hệt nhau.

Preview này chỉ dùng để nghiệm thu UX; chưa được phép merge production trước phản hồi người dùng.
