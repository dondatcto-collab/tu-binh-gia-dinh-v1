# BÁO CÁO 0.3.1 — MEANINGFUL DECISION LAYER

## Mục tiêu
Không đổi UI. Tăng giá trị thực tế của kết luận Tháng/Hôm nay bằng dữ liệu Engine đã có, không bịa thêm Dụng/Hỷ/Kỵ hay điểm số.

## Đã làm
- Thêm `yeu_to_chinh`: tối đa 3 yếu tố trực tiếp tạo kết luận.
- Thêm `nen_cu_the` và `tranh_cu_the` theo 5 nhóm chủ đề Thập Thần: RESOURCE/AUTHORITY/WEALTH/OUTPUT/PEER.
- Giữ 4 lĩnh vực Công việc/Tài chính/Quan hệ/Việc lớn.
- Tài chính luôn có kết luận, kể cả khi chỉ có thể nói chưa có tín hiệu trực tiếp.
- Làm mềm tầng gia đình: không đưa Lục xung/Lục hại vào headline chính; thuật ngữ kỹ thuật vẫn truy được.
- API trả so sánh liền kề: hôm qua/ngày mai và tháng trước/tháng sau.
- UI chi tiết hiển thị 3 yếu tố, hành động cụ thể và điểm khác biệt liền kề.
- Trang chủ bổ sung Tài chính, việc nên làm cụ thể và so sánh với ngày mai khi có dữ liệu.
- Version PWA: 0.3.1; Engine: 0.3.1-meaningful-decision.

## Kiểm thử
- 34 test trọng tâm: PASS.
- Test mới: 10 Nhật chủ với Can Bính phải tạo >=5 nhóm Thập Thần/diễn giải khác nhau: PASS.
- Cùng người, hai ngày có Can/Chi khác nhau phải tạo hành động khác: PASS.
- Mỗi kết luận có 3 yếu tố + hành động cụ thể: PASS.
- Tài chính không được mất khỏi kết luận: PASS.
- Python compile toàn source: PASS.
- JavaScript syntax: PASS.
- SQLite integrity: OK; 13 nhóm việc active.
- public/giao_dien JS/CSS/service-worker đồng bộ.

## Full suite
Full pytest trong container vẫn bị chặn ở các test Calendar/Golden vì môi trường hiện tại thiếu module `astronomy`; lỗi đầu tiên là `No module named 'astronomy'`. Đây là giới hạn môi trường kiểm thử, không được tính thành PASS.

## Những gì KHÔNG làm
- Không tạo điểm 0–10.
- Không tự suy Dụng/Hỷ/Kỵ.
- Không thay bố cục UI đã chốt.
- Không mở thêm nhóm việc.
