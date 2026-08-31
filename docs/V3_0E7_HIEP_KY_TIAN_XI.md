# V3.0E7 — Hiệp Kỷ Thiên Hỷ (天喜)

## Phạm vi
Kích hoạt đúng một token mới: `天喜` — Thiên Hỷ.

## Nguồn khóa
- 《御定星曆考原》卷三 · 天喜: `春午、夏丑、秋辰、冬未`.
- 《欽定協紀辨方書》卷五 có mục 天喜 trong cùng hệ thần sát; release không suy thêm công thức ngoài chính văn đã khóa ở trên.

## Công thức
Theo mùa tiết khí hiện hành:
- Xuân (Dần/Mão/Thìn): ngày Ngọ.
- Hạ (Tỵ/Ngọ/Mùi): ngày Sửu.
- Thu (Thân/Dậu/Tuất): ngày Thìn.
- Đông (Hợi/Tý/Sửu): ngày Mùi.

Calculator: `SEASON_DAY_BRANCH_V30E7`.

Thiên Hỷ chỉ cần Chi tháng để xác định mùa và Chi ngày; không phụ thuộc Can ngày. Vì vậy thiếu `current_stem` không được làm Thiên Hỷ biến mất, trong khi các rule Can-ngày vẫn phải fail-closed như trước.

## Event evidence hiện hành
`天喜` có trong 宜 của:
- Cưới hỏi (`CUOI_HOI`) — VERIFIED.
- Xuất hành (`XUAT_HANH`) — VERIFIED.
- Đàm phán/hội họp (`DAM_PHAN`) — PROVISIONAL, tiếp tục bị cap.
- Nhậm chức (`NHAM_CHUC`) — VERIFIED.

Không tự suy mở sang các event còn lại.

## Chính sách quyết định
`天喜 = FAVORABLE_SUPPORT_ONLY`.
- Không tạo HARD_BLOCK.
- Không cứu HARD_BLOCK.
- Nếu cùng ngày có matched 忌 thì 忌 thắng.
- Mapping PROVISIONAL không được nâng thành Ưu tiên tuyệt đối.
- Không dùng numeric score.

## Positive gate
Tháng Mão + ngày Ngọ + Cưới hỏi:
- `天喜` là 宜.
- Không cần Can ngày.
- Nếu không có matched 忌 và lớp cá nhân SUPPORT: `FAVORABLE / Ưu tiên`.

## Conflict gate
Tháng Ngọ + ngày Sửu + Cưới hỏi:
- `天喜` = 宜 theo mùa Hạ.
- `月煞` = 忌 theo tháng Ngọ.
- Kết quả phải là `CAUTION / Không ưu tiên`, không HARD_BLOCK, score null.

## Nợ không gộp vào E7
- HK-0002…HK-0012 tiếp tục PENDING cho review độc lập; không tự phê duyệt để làm đẹp số liệu.
- `TIME-0007` là nợ nguồn lớp giờ, không chặn calculator ngày này.
- Không kích hoạt `天徳` khi semantics 乾/坤/艮/巽 chưa được giải quyết.

## Production gate
Chỉ gọi V3.0E7 CLOSED khi PR smoke + full regression PASS, merge main PASS, Vercel production READY đúng main, canonical schema trả `V3_0E7_TIAN_XI`, active 27 / pending 54, calculator `SEASON_DAY_BRANCH_V30E7`, score LOCKED_OFF, và main smoke + regression cuối PASS.
