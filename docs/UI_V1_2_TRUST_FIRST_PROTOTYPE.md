# UI V1.2.1 — TRUST FIRST

## Mục tiêu
Biến kết quả kỹ thuật thành nội dung người dùng có thể hiểu, so sánh và kiểm chứng mà không tạo cảm giác đang cộng điểm các sao.

## Luồng chuẩn
1. Nêu rõ đang xem cho ai, việc gì, khoảng ngày nào.
2. Hiển thị lựa chọn đầu tiên bằng ngày thân thiện và lý do theo đúng việc đang chọn.
3. Dịch tên quy tắc sang ý nghĩa hành động trước; tên cổ và kỹ thuật để người dùng kiểm sau.
4. Nêu riêng lớp cá nhân bằng ngôn ngữ dễ hiểu; thuật ngữ Tử Bình nằm trong phần mở rộng.
5. Top 3 chỉ hiển thị từng căn cứ chính; không dùng +n/-n và không suy diễn rằng nhiều sao hơn là tốt hơn.
6. Toàn bộ ngày được gom thành: Nên xem trước · Có thể cân nhắc · Không ưu tiên · Bị chặn.
7. Chi tiết ngày chia thành Kết luận · Cá nhân · Giờ · Căn cứ.
8. Căn cứ hiển thị trạng thái xác minh và vị trí nguồn trước; Rule ID/Source ID để trong phần kỹ thuật.

## Nguyên tắc khóa
- Không thay engine 43-rule.
- Không tự tính lại ranking.
- Không dùng số lượng tín hiệu như công thức điểm.
- HARD_BLOCK > EVENT > PERSONAL giữ nguyên.
- Numeric score không hiển thị.
- Giờ chỉ gọi là “Giờ tham khảo có căn cứ hiện tại”.
- Không giả vờ cá nhân hóa khi engine chưa trả dữ liệu đủ rõ.

## Tiêu chí nghiệm thu
- Hiện đúng tên hồ sơ đang chọn.
- Người dùng hiểu ngay ngày nào nên xem trước và căn cứ nổi bật là gì.
- Không còn nghịch lý thị giác kiểu “+3 hỗ trợ” đứng dưới “+1 hỗ trợ”.
- Danh sách dài được gom theo trạng thái để quét nhanh trên điện thoại.
- Lớp cá nhân nói ngôn ngữ đời thường trước, thuật ngữ Tử Bình sau.
- Source/public renderer và service worker phải giống hệt nhau.

Preview này chỉ dùng để nghiệm thu UX; chưa được phép merge production trước phản hồi người dùng.
