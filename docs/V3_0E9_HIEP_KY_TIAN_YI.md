# V3.0E9 — Hiệp Kỷ Thiên Y (天醫)

## Trạng thái

Source-first, một token duy nhất. Numeric score tiếp tục `LOCKED_OFF`.

## Nguồn khóa

《欽定協紀辨方書》卷五 · 天醫:

- `總要歷曰：天醫者，天之巫醫，其日宜請藥避病...`
- `歷例曰：天醫者，正月起戌，順行十二辰。`

《欽定協紀辨方書》卷十一 · 求醫療病:

- `宜...天醫...`

Quy ước app: tháng tiết khí Dần = 正月, Mão = 二月 ... Sửu = 十二月.

## Công thức

| Chi tháng | Chi ngày Thiên Y |
|---|---|
| Dần | Tuất |
| Mão | Hợi |
| Thìn | Tý |
| Tỵ | Sửu |
| Ngọ | Dần |
| Mùi | Mão |
| Thân | Thìn |
| Dậu | Tỵ |
| Tuất | Ngọ |
| Hợi | Mùi |
| Tý | Thân |
| Sửu | Dậu |

Calculator: `MONTH_BRANCH_DAY_BRANCH_V30E9`.

## Phạm vi quyết định

`天醫 = FAVORABLE_SUPPORT_ONLY`.

Hiện chỉ `DIEU_TRI / 求醫療病` có `天醫` trong `宜` của inventory đã xác minh. Không suy lan sang sự kiện khác.

- Không cần Can ngày.
- Không tạo HARD_BLOCK.
- Không cứu JI/HARD_BLOCK.
- JI thắng YI.
- Không cộng điểm.
- Không tuyên bố đã phủ toàn bộ Hiệp Kỷ.
- Chọn ngày điều trị chỉ dùng khi thời điểm y khoa linh hoạt; không trì hoãn cấp cứu hoặc điều trị cần thiết.

## Gate kiểm thử

1. Khóa đủ 12 tháng → 12 Chi ngày.
2. Input sai fail closed.
3. Positive gate: tháng Mão + ngày Hợi + DIEU_TRI → `天醫` hỗ trợ, không có JI trong fixture.
4. Conflict gate: tháng Dần + ngày Tuất + DIEU_TRI → `天醫` YI nhưng `月厭` JI thắng → CAUTION.
5. HARD_BLOCK vẫn thắng.
6. Không cần `current_stem`.
7. Không leak sang event không hỗ trợ.
8. Capability kỳ vọng: 29/81 active, 52/81 pending.
9. Golden HK-0014 giữ `PENDING` cho tới review độc lập.
