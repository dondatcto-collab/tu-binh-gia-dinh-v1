# V3.0E15 — Hiệp Kỷ Dân Nhật (民日)

## Nguồn khóa
《欽定協紀辨方書》卷五 · 王官守相民日:

- 民日: 春午、夏酉、秋子、冬卯.

Quy đổi theo mùa của Chi tháng:
- Xuân → ngày Ngọ.
- Hạ → ngày Dậu.
- Thu → ngày Tý.
- Đông → ngày Mão.

## Event scope
Inventory hiện hành có 民日 trong 宜 của:
- VERIFIED: `KHAI_TRUONG / 開市`, `KY_HOP_DONG / 立券交易`, `NHAP_TRACH / 般移`, `CAU_TAI / 納財`.
- PROVISIONAL: `DAM_PHAN / 宴會〈會親友同〉`; giữ nguyên cơ chế hạ cấp mapping provisional.

## Chính sách
- FAVORABLE_SUPPORT_ONLY.
- Không tạo HARD_BLOCK.
- JI/HARD_BLOCK luôn thắng.
- Không lan sang event không có evidence.
- Numeric score = null / LOCKED_OFF.
- Không tuyên bố full classical Hiệp Kỷ.

## Golden
HK-0020 giữ `PENDING` để review độc lập.

## Coverage
Sau E15 trên branch dự kiến:
- active 35/81;
- pending 46/81;
- target band vẫn 42–48;
- V1 Engine chưa ready chỉ vì thêm 民日.

## Release guard
E15 không được merge vào `main` khi production E14 chưa deploy vì Vercel đang build-rate-limit.
