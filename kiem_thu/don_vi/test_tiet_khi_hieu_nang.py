from datetime import datetime, timedelta, timezone
from loi.lich.quy_uoc_can_chi import quy_uoc_mac_dinh
from loi.lich.tiet_khi import BoTinhTietKhi

class NenGiaLap:
    ten='fake-perf'
    def __init__(self): self.calls=0
    def tim_kinh_do(self,kinh_do,bat_dau_utc,so_ngay):
        self.calls+=1
        return bat_dau_utc+timedelta(days=25,minutes=(int(kinh_do)%17)-8)

def full_reference(bo,moc):
    ds=[]
    for n in (moc.year-1,moc.year,moc.year+1): ds.extend(bo.tat_ca_trong_nam(n))
    ds.sort(key=lambda x:x.thoi_diem_utc)
    pre=[x for x in ds if x.thoi_diem_utc<=moc]; post=[x for x in ds if x.thoi_diem_utc>moc]
    jp=[x for x in pre if bo.quy_uoc.la_mo_thang(x.dinh_nghia)]; jn=[x for x in post if bo.quy_uoc.la_mo_thang(x.dinh_nghia)]
    return pre[-1].dinh_nghia.code,post[0].dinh_nghia.code,jp[-1].dinh_nghia.code,jn[0].dinh_nghia.code

def test_dinh_vi_nhanh_giong_full_reference():
    q=quy_uoc_mac_dinh()
    for moc in [datetime(1988,11,19,1,tzinfo=timezone.utc),datetime(2026,8,23,5,tzinfo=timezone.utc),datetime(2026,2,4,2,tzinfo=timezone.utc)]:
        n1=NenGiaLap(); n1.ten+='-fast-'+str(moc.timestamp()); a=BoTinhTietKhi(q,n1); got=a.dinh_vi(moc)
        assert n1.calls<=10
        n2=NenGiaLap(); n2.ten+='-full-'+str(moc.timestamp()); b=BoTinhTietKhi(q,n2); ref=full_reference(b,moc)
        assert (got.truoc.dinh_nghia.code,got.sau.dinh_nghia.code,got.jie_truoc.dinh_nghia.code,got.jie_sau.dinh_nghia.code)==ref
