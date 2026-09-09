from pathlib import Path
import base64, gzip, re, hashlib, sys

ROOT = Path(__file__).resolve().parent if '__file__' in globals() else Path('.')

def transform(html: str) -> str:
    html = html.replace('<title>Sổ tay Tử Bình — Mậu Thổ sinh tháng Hợi</title>', '<title>Tử Bình Đạt Võ — Sổ tay cá nhân</title>')
    html = html.replace('Sổ tay cá nhân · xem nhanh để dễ quyết định', 'Tử Bình Đạt Võ · Sổ tay cá nhân')

    css = r'''
/* ===== TỬ BÌNH ĐẠT VÕ · ẤN TRIỆN CÁ NHÂN ===== */
.brand-hero{position:relative;margin:10px 0 20px;padding:22px 16px 18px;border:1px solid rgba(240,180,41,.34);border-radius:10px;overflow:hidden;text-align:center;background:radial-gradient(ellipse at 50% 0%,rgba(255,154,55,.15),transparent 54%),linear-gradient(180deg,#2a160d 0%,#171210 78%);box-shadow:0 12px 34px rgba(0,0,0,.28),inset 0 1px rgba(255,210,135,.08)}
.brand-hero::before,.brand-hero::after{content:"";position:absolute;top:52%;width:22%;height:1px;background:linear-gradient(90deg,transparent,#b8794a)}
.brand-hero::before{left:2%}.brand-hero::after{right:2%;transform:scaleX(-1)}
.brand-emblem{display:flex;justify-content:center;align-items:center;gap:13px;margin-bottom:8px}
.brand-seal{width:58px;height:58px;border:2px solid #d89a46;border-radius:7px;background:linear-gradient(145deg,#6e1c12,#36100c);box-shadow:0 0 0 4px rgba(240,180,41,.06),inset 0 0 18px rgba(255,173,60,.16);display:flex;align-items:center;justify-content:center;color:#f2c572;font-family:"Noto Serif CJK SC","Songti SC","SimSun",serif;font-size:21px;font-weight:800;line-height:1.05;letter-spacing:.04em;writing-mode:vertical-rl}
.brand-cn{font-family:"Noto Serif CJK SC","Songti SC","SimSun",serif;color:#b8794a;font-size:11px;letter-spacing:.28em;text-transform:uppercase}
.brand-title{font-family:"Noto Serif","Times New Roman","Be Vietnam Pro",serif;font-size:clamp(31px,7vw,48px);font-weight:800;line-height:1.05;letter-spacing:.025em;color:#f2d096;text-shadow:0 1px 0 #6b3517,0 4px 18px rgba(255,137,36,.16);margin:7px 0 8px}
.brand-title .accent{color:#f0b429}.brand-sub{font-size:13px;color:#b9aa9e;margin:0 auto;max-width:56ch}.brand-sub b{color:#e3bd79;font-weight:500}
@media(max-width:640px){.brand-hero{padding:18px 12px 15px}.brand-seal{width:50px;height:50px;font-size:18px}.brand-title{font-size:34px}.brand-hero::before,.brand-hero::after{width:13%}}
'''
    html = html.replace('</style>', css + '\n</style>', 1)

    pat = re.compile(r'<header>\s*<div class="quickbox" style="margin-top:18px">.*?</div>\s*<div class="eyebrow">.*?</div>\s*<h1>.*?</h1>', re.S)
    header = '''<header>
  <div class="brand-hero">
    <div class="brand-emblem"><div class="brand-seal">子平</div><div class="brand-cn">命理手札 · PERSONAL EDITION</div></div>
    <div class="brand-title">Tử Bình <span class="accent">Đạt Võ</span></div>
    <p class="brand-sub"><b>Sổ tay cá nhân</b> · mở ra để biết nên ưu tiên gì; phần sách và thuật ngữ chỉ hiện khi anh muốn xem sâu.</p>
  </div>
  <div class="quickbox" style="margin-top:16px">
    <div class="qh">Cách dùng nhanh</div>
    <p>Đọc <b>Nên làm / Nên tránh / Giờ ưu tiên</b> trước. Khi cần kiểm chứng mới mở <b>Theo sách / Vì sao?</b>.</p>
  </div>
  <div class="eyebrow">Võ Tấn Đạt · bản dùng riêng</div>
  <h1>Giữ nhịp tốt,<br>quyết định <em>gọn hơn</em>.</h1>'''
    html, n = pat.subn(header, html, count=1)
    if n != 1:
        raise RuntimeError('Không thay được header branding')
    html = html.replace('<p class="birth">19/11/1988 · 08:00 · Sóc Trăng · nam · giờ Thìn</p>', '<p class="birth">Võ Tấn Đạt · 19/11/1988 · 08:00 · Sóc Trăng · nam · giờ Thìn</p>')

    visible = {
        'ẤN — thứ nuôi anh':'HỌC & HỆ THỐNG — thứ giúp anh vững',
        'MÌNH — sức của bản thân':'SỨC MÌNH — khả năng gánh việc',
        'KIM — cái van để nói ra':'ĐẦU RA — biến cái biết thành thứ dùng được',
        'TIỀN — của cải và cơ hội':'TIỀN & CƠ HỘI — phần dễ đến nhiều',
        'MỘC — áp lực hóa thành sức':'ÁP LỰC TỐT — thứ buộc anh nâng cấp',
        'HỎA · dụng thần':'Hỗ trợ chính','MỘC · hỷ':'Giúp nâng cấp','THỔ · có gốc':'Sức mình',
        'THỦY · rất nhiều':'Tiền & cơ hội','TRỐNG · kỵ':'Đầu ra còn thiếu','Hỏa · dụng':'Hỗ trợ chính',
        'Mộc · hỷ':'Giúp nâng cấp','Thổ · tùy thế':'Tùy tình huống','Kim · kỵ':'Dễ hao sức',
        'Thủy · kỵ':'Cơ hội cần kiểm soát','Dụng thần — có và mạnh':'Hỗ trợ chính — đang có',
        'Có gốc, tùy vận mà mạnh yếu':'Có nền, thay đổi theo giai đoạn',
        'Trống và kỵ — phải tự bồi có chọn lọc':'Cần xây thêm, nhưng không nên quá tay',
        'Rất nhiều — nhiều hơn sức giữ':'Nổi bật — cần quản lý kỹ','Hỷ thần — áp lực là nhiên liệu':'Áp lực tốt — giúp nâng cấp',
    }
    for a,b in visible.items(): html = html.replace(a,b)

    html = html.replace('<div class="god">Ấn</div>','<div class="god">hỗ trợ chính</div>')
    html = html.replace('<div class="god">Tài chính ổn định</div>','<div class="god">tiền & cơ hội</div>')
    html = html.replace('<div class="god">Người cùng phe</div>','<div class="god">nền hỗ trợ</div>')
    html = html.replace('<div class="k">Thổ · mình</div>','<div class="k">Sức mình</div>')
    html = html.replace('<div class="k">Thủy · tiền</div>','<div class="k">Tiền & cơ hội</div>')
    html = html.replace('<div class="k">Mộc · sinh Ấn</div>','<div class="k">Áp lực giúp nâng cấp</div>')
    html = html.replace('<div class="k">Hỏa · dụng thần</div>','<div class="k">Hỗ trợ chính</div>')
    html = html.replace('<div class="k">Kim · trống</div>','<div class="k">Đầu ra còn thiếu</div>')

    old = '''        <div class="goodhours">\n          <div class="lbl">Lớp 2 · thần sát hôm nay</div>\n          <div id="todayTS"></div>\n        </div>'''
    new = '''        <div class="disclosure" style="margin-top:12px">\n          <details><summary>Theo sách / nhãn kỹ thuật hôm nay</summary><div class="inside"><div id="todayTS"></div></div></details>\n        </div>'''
    html = html.replace(old, new)

    html = html.replace('v=["bình thường","v-mid"]','v=["Bình thường","v-mid"]')
    html = html.replace('v=["rất thuận","v-great"]','v=["Ưu tiên cao","v-great"]')
    html = html.replace('v=["thuận","v-good"]','v=["Có thể làm","v-good"]')
    html = html.replace('v=["nên lùi","v-low"]','v=["Hạn chế việc lớn","v-low"]')
    html = html.replace('v=["giữ sức","v-low"]','v=["Thận trọng","v-low"]')
    html = html.replace('m.s>=4?"rất mạnh":m.s>=2?"thuận":m.s>=-2?"bình thường":"giữ sức"','m.s>=4?"Ưu tiên cao":m.s>=2?"Có thể làm":m.s>=-2?"Bình thường":"Thận trọng"')
    static = {'>Rất thuận<':'>Ưu tiên cao<','>Thuận<':'>Có thể làm<','>Cần giữ<':'>Thận trọng<','>Nghịch<':'>Hạn chế việc lớn<','>Nghịch nặng<':'>Hạn chế việc lớn<','>Công<':'>Ưu tiên mở rộng<','>Thủ<':'>Ưu tiên củng cố<','>Thủ chặt nhất<':'>Ưu tiên giảm rủi ro<','>Được tiền, kèm xáo trộn<':'>Có cơ hội nhưng cần kiểm soát<','>Tiền có, người mệt<':'>Có việc nhưng dễ quá tải<','>Mở kho — chuẩn bị trước<':'>Biến động — chuẩn bị trước<','>Không phải năm tiền<':'>Không ưu tiên tăng quy mô<'}
    for a,b in static.items(): html=html.replace(a,b)

    start = html.find('<section id="tailoc">'); end = html.find('</section>', start)
    if start != -1 and end != -1:
        sec = html[start:end+10]
        a = sec.find('<h3>Vì sao cơ hội tiền bạc thường nổi bật</h3>')
        if a == -1: a = sec.find('<h3>Tiền nằm ở đâu trong lá số</h3>')
        b = sec.find('<h3>Bảy nguyên tắc quản trị tiền có thể áp dụng</h3>')
        if a != -1 and b != -1:
            tech = sec[a:b]
            sec = sec[:a] + '<div class="disclosure"><details><summary>Theo sách / vì sao phần tài chính nổi bật?</summary><div class="inside">' + tech + '</div></details></div>\n  ' + sec[b:]
        a2 = sec.find('<h3>Tài chính theo từng chặng</h3>')
        if a2 != -1:
            tech2 = sec[a2:]
            sec = sec[:a2] + '<div class="disclosure"><details><summary>Xem chi tiết tài chính theo từng năm / từng chặng</summary><div class="inside">' + tech2 + '</div></details></div>'
        html = html[:start] + sec + html[end+10:]

    finance = {
        '<b>Không dùng đòn bẩy để mở rộng.</b> Tài đã nhiều hơn sức, vay thêm là chất thêm bao lên vai':'<b>Hạn chế đòn bẩy khi mở rộng.</b> Chỉ tăng vay/margin khi hệ thống quản trị và sức chịu rủi ro thực tế theo kịp',
        '<b>Giữ Ấn trước, tăng thu sau.</b> Học, hệ thống, sức khỏe — đây là giữ cách cục thành cách':'<b>Giữ năng lực trước, tăng thu sau.</b> Ưu tiên kỹ năng, hệ thống, sức khỏe và khả năng kiểm soát',
        '<b>Mỗi năm phải nối thêm một mắt xích Kim.</b> Một sản phẩm, một tài liệu — nhưng chỉ một, vì Kim là kỵ':'<b>Đóng gói một thành quả định kỳ.</b> Một sản phẩm, tài liệu hoặc quy trình đủ dùng; không cần làm quá nhiều',
        '<b>Ưu tiên tài sản nặng hơn tài sản chạy.</b> Đất đai, nền tảng, hợp với đất và hai kho Thìn':'<b>Ưu tiên thứ mình hiểu và quản được.</b> Không chọn loại tài sản chỉ vì lời luận; quyết định đầu tư phải dựa dữ liệu và rủi ro thực tế',
    }
    for a,b in finance.items(): html=html.replace(a,b)

    html = html.replace('<h2>Trong nhà</h2>', '''<h2>Trong nhà</h2>
  <div class="practical-actions">
    <div class="pa good"><div class="ph">Nên làm</div><ul><li>Tách chuyện tiền, công việc và chuyện gia đình khi trao đổi.</li><li>Những việc dễ lặp lại nên thống nhất thành quy tắc trước.</li><li>Với con: ưu tiên làm chung, giải thích rõ và quan sát nhu cầu thật.</li></ul></div>
    <div class="pa avoid"><div class="ph">Nên tránh</div><ul><li>Gắn nhãn tính cách người thân từ một vài chữ trong lá số.</li><li>Dùng Tử Bình thay cho giao tiếp trực tiếp hoặc quyết định gia đình.</li></ul></div>
  </div>''', 1)
    start = html.find('<section id="nha">'); end = html.find('</section>', start)
    if start != -1 and end != -1:
        sec = html[start:end+10]
        a = sec.find('<h3>Các mối quan hệ trong gia đình</h3>'); b = sec.find('<h3>Hai điểm nên lưu ý trong gia đình</h3>', a)
        if a != -1 and b != -1:
            tech = sec[a:b]
            sec = sec[:a] + '<div class="disclosure"><details><summary>Theo sách / cách Tử Bình gán các mối quan hệ</summary><div class="inside">' + tech + '</div></details></div>\n  ' + sec[b:]
        a2 = sec.find('<h3>Chọn người phối hợp công việc</h3>')
        if a2 != -1:
            tech2 = sec[a2:]
            sec = sec[:a2] + '<div class="disclosure"><details><summary>Theo sách / tham khảo nhịp phối hợp với người khác</summary><div class="inside">' + tech2 + '</div></details></div>'
        html = html[:start] + sec + html[end+10:]

    habits = {
        'Dồn việc khó và việc phải quyết vào khung 9h đến 15h':'Nếu lịch cho phép, ưu tiên việc khó vào khung anh tỉnh tááo và tập trung nhất; app gợi ý 9h–15h',
        'Ăn sáng ấm, đúng giờ. Không bỏ bữa':'Giữ bữa ăn và nhịp sinh hoạt ổn định; ưu tiên cách ăn phù hợp sức khỏe thực tế',
        'Sau 21h không ký, không chốt, không nhắn tin lúc nóng':'Hạn chế quyết định lớn hoặc phản hồi lúc đang mệt, nóng hoặc thiếu thông tin vào cuối ngày',
        'Ngủ trước 23h':'Giữ giờ ngủ ổn định và ngủ đủ theo nhu cầu cơ thể',
        'Ra nắng ít nhất mười lăm phút':'Vận động và ra ngoài trời đều đặn khi điều kiện sức khỏe cho phép',
    }
    for a,b in habits.items(): html=html.replace(a,b)

    html = html.replace('Chỉ xét theo dụng thần cách cục: Hỏa dụng, Mộc hỷ, Thổ tùy thế, Kim và Thủy kỵ.','Bộ lọc này chỉ dùng để xếp mức ưu tiên theo lá số cá nhân.')
    html = html.replace('<footer>', '<footer>\n  <div style="text-align:center;margin-bottom:16px"><span class="brand-cn">子平 · TỬ BÌNH ĐẠT VÕ</span></div>', 1)
    return html

def main():
    parts = sorted((ROOT / 'htmlparts').glob('part*.txt'))
    if len(parts) != 10:
        raise RuntimeError(f'Cần đúng 10 htmlparts nguồn, có {len(parts)}')
    encoded = ''.join(p.read_text(encoding='ascii').strip() for p in parts)
    source = gzip.decompress(base64.b64decode(encoded)).decode('utf-8')
    final = transform(source)

    required = ['Tử Bình <span class="accent">Đạt Võ</span>', 'id="calGrid"', 'id="calAnalysis"', 'practicalDayText', 'Theo sách / nhãn kỹ thuật hôm nay']
    missing = [x for x in required if x not in final]
    if missing:
        raise RuntimeError('Thiếu marker sau transform: ' + ', '.join(missing))

    payload = base64.b64encode(gzip.compress(final.encode('utf-8'), 9)).decode('ascii')
    outdir = ROOT / 'app' / 'src' / 'main' / 'assets' / 'htmlparts'
    outdir.mkdir(parents=True, exist_ok=True)
    count = 10
    size = (len(payload) + count - 1) // count
    for i in range(count):
        (outdir / f'part{i:02d}.txt').write_text(payload[i*size:(i+1)*size], encoding='ascii')

    rebuilt = ''.join((outdir / f'part{i:02d}.txt').read_text(encoding='ascii') for i in range(count))
    verify = gzip.decompress(base64.b64decode(rebuilt)).decode('utf-8')
    if verify != final:
        raise RuntimeError('Payload verify mismatch')
    print('FINAL_HTML_BYTES=', len(final.encode('utf-8')))
    print('FINAL_SHA256=', hashlib.sha256(final.encode('utf-8')).hexdigest())
    print('PAYLOAD_PARTS=', count)

if __name__ == '__main__':
    main()
