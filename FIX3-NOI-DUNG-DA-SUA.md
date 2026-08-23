# FIX3 — Tối ưu trạng thái Engine và UX

## Hai nội dung đã khóa lại

1. **Lõi tính toán đã chạy/hoàn thiện ở các phần đã xác minh**: lịch pháp, cấu trúc sinh, các tầng thời gian, hợp lưu khung và truy nguồn.
2. **Lớp kết luận/xếp hạng chỉ hiển thị khi đủ căn cứ**: không gọi chung là “Engine chưa hoàn thiện”; không tự tạo điểm, nhãn hay tốt/xấu khi nhóm rule quyết định chưa đủ trạng thái xác minh.

## Sửa UX

- Màn **Tháng này** không còn lẫn dữ liệu/ngôn ngữ của ngày.
- Màn **Hôm nay** bỏ lặp “chưa đánh giá thuận/nghịch” ở từng tầng; chỉ có một trạng thái kết luận chung.
- Tầng gia đình dùng lời thường; thuật ngữ kỹ thuật dồn xuống **Tại sao?/Chuyên sâu**.
- Màn **Tìm ngày** không hiện danh sách Thập Thần như thể bảng xếp hạng; chi tiết kỹ thuật được ẩn trong “Xem chi tiết nghiên cứu”.
- Thay emoji điều hướng bằng SVG đồng nhất.
- Làm lại avatar chi tiết hơn, giữ đúng 6 nhóm đã chốt.
- Viết lại trạng thái hệ thống theo hai lớp: “Lõi tính toán đã chạy” và “Kết luận chỉ hiện khi đủ căn cứ”.
- Tăng cache PWA lên shell-4 để nhận FIX3.
