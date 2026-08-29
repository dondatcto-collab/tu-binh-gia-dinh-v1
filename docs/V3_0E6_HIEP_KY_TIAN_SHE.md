# V3.0E6 — Hiệp Kỷ Thiên Xá (天赦)

## Phạm vi
Kích hoạt đúng một token mới: `天赦` — Thiên Xá.

## Nguồn khóa
- 《御定星曆考原》卷三 · 天赦.
- 《欽定協紀辨方書》卷五 · 天赦.

Công thức cổ thư:
- Xuân: Mậu Dần (`戊寅`).
- Hạ: Giáp Ngọ (`甲午`).
- Thu: Mậu Thân (`戊申`).
- Đông: Giáp Tý (`甲子`).

Release dùng mùa theo Chi tháng tiết khí hiện hành:
- Xuân = Dần/Mão/Thìn.
- Hạ = Tỵ/Ngọ/Mùi.
- Thu = Thân/Dậu/Tuất.
- Đông = Hợi/Tý/Sửu.

## Calculator
`SEASON_DAY_PILLAR_V30E6`

Thiên Xá yêu cầu khớp toàn bộ Can-Chi ngày theo mùa. Không được kích hoạt chỉ vì Can ngày hoặc Chi ngày trùng.

## Event evidence hiện hành
`天赦` có trong 宜 của:
- Động thổ (`DONG_THO`).
- Nhập trạch / di chuyển (`NHAP_TRACH`).
- Cưới hỏi (`CUOI_HOI`).
- Xuất hành (`XUAT_HANH`).
- Điều trị (`DIEU_TRI`).
- Đàm phán/hội họp (`DAM_PHAN`, mapping PROVISIONAL).
- Nhậm chức (`NHAM_CHUC`).
- An táng (`AN_TANG`).

Không có `天赦` trong event inventory hiện hành của `KHAI_TRUONG`, `KY_HOP_DONG`, `MUA_TAI_SAN`, `CAU_TAI`; runtime không được tự suy mở sang bốn event này.

## Chính sách quyết định
`天赦` là `FAVORABLE_SUPPORT_ONLY`.

- Chỉ tác động nếu event inventory ghi `天赦` trong 宜.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Positive gate
Tháng Thìn (mùa xuân) + ngày Mậu Dần + Điều trị:
- `天赦` = 宜.
- Không có matched 忌 trong fixture.
- Kết quả: `FAVORABLE / Ưu tiên` khi lớp cá nhân SUPPORT.

## Conflict gate
Tháng Dần + ngày Mậu Dần + Động thổ:
- `天赦` = 宜.
- `月建` = 忌.
- Kết quả: `CAUTION / Không ưu tiên`.
- `hard_block = false`.
- score = null.

## Giới hạn
Không kích hoạt `天徳`, `天徳合` hoặc rule khác trong release này. Không tuyên bố full classical Hiệp Kỷ. Golden HK-0011 giữ `PENDING` cho tới review độc lập.

## Production gate
Chỉ gọi V3.0E6 CLOSED khi PR smoke + full regression PASS, merge main PASS, Vercel production READY đúng commit, canonical schema trả `V3_0E6_TIAN_SHE`, active 26 / pending 55 và main smoke + regression cuối đều PASS.
