# V2.1 — Lĩnh vực Công việc

## Mục tiêu

Tạo kết luận riêng cho lĩnh vực Công việc nhưng vẫn giữ nguyên các nguyên tắc V2:

1. người dùng phổ thông hiểu trước;
2. không đủ căn cứ thì không kết luận;
3. không dùng numeric score;
4. UI không tự suy từ dữ liệu kỹ thuật;
5. mọi kết luận phải truy ngược được;
6. không dùng kết luận Công việc để đảo HARD_BLOCK của lớp chọn ngày.

## Phạm vi V2.1

Hỗ trợ:

- `day` — Công việc hôm nay;
- `month` — Công việc tháng này.

Chưa hỗ trợ:

- năm;
- Đại vận như một kết luận Công việc độc lập;
- Tiền bạc;
- Quan hệ;
- giờ cá nhân.

## Dữ kiện được phép dùng

V2.1 chỉ dùng dữ kiện đã có trong lớp cá nhân 0.5.0:

- Cách cục/Hỷ-Kỵ và trạng thái `READY`;
- hành vận cá nhân `SUPPORT / CAUTION / NEUTRAL / DESCRIPTIVE_ONLY`;
- chủ đề Thập Thần;
- quan hệ Chi như evidence bổ sung;
- rule/source trace đã có sẵn.

Không tạo thêm một hệ suy luận Tử Bình thứ hai.

## Nhóm Thập Thần được phép nối sang Công việc

V2.1 chỉ coi bốn nhóm sau là liên quan trực tiếp đến cách xử lý công việc:

- `AUTHORITY`: trách nhiệm, quy tắc, vị trí công việc;
- `RESOURCE`: học hỏi, hồ sơ, chuẩn bị, nguồn hỗ trợ;
- `OUTPUT`: thực thi, trình bày, tạo đầu ra;
- `PEER`: phối hợp, tự chủ, cạnh tranh nguồn lực.

`WEALTH` không được dùng để tự suy thành kết luận Công việc. Đây là khóa chống lẫn domain trước khi V2.2 Tiền bạc được xây riêng.

## Luật V2-WORK-001

Chỉ sinh kết luận Công việc khi:

1. Cách cục/Hỷ-Kỵ đã ở trạng thái `READY`;
2. lớp cá nhân không phải `DESCRIPTIVE_ONLY`;
3. chủ đề Thập Thần thuộc một trong bốn nhóm Công việc đã cho phép.

Sau đó:

- nền `SUPPORT` → `Hỗ trợ công việc`;
- nền `CAUTION` → `Nên thận trọng trong công việc`;
- nền trung tính → `Công việc tương đối cân bằng`;
- thiếu bất kỳ điều kiện nào → `Chưa đủ căn cứ riêng về công việc`.

Quan hệ Chi không được tự lật trạng thái nền; chỉ là evidence bổ sung.

## Những điều V2.1 tuyệt đối không tuyên bố

Không suy hoặc dự đoán trực tiếp:

- thăng chức;
- tăng lương;
- mất việc;
- chuyển việc chắc chắn;
- mâu thuẫn với sếp/đồng nghiệp chắc chắn;
- thành công hay thất bại nghề nghiệp cụ thể.

Nếu người dùng có một việc cụ thể như ký hợp đồng, nhậm chức, khai trương..., phải chuyển sang luồng `Tìm ngày cho một việc`; lớp Công việc không thay thế lớp sự kiện.

## Nguồn

V2.1 không tuyên bố rằng cổ thư có một chương hiện đại tên “Công việc”. Đây là lớp ánh xạ sản phẩm có kiểm soát từ:

- Thập Thần;
- Cách cục/Hỷ-Kỵ;
- hành vận;
- rule/source trace đã được hệ thống lưu và truy ngược.

Rule `V2-WORK-001` là **product interpretation policy**, không phải quy tắc cổ thư mới.

## Trình tự phát triển sau V2.1

Chỉ sau khi V2.1 PASS production mới mở:

1. V2.2 Tiền bạc;
2. V2.3 Quan hệ;
3. V2.4 Giờ cá nhân;
4. V2.5 Hiệp Kỷ mở rộng.
