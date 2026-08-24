from loi.quyet_dinh.v1 import tinh_truc, quan_he_chi, danh_gia_event, xep_hang


def test_12_truc_khoi_tu_chi_thang():
    assert tinh_truc("YIN","YIN")=="KIEN"; assert tinh_truc("YIN","MAO")=="TRU"; assert tinh_truc("YIN","SHEN")=="PHA"; assert tinh_truc("SHEN","SHEN")=="KIEN"


def test_luc_hop_va_xung():
    assert quan_he_chi("YIN","HAI").ma=="LUC_HOP"; assert quan_he_chi("YIN","SHEN").ma=="LUC_XUNG"


def test_khai_truong_khai_nhat_duoc_uu_tien():
    d=danh_gia_event("YIN","ZI","CHOU","KHAI_TRUONG"); assert d["truc"]=="KHAI" and d["event_state"]=="YI" and d["rank_group"]<=1


def test_khai_truong_pha_nhat_khong_uu_tien():
    d=danh_gia_event("YIN","SHEN","MAO","KHAI_TRUONG"); assert d["truc"]=="PHA" and d["event_state"]=="JI" and d["label"]=="Không ưu tiên theo việc"


def test_xep_hang_khong_dung_trong_so():
    ds=[{"ngay":"2026-01-02","rank_group":3},{"ngay":"2026-01-01","rank_group":1},{"ngay":"2026-01-03","rank_group":5}]; assert [x["rank_group"] for x in xep_hang(ds)]==[1,3,5]


def test_khong_bia_diem_so():
    d=danh_gia_event("YIN","ZI","CHOU","KHAI_TRUONG"); assert d["score"] is None and d["scoring_status"]=="NO_NUMERIC_SCORE" and d["numeric_score_status"]=="LOCKED_OFF"


def test_thi_cu_da_ra_backlog_v1():
    d=danh_gia_event("DAN","TUAT","MAO","THI_CU"); assert d["support_level"]=="BACKLOG_NOT_V1" and d["score"] is None


def test_12_nhom_viec_deu_chay_12_truc_khong_co_diem_gia():
    from loi.quyet_dinh.v1 import EVENT_RULES, CHI
    assert len(EVENT_RULES)==12 and "THI_CU" not in EVENT_RULES
    for code in EVENT_RULES:
        for day_chi in CHI:
            d=danh_gia_event("YIN",day_chi,"MAO",code); assert d["support_level"]=="ACTIVE_BASIC" and d["score"] is None and d["label"] in {"Phù hợp theo Hiệp Kỷ","Có thể cân nhắc theo Hiệp Kỷ","Chưa có tín hiệu theo việc","Không ưu tiên theo việc"}


def test_ma_dia_chi_native_cua_engine():
    from loi.lich.quy_uoc_can_chi import CHI as CHI_ENGINE
    for a in CHI_ENGINE:
        for b in CHI_ENGINE: assert quan_he_chi(a,b).ma
    assert quan_he_chi("DAN","HOI").ma=="LUC_HOP" and quan_he_chi("DAN","THAN").ma=="LUC_XUNG"


def test_nhan_trung_tinh_khong_tao_ket_luan_chac_chan():
    from loi.quyet_dinh.v1 import danh_gia_giai_doan
    d=danh_gia_giai_doan("DAN","TY","day"); assert d["state"]=="DESCRIPTIVE_ONLY" and d["recommended"]==[]


def test_an_tang_khong_tu_tao_nhom_yi():
    from loi.quyet_dinh.v1 import EVENT_RULES, CHI
    assert EVENT_RULES["AN_TANG"].yi_truc==frozenset()
    for day_chi in CHI: assert danh_gia_event("DAN",day_chi,"MAO","AN_TANG")["label"]!="Phù hợp theo Hiệp Kỷ"


def test_chon_viec_lam_thay_doi_ket_qua_cung_ngay():
    a=danh_gia_event("DAN","TY","SUU","KHAI_TRUONG"); b=danh_gia_event("DAN","TY","SUU","CAU_TAI")
    assert a["event_state"]=="YI" and b["event_state"]=="NEUTRAL" and (a["rank_group"],a["label"])!=(b["rank_group"],b["label"])
