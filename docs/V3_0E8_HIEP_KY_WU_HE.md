# V3.0E8 — Ngũ Hợp (五合)

## Nguồn khóa

《欽定協紀辨方書》卷五 · 五合:
- 樞要歷: 五合 là ngày lành trong tháng; phù hợp kết hôn, hội thân hữu, lập券交易.
- 歷例: `五合者寅卯日也`.

Chuẩn hóa:
- ngày Dần (`DAN`) -> 五合
- ngày Mão (`MAO`) -> 五合
- các Chi ngày khác -> không kích hoạt 五合

## Calculator

`DAY_BRANCH_V30E8`

Input duy nhất: Chi ngày. Không phụ thuộc tháng, mùa hoặc Can ngày.

## Phạm vi sự kiện

Inventory hiện hành chỉ cho 五合 tác động khi chính event evidence đã ghi token này:
- `KY_HOP_DONG` / 立券交易 — VERIFIED, 宜.
- `DAM_PHAN` / 宴會〈會親友同〉 — PROVISIONAL, 宜.

Không suy rộng sang các event khác.

## Chính sách

- `FAVORABLE_SUPPORT_ONLY`.
- JI thắng YI.
- HARD_BLOCK luôn thắng.
- Mapping PROVISIONAL tối đa `Có thể cân nhắc`.
- Không cộng điểm; numeric score vẫn `LOCKED_OFF`.
- Không tuyên bố đã hoàn thiện toàn bộ Hiệp Kỷ.

## Gate kiểm thử

- Dần/Mão kích hoạt chính xác; 10 Chi còn lại không kích hoạt.
- Input Chi sai fail closed.
- Positive gate cho `KY_HOP_DONG` không cần Can ngày.
- Dần + tháng Tỵ: 五合 gặp 月害, phải CAUTION/Không ưu tiên.
- HARD_BLOCK thắng.
- Không leak sang event không có 五合.
- `DAM_PHAN` giữ PROVISIONAL cap.
- Golden `HK-0013-wu-he.yaml` giữ `PENDING` cho tới review độc lập.

## Kỳ vọng sau release PASS

- token inventory: 81.
- active calculable: 28.
- pending calculator: 53.
- extension: `V3_0E8_WU_HE`.
- numeric score: OFF.
