# V2.5 Schema Canonicalization Release

Mục tiêu duy nhất: loại bỏ mâu thuẫn phiên bản schema ở biên API trước khi mở V2.6.

## Contract đã khóa
- Mọi Result object public dưới `/api/v2/*` mang `schema_version = 2.5-alpha.1`.
- `product_schema_version = 2.5-alpha.1` luôn hiện diện.
- Component cũ vẫn giữ truy nguyên qua `component_schema_version` khi khác V2.5.
- Hour component vẫn là semantics V2.4 và vẫn `DESCRIPTIVE_ONLY`; chỉ public envelope lên V2.5.
- Không đổi engine 0.5.0, không đổi rule, ranking, HARD_BLOCK hay numeric score.
- V2.5 Hiệp Kỷ vẫn PARTIAL; không mở thêm thần sát.

## Release gate
Branch regression phải PASS trước release candidate. Chỉ commit cuối có marker `[vercel-preview]` được build preview. Sau preview PASS mới mở/merge PR; sau merge phải live-smoke production PASS rồi mới đóng ưu tiên số 1.
