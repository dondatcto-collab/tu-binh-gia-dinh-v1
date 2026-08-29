# V3.0E4 — Hiệp Kỷ Tứ Tướng (四相)

## Phạm vi
Kích hoạt đúng một token mới: `四相` — Tứ Tướng.

## Nguồn khóa
- 《御定星曆考原》卷三 · 四相: `春丙丁、夏戊己、秋壬癸、冬甲乙`.
- 《欽定協紀辨方書》卷五 · 四相 ghi cùng công thức.

Ý nghĩa công thức trong cổ thư là lấy Can do khí mùa sinh ra; release này chỉ dùng bảng Can theo mùa đã ghi trực tiếp, không suy rộng thêm.

## Quy đổi mùa theo Chi tháng tiết khí
- Xuân: Dần, Mão, Thìn → Bính hoặc Đinh.
- Hạ: Tỵ, Ngọ, Mùi → Mậu hoặc Kỷ.
- Thu: Thân, Dậu, Tuất → Nhâm hoặc Quý.
- Đông: Hợi, Tý, Sửu → Giáp hoặc Ất.

## Calculator
`SEASON_DAY_STEM_V30E4`

Calculator tách riêng khỏi `MONTH_BRANCH_DAY_STEM_V30E3` vì Tứ Tướng là quy tắc mùa và có hai Can hợp lệ cho mỗi mùa.

## Event evidence hiện hành
`四相` có trong 宜 của:
- Động thổ (`DONG_THO`)
- Nhập trạch / di chuyển (`NHAP_TRACH`)
- Xuất hành (`XUAT_HANH`)
- Điều trị khi thời điểm linh hoạt (`DIEU_TRI`)
- Đàm phán/hội họp (`DAM_PHAN`, mapping PROVISIONAL)
- Nhậm chức (`NHAM_CHUC`)
- Cầu tài / nạp tài (`CAU_TAI`)

Không dùng `四相` cho event không có evidence trong inventory hiện hành.

## Chính sách quyết định
`四相` là `FAVORABLE_SUPPORT_ONLY`.

- Chỉ tác động nếu event inventory ghi `四相` trong 宜.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Positive gate
Tháng Dần + ngày Đinh Mão + Xuất hành:
- `四相` = 宜
- không trùng các cát thần Can-ngày E1–E3 trong fixture
- không có matched 忌
- kết quả: `FAVORABLE / Ưu tiên` khi lớp cá nhân SUPPORT.

## Conflict gate
Tháng Dần + ngày Đinh Hợi + Xuất hành:
- `四相` = 宜
- `劫煞` = 忌
- kết quả: `CAUTION / Không ưu tiên`
- `hard_block = false`
- score = null.

## Giới hạn
Không kích hoạt `天徳`, `天徳合` hoặc rule khác trong release này. Không tuyên bố full classical Hiệp Kỷ. Golden HK-0009 giữ `PENDING` cho tới review độc lập.
