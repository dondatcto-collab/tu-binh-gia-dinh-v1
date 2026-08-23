from loi.quyet_dinh.v1 import danh_gia_giai_doan


def test_luc_xung_duoc_dien_giai_cu_the_theo_linh_vuc():
    d = danh_gia_giai_doan('DAN', 'THAN', 'month')
    g = d['dien_giai']
    assert d['label'] == 'Có điểm cần lưu ý'
    assert 'thay đổi' in g['headline'].lower() or 'va chạm' in g['headline'].lower()
    assert 'phương án B' in g['cong_viec']
    assert 'Không tự suy ra hao tài' in g['tai_chinh']
    assert g['quan_he'] != g['cong_viec']
    assert g['viec_lon'] != g['cong_viec']
    assert g['interpretation_status'] == 'PRODUCT_INTERPRETATION'
    assert g['evidence_scope'] == 'VERIFIED_BRANCH_RELATION_ONLY'


def test_luc_hop_khong_bi_bien_thanh_loi_hua_tai_loc():
    d = danh_gia_giai_doan('DAN', 'HOI', 'day')
    g = d['dien_giai']
    assert d['label'] == 'Khá thuận'
    assert 'phối hợp' in g['headline'].lower()
    assert 'Chưa có căn cứ riêng' in g['tai_chinh']
    assert 'không dùng Lục hợp một mình' in g['viec_lon']


def test_khong_co_quan_he_noi_ro_tung_linh_vuc_thay_vi_loi_khuyen_chung():
    d = danh_gia_giai_doan('DAN', 'TY', 'day')
    g = d['dien_giai']
    assert d['label'] == 'Chưa có tín hiệu nổi bật'
    assert set(['cong_viec','tai_chinh','quan_he','viec_lon','focus']).issubset(g)
    assert 'Việc lớn' in g['focus'][1]


def test_tang_gia_dinh_trigger_khong_bat_nguoi_dung_hieu_thuat_ngu():
    for b in ('THAN','HOI','TI','TY'):
        g = danh_gia_giai_doan('DAN', b, 'day')['dien_giai']
        assert 'Lục xung' not in g['trigger']
        assert 'Lục hợp' not in g['trigger']
        assert 'Lục hại' not in g['trigger']
        assert 'Hình' not in g['trigger']
        assert g['technical_trigger']
