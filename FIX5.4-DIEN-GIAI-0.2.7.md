# TỬ BÌNH GIA ĐÌNH V1 — 0.2.7 DIỄN GIẢI CỤ THỂ

## Mục tiêu
Sửa nhược điểm của 0.2.6: kết luận đúng nhưng quá chung chung, người dùng đọc xong không biết tháng/ngày này khác thời điểm khác ở đâu.

## Thay đổi chính
- Giữ nguyên bố cục đã chốt.
- Mỗi nhịp Tháng/Ngày trả thêm 4 vùng diễn giải: Công việc, Tài chính, Quan hệ, Việc lớn.
- Thêm `headline`, `trigger`, `focus`, `khong_suy_dien`.
- Phân biệt rõ:
  - quan hệ cấu trúc có nguồn (`VERIFIED_BRANCH_RELATION_ONLY`);
  - diễn giải ứng dụng của sản phẩm (`PRODUCT_INTERPRETATION`).
- Tầng gia đình không buộc hiểu Lục hợp/Lục xung/Lục hại/Hình; thuật ngữ và mô tả kỹ thuật vẫn ở tầng chuyên sâu.
- Không dùng quan hệ Địa Chi một mình để suy ra tài lộc, sức khỏe hay thành bại việc lớn.

## Ví dụ với cấu trúc ngày sinh Dần gặp tháng Thân
- Tổng quan: Tháng có nhịp thay đổi và va chạm trực tiếp.
- Công việc: dễ đổi lịch/đổi cách làm/việc chen ngang; nên có phương án B.
- Tài chính: không tự suy ra hao tài; khoản lớn cần kiểm tra điều kiện và dòng tiền.
- Quan hệ: dễ khó đồng bộ quan điểm; xử lý từng việc cụ thể.
- Việc lớn: không mặc định phải hoãn; nếu làm, cần phương án dự phòng và chọn ngày theo đúng loại việc.

## Kiểm thử
- `test_quyet_dinh_v1.py` + `test_dien_giai_v1.py` + deploy tests: 23 PASS.
- Python compile: PASS.
- JavaScript syntax: PASS.
- SQLite integrity: ok.
- Event active: 13/13.
- Seed DB profile count: 0.

## Giới hạn giữ nguyên
- Không tạo điểm 0–10 khi chưa hiệu chỉnh.
- Dụng/Hỷ/Kỵ chưa dùng trong kết luận V1-basic.
- Diễn giải ứng dụng không được trình bày như nguyên văn cổ thư.
