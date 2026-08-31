# V3.0E11 — Hiệp Kỷ Ngũ Phú (五富)

## Mục tiêu
Kích hoạt đúng một rule mới có công thức cổ thư rõ và giá trị thực tế cao cho V1 Engine: 五富.

## Nguồn khóa
《欽定協紀辨方書》卷六 · 五富:

- 總要歷曰：五富者，富盛之神也，其日宜興舉運動估市經求。
- 歷例曰：正月起亥，順行四孟。

Quy ước project: tháng Dần là chính nguyệt. Suy ra 12 tháng:

- Dần → Hợi
- Mão → Dần
- Thìn → Tỵ
- Tỵ → Thân
- Ngọ → Hợi
- Mùi → Dần
- Thân → Tỵ
- Dậu → Thân
- Tuất → Hợi
- Hợi → Dần
- Tý → Tỵ
- Sửu → Thân

## Event scope
Chỉ tác động khi inventory 卷十一 đã VERIFIED và có 五富 trong 宜:

- KHAI_TRUONG / 開市
- KY_HOP_DONG / 立券交易
- CAU_TAI / 納財

Không lan sang event khác.

## Chính sách quyết định
- FAVORABLE_SUPPORT_ONLY.
- Không tạo HARD_BLOCK.
- JI thắng YI.
- HARD_BLOCK thắng tất cả.
- Không cần Can ngày.
- Numeric score = null / LOCKED_OFF.
- Không tuyên bố full classical Hiệp Kỷ.

## Golden
HK-0016 — tháng Tỵ + ngày Thân + Khai trương: 五富 là Yi nhưng 月刑 là Ji, kết quả phải CAUTION / Không ưu tiên. Golden giữ PENDING để chờ duyệt độc lập.

## Coverage-first
Sau E11:

- active: 31/81
- pending: 50/81
- mục tiêu V1 Engine: 45, dải chấp nhận 42–48
- verified event balance gate vẫn phải PASS
- V1 Engine chưa được coi là ready chỉ vì thêm 五富.
