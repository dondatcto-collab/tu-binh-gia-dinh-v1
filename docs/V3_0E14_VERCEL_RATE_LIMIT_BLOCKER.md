# V3.0E14 — Vercel production blocker

Main commit: `1a22b9c2e2efd00db7d66ef51d33800ec71577fa`.

GitHub Actions:
- PR #51 regression #817: PASS.
- PR #51 live smoke #230: PASS.
- Main regression #818: PASS.
- Main live smoke #231: PASS.

Vercel commit status trên main:
- state: failure
- description: `Deployment rate limited — retry in 24 hours.`

Vì vậy:
- E14 là MAIN/CI PASS.
- E14 chưa được gọi PRODUCTION PASS.
- Production hiện vẫn ở E13 (`915d4948e422cfeda33c4e17c83740384b73b343`).
- Các E-release sau có thể được chuẩn bị/CI trên branch nhưng không merge vào main cho tới khi production E14 bắt kịp.

Không dùng deploy hook/force deploy như một cách lách rate limit khi chưa có bằng chứng nền tảng cho phép.
