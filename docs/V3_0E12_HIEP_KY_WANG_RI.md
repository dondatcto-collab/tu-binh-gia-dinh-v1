# V3.0E12 — Hiệp Kỷ Vương Nhật (王日)

## Mục tiêu
Kích hoạt đúng một rule mới có công thức cổ thư rõ: 王日.

## Nguồn khóa
《欽定協紀辨方書》卷五 · 王官守相民日 giữ phép cổ:

- 王日: 春寅、夏巳、秋申、冬亥.

Quy ước mùa theo Chi tháng của project:
- Xuân: Dần/Mão/Thìn → ngày Dần.
- Hạ: Tỵ/Ngọ/Mùi → ngày Tỵ.
- Thu: Thân/Dậu/Tuất → ngày Thân.
- Đông: Hợi/Tý/Sửu → ngày Hợi.

## Event scope
Runtime chỉ cho 王日 tác động khi inventory sự kiện có token này. Trong các event VERIFIED hiện tại, 王日 thuộc 宜 của:
- XUAT_HANH / 行幸遣使〈出行同〉;
- NHAM_CHUC / 上官赴任.

Mapping PROVISIONAL vẫn giữ cơ chế hạ cấp sẵn có, không được dùng để tuyên bố tương đương cổ điển.

## Chính sách
- FAVORABLE_SUPPORT_ONLY.
- Không tạo HARD_BLOCK.
- JI thắng YI.
- HARD_BLOCK thắng tất cả.
- Không cần Can ngày.
- Numeric score = null / LOCKED_OFF.
- Không tuyên bố full classical Hiệp Kỷ.

## Golden
HK-0017 — Xuân + ngày Dần + Xuất hành: 王日 được nhận diện là Yi; golden giữ PENDING để duyệt độc lập.

## Coverage-first
Sau E12 dự kiến:
- active 32/81;
- pending 49/81;
- target band vẫn 42–48;
- verified balance gate phải tiếp tục PASS;
- V1 Engine chưa ready chỉ vì thêm 王日.
