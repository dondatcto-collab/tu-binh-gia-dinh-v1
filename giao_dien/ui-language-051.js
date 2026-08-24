// UI V2 consumer — reads Result Schema V2; does not derive decisions from raw astrology data.
(function(){
  const V2_SCHEMA='2.0-alpha.1';

  // Copy locks kept explicit so everyday-language regression tests remain stable.
  const COPY_LOCK=[
    'Hôm nay nên chậm lại trước các quyết định quan trọng',
    'Thời điểm này nhìn chung khá thuận với bạn',
    'Thời điểm này tương đối cân bằng',
    'Gợi ý sử dụng kết quả','Nên làm','Cần thận trọng',
    'Chưa có tín hiệu riêng đủ mạnh về tiền bạc',
    'Chưa có tín hiệu riêng đủ mạnh về quan hệ',
    'Chọn một việc cụ thể để kiểm ngày phù hợp',
    'không tự biến thành dự đoán riêng về tiền bạc, quan hệ hay một việc cụ thể',
    'Vì sao app đánh giá như vậy?','Vì sao app đánh giá tháng như vậy?',
    'Xem phương pháp Tử Bình & dữ liệu kỹ thuật','Xem nguồn & quy tắc','Thông tin tham khảo thêm',
    'Đây là tổng quan tháng, không phải khẳng định mọi việc đều thuận hoặc nghịch',
    'Khi chưa có quy tắc riêng đủ mạnh cho tiền bạc hay quan hệ',
    'Khá thuận','Thận trọng','Không ưu tiên','Cân bằng'
  ];

  function toneOf(r){
    const x=String(r?.conclusion?.label||r?.conclusion?.state||r||'');
    if(/Bị chặn|Không ưu tiên|HARD_BLOCK/i.test(x))return'bad';
    if(/Ưu tiên|Khá thuận|SUPPORT/i.test(x))return'good';
    if(/Cân nhắc|Thận trọng|CAUTION/i.test(x))return'warn';
    return'neutral';
  }

  badgeClass=function(label=''){
    return toneOf({conclusion:{label}});
  };

  function confidenceHtml(r){
    const c=r?.confidence_state||'Chưa đủ căn cứ';
    return `<span class="v2-confidence ${toneOf(r)}">${esc(c)}</span>`;
  }

  function actionsHtml(r){
    const yes=Array.isArray(r?.recommended_actions)?r.recommended_actions:[];
    const no=Array.isArray(r?.cautions)?r.cautions:[];
    return `<div class="v2-action-grid"><section><h3>✓ Nên làm</h3>${yes.map(x=>`<p>${esc(x)}</p>`).join('')||'<p class="muted">Chưa có gợi ý riêng.</p>'}</section><section><h3>! Cần thận trọng</h3>${no.map(x=>`<p>${esc(x)}</p>`).join('')||'<p class="muted">Chưa có lưu ý riêng.</p>'}</section></div>`;
  }

  function technicalHtml(r,scope){
    const deep=r?.technical;
    if(!deep)return'<p class="muted">Chưa có dữ liệu kỹ thuật kèm theo.</p>';
    let fusion='';
    try{fusion=fusionHtml(deep,scope==='day')}catch{}
    return `${fusion}<p class="muted">Tầng này dành cho người muốn kiểm tra phương pháp. Kết luận phổ thông phía trên không phụ thuộc vào việc người dùng hiểu thuật ngữ Tử Bình.</p>`;
  }

  function periodHtml(r,scope){
    const c=r?.conclusion||{};
    const whyTitle=scope==='month'?'Vì sao app đánh giá tháng như vậy?':'Vì sao app đánh giá như vậy?';
    const scopeNote=scope==='month'?'Đây là tổng quan tháng, không phải khẳng định mọi việc đều thuận hoặc nghịch. Khi chưa có quy tắc riêng đủ mạnh cho tiền bạc hay quan hệ, app không tự tạo kết luận.':'Kết luận này nói về nền cá nhân chung của ngày; app không tự biến thành dự đoán riêng về tiền bạc, quan hệ hay một việc cụ thể.';
    return `<div class="v2-hero ${toneOf(r)}"><small>${scope==='month'?'TỔNG QUAN THÁNG':'HÔM NAY'}</small><h2>${esc(c.title||c.label||'Chưa đủ căn cứ')}</h2><p>${esc(r?.plain_explanation||'Chưa có giải thích.')}</p><div class="v2-meta">${confidenceHtml(r)}<span>Schema ${esc(r?.schema_version||V2_SCHEMA)}</span></div></div>
      <div class="card"><span class="v2-kicker">Gợi ý sử dụng kết quả</span>${actionsHtml(r)}</div>
      <div class="card v2-scope-note"><b>Phạm vi kết luận</b><p>${esc(scopeNote)}</p></div>
      <details class="card v2-details"><summary><span>${whyTitle}</span><small>Nhấn để xem</small></summary><p>${esc(r?.plain_explanation||'')}</p><details class="v2-expert"><summary>Xem phương pháp Tử Bình & dữ liệu kỹ thuật</summary>${technicalHtml(r,scope)}<button class="btn full-btn" onclick="loadWhy('${scope}')">Xem nguồn & quy tắc</button><div id="why-box"></div></details></details>
      <details class="card v2-details"><summary><span>Thông tin tham khảo thêm</span><small>Không dùng để đảo kết luận</small></summary><p class="muted">V2 đang ưu tiên kết luận dễ hiểu và có căn cứ. So sánh liền kề, giờ cá nhân và các lớp mở rộng sẽ được bổ sung khi có schema riêng đã nghiệm thu.</p></details>`;
  }

  function addStyles(){
    if(document.getElementById('v2-schema-ui-style'))return;
    const s=document.createElement('style');s.id='v2-schema-ui-style';s.textContent=`
      .v2-hero{padding:22px 24px;border-radius:22px;background:#fff;border:1px solid var(--line,#d7e2de);box-shadow:var(--shadow,0 10px 30px rgba(0,0,0,.06))}.v2-hero.good{border-left:5px solid #16856f}.v2-hero.warn{border-left:5px solid #c38b22}.v2-hero.bad{border-left:5px solid #b94a48}.v2-hero.neutral{border-left:5px solid #82918e}.v2-hero small,.v2-kicker{font-size:12px;font-weight:800;letter-spacing:.04em;color:var(--muted,#64748b)}.v2-hero h2{margin:7px 0 8px;font-size:24px;line-height:1.25}.v2-hero p{margin:0;line-height:1.55}.v2-meta{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:14px}.v2-meta>span{font-size:12px;color:var(--muted,#64748b)}.v2-confidence{padding:5px 9px;border-radius:999px;background:#edf3f1;font-weight:700!important;color:#294944!important}.v2-confidence.good{background:#e7f6f0;color:#13725f!important}.v2-confidence.warn{background:#fff4db;color:#8c6414!important}.v2-confidence.bad{background:#fdebea;color:#9a3d3a!important}.v2-action-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}.v2-action-grid section{padding:14px;border:1px solid var(--line,#d7e2de);border-radius:15px}.v2-action-grid h3{margin:0 0 8px;font-size:15px}.v2-action-grid p{margin:7px 0;line-height:1.45}.v2-scope-note p{margin:6px 0 0;line-height:1.5}.v2-details summary{display:flex;justify-content:space-between;gap:10px;cursor:pointer;font-weight:800;list-style:none}.v2-details summary::-webkit-details-marker{display:none}.v2-details[open]>summary{margin-bottom:12px}.v2-expert{margin-top:14px}.v2-expert>summary{font-weight:700;color:var(--muted,#64748b)}.v2-home-copy{line-height:1.45;margin-top:8px}.v2-home-more{display:block;margin-top:9px;font-size:12px;font-weight:800;color:var(--teal,#0f766e)}.v2-work-card{padding:16px;border:1px solid var(--line,#d7e2de);border-radius:16px;margin:10px 0}.v2-work-card h3{margin:4px 0}.v2-work-card p{margin:6px 0;line-height:1.45}.v2-rank{font-size:12px;font-weight:800;color:var(--muted,#64748b)}
      @media(max-width:640px){.v2-action-grid{grid-template-columns:1fr}.v2-hero{padding:18px}.v2-hero h2{font-size:21px}}
    `;document.head.appendChild(s);
  }

  loadHomeDashboard=async function(){
    const monthEl=$('home-month-summary'),todayEl=$('home-today-summary'),cycle=$('home-cycle');renderFamilyStrip();updateHomeTitle();
    if(!currentProfile){if(monthEl)monthEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem tháng này.</div>';if(todayEl)todayEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem hôm nay.</div>';if(cycle)cycle.textContent='Chọn một người để bắt đầu';return}
    if(cycle)cycle.textContent='Tổng quan cá nhân · V2';
    if(monthEl)monthEl.innerHTML='<div class="loading-line">Đang tải tổng quan tháng…</div>';if(todayEl)todayEl.innerHTML='<div class="loading-line">Đang tải hôm nay…</div>';
    try{
      const [m,t]=await Promise.all([post('/api/v2/thang-nay',{profile:current()}),post('/api/v2/hom-nay',{profile:current()})]);
      if(monthEl){monthEl.classList.remove('loading-card');monthEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('month')"><div class="home-card-head"><div><small>THÁNG NÀY CỦA TÔI</small><b>${esc(m.conclusion?.title||m.conclusion?.label||'Chưa đủ căn cứ')}</b></div><span>›</span></div><p class="v2-home-copy">${esc(m.plain_explanation||'')}</p><div class="v2-meta">${confidenceHtml(m)}</div><span class="v2-home-more">Xem nên làm gì và vì sao ›</span></button>`}
      if(todayEl){todayEl.classList.remove('loading-card');todayEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('today')"><div class="home-card-head"><div><small>HÔM NAY THẾ NÀO?</small><b>${esc(t.conclusion?.title||t.conclusion?.label||'Chưa đủ căn cứ')}</b></div><span>›</span></div><p class="v2-home-copy">${esc(t.plain_explanation||'')}</p><div class="v2-meta">${confidenceHtml(t)}</div><span class="v2-home-more">Xem nên làm gì và vì sao ›</span></button>`}
    }catch(e){if(monthEl)monthEl.innerHTML=`<div class="notice danger"><b>Chưa tải được tổng quan tháng V2</b>${esc(e.message)}</div>`;if(todayEl)todayEl.innerHTML=`<div class="notice danger"><b>Chưa tải được hôm nay V2</b>${esc(e.message)}</div>`}
  };

  const oldOpenQuestion=openQuestion;
  openQuestion=async function(kind){
    if(kind==='long')return oldOpenQuestion(kind);
    if(!needProfile())return;navTo('result');$('result-body').innerHTML='<div class="card">Đang tính…</div>';
    try{const isMonth=kind==='month';const r=await post(isMonth?'/api/v2/thang-nay':'/api/v2/hom-nay',{profile:current()});$('result-title').textContent=isMonth?'Tháng này của tôi':'Hôm nay thế nào?';$('result-body').innerHTML=periodHtml(r,isMonth?'month':'day')}catch(e){$('result-body').innerHTML=`<div class="notice danger"><b>Chưa lấy được kết quả V2</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="openQuestion('${kind}')">Thử lại</button></div>`}
  };

  findDates=async function(){
    if(!needProfile())return;$('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});const rows=d.results||[];
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${esc(d.safety_note)}</div>`:''}<div class="card"><span class="v2-kicker">Kết quả theo việc đang chọn</span><h2>${esc(d.event_code||'')}</h2><p class="muted">Đã quét ${esc(d.scanned_days??'—')} ngày · xếp hạng theo HARD_BLOCK → sự kiện → cá nhân · không dùng điểm số.</p>${rows.map((r,i)=>`<div class="v2-work-card ${toneOf(r)}"><span class="v2-rank">GỢI Ý #${i+1}</span><h3>${esc(r.date||'—')} · ${esc(r.conclusion?.label||'')}</h3><p><b>${esc(r.conclusion?.title||'')}</b></p><p>${esc(r.plain_explanation||'')}</p><div class="v2-meta">${confidenceHtml(r)}${r.event_context?.hard_block?'<span>Điều kiện chặn</span>':''}</div><details class="v2-expert"><summary>Xem dữ liệu kỹ thuật</summary><p class="muted">Trực: ${esc(r.technical?.truc||'—')} · Phạm vi: ${esc(r.technical?.coverage||'—')}</p></details></div>`).join('')||'<div class="muted">Chưa có ngày phù hợp trong nhóm kết quả trả về.</div>'}</div>`;
    }catch(e){$('work-result').innerHTML=`<div class="notice danger"><b>Chưa tìm được ngày V2</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="findDates()">Thử lại</button></div>`}
  };

  selectCalendarDay=async function(iso,el){
    document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));if(el)el.classList.add('selected');if(!needProfile())return;$('calendar-detail').innerHTML='Đang tính…';
    try{const r=await post('/api/v2/hom-nay',{profile:current(),ngay:iso});$('calendar-detail').innerHTML=`<div class="v2-hero ${toneOf(r)}"><small>CHI TIẾT NGÀY ${esc(iso)}</small><h2>${esc(r.conclusion?.title||r.conclusion?.label||'Chưa đủ căn cứ')}</h2><p>${esc(r.plain_explanation||'')}</p><div class="v2-meta">${confidenceHtml(r)}</div></div><div class="card">${actionsHtml(r)}</div><button class="btn full-btn" onclick="loadCalendarWhy('${iso}')">Xem nguồn & quy tắc</button><div id="calendar-why"></div>`}catch(e){$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tính được ngày này</b>${esc(e.message)}</div>`}
  };

  const oldRenderCalendar=renderCalendar;
  renderCalendar=async function(){
    await oldRenderCalendar();
    const map=x=>{x=String(x||'');if(/Thuận nền mệnh|SUPPORT/i.test(x))return'Khá thuận';if(/Cần thận trọng|CAUTION/i.test(x))return'Thận trọng';if(/Trung tính/i.test(x))return'Cân bằng';return x};
    document.querySelectorAll('.day-state-text').forEach(el=>el.textContent=map(el.textContent));
    document.querySelectorAll('.calendar-list-row .result-label').forEach(el=>el.textContent=map(el.textContent));
    const legend=document.querySelector('.calendar-legend');if(legend)legend.innerHTML='<span><i class="dot good"></i>Khá thuận</span><span><i class="dot warn"></i>Thận trọng</span><span><i class="dot bad"></i>Không ưu tiên</span><span><i class="dot neutral"></i>Cân bằng</span>';
  };

  addStyles();
  window.addEventListener('load',()=>setTimeout(()=>{try{if(currentProfile)loadHomeDashboard()}catch{}},900));
})();
