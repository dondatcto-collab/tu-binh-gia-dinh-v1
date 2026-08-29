# V3.0D — Hiệp Kỷ: kích hoạt 時徳 (Thời Đức)

## Mục tiêu
Cân bằng hệ thống sau các rule cảnh báo bằng một cát thần có công thức trực tiếp, không mở UI và không dùng numeric score.

## Nguồn
《欽定協紀辨方書》卷五 ghi Thời Đức theo bốn mùa: **春午、夏辰、秋子、冬寅**. Quyển 11 liệt kê 時徳 trong nhóm 宜 của nhiều loại việc hiện hành như động thổ, nhập trạch, xuất hành, điều trị, đàm phán, nhậm chức, cầu tài.

## Calculator
Ánh xạ Chi tháng theo mùa sang Chi ngày:
- Xuân: Dần/Mão/Thìn → Ngọ
- Hạ: Tỵ/Ngọ/Mùi → Thìn
- Thu: Thân/Dậu/Tuất → Tý
- Đông: Hợi/Tý/Sửu → Dần

Calculator dùng chính Chi tháng và Chi ngày đã có; không cần mở input mới.

## Chính sách
- Chỉ có hiệu lực khi inventory của sự kiện ghi 時徳 trong 宜.
- Là tín hiệu FAVORABLE hỗ trợ.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có JI, JI thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không cộng/trừ điểm.

## Conflict test khóa
Tháng Thìn + ngày Ngọ đồng thời có 時徳 và 災煞. Với Xuất hành, cả hai đều có trong inventory; kết luận phải là CAUTION / Không ưu tiên, không HARD_BLOCK.

## Giới hạn
Thiên Đức chưa kích hoạt vì có tháng dùng quẻ phương vị; Nguyệt Đức, Nguyệt Ân, Tứ Tướng cần lớp Can ngày riêng và sẽ được xử lý ở giai đoạn sau.
