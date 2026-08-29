# V3.0E3 — Hiệp Kỷ Nguyệt Ân (月恩)

## Phạm vi
Kích hoạt đúng một token mới: `月恩` — Nguyệt Ân.

## Nguồn khóa
- 《御定星曆考原》卷三 · 月恩.
- Bản đối chiếu 《選擇紀要》上編 · 月恩、天願、母倉 cho cùng bảng 12 tháng.

Chính văn giải thích 月恩 là Can do dương kiến sinh ra, theo nghĩa tử mẫu tương tòng; release này chỉ dùng bảng Can theo tháng đã ghi trực tiếp, không suy rộng thêm.

## Bảng 12 tháng
Theo thứ tự tháng 1–12 tương ứng Dần→Sửu:

- Dần → Bính (`丙`)
- Mão → Đinh (`丁`)
- Thìn → Canh (`庚`)
- Tỵ → Kỷ (`己`)
- Ngọ → Mậu (`戊`)
- Mùi → Tân (`辛`)
- Thân → Nhâm (`壬`)
- Dậu → Quý (`癸`)
- Tuất → Canh (`庚`)
- Hợi → Ất (`乙`)
- Tý → Giáp (`甲`)
- Sửu → Tân (`辛`)

## Calculator
`MONTH_BRANCH_DAY_STEM_V30E3`

Calculator này tính ba token độc lập:
- `月徳`
- `月徳合`
- `月恩`

## Chính sách quyết định
`月恩` là `FAVORABLE_SUPPORT_ONLY`.

- Chỉ tác động nếu event inventory hiện hành ghi `月恩` trong 宜.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Positive gate
Tháng Dần + ngày Bính Mão + Xuất hành:
- `月恩` = 宜
- không có matched 忌 trong fixture
- kết quả: `FAVORABLE / Ưu tiên` khi lớp cá nhân SUPPORT.

## Conflict gate khóa
Tháng Dần + ngày Bính Hợi + Xuất hành:
- `月恩` = 宜
- `劫煞` = 忌
- kết quả phải là `CAUTION / Không ưu tiên`
- `hard_block = false`

## Production gate
Merge logic V3.0E3 phải được Vercel triển khai từ `main`; canonical chỉ được coi là PASS khi `/api/health` và `/api/v2/schema-status` xác nhận E3, capability 23/81 và score vẫn `LOCKED_OFF`.

## Giới hạn
Không kích hoạt `四相`, `天徳`, `天徳合` hoặc rule khác trong release này. Không tuyên bố full classical Hiệp Kỷ. Golden HK-0008 giữ `PENDING` cho tới review độc lập.
