# V3.0E1 — Hiệp Kỷ: kích hoạt 月徳 (Nguyệt Đức)

## Mục tiêu

Mở đúng một cát thần Can-ngày có nguồn rõ: `月徳`.
Không mở UI, không bật điểm số và không coi Hiệp Kỷ hiện tại là đầy đủ cổ điển.

## Nguồn và công thức

Nguồn chính: **《欽定協紀辨方書》卷五 · 月徳**.
Quy tắc khóa:

- 寅午戌月丙 — tháng Dần/Ngọ/Tuất lấy ngày can Bính;
- 亥卯未月甲 — tháng Hợi/Mão/Mùi lấy ngày can Giáp;
- 申子辰月壬 — tháng Thân/Tý/Thìn lấy ngày can Nhâm;
- 巳酉丑月庚 — tháng Tỵ/Dậu/Sửu lấy ngày can Canh.

Đối chiếu thêm 《淵海子平》 cho cùng mô hình. Calculator V3.0E1 chỉ dùng
**Chi tháng + Can ngày hiện hành**, không suy từ Bát Tự mệnh chủ.

## Kiến trúc

Tạo calculator riêng `MONTH_BRANCH_DAY_STEM_V30E1` trong
`loi/quyet_dinh/hiep_ky_stem_v30e.py`.

Không đưa `月徳` vào calculator `MONTH_BRANCH_RELATIONS_V25_V30D`, vì đó là
hai loại đầu vào khác nhau. Cách tách này cho phép các rule Can-ngày sau mở độc lập.

Runtime fail-closed: nếu không xác định được Can ngày thì `月徳` không được kích hoạt.

## Chính sách quyết định

- `月徳` chỉ có hiệu lực khi loại việc đang xét ghi token này trong 宜.
- Tác động: `FAVORABLE_SUPPORT_ONLY`.
- Không cứu `HARD_BLOCK`.
- Không xóa hoặc thắng token 忌.
- Nếu cùng ngày có 宜 và 忌, giữ đủ evidence; 忌 thắng trong quyết định sự kiện.
- Thứ bậc giữ nguyên: `HARD_BLOCK > EVENT > PERSONAL`.
- `numeric_score = LOCKED_OFF`.

## Gate thuận

Với `XUAT_HANH`:

- tháng Dần;
- ngày Bính Thìn;
- `月徳` active;
- không có token month-branch JI đang kích hoạt trong fixture này.

Kết quả mong đợi: `FAVORABLE / Ưu tiên` khi nền sự kiện VERIFIED và không bị chặn.

## Gate xung đột

Với `XUAT_HANH`:

- tháng Dần;
- ngày Bính Tý;
- `月徳` active theo Can Bính;
- `災煞` active theo Chi Tý.

Inventory Xuất hành ghi `月徳` trong 宜 và `災煞` trong 忌. Runtime phải giữ cả
hai evidence nhưng kết luận `CAUTION / Không ưu tiên`; không tạo HARD_BLOCK.

## Capability sau V3.0E1

- inventory: 81 token;
- ACTIVE_CALCULABLE: 21;
- PENDING_CALCULATOR: 60;
- coverage: `12_TRUC_PLUS_MONTH_BRANCH_11_PLUS_DAY_STEM_1`.

## Ca vàng

`HK-0006-yue-de.yaml` được thêm với `review_status: PENDING`.
Không được tính là golden-approved trước lượt duyệt độc lập.

## Chưa mở

`月徳合`, `月恩`, `四相`, `天徳` và các cát/hung thần khác vẫn PENDING cho đến
khi hoàn thành riêng chuỗi nguồn → calculator → test → conflict → golden.
