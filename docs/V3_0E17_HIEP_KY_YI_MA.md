# V3.0E17 — Hiệp Kỷ Dịch Mã (驛馬)

## Nguồn khóa
《欽定協紀辨方書》卷六 · 驛馬:

`驛馬者正月起申，逆行四孟`.

Quy đổi theo Chi tháng:
- Dần→Thân; Mão→Tỵ; Thìn→Dần; Tỵ→Hợi;
- Ngọ→Thân; Mùi→Tỵ; Thân→Dần; Dậu→Hợi;
- Tuất→Thân; Hợi→Tỵ; Tý→Dần; Sửu→Hợi.

## Event scope
Inventory VERIFIED hiện tại có 驛馬 trong 宜 của:
- `XUAT_HANH / 行幸遣使〈出行同〉`;
- `NHAP_TRACH / 般移〈移徙同〉`.

## Chính sách
- FAVORABLE_SUPPORT_ONLY.
- Không tạo HARD_BLOCK.
- JI/HARD_BLOCK luôn thắng.
- Không cộng điểm; numeric score LOCKED_OFF.
- Không mở rộng sang event không có evidence.

## Golden
HK-0022 giữ `PENDING` để review độc lập.

## Coverage
Sau E17 dự kiến 37/81 active, 44/81 pending. Đây là stacked release trên E16; chưa merge main trước khi chuỗi production E14→E15→E16 được khóa PASS.
