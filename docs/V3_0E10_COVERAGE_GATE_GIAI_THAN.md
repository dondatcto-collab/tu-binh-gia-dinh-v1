# V3.0E10 — Coverage-first + Giải Thần (解神)

## Quyết định V1 Engine

Không dùng 81/81 làm điều kiện hoàn thành V1.

- Mục tiêu trung tâm: **45 active rule**.
- Dải chấp nhận: **42–48 active rule**.
- Đồng thời mỗi event `VERIFIED` phải có tối thiểu **2 rule thuận + 2 rule tránh** đang tính được.
- Nếu đạt số rule nhưng event VERIFIED còn lệch một phía, V1 Engine vẫn **chưa READY**.
- Numeric score tiếp tục `LOCKED_OFF`.

Module đo tự động: `loi/quyet_dinh/hiep_ky_coverage_gate_v30e10.py`.
Schema công bố: `hiep_ky_v1_engine_readiness`.

## E10 — Giải Thần

Nguồn: 《欽定協紀辨方書》卷五 · 解神:

`歷例曰正二月申三四月戌五六月子七八月寅九十月辰十一月十二月午也`

Quy đổi tháng tiết khí của app:

- Dần/Mão → Thân
- Thìn/Tỵ → Tuất
- Ngọ/Mùi → Tý
- Thân/Dậu → Dần
- Tuất/Hợi → Thìn
- Tý/Sửu → Ngọ

Calculator: `MONTH_BRANCH_DAY_BRANCH_V30E10_GIAI_THAN`.

## Phạm vi quyết định

Inventory hiện tại chỉ dùng `解神` cho `DIEU_TRI / 求醫療病`, mapping `VERIFIED`.

- FAVORABLE_SUPPORT_ONLY.
- Không cần Can ngày.
- Không tạo HARD_BLOCK.
- Không cứu JI/HARD_BLOCK.
- Không leak sang event khác.
- Không cộng điểm.
- Chỉ chọn thời điểm khi y khoa cho phép; không trì hoãn cấp cứu hay điều trị cần thiết.

## Golden

`HK-0015-giai-than.yaml` giữ `PENDING` cho review độc lập.
