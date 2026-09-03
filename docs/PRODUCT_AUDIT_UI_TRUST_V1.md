# PRODUCT AUDIT — UI, nội dung và độ tin cậy

## Kết luận điều hành
Engine hiện có nền tảng tốt và truy nguồn được, nhưng lớp sản phẩm đang truyền đạt chưa tương xứng. Vấn đề chính không còn là thiếu rule hay thiếu dữ liệu mà là: người dùng chưa nhìn thấy rõ app đã xét gì, vì sao ngày này hơn ngày khác, phần nào thuộc quy tắc sự kiện, phần nào thuộc cá nhân Tử Bình, và mức chắc chắn nằm ở đâu. UI V1/V1.1 mới giải quyết độ dài, chưa giải quyết niềm tin.

## 1. Kiểm toán nội dung người dùng nhìn thấy

### FAIL — Kết luận còn chung chung
Các nhãn như “Ưu tiên”, “Có thể cân nhắc”, “Không ưu tiên”, “Bị chặn” là đúng về máy quyết định nhưng chưa trả lời đủ câu hỏi của người dùng: ưu tiên cho ai, cho việc gì, so với ngày nào, nhờ yếu tố nào, bị trừ bởi yếu tố nào.

### FAIL — Lý do đang thiên về tên rule
Các token như Cát Kỳ, Ngũ Phú, Thiên Mã… có giá trị nội bộ nhưng nếu chỉ liệt kê tên thì người dùng phổ thông không hiểu ý nghĩa thực tế. Cần diễn giải theo ngữ cảnh sự kiện: “hỗ trợ ký kết”, “thuận di chuyển”, “có yếu tố hao tán cần thận trọng”… và sau đó mới cho xem tên sao/rule.

### FAIL — Cá nhân Tử Bình chưa tạo cảm giác “cá nhân”
Nhiều kết quả hiện chỉ có diễn giải tổng quát hoặc không có diễn giải cá nhân bổ sung. Người dùng nhập tên, ngày giờ nơi sinh nhưng lại chưa thấy rõ: ngày này tương tác với mệnh ở đâu, điểm nào hỗ trợ, điểm nào xung, vai trò của dụng/hỷ/kỵ thần nếu dữ liệu đã đủ. Khi không đủ dữ liệu phải nói rõ “chưa dùng lớp cá nhân này” thay vì để trống/generic.

### FAIL — Nguồn có nhưng chưa biến thành bằng chứng dễ tin
Hiện Rule ID/Source ID/evidence status tốt cho kiểm toán kỹ thuật, nhưng người dùng cần 3 tầng: (1) tên quy tắc bằng tiếng Việt, (2) câu cổ thư/ý nghĩa đã chuẩn hóa ngắn gọn, (3) nguồn và trạng thái xác minh khi muốn xem sâu. Chỉ đưa mã kỹ thuật không tạo niềm tin.

### WARN — Giờ cá nhân dễ bị hiểu quá mức
Engine hiện vẫn ghi personal_hour_decision_ready=false và full_classical_hour_auspiciousness_ready=false. UI không được gọi chung là “giờ tốt/xấu cá nhân” nếu lớp giờ mới ở mức tham khảo/có quan hệ đã xác minh. Cần nhãn rõ “Giờ tham khảo” hoặc “Giờ có căn cứ hiện tại”.

## 2. Kiểm toán kiến trúc trải nghiệm

### FAIL — Màn Tìm ngày đang mang tư duy báo cáo kỹ thuật
UI V1: 5 lớp nối tiếp tạo bức tường chữ. UI V1.1: rút ngắn thành card + modal, nhưng cấu trúc thông tin vẫn xoay quanh dữ liệu engine thay vì câu hỏi của người dùng.

Người dùng thực tế cần thứ tự:
1. Tôi nên chọn ngày nào?
2. Vì sao ngày #1 hơn #2?
3. Có điều gì cần tránh?
4. Ngày này hợp riêng với tôi ở điểm nào?
5. Nếu dùng ngày này, khung giờ nào nên xem trước?
6. Căn cứ từ đâu?

### FAIL — Thiếu màn so sánh
Danh sách hiện cho từng ngày riêng lẻ nhưng chưa cho thấy “vì sao ngày A đứng trên ngày B”. Đây là nguyên nhân lớn làm kết quả giống hộp đen. Cần bảng/khối so sánh top 3 theo cùng tiêu chí: kết luận sự kiện, yếu tố hỗ trợ, yếu tố cảnh báo, lớp cá nhân, mức căn cứ.

### FAIL — Quá nhiều thuật ngữ kỹ thuật đi thẳng ra UI
HARD_BLOCK, EVENT, PERSONAL, coverage, extension, Rule ID, Source ID… nên nằm ở chế độ “Chuyên sâu”. Giao diện phổ thông phải dùng tiếng Việt tự nhiên.

### WARN — 7 màn hình và bottom nav chưa chắc phản ánh tác vụ chính
Tác vụ cốt lõi là: hồ sơ → chọn việc → xem ngày → xem ngày cụ thể → giờ/căn cứ. Trang chủ, Lịch, Việc, Hồ sơ, Cài đặt vẫn có thể giữ nhưng hierarchy cần xoay quanh “Hôm nay” và “Tìm ngày”, không quanh cấu trúc module.

## 3. Kiểm toán độ tin cậy

### PASS — Engine có thứ bậc quyết định rõ
HARD_BLOCK > EVENT > PERSONAL và numeric score vẫn khóa là hướng đúng.

### PASS — Có khả năng truy nguồn
Rule/source/evidence đã tồn tại và schema-status phản ánh 43 active / 38 pending.

### FAIL — UI chưa thể hiện “đã xét gì”
Người dùng không biết app đã quét bao nhiêu ngày, tiêu chí nào được áp dụng cho sự kiện này, bao nhiêu rule hỗ trợ/cảnh báo thực sự match, rule nào chưa được dùng vì còn pending.

### FAIL — Confidence hiện giống nhãn hệ thống hơn là lời giải thích
“Căn cứ rõ / vừa / chưa đủ” chỉ có giá trị khi đi kèm nguyên nhân cụ thể: số nguồn, trạng thái VERIFIED/PROVISIONAL, lớp cá nhân có/không, có xung đột nguồn hay không.

### FAIL — Phiên bản người dùng nhìn thấy không đồng nhất với nội bộ
Index/Cài đặt vẫn có dấu vết nhãn phiên bản sản phẩm cũ trong khi renderer đã sang UI 3.x. Điều này làm giảm cảm giác hoàn thiện và phải được chuẩn hóa trước release kế tiếp.

## 4. Đánh giá theo hạng mục

| Hạng mục | Điểm hiện tại | Trạng thái |
|---|---:|---|
| Độ đúng của engine | 8.5/10 | PASS |
| Truy nguồn kỹ thuật | 8/10 | PASS |
| Giải thích cho người phổ thông | 4/10 | FAIL |
| Cảm giác cá nhân hóa | 3.5/10 | FAIL |
| So sánh để ra quyết định | 3/10 | FAIL |
| UX mobile | 5/10 | FAIL |
| Tạo niềm tin | 4/10 | FAIL |
| Tính nhất quán sản phẩm | 5/10 | WARN |

## 5. Kiến trúc UI V1.2 đề xuất — TRUST FIRST

### Màn 1: Kết quả tìm ngày
Không hiển thị báo cáo dài. Hiển thị:
- Việc đang chọn + người đang xét + khoảng thời gian.
- “Đã xét N ngày”.
- Top 3 ngày theo card so sánh ngang/dọc.
- Mỗi card chỉ có: ngày, nhãn, 2 lý do chính, 1 cảnh báo chính, mức căn cứ.
- Một khối “Vì sao ngày #1 đứng đầu?” so sánh trực tiếp #1 với #2/#3.

### Màn 2: Chi tiết một ngày
5 câu hỏi, không phải 5 tầng kỹ thuật:
1. Ngày này phù hợp việc gì / không phù hợp việc gì?
2. Vì sao được chọn?
3. Điểm cần tránh là gì?
4. Riêng với hồ sơ này thì sao?
5. Căn cứ và nguồn ở đâu?

### Màn 3: Cá nhân hóa
Hiển thị theo dạng:
- “Tác động cá nhân: hỗ trợ / trung tính / cần thận trọng”.
- Nêu quan hệ cụ thể nếu engine có dữ liệu.
- Nếu lớp cá nhân chưa đủ: nói thẳng “Kết quả này hiện chủ yếu dựa trên quy tắc ngày/sự kiện; chưa đủ căn cứ cá nhân để nâng/hạ xếp hạng.”

### Màn 4: Giờ
Chỉ hiển thị khi có evidence đủ.
- Nếu chưa full-ready: tiêu đề “Giờ tham khảo”.
- Không dùng màu xanh/đỏ mạnh như kết luận ngày nếu engine chưa có quyết định giờ hoàn chỉnh.

### Màn 5: Căn cứ
Mặc định hiển thị bằng tiếng Việt:
- Tên quy tắc.
- Ý nghĩa trong đúng sự kiện.
- Trạng thái: đã xác minh / tạm dùng / chưa kích hoạt.
- Nút “Xem nguồn gốc” mới lộ Rule ID, Source ID, vị trí cổ thư.

## 6. Quy tắc nội dung bắt buộc cho UI V1.2
1. Mọi kết luận phải gắn với “người + việc + ngày”.
2. Không dùng tên sao/rule làm lý do cuối cùng; phải dịch sang tác động thực tế.
3. Không nói “hợp với bạn” nếu không chỉ ra quan hệ cá nhân đã dùng.
4. Không gọi “giờ tốt/xấu cá nhân” khi hour readiness chưa PASS.
5. Không hiển thị mã kỹ thuật ở màn chính.
6. Khi confidence thấp phải nêu nguyên nhân cụ thể.
7. Top 3 phải có so sánh trực tiếp, không chỉ 3 card độc lập.
8. Một màn hình mobile chỉ nên có một câu hỏi chính.

## 7. Quyết định sau audit
- Không merge UI V1.1 hiện tại.
- Không mở thêm rule engine.
- UI V1.2 phải được thiết kế lại từ “trust-first”, không tiếp tục vá card/modal của V1.1.
- Chỉ code sau khi khóa wireframe và mẫu nội dung cho 1 case hoàn chỉnh.
- Case nghiệm thu đầu tiên phải chạy từ: hồ sơ → chọn một việc → top 3 → so sánh → chi tiết ngày → cá nhân → giờ → nguồn.
