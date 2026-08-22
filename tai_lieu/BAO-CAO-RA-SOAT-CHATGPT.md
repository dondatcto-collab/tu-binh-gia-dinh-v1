# BÁO CÁO RÀ SOÁT V1

## Kết luận
Repository có nền kỹ thuật tốt và giữ kỷ luật “không bịa”. Tuy nhiên đây chưa phải V1 chức năng hoàn chỉnh theo phạm vi sản phẩm vì chưa chấm ngày, chưa xếp hạng ngày theo việc và chưa chọn giờ tốt cá nhân.

## Lỗi/điểm đã sửa trong vòng rà soát
1. “Hôm nay” trước đây lấy ngày UTC; đã đổi sang múi giờ của hồ sơ.
2. Dòng thời gian mặc định trước đây lấy UTC; đã ưu tiên múi giờ hồ sơ.
3. UI tạo hồ sơ trước đây hard-code Asia/Ho_Chi_Minh; nay có chọn múi giờ, Việt Nam là mặc định.
4. Bỏ hướng dẫn “không nhớ giờ thì điền gần đúng”; thay bằng cảnh báo nhập đúng giờ sinh.
5. Thêm sửa hồ sơ và xác nhận trước khi xóa.
6. Ráp giao diện 5 tab, 6 avatar và 5 phong cách đã chốt.
7. Lịch không tô xanh/đỏ khi scoring chưa hiệu chỉnh.
8. Tháng/Hôm nay thể hiện theo lớp hợp lưu nhưng không giả thuận/xấu.
9. Cập nhật installer dùng `.venv`, kiểm tra dependency trước khi chạy.
10. `pyproject.toml` trước đây thiếu dependency runtime; đã bổ sung FastAPI, uvicorn, astronomy-engine, pymeeus.
11. README cũ có lỗi mã hóa một số chữ; đã viết lại UTF-8 rõ ràng.

## Kiểm tra đã chạy tại môi trường rà soát
- Python compile: PASS.
- JavaScript syntax (`node --check`): PASS.
- HTML parse cơ bản: PASS.
- Migration + seed: PASS, nạp 11 nguồn và 48 rule version.
- API tĩnh `/`, `/huong-dan`, `/api/tinh-trang`, `/api/loai-viec`, `/api/ho-so`: PASS.
- Tạo -> sửa -> xóa hồ sơ qua API: PASS.

## Giới hạn của lần kiểm tra
Môi trường rà soát không có Internet nên không cài được `astronomy-engine` và `pymeeus`; vì vậy không thể tái chạy toàn bộ suite Calendar/Golden 675 test từ đầu tại đây. Khi chạy ngay từ ZIP, các test Calendar thất bại ở bước import `astronomy`, không phải do mismatch logic. Installer mới đã có bước kiểm tra rõ dependency để máy người dùng không chạy nửa chừng.

## Chưa được tuyên bố hoàn thành
- Vượng suy.
- Cách cục.
- Dụng/Hỷ/Kỵ.
- Hợp/xung/hình/hại/phá đầy đủ.
- Hiệp Kỷ.
- Thần sát.
- Scoring/label đã hiệu chỉnh.
- Xếp hạng ngày cho việc.
- Chọn giờ tốt cá nhân.

Do đó gói này là **V1 nền đã rà soát để gia đình dùng các phần có căn cứ**, chưa phải bản thương mại hay bản chọn ngày hoàn chỉnh.
