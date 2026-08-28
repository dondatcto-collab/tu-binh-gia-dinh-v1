# V2.9B — Verified Relation Hour Decision

## Mục tiêu
Mở lớp quyết định giờ cá nhân có căn cứ truy nguyên mà không phá thứ bậc ngày/sự kiện và không phát minh numeric score.

## Phạm vi đã khóa
- Ngày HARD_BLOCK: toàn bộ giờ `INELIGIBLE_BY_DAY`; giờ không được cứu ngày.
- Ngày đã qua cổng sự kiện: xét 12 giờ bằng quan hệ Địa Chi đã có Rule ID/Source ID.
- `LUC_HOP` -> `PERSONAL_GOOD_CANDIDATE` / Có thể ưu tiên.
- `LUC_XUNG`, `LUC_HAI`, `HINH`, `TU_HINH` -> `PERSONAL_CAUTION_HOUR` / Nên thận trọng.
- Không có quan hệ trực tiếp -> `PERSONAL_NEUTRAL_HOUR` / Trung tính.
- Caution không được đổi thành “hung tuyệt đối”; `is_personal_bad_hour` vẫn false.
- `numeric_score` tiếp tục `LOCKED_OFF`.

## Nguồn/rule dùng ở lớp giờ
- `BT-REL-0001` — Lục hợp — `SRC-TMTH-V02-WIKISOURCE`.
- `BT-REL-0002` — Lục xung — `SRC-TMTH-V02-WIKISOURCE`.
- `BT-REL-0003` — Lục hại — `SRC-TMTH-V02-WIKISOURCE`.
- `BT-REL-0004` — Hình/Tự hình — `SRC-TMTH-V02-WIKISOURCE`.

## Giới hạn chủ động
V2.9B chưa tuyên bố hệ cát-hung giờ cổ điển đầy đủ. Đây là lớp quyết định giờ giới hạn dựa trên quan hệ Địa Chi đã truy nguồn, luôn đứng sau cổng ngày/sự kiện.

## Release gate
Chỉ merge khi full regression PASS. Sau merge phải có Vercel production READY và live smoke production PASS trước khi đóng V2.9B.
