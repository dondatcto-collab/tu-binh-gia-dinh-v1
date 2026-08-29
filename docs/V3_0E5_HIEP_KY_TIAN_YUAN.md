# V3.0E5 — Hiệp Kỷ Thiên Nguyện (天願)

## Phạm vi
Kích hoạt đúng một token mới: `天願` — Thiên Nguyện.

## Nguồn khóa
- 《欽定協紀辨方書》卷五 · 天願.
- 《御定星曆考原》卷三 · 天願.

Hai nguồn cùng ghi bảng 12 tháng:
- Chính nguyệt: Giáp Ngọ.
- Tháng 2: Giáp Tuất.
- Tháng 3: Ất Dậu.
- Tháng 4: Bính Tý.
- Tháng 5: Đinh Sửu.
- Tháng 6: Mậu Ngọ.
- Tháng 7: Giáp Dần.
- Tháng 8: Bính Thìn.
- Tháng 9: Tân Mão.
- Tháng 10: Mậu Thìn.
- Tháng 11: Giáp Tý.
- Tháng 12: Quý Mùi.

Release dùng Chi tháng tiết khí hiện hành: Dần = chính nguyệt ... Sửu = tháng 12.

## Calculator
`MONTH_BRANCH_DAY_PILLAR_V30E5`

Thiên Nguyện yêu cầu khớp toàn bộ Can-Chi ngày. Không được kích hoạt chỉ vì Can ngày trùng.

## Event evidence hiện hành
`天願` có trong 宜 của:
- Khai trương (`KHAI_TRUONG`).
- Ký hợp đồng (`KY_HOP_DONG`).
- Động thổ (`DONG_THO`).
- Nhập trạch / di chuyển (`NHAP_TRACH`).
- Cưới hỏi (`CUOI_HOI`).
- Xuất hành (`XUAT_HANH`).
- Đàm phán/hội họp (`DAM_PHAN`, mapping PROVISIONAL).
- Nhậm chức (`NHAM_CHUC`).
- Cầu tài / nạp tài (`CAU_TAI`).
- An táng (`AN_TANG`).

Không có `天願` trong event inventory hiện hành của `DIEU_TRI` và `MUA_TAI_SAN`; runtime không được tự suy mở sang hai event này.

## Chính sách quyết định
`天願` là `FAVORABLE_SUPPORT_ONLY`.

- Chỉ tác động nếu event inventory ghi `天願` trong 宜.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Positive gate
Tháng Dần + ngày Giáp Ngọ + Khai trương:
- `天願` = 宜.
- Không có matched 忌 trong fixture.
- Kết quả: `FAVORABLE / Ưu tiên` khi lớp cá nhân SUPPORT.

## Conflict gate
Tháng Mão + ngày Giáp Tuất + Xuất hành:
- `天願` = 宜.
- `月煞` = 忌.
- Kết quả: `CAUTION / Không ưu tiên`.
- `hard_block = false`.
- score = null.

## Production gate
Merge logic V3.0E5 phải được Vercel triển khai từ `main`; canonical chỉ được coi là PASS khi `/api/health` và `/api/v2/schema-status` xác nhận E5, capability 25/81, pending 56/81 và score vẫn `LOCKED_OFF`.
Nếu merge logic không tạo deployment mới, chỉ dùng PR tài liệu nhỏ để phát lại webhook Vercel; không thay đổi rule, calculator hay dữ liệu quyết định.

## Giới hạn
Không kích hoạt `天徳`, `天徳合` hoặc rule khác trong release này. Không tuyên bố full classical Hiệp Kỷ. Golden HK-0010 giữ `PENDING` cho tới review độc lập.
