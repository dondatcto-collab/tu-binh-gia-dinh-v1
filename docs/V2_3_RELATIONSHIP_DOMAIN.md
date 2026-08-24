# V2.3 — Quan hệ

## Phạm vi khóa

V2.3 chỉ đánh giá **tương tác xã hội và phối hợp thường ngày** theo dữ kiện Tử Bình đã có.

Không bao gồm trong V2.3:
- dự đoán yêu đương;
- hôn nhân;
- chia tay/ly hôn;
- ngoại tình;
- kết luận một người cụ thể tốt/xấu với người dùng;
- kết quả quan hệ chắc chắn.

## Điều kiện tạo kết luận

Chỉ tạo SUPPORT / CAUTION / NEUTRAL khi đồng thời:
1. Cách cục/Hỷ-Kỵ ở trạng thái `READY`;
2. lớp cá nhân không phải `DESCRIPTIVE_ONLY`;
3. chủ đề Thập Thần hiện tại thuộc `PEER`.

Nếu thiếu một điều kiện: `INSUFFICIENT`.

Quan hệ Chi (hợp/xung/hình/hại...) chỉ là evidence bổ sung, không tự lật kết luận nền và không tự tạo dự báo tình cảm.

## Trật tự sản phẩm

Engine → `danh_gia_quan_he` → `relationship_result` → `/api/v2/quan-he` → UI.

UI không được gọi route V1 để tự suy lại quyết định. `numeric_score` luôn khóa OFF.

Sau V2.3 mới được mở `personal_hour`; không mở Hiệp Kỷ mở rộng trong cùng PR.
