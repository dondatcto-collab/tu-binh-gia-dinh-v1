# UI V1 — nền hiển thị cho engine 43-rule

## Phạm vi
UI-only. Không thay calculator, evidence, precedence, ranking hay scoring của engine.

## 5 lớp hiển thị
1. Kết luận: nhãn do engine trả về.
2. Vì sao: tín hiệu hỗ trợ/cần tránh và diễn giải engine.
3. Cá nhân Tử Bình: bối cảnh cá nhân, không được cứu HARD_BLOCK/JI.
4. Nguồn & quy tắc: Rule ID, Source ID, evidence status, source location khi API có dữ liệu.
5. Chi tiết kỹ thuật: authority, event signal, state, Trực, coverage, extension; thu gọn mặc định.

## Nguyên tắc khóa
- UI không tự suy lại kết luận.
- Không cộng/trừ điểm.
- Không hiển thị điểm tổng hợp khi numeric score LOCKED_OFF.
- HARD_BLOCK > EVENT > PERSONAL giữ nguyên.
- Kết quả không đủ evidence phải nói đúng mức căn cứ.
- Bố cục 7 màn hình FIX5.1 và 5 phong cách hiển thị giữ nguyên.
- Hồ sơ tiếp tục lưu cục bộ trên thiết bị.

## PWA
Cache được bump sang `tubinh-ui-v3.0-ui-v1` để thiết bị đang cài PWA nhận renderer mới.

## Nghiệm thu Preview
- Preview chỉ dùng để kiểm giao diện trước merge.
- Không thay đổi logic engine hoặc dữ liệu production.
