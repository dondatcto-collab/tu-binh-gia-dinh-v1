# V3.0B — Hiệp Kỷ: kích hoạt 劫煞・災煞・月煞

## Mục tiêu

Mở thêm đúng **ba** quy tắc Hiệp Kỷ có cùng nền tính theo Chi tháng/ngày:

- `劫煞` — Kiếp Sát;
- `災煞` — Tai Sát;
- `月煞` — Nguyệt Sát.

Không mở rộng UI. Không dùng numeric score. Không coi V3.0B là Hiệp Kỷ đầy đủ.

## Nguồn

Nguồn gốc: **《欽定協紀辨方書》四庫全書本**.

- Quyển 11 · 用事: cả ba token nằm trong nhóm 忌 của 12/12 loại việc hiện hành.
- Quyển 20–31 · 月表一至十二: ghi trực tiếp vị trí 劫煞、災煞、月煞 theo từng tháng.
- Source ID inventory sự kiện: `SRC-HK-QD-V11-WIKISOURCE`.

Bộ tính khóa trực tiếp bảng 12 tháng; không suy bảng bằng một công thức hiện đại.

## Bảng đã khóa

| Chi tháng | 劫煞 | 災煞 | 月煞 |
|---|---|---|---|
| Dần | Hợi | Tý | Sửu |
| Mão | Thân | Dậu | Tuất |
| Thìn | Tỵ | Ngọ | Mùi |
| Tỵ | Dần | Mão | Thìn |
| Ngọ | Hợi | Tý | Sửu |
| Mùi | Thân | Dậu | Tuất |
| Thân | Tỵ | Ngọ | Mùi |
| Dậu | Dần | Mão | Thìn |
| Tuất | Hợi | Tý | Sửu |
| Hợi | Thân | Dậu | Tuất |
| Tý | Tỵ | Ngọ | Mùi |
| Sửu | Dần | Mão | Thìn |

## Chính sách quyết định

- Chỉ tác động khi token đó có trong inventory 忌 của loại việc đang xét.
- Khi khớp: tạo `CAUTION` / “Không ưu tiên”.
- Không token nào trong ba token mới tự tạo `HARD_BLOCK`.
- HARD_BLOCK V1 vẫn có quyền cao nhất.
- Nếu một ngày có tín hiệu thuận và một trong ba sát cùng lúc, cảnh báo sự kiện thắng tín hiệu thuận.
- Ví dụ khóa regression: tháng Dần + ngày Hợi có `六合 + 劫煞`; với KHAI_TRUONG phải ra CAUTION, không được nâng thành Ưu tiên.
- Một ngày có thể mang nhiều evidence đồng thời; engine không được ghi đè.
- `numeric_score = LOCKED_OFF`.

## Truy nguyên

Rule ID tiếp tục sinh deterministic từ `event_code | polarity | token` trong `hiep_ky_evidence_v25.py`.
Không tạo namespace Rule ID mới và không tạo Source ID giả.

## Ca vàng

`HK-0003-sat-trio.yaml` được thêm ở trạng thái `PENDING`.
Nó không được tính là golden-approved cho tới khi có lượt duyệt độc lập.

## Giới hạn

Các token khác như Thiên Đức, Nguyệt Đức, Thiên Y, Nguyệt Yếm, Đại Thời... vẫn `PENDING_CALCULATOR` cho tới khi có nguồn công thức + calculator + test + ca vàng tương ứng.
