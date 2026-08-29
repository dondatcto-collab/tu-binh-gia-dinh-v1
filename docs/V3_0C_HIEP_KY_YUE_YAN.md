# V3.0C — Hiệp Kỷ: kích hoạt 月厭 (Nguyệt Yếm)

## Mục tiêu

Mở thêm đúng **một** quy tắc Hiệp Kỷ có giá trị rộng và có thể tính chắc chắn: `月厭`.
Không mở rộng UI. Không dùng numeric score. Không coi V3.0C là Hiệp Kỷ đầy đủ.

## Nguồn

Nguồn gốc: **《欽定協紀辨方書》四庫全書本**.

- Quyển 11 · 用事: `月厭` nằm trong nhóm 忌 của cả 12/12 loại việc hiện hành.
- Quyển 20–31 · 月表一至十二: ghi trực tiếp vị trí `月厭` theo từng tháng.
- Source ID inventory sự kiện: `SRC-HK-QD-V11-WIKISOURCE`.

Bộ tính khóa trực tiếp bảng 12 tháng; không suy bảng bằng công thức hiện đại.

## Bảng đã khóa

| Chi tháng | 月厭 ở Chi ngày |
|---|---|
| Dần | Tuất |
| Mão | Dậu |
| Thìn | Thân |
| Tỵ | Mùi |
| Ngọ | Ngọ |
| Mùi | Tỵ |
| Thân | Thìn |
| Dậu | Mão |
| Tuất | Dần |
| Hợi | Sửu |
| Tý | Tý |
| Sửu | Hợi |

## Chính sách quyết định

- `月厭` chỉ có hiệu lực khi inventory của loại việc đang xét ghi token này trong 忌.
- Với 12 loại việc hiện hành, inventory đều có `月厭` trong 忌.
- Khi khớp: tạo `CAUTION` / “Không ưu tiên”.
- Không tự tạo `HARD_BLOCK`.
- HARD_BLOCK V1 vẫn thắng.
- Cá nhân thuận không cứu được cảnh báo sự kiện.
- Nếu cùng ngày có nhiều token, giữ đủ evidence; không ghi đè.
- `numeric_score = LOCKED_OFF`.

## Kiểm thử khóa

- đủ bảng 12 tháng;
- tháng Dần + ngày Tuất kích hoạt `月厭`;
- với `KY_HOP_DONG`, `月厭` tạo CAUTION nhưng không HARD_BLOCK;
- tháng Ngọ + ngày Ngọ giữ đồng thời `月建 + 月刑 + 月厭`;
- Rule ID tiếp tục sinh deterministic từ `event_code | polarity | token`;
- Source ID giữ `SRC-HK-QD-V11-WIKISOURCE`.

## Ca vàng

`HK-0004-yue-yan.yaml` được thêm ở trạng thái `PENDING`.
Không được tính là golden-approved cho tới khi có lượt duyệt độc lập.

## Giới hạn

Các token như Thiên Đức, Nguyệt Đức, Đại Thời, Thiên Lại, Thiên Y... vẫn `PENDING_CALCULATOR` cho tới khi có nguồn công thức + calculator + test + ca vàng tương ứng.
