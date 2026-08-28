# V2.8 Release Candidate — Evidence-based Confidence

RC scope:
- confidence đi từ chất lượng bằng chứng, không từ độ mạnh của nhãn kết luận;
- PROVISIONAL bị chặn tối đa ở `Căn cứ vừa`;
- thiếu Rule/Source sự kiện => `Chưa đủ căn cứ`;
- giờ sinh chỉ hạ confidence khi lớp cá nhân thực sự tham gia authority;
- verified EVENT hard-block không bị làm yếu bởi giờ sinh không chắc;
- UI giải thích `confidence_basis` trong tầng “Vì sao?”;
- không đổi ranking, `HARD_BLOCK > EVENT > PERSONAL`, Hiệp Kỷ coverage hay numeric-score lock.

Release gates trước RC: full GitHub Actions regression PASS.
