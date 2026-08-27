# V2.5 — Kiểm kê nguồn Hiệp Kỷ cho 12 sự kiện

## Nguồn gốc

Nguồn khóa cho giai đoạn này: **《欽定協紀辨方書》四庫全書本 · 卷十一 · 用事**.

Source ID trong code: `SRC-HK-QD-V11-WIKISOURCE`.

V2.5 không tuyên bố đã triển khai toàn bộ Hiệp Kỷ. Mốc hiện tại chỉ là **kiểm kê nguồn 12/12**; lớp quyết định đang dùng vẫn là 12 Trực cho tới khi từng thần sát được tính đúng và có golden conflict tests.

## Ánh xạ 12 sự kiện

| Mã | Việc hiện đại | Mục cổ thư | Trạng thái |
|---|---|---|---|
| KHAI_TRUONG | Khai trương | 開市 | VERIFIED |
| KY_HOP_DONG | Ký hợp đồng / giao dịch quan trọng | 立券交易 | VERIFIED |
| MUA_TAI_SAN | Mua tài sản lớn | 修置產室 / 納財 | PROVISIONAL |
| DONG_THO | Động thổ / sửa nhà | 興造動土〈修造同〉 | VERIFIED |
| NHAP_TRACH | Chuyển nhà / di dời | 般移〈移徙同〉 | VERIFIED |
| CUOI_HOI | Cưới hỏi | 嫁娶 | VERIFIED |
| XUAT_HANH | Đi xa / xuất hành | 行幸遣使〈出行同〉 | VERIFIED |
| DIEU_TRI | Khám / điều trị | 求醫療病 | VERIFIED |
| DAM_PHAN | Họp / gặp gỡ / đàm phán | 宴會〈會親友同〉 | PROVISIONAL |
| NHAM_CHUC | Nhận chức / nhậm chức | 上官赴任 | VERIFIED |
| CAU_TAI | Thu / nhận tiền | 納財 | VERIFIED |
| AN_TANG | Tang lễ / an táng | 安葬 | VERIFIED |

Hai ánh xạ PROVISIONAL không được nâng thành VERIFIED chỉ vì có chữ gần nghĩa. `MUA_TAI_SAN` là khái niệm hiện đại quá rộng; `DAM_PHAN` rộng hơn hội thân hữu/yến hội.

## Khóa quyết định

- `numeric_score = LOCKED_OFF`.
- Thứ bậc cố định: `HARD_BLOCK > EVENT > PERSONAL`.
- Không lấy số lượng cát/hung thần để cộng trừ điểm.
- Không cho tín hiệu cá nhân cứu một ngày bị chặn.
- Không cho giờ cứu một ngày bị chặn.
- Tín hiệu ngoài 12 Trực ở file `hiep_ky_v25.py` hiện là `INVENTORY_ONLY`.

## Trình tự kích hoạt

1. Kiểm kê nguồn và ánh xạ 12/12.
2. Khóa Rule ID và trạng thái evidence.
3. Viết golden conflict tests trước.
4. Cài bộ tính từng thần sát cần thiết, không cài danh mục thần sát khổng lồ.
5. Chỉ khi bộ tính + test PASS mới cho rule tương ứng tác động vào quyết định.
6. API/Result Schema phải trả nguồn và lý do; UI phổ thông chỉ hiện kết luận dễ hiểu, tầng chuyên sâu mở khi cần.

## Ghi chú an toàn nội dung

`DIEU_TRI` chỉ dùng cho lựa chọn ngày khi thời điểm y khoa có thể linh hoạt; không dùng để trì hoãn cấp cứu hay dự đoán hiệu quả điều trị.
