# Tình trạng thật của từng phần

Cập nhật: 2026-08-22 · `ENGINE_VERSION` 0.1.0-phase1 · `RULESET_VERSION` RS-2026.08-P1

## Hai con số phải đọc tách rời

```
IMPLEMENTATION_STATUS       = PASS        (675 test đạt, 0 trượt)
SOURCE_VERIFICATION_STATUS  = PARTIAL     (tầng đánh giá chưa có nguồn)
```

**Test đạt không có nghĩa cổ thư đã được xác minh.** Đây là hai chuyện khác nhau.

## Phần đã chạy và đã có nguồn

| Phần | Trạng thái | Nguồn |
|---|---|---|
| 24 tiết khí tới từng giây | VERIFIED / HIGH | VSOP87, đối chiếu 3 cài đặt |
| Chu kỳ Can Chi ngày | VERIFIED / HIGH | Xuân Thu + thiên văn, phủ 2738 năm |
| Mốc neo ngày (Kỷ Tị, 720 TCN) | VERIFIED / MEDIUM | Xuân Thu + thiên văn, 4 nhóm bằng chứng |
| Ngũ Hổ Độn (Can tháng) | VERIFIED / MEDIUM | Uyên Hải Tử Bình, 5 nhóm |
| Ngũ Thử Độn (Can giờ) | VERIFIED / MEDIUM | Uyên Hải Tử Bình, 5 nhóm |
| Tàng Can 12 Chi | VERIFIED / MEDIUM | Uyên Hải Tử Bình, 又地支藏遁歌 |
| Thập Thần 10 ô | VERIFIED / MEDIUM | Uyên Hải Tử Bình, quyển một |
| Nguyệt lệnh 12 tháng | VERIFIED / HIGH | suy từ Tiết mở tháng |
| Khởi Đại vận (chiều, đếm Tiết, 3 ngày 1 tuổi) | VERIFIED / MEDIUM | Tam Mệnh Thông Hội |

## Phần chưa chắc

| Phần | Trạng thái | Vì sao |
|---|---|---|
| Tháng mở tại Tiết | PROVISIONAL / HIGH | bằng chứng gián tiếp, chưa có phát biểu trọn vẹn |
| Mốc chuyển Đại vận ra ngày dương lịch | PROVISIONAL / LOW | cổ thư dùng năm 360 ngày, cài đặt dùng 365,2422 — lệch ~52 ngày |
| Quyền khí theo tiết | PROVISIONAL, không bật | mới một nguồn, 22 tiết đều INSUFFICIENT_SOURCES |
| Thứ tự liệt kê Tàng Can | CONFLICTED | hai nguồn khác thứ tự ở 5 Chi |
| Can giờ Tý trước nửa đêm | CONFLICTED, KNOWN_CONFLICT mở | hai cách hiểu, không tự chọn |
| Tên gọi ô đồng hành | CONFLICTED, NOT_A_DIRECT_ALIAS | Tỷ Kiên và Dương Nhận là hai khái niệm khác nhau |

## Phần HOÀN TOÀN CHƯA CÓ

Đây là lý do ứng dụng chưa chấm điểm được.

| Phần | Số quy tắc | Cần gì để gỡ |
|---|---|---|
| Vượng suy | 0 | giải xong quyền khí trước |
| Cách cục | 0 | phần Luận cách cục của Tử Bình Chân Thuyên |
| Dụng / Hỷ / Kỵ | 0 | đứng trên vượng suy và cách cục |
| Hợp, xung, hình, hại, phá | 0 | nguồn cổ cho từng loại quan hệ |
| **Hiệp Kỷ theo loại việc** | **0** | **nguyên văn Khâm Định Hiệp Kỷ Biện Phương Thư** |
| Thần sát | 0 | nguồn và công thức khởi |
| Chấm điểm | NOT_CALIBRATED | ca vàng nhóm GOLD-FUS đã duyệt |

## Ba thứ cần, theo thứ tự ưu tiên

1. **Nguyên văn Hiệp Kỷ cho 13 nhóm việc** — gỡ được chức năng "Tìm ngày".
2. **Bảng chia ngày của Tam Mệnh Thông Hội, phần 論人元司事** — gỡ được quyền khí, rồi vượng suy, rồi Dụng/Hỷ/Kỵ.
3. **Phần Luận cách cục của Tử Bình Chân Thuyên** — gỡ được cách cục.

Chỉ cần thứ nhất là "Tìm ngày" chạy được.
Cần cả ba thì mới chấm điểm được.

## Ca vàng

```
APPROVED = 12    PENDING = 6
```

Ca chờ duyệt không được tính vào bất kỳ con số độ phủ nào.

## Về bản chép cổ thư

M��i nguồn cổ trong hệ thống đều ở mức `edition_certainty = TRANSCRIPTION_ONLY`.
Nghĩa là: đọc được nguyên văn, nhưng **chưa khóa được bản in cụ thể**.
Không bản nào là bản chụp nguyên bản.
