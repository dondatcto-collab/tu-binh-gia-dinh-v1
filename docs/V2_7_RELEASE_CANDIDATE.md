# V2.7 Release Candidate

Scope khóa:
- Event Search trả 3 lựa chọn đầu và toàn bộ ngày đã xét từ cùng Result contract.
- Calendar khi chọn loại việc dùng cùng `/api/v2/tim-ngay` cho màu ngày và chi tiết.
- Không thay engine, ranking, hierarchy, numeric score hay phạm vi Hiệp Kỷ.
- V2.6 single-bootstrap architecture được giữ nguyên.
- PWA cache nâng lên V2.7 và tương thích cache-key bootstrap hiện tại.

Release gate:
GitHub full regression PASS trước preview. Commit này là release candidate duy nhất được phép tạo Vercel preview.
