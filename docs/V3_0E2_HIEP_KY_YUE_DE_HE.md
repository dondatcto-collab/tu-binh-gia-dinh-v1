# V3.0E2 — Hiệp Kỷ Nguyệt Đức Hợp (月徳合)

## Phạm vi
Kích hoạt đúng một token mới: `月徳合` — Nguyệt Đức Hợp.

## Nguồn
- 《欽定協紀辨方書》卷五 · 月徳合.
- 《御定星曆考原》卷三 · 月徳合.

Bản OCR của một số ấn bản hiện `巳` ở câu `二六十月在巳`, nhưng 《御定星曆考原》 có bản đọc rõ `己`; đồng thời chính văn giải thích 月徳合 là Can hợp với 月徳. Vì vậy khóa `己` (Kỷ), không dùng `巳` (Tỵ).

## Quy tắc
- Dần / Ngọ / Tuất → Tân (`辛`)
- Hợi / Mão / Mùi → Kỷ (`己`)
- Thân / Tý / Thìn → Đinh (`丁`)
- Tỵ / Dậu / Sửu → Ất (`乙`)

Đây tương ứng các cặp hợp Can với Nguyệt Đức: 丙辛、甲己、壬丁、庚乙.

## Calculator
`MONTH_BRANCH_DAY_STEM_V30E2`

Calculator này tính hai token độc lập:
- `月徳`
- `月徳合`

## Chính sách quyết định
`月徳合` là `FAVORABLE_SUPPORT_ONLY`.

- Chỉ tác động nếu event inventory hiện hành ghi `月徳合` trong 宜.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Conflict gate khóa
Tháng Dần + ngày Tân Hợi + Xuất hành:
- `月徳合` = 宜
- `劫煞` = 忌
- kết quả phải là `CAUTION / Không ưu tiên`
- `hard_block = false`

## Gate phát hành
- PR logic phải PASS full regression trước merge.
- Main phải PASS live-smoke và full regression.
- Canonical production chỉ được gọi PASS khi `/api/v2/schema-status` trả `V3_0E2_YUE_DE_HE`, capability 22/81 và score vẫn `LOCKED_OFF`.
- Nếu Git integration bỏ sót webhook merge, dùng một PR tài liệu không đổi logic để kích hoạt lại deployment; không sửa trực tiếp rule trên main.

## Giới hạn
Không kích hoạt `月恩`, `四相`, `天徳` hoặc rule khác trong release này. Không tuyên bố full classical Hiệp Kỷ.
