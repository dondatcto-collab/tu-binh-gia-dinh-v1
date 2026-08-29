# V3.0A — Hiệp Kỷ: kích hoạt 月刑 (Nguyệt Hình)

## Mục tiêu

Mở thêm đúng **một** quy tắc Hiệp Kỷ có giá trị rộng và có thể tính chắc chắn: `月刑`.
Không mở hàng loạt thần sát. Không thay đổi UI. Không dùng numeric score.

## Nguồn

Nguồn gốc: **《欽定協紀辨方書》四庫全書本**.

- Quyển 11 · 用事: xác nhận `月刑` nằm trong nhóm 忌 của 12 loại việc hiện hành.
- Quyển 20–31 · 月表一至十二: ghi trực tiếp vị trí `月刑` theo từng tháng.
- Source ID của inventory sự kiện: `SRC-HK-QD-V11-WIKISOURCE`.

## Bảng đã khóa

| Chi tháng | 月刑 ở Chi ngày |
|---|---|
| Dần | Tỵ |
| Mão | Tý |
| Thìn | Thìn |
| Tỵ | Thân |
| Ngọ | Ngọ |
| Mùi | Sửu |
| Thân | Dần |
| Dậu | Dậu |
| Tuất | Mùi |
| Hợi | Hợi |
| Tý | Mão |
| Sửu | Tuất |

Bộ tính không suy ra bảng này từ một quy tắc hiện đại; bảng được khóa trực tiếp từ 12 月表.

## Chính sách quyết định

- `月刑` chỉ có hiệu lực khi event inventory của loại việc đó ghi `月刑` trong 忌.
- Khi khớp: tạo `CAUTION` / “Không ưu tiên”, **không tự tạo HARD_BLOCK**.
- Nếu ngày đã HARD_BLOCK ở lớp V1 thì HARD_BLOCK vẫn thắng.
- Nếu cá nhân thuận nhưng `月刑` cảnh báo thì lớp sự kiện thắng; cá nhân không cứu được.
- Một ngày có thể đồng thời mang nhiều token như `月害 + 月刑` hoặc `月建 + 月刑`; evidence phải giữ đủ, không ghi đè.
- `numeric_score = LOCKED_OFF`.

## Truy nguyên

Rule ID tiếp tục dùng cơ chế deterministic của `hiep_ky_evidence_v25.py` theo bộ ba:
`event_code | polarity | token`.

Vì vậy V3.0A không bịa thêm namespace Rule ID; `月刑` nhận Rule ID ổn định từ inventory đã có.

## Giới hạn

V3.0A **không** đồng nghĩa Hiệp Kỷ đầy đủ. Các token như Thiên Đức, Nguyệt Đức, Thiên Y, Kiếp Sát, Tai Sát... tiếp tục `PENDING_CALCULATOR` cho tới khi có công thức nguồn + bộ tính + test + ca vàng.
