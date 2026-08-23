from loi.quyet_dinh.v1 import tinh_truc, quan_he_chi, danh_gia_event, xep_hang


def test_12_truc_khoi_tu_chi_thang():
    assert tinh_truc("YIN", "YIN") == "KIEN"
    assert tinh_truc("YIN", "MAO") == "TRU"
    assert tinh_truc("YIN", "SHEN") == "PHA"
    assert tinh_truc("SHEN", "SHEN") == "KIEN"


def test_luc_hop_va_xung():
    assert quan_he_chi("YIN", "HAI").ma == "LUC_HOP"
    assert quan_he_chi("YIN", "SHEN").ma == "LUC_XUNG"


def test_khai_truong_khai_nhat_duoc_uu_tien():
    # Tháng Dần: ngày Tý là Khai.
    d = danh_gia_event("YIN", "ZI", "CHOU", "KHAI_TRUONG")
    assert d["truc"] == "KHAI"
    assert d["event_state"] == "YI"
    assert d["rank_group"] <= 1


def test_khai_truong_pha_nhat_khong_uu_tien():
    d = danh_gia_event("YIN", "SHEN", "MAO", "KHAI_TRUONG")
    assert d["truc"] == "PHA"
    assert d["event_state"] == "JI"
    assert d["label"] == "Không ưu tiên"


def test_xep_hang_khong_dung_trong_so():
    ds=[{"ngay":"2026-01-02","rank_group":3},{"ngay":"2026-01-01","rank_group":1},{"ngay":"2026-01-03","rank_group":5}]
    assert [x["rank_group"] for x in xep_hang(ds)] == [1,3,5]


def test_khong_bia_diem_so():
    d = danh_gia_event("YIN", "ZI", "CHOU", "KHAI_TRUONG")
    assert d["score"] is None
    assert d["scoring_status"] == "ORDINAL_RULESET_V1"


def test_anh_xa_tam_khong_duoc_nang_thanh_rat_phu_hop():
    # THI_CU ánh xạ hiện đại -> 入學 là PROVISIONAL. Dù Trực Thành/Khai và
    # quan hệ cá nhân thuận, V1 không được gắn nhãn mạnh nhất.
    d = danh_gia_event("YIN", "XU", "MAO", "THI_CU")  # Dần -> Tuất = Thành
    assert d["mapping_status"] == "PROVISIONAL"
    assert d["label"] != "Rất phù hợp"


def test_13_nhom_viec_deu_chay_12_truc_khong_co_diem_gia():
    from loi.quyet_dinh.v1 import EVENT_RULES, CHI
    for code in EVENT_RULES:
        for day_chi in CHI:
            d = danh_gia_event("YIN", day_chi, "MAO", code)
            assert d["support_level"] == "ACTIVE_BASIC"
            assert d["score"] is None
            assert d["label"] in {"Rất phù hợp", "Phù hợp", "Có thể cân nhắc", "Trung tính", "Cân nhắc", "Không ưu tiên"}


def test_ma_dia_chi_tu_calendar_engine_duoc_nhan_truc_tiep():
    from loi.lich.quy_uoc_can_chi import CHI as CHI_ENGINE
    for a in CHI_ENGINE:
        for b in CHI_ENGINE: assert quan_he_chi(a,b).ma
    assert quan_he_chi("DAN","HOI").ma=="LUC_HOP"
    assert quan_he_chi("DAN","THAN").ma=="LUC_XUNG"
    assert tinh_truc("DAN","DAN")=="KIEN"
    assert tinh_truc("DAN","THAN")=="PHA"

def test_13_loai_viec_nhan_ma_chi_native_cua_engine():
    from loi.lich.quy_uoc_can_chi import CHI as CHI_ENGINE
    from loi.quyet_dinh.v1 import EVENT_RULES
    for code in EVENT_RULES:
        for day_chi in CHI_ENGINE:
            d=danh_gia_event("DAN",day_chi,"MAO",code); assert d["support_level"]=="ACTIVE_BASIC" and d["label"]
