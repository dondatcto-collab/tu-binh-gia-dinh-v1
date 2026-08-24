# Tử Bình Gia Đình — Product Blueprint V2

## Mục tiêu

Người không biết Tử Bình vẫn phải hiểu được kết quả trong vài giây. Tử Bình là nền tính toán và truy nguồn, không phải ngôn ngữ bắt buộc của giao diện.

## 5 nguyên tắc khóa

1. Người dùng phổ thông hiểu trước.
2. Tử Bình làm engine, không làm giao diện tầng đầu.
3. Việc cụ thể quan trọng hơn khái niệm “ngày tốt chung chung”.
4. Không đủ căn cứ thì không kết luận.
5. Mọi kết luận đều truy ngược được tới rule và nguồn.

## Ba tầng thông tin

### Tầng 1 — Kết luận phổ thông
- Kết luận ngắn.
- Giải thích đời thường.
- Nên làm.
- Cần thận trọng.
- Không dùng Can Chi, Cách cục, Hỷ/Kỵ hoặc Rule ID như điều kiện để hiểu.

### Tầng 2 — Vì sao
- Giải thích mối liên hệ giữa nền cá nhân, vận và thời điểm.
- Nêu rõ phạm vi kết luận và phần chưa đủ căn cứ.

### Tầng 3 — Chuyên sâu
- Tứ Trụ, Đại vận, năm, tháng, ngày.
- Cách cục, Hỷ/Kỵ, Thập Thần, quan hệ Can Chi.
- 12 Trực / lớp sự kiện.
- Rule ID, nguồn, trạng thái xác minh, nguyên văn khi cần.

## Hai hệ trạng thái tách biệt

### Tổng quan cá nhân
- Khá thuận
- Cân bằng
- Nên thận trọng
- Chưa đủ căn cứ

### Chọn việc
- Ưu tiên
- Có thể cân nhắc
- Không ưu tiên
- Bị chặn

Không trộn hai hệ này. HARD_BLOCK luôn thắng và giờ không được cứu ngày bị chặn.

## Result Schema V2

Mọi màn V2 đọc cùng cấu trúc:

- conclusion
- plain_explanation
- recommended_actions[]
- cautions[]
- confidence_state
- domain
- event_context
- personal_context
- evidence[]
- rules[]
- sources[]
- technical
- numeric_score = null
- numeric_score_status = LOCKED_OFF

## Confidence

- Căn cứ rõ
- Căn cứ vừa
- Chưa đủ căn cứ

Confidence là độ mạnh của căn cứ, không phải điểm tốt/xấu.

## Lộ trình

### 2.0-alpha
- Result Schema V2.
- Adapter từ engine hiện tại.
- Shadow API cho Hôm nay, Tháng, Tìm ngày.

### 2.0-beta
- UI V2 đọc Result Schema thay vì tự diễn giải dữ liệu raw.
- Trang chủ / Hôm nay / Tháng / Tìm ngày.
- Đại vận theo ba tầng.

### 2.0
- Ổn định UX, migration và backward compatibility.

### 2.1+
- Công việc.
- Tiền bạc.
- Quan hệ.
- Giờ cá nhân.
- Hiệp Kỷ mở rộng.

Mỗi domain mới phải có rule, bằng chứng, nguồn và test riêng trước khi được phép tạo kết luận đời sống.
