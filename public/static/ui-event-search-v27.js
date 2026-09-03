// UI V1.2 TRUST FIRST — giải thích được, so sánh được, truy nguồn được. Không tự tính lại quyết định engine.
(function(){
  window.TU_BINH_EVENT_SEARCH_UI_VERSION='3.2-ui-v1.2-trust';
  const previousRenderCalendar=renderCalendar;
  const previousSelectCalendarDay=selectCalendarDay;
  let resultMap=new Map();
  let calendarMap=new Map();
  let activeDate='';
  let activeTab='overview';

  const arr=v=>Array.isArray(v)?v:[];
  const safe=v=>esc(v==null?'':String(v));
  function tone(r){
    const x=String(r?.conclusion?.label||r?.conclusion?.state||'');
    if(/Bị chặn|Không ưu tiên|HARD_BLOCK/i.test(x))return'bad';
    if(/Ưu tiên|Khá thuận|SUPPORT/i.test(x))return'good';
    if(/Cân nhắc|Thận trọng|CAUTION/i.test(x))return'warn';
    return'neutral';
  }
  function shortDate(v){const m=String(v||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);return m?`${m[3]}/${m[2]}`:String(v||'');}
  function profileName(){const p=current?.()||{};return p.name||p.ten||p.display_name||'người đã chọn';}
  function eventName(){const el=$('work-type');return el?.selectedOptions?.[0]?.textContent?.trim()||'việc đã chọn';}
  function evidenceStatusLabel(v){
    if(v==='VERIFIED')return'Đã xác minh';
    if(v==='PROVISIONAL')return'Tạm dùng — còn cần đối chiếu';
    if(v==='PENDING')return'Đang chờ xác minh';
    return v||'Chưa ghi trạng thái';
  }
  function tokenMeaning(token,polarity){
    const good={
      '吉期':'Cát Kỳ — tín hiệu thuận được nguồn cổ dùng cho việc phù hợp.',
      '五富':'Ngũ Phú — tín hiệu thuận liên quan tài lộc, kinh doanh trong phạm vi sự kiện đã xác minh.',
      '天倉':'Thiên Thương — tín hiệu thuận liên quan nạp tài trong phạm vi đã xác minh.',
      '天馬':'Thiên Mã — tín hiệu thuận cho di chuyển hoặc thay đổi nơi chốn trong phạm vi đã xác minh.',
      '驛馬':'Dịch Mã — tín hiệu thuận cho xuất hành hoặc di chuyển trong phạm vi đã xác minh.',
      '天醫':'Thiên Y — tín hiệu thuận cho điều trị trong phạm vi đã xác minh.',
      '天后':'Thiên Hậu — tín hiệu thuận cho cầu y, chữa bệnh trong phạm vi đã xác minh.',
      '除神':'Trừ Thần — tín hiệu thuận cho điều trị trong phạm vi đã xác minh.',
      '王日':'Vương Nhật — tín hiệu thuận được dùng cho công việc phù hợp trong phạm vi đã xác minh.',
      '官日':'Quan Nhật — tín hiệu thuận cho nhậm chức/công việc công vụ trong phạm vi đã xác minh.',
      '相日':'Tướng Nhật — tín hiệu thuận cho nhậm chức trong phạm vi đã xác minh.',
      '民日':'Dân Nhật — tín hiệu thuận cho một số việc dân sinh, giao dịch trong phạm vi đã xác minh.',
      '臨日':'Lâm Nhật — tín hiệu thuận cho nhậm chức trong phạm vi đã xác minh.',
      '月徳':'Nguyệt Đức — tín hiệu cát hỗ trợ, không có quyền cứu ngày bị chặn.',
      '月徳合':'Nguyệt Đức Hợp — tín hiệu cát hỗ trợ, không có quyền cứu ngày bị chặn.',
      '月恩':'Nguyệt Ân — tín hiệu cát hỗ trợ trong lớp ngày.',
      '天赦':'Thiên Xá — tín hiệu cát mạnh nhưng vẫn tuân theo điều kiện chặn của sự kiện.',
      '天願':'Thiên Nguyện — tín hiệu cát hỗ trợ trong phạm vi ngày.',
      '天喜':'Thiên Hỷ — tín hiệu cát hỗ trợ trong phạm vi đã xác minh.',
      '五合':'Ngũ Hợp — tín hiệu hợp trợ trong phạm vi ngày.',
      '五富':'Ngũ Phú — tín hiệu thuận liên quan tài lộc, kinh doanh trong phạm vi sự kiện đã xác minh.'
    };
    const bad={
      '大耗':'Đại Hao — tín hiệu hao tán; app dùng như cảnh báo, tự nó không tạo HARD_BLOCK.',
      '月破':'Nguyệt Phá — tín hiệu phá, được dùng ở lớp cần tránh.',
      '月刑':'Nguyệt Hình — tín hiệu hình, được dùng như cảnh báo.',
      '月厭':'Nguyệt Yếm — tín hiệu cần thận trọng trong lớp sự kiện.',
      '劫煞':'Kiếp Sát — tín hiệu sát, được dùng như cảnh báo.',
      '災煞':'Tai Sát — tín hiệu sát, được dùng như cảnh báo.',
      '月煞':'Nguyệt Sát — tín hiệu sát, được dùng như cảnh báo.'
    };
    return (polarity==='JI'?bad[token]:good[token])||`${token} — ${polarity==='JI'?'tín hiệu cần tránh':'tín hiệu hỗ trợ'} được engine dùng cho đúng việc đã chọn.`;
  }
  function visibleEvidence(r){return arr(r?.technical?.matched_evidence);}
  function yi(r){return arr(r?.technical?.matched_yi_tokens);}
  function ji(r){return arr(r?.technical?.matched_ji_tokens);}
  function personalData(r){return r?.personal_context||r?.personal_v1_1||r?.technical?.personal_context||{};}
  function personalSummary(r){
    const p=personalData(r); const text=p?.headline||r?.personal_explanation||''; const state=p?.decision_effect||r?.technical?.personal_state||'';
    if(text)return text;
    if(state)return `Lớp cá nhân hiện ghi nhận: ${state}.`;
    return 'Chưa có căn cứ cá nhân đủ rõ để nâng hoặc hạ kết luận của ngày này.';
  }
  function confidence(r){return r?.confidence_state||'Chưa đủ căn cứ';}
  function decisionReason(r){
    if(r?.event_context?.hard_block)return'Ngày bị chặn ở lớp sự kiện; tín hiệu thuận khác không được đảo ngược kết luận.';
    const y=yi(r),j=ji(r);
    if(y.length&&j.length)return `Có ${y.length} tín hiệu hỗ trợ và ${j.length} tín hiệu cần tránh; engine vẫn giữ kết luận hiện tại theo thứ bậc đã khóa.`;
    if(y.length)return `Có ${y.length} tín hiệu hỗ trợ trực tiếp cho ${eventName()}; chưa thấy tín hiệu cần tránh trực tiếp trong payload của ngày.`;
    if(j.length)return `Có ${j.length} tín hiệu cần tránh trực tiếp cho ${eventName()}.`;
    return r?.plain_explanation||'Chưa có tín hiệu trực tiếp đủ rõ để giải thích mạnh hơn.';
  }
  function trustBadge(r){
    const ev=visibleEvidence(r); const verified=ev.filter(x=>x.evidence_status==='VERIFIED').length;
    const total=ev.length;
    const text=total?`${verified}/${total} căn cứ trực tiếp đã xác minh`:confidence(r);
    return `<span class="t12-trust">Căn cứ: <b>${safe(text)}</b></span>`;
  }
  function tokenLines(r,limit=3){
    const rows=[...yi(r).map(x=>({x,p:'YI'})),...ji(r).map(x=>({x,p:'JI'}))].slice(0,limit);
    if(!rows.length)return'<div class="t12-empty">Chưa có rule trực tiếp nổi bật trong ngày này.</div>';
    return rows.map(o=>`<div class="t12-signal ${o.p==='JI'?'bad':'good'}"><span>${o.p==='JI'?'−':'+'}</span><p><b>${safe(o.x)}</b><small>${safe(tokenMeaning(o.x,o.p))}</small></p></div>`).join('');
  }
  function topHero(r){
    return `<section class="t12-hero ${tone(r)}"><div class="t12-kicker">LỰA CHỌN #1 CHO ${safe(eventName().toUpperCase())}</div><div class="t12-hero-head"><div><h2>${safe(r?.date||'—')}</h2><strong>${safe(r?.conclusion?.label||'Chưa đủ căn cứ')}</strong></div>${trustBadge(r)}</div><p class="t12-lead">${safe(decisionReason(r))}</p><div class="t12-signals">${tokenLines(r,4)}</div><div class="t12-personal"><b>Riêng với ${safe(profileName())}</b><span>${safe(personalSummary(r))}</span></div><button class="t12-primary" onclick="openTrustDetail('${safe(r?.date||'')}','overview')">Xem đầy đủ căn cứ ngày này</button></section>`;
  }
  function compareReason(a,b){
    if(!a||!b)return'';
    const parts=[];
    const ay=yi(a).length,by=yi(b).length,aj=ji(a).length,bj=ji(b).length;
    if(ay!==by)parts.push(`#1 có ${ay} tín hiệu hỗ trợ trực tiếp; ngày này có ${by}.`);
    if(aj!==bj)parts.push(`#1 có ${aj} tín hiệu cần tránh; ngày này có ${bj}.`);
    if(!!a?.event_context?.hard_block!==!!b?.event_context?.hard_block)parts.push(a?.event_context?.hard_block?'#1 có điều kiện chặn.':'Ngày này có điều kiện chặn trong khi #1 không có.');
    if(confidence(a)!==confidence(b))parts.push(`Mức căn cứ: #1 “${confidence(a)}”, ngày này “${confidence(b)}”.`);
    return parts.join(' ')||'Hai ngày khá gần nhau ở các khác biệt đang hiển thị; thứ tự cuối cùng vẫn lấy nguyên từ engine.';
  }
  function compareCard(r,index,top){
    return `<button class="t12-compare-card ${tone(r)}" onclick="openTrustDetail('${safe(r?.date||'')}','overview')"><span class="t12-rank">#${index+1}</span><b>${safe(shortDate(r?.date))} · ${safe(r?.conclusion?.label||'')}</b><small>${safe(index===0?decisionReason(r):compareReason(top,r))}</small><div class="t12-mini">+${yi(r).length} hỗ trợ · −${ji(r).length} cần tránh</div></button>`;
  }
  function compactRow(r){return `<button class="t12-row" onclick="openTrustDetail('${safe(r?.date||'')}','overview')"><b>${safe(shortDate(r?.date))}</b><span><strong>${safe(r?.conclusion?.label||'Chưa đủ căn cứ')}</strong><small>${safe(decisionReason(r))}</small></span><em>›</em></button>`;}
  function evidenceHtml(r){
    const ev=visibleEvidence(r);
    if(!ev.length)return'<div class="t12-empty">Ngày này chưa có evidence chi tiết gắn trực tiếp trong payload.</div>';
    return ev.map(x=>`<article class="t12-proof"><div><b>${safe(x.token||x.rule_id||'Quy tắc')}</b><span class="${x.polarity==='JI'?'bad':'good'}">${x.polarity==='JI'?'Cần tránh':'Hỗ trợ'}</span></div><p>${safe(tokenMeaning(x.token||x.rule_id,x.polarity))}</p><dl><div><dt>Trạng thái</dt><dd>${safe(evidenceStatusLabel(x.evidence_status))}</dd></div><div><dt>Nguồn</dt><dd>${safe(x.source_location||x.source_id||'Chưa ghi vị trí nguồn')}</dd></div></dl></article>`).join('');
  }
  function overviewTab(r){return `<section class="t12-detail-section"><div class="t12-detail-verdict ${tone(r)}"><small>KẾT LUẬN CHO ${safe(eventName().toUpperCase())}</small><h2>${safe(r?.conclusion?.label||'')}</h2><p>${safe(decisionReason(r))}</p></div><h3>Những gì thực sự làm nên kết quả</h3>${tokenLines(r,99)}<div class="t12-boundary"><b>Giới hạn diễn giải</b><span>UI không tự cộng điểm và không tự tạo lý do ngoài dữ liệu engine. HARD_BLOCK luôn thắng lớp sự kiện và cá nhân.</span></div></section>`;}
  function personalTab(r){const p=personalData(r);const facts=arr(p?.branch_impacts||p?.technical_facts);return `<section class="t12-detail-section"><h3>Riêng với ${safe(profileName())}</h3><p class="t12-lead">${safe(personalSummary(r))}</p>${facts.length?`<ul>${facts.map(x=>`<li>${safe(x)}</li>`).join('')}</ul>`:'<div class="t12-empty">Engine chưa trả về chi tiết cá nhân đủ rõ cho ngày này.</div>'}<div class="t12-boundary"><b>Cách hiểu đúng</b><span>Nếu lớp cá nhân chưa đủ căn cứ, app nói thẳng là chưa đủ; không giả vờ cá nhân hóa. Lớp cá nhân không cứu ngày bị HARD_BLOCK.</span></div></section>`;}
  function hourTab(r){const t=r?.technical||{};const h=r?.hour_context||r?.personal_hour||t?.hour_context||{};const items=arr(h?.items||h?.hours||h?.recommendations);return `<section class="t12-detail-section"><h3>Giờ tham khảo có căn cứ hiện tại</h3>${items.length?items.map(x=>`<div class="t12-hour"><b>${safe(x.label||x.hour||x.name||'Giờ')}</b><span>${safe(x.reason||x.state||'')}</span></div>`).join(''):'<div class="t12-empty">Chưa đủ dữ liệu giờ cá nhân để đề xuất giờ cụ thể cho ngày này.</div>'}<div class="t12-boundary"><b>Chưa phải “giờ tốt/xấu cá nhân hoàn chỉnh”</b><span>Engine hiện vẫn khóa phạm vi giờ; ngày/sự kiện luôn được xét trước và giờ không được đảo HARD_BLOCK.</span></div></section>`;}
  function sourceTab(r){const t=r?.technical||{};return `<section class="t12-detail-section"><h3>Căn cứ cổ thư & trạng thái xác minh</h3>${evidenceHtml(r)}<details class="t12-tech"><summary>Dành cho người muốn kiểm tra kỹ thuật</summary><p><b>Rule ID:</b> ${arr(r?.rules).map(safe).join(' · ')||'—'}</p><p><b>Source ID:</b> ${arr(r?.sources).map(safe).join(' · ')||'—'}</p><p><b>Decision authority:</b> ${safe(t.decision_authority||'—')}</p><p><b>Coverage:</b> ${safe(t.coverage||'—')}</p><p><b>Hiệp Kỷ:</b> ${safe(t.hiep_ky_extension||'—')}</p></details></section>`;}
  function ensureSheet(){
    if(document.getElementById('t12-sheet'))return;
    const el=document.createElement('div');el.id='t12-sheet';el.className='t12-sheet';
    el.innerHTML=`<div class="t12-backdrop" onclick="closeTrustDetail()"></div><div class="t12-panel"><header><div><small>CHI TIẾT NGÀY</small><h2 id="t12-date">—</h2></div><button onclick="closeTrustDetail()">×</button></header><nav><button data-tab="overview" onclick="switchTrustTab('overview')">Tổng quan</button><button data-tab="personal" onclick="switchTrustTab('personal')">Riêng với tôi</button><button data-tab="hour" onclick="switchTrustTab('hour')">Giờ</button><button data-tab="source" onclick="switchTrustTab('source')">Căn cứ</button></nav><main id="t12-body"></main></div>`;
    document.body.appendChild(el);
  }
  function renderDetail(){const r=resultMap.get(activeDate)||calendarMap.get(activeDate);if(!r)return;document.getElementById('t12-date').textContent=activeDate;document.getElementById('t12-body').innerHTML=activeTab==='personal'?personalTab(r):activeTab==='hour'?hourTab(r):activeTab==='source'?sourceTab(r):overviewTab(r);document.querySelectorAll('#t12-sheet nav button').forEach(b=>b.classList.toggle('active',b.dataset.tab===activeTab));}
  window.openTrustDetail=function(date,tab='overview'){ensureSheet();activeDate=date;activeTab=tab;renderDetail();document.getElementById('t12-sheet').classList.add('open');document.body.classList.add('t12-lock');};
  window.closeTrustDetail=function(){document.getElementById('t12-sheet')?.classList.remove('open');document.body.classList.remove('t12-lock');};
  window.switchTrustTab=function(tab){activeTab=tab;renderDetail();};

  function addStyles(){
    if(document.getElementById('t12-style'))return;
    const s=document.createElement('style');s.id='t12-style';s.textContent=`
      .t12-context{padding:14px 16px;border-radius:16px;background:var(--soft,#f2f6f4);display:grid;gap:4px}.t12-context b{font-size:16px}.t12-context small{color:var(--muted,#64748b)}
      .t12-hero{border:1px solid var(--line,#d8e3df);border-radius:20px;padding:18px;background:var(--card,#fff);display:grid;gap:14px}.t12-hero.good{border-top:5px solid #15836e}.t12-hero.warn{border-top:5px solid #c58a20}.t12-hero.bad{border-top:5px solid #b94b48}.t12-kicker{font-size:11px;font-weight:900;letter-spacing:.05em;color:var(--muted,#64748b)}.t12-hero-head{display:flex;justify-content:space-between;gap:12px;align-items:start}.t12-hero h2{margin:0;font-size:28px}.t12-hero strong{display:block;margin-top:3px;font-size:16px}.t12-trust{font-size:11px;background:var(--soft,#f2f6f4);padding:7px 9px;border-radius:999px}.t12-lead{font-size:15px;line-height:1.55;margin:0}.t12-signals{display:grid;gap:7px}.t12-signal{display:grid;grid-template-columns:24px 1fr;gap:8px;padding:10px;border-radius:12px;background:var(--soft,#f5f7f6)}.t12-signal>span{font-size:18px;font-weight:900}.t12-signal.good>span{color:#14745f}.t12-signal.bad>span{color:#a23f3b}.t12-signal p{margin:0;display:grid;gap:2px}.t12-signal small{color:var(--muted,#64748b);line-height:1.4}.t12-personal{padding:12px;border-left:3px solid #6b7f79;background:var(--soft,#f5f7f6);display:grid;gap:4px}.t12-personal span{font-size:13px;line-height:1.45}.t12-primary{border:0;border-radius:12px;padding:12px 14px;background:#0f766e;color:white;font-weight:800}
      .t12-section-title{margin:18px 0 8px}.t12-section-title h3{margin:0}.t12-section-title p{margin:3px 0;color:var(--muted,#64748b);font-size:13px}.t12-compare{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.t12-compare-card{border:1px solid var(--line,#d8e3df);border-radius:14px;background:var(--card,#fff);padding:12px;text-align:left;display:grid;gap:5px}.t12-compare-card.good{border-top:3px solid #15836e}.t12-compare-card.warn{border-top:3px solid #c58a20}.t12-compare-card.bad{border-top:3px solid #b94b48}.t12-rank{font-size:10px;font-weight:900;color:var(--muted,#64748b)}.t12-compare-card small{line-height:1.35;color:var(--muted,#64748b)}.t12-mini{font-size:11px;font-weight:700;margin-top:4px}.t12-list{border:1px solid var(--line,#d8e3df);border-radius:15px;overflow:hidden}.t12-row{width:100%;border:0;border-bottom:1px solid var(--line,#e5ece9);background:var(--card,#fff);display:grid;grid-template-columns:58px 1fr 20px;gap:10px;padding:11px 13px;text-align:left;align-items:center}.t12-row:last-child{border-bottom:0}.t12-row>span{display:grid;gap:2px}.t12-row small{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--muted,#64748b)}.t12-row em{font-size:22px;font-style:normal;color:var(--muted,#64748b)}.t12-empty{padding:12px;border-radius:12px;background:var(--soft,#f5f7f6);color:var(--muted,#64748b);font-size:13px}
      .t12-sheet{position:fixed;inset:0;z-index:9999;display:none}.t12-sheet.open{display:block}.t12-backdrop{position:absolute;inset:0;background:rgba(15,23,42,.42)}.t12-panel{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(720px,92vw);max-height:88vh;background:var(--card,#fff);border-radius:20px;overflow:hidden;display:grid;grid-template-rows:auto auto 1fr;box-shadow:0 24px 80px rgba(0,0,0,.24)}.t12-panel>header{display:flex;justify-content:space-between;padding:16px 18px 10px}.t12-panel>header h2{margin:2px 0}.t12-panel>header button{border:0;background:var(--soft,#f2f6f4);width:36px;height:36px;border-radius:50%;font-size:22px}.t12-panel>nav{display:flex;gap:6px;padding:0 14px 10px;overflow:auto}.t12-panel>nav button{border:0;background:transparent;padding:9px 11px;border-radius:999px;white-space:nowrap}.t12-panel>nav button.active{background:#0f766e;color:#fff}.t12-panel>main{overflow:auto;padding:0 18px 22px}.t12-detail-section{display:grid;gap:12px}.t12-detail-verdict{padding:15px;border-radius:15px;background:var(--soft,#f5f7f6)}.t12-detail-verdict h2{margin:4px 0}.t12-proof{border:1px solid var(--line,#d8e3df);border-radius:14px;padding:12px}.t12-proof>div:first-child{display:flex;justify-content:space-between;gap:8px}.t12-proof span.good{color:#14745f}.t12-proof span.bad{color:#a23f3b}.t12-proof p{font-size:13px;line-height:1.45}.t12-proof dl{display:grid;gap:5px;margin:0}.t12-proof dl>div{display:grid;grid-template-columns:90px 1fr;gap:8px;font-size:12px}.t12-proof dt{color:var(--muted,#64748b)}.t12-boundary{padding:12px;border-radius:12px;background:#fff7e7;display:grid;gap:4px;font-size:12px}.t12-hour{padding:12px;border-radius:12px;background:var(--soft,#f5f7f6);display:grid;gap:3px}.t12-tech{border-top:1px solid var(--line,#d8e3df);padding-top:10px}.t12-lock{overflow:hidden}
      @media(max-width:640px){.t12-compare{grid-template-columns:1fr}.t12-hero-head{display:grid}.t12-panel{left:0;top:auto;bottom:0;transform:none;width:100%;max-height:94vh;border-radius:18px 18px 0 0}.t12-row{grid-template-columns:50px 1fr 18px}.t12-context{border-radius:14px}.t12-hero{padding:15px;border-radius:16px}.t12-hero h2{font-size:24px}}
    `;document.head.appendChild(s);
  }

  findDates=async function(){
    if(!needProfile())return;
    $('work-result').innerHTML='<div class="card">Đang đối chiếu ngày, cá nhân và căn cứ…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
      const top=arr(d.results),all=arr(d.all_results).length?arr(d.all_results):top;resultMap=new Map(all.map(x=>[x.date,x]));
      const best=top[0];
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${safe(d.safety_note)}</div>`:''}<div class="t12-context"><small>ĐANG XEM CHO</small><b>${safe(profileName())} · ${safe(eventName())}</b><span>${safe($('work-from').value)} → ${safe($('work-to').value)} · đã xét ${safe(d.result_count??all.length)} ngày</span></div>${best?topHero(best):'<div class="card">Chưa có kết quả.</div>'}<div class="t12-section-title"><h3>So sánh 3 ngày đầu</h3><p>App chỉ mô tả những khác biệt có trong payload; thứ tự xếp hạng vẫn lấy nguyên từ engine.</p></div><div class="t12-compare">${top.map((r,i)=>compareCard(r,i,best)).join('')}</div><div class="t12-section-title"><h3>Tất cả ngày đã xét</h3><p>Bấm một ngày để xem riêng: tổng quan, cá nhân, giờ và căn cứ.</p></div><div class="t12-list">${all.map(compactRow).join('')}</div>`;
    }catch(e){$('work-result').innerHTML=`<div class="notice danger"><b>Chưa tìm được ngày</b>${safe(e.message)}<button class="btn secondary small" onclick="findDates()">Thử lại</button></div>`;}
  };

  renderCalendar=async function(){
    const eventCode=$('calendar-work')?.value||'';if(!eventCode){calendarMap=new Map();return previousRenderCalendar();}
    const y=calCursor.getFullYear(),m=calCursor.getMonth();$('cal-title').textContent=`Tháng ${m+1} / ${y}`;
    const first=new Date(y,m,1),offset=(first.getDay()+6)%7,start=new Date(y,m,1-offset),today=localISODate();
    let html=['T2','T3','T4','T5','T6','T7','CN'].map(x=>`<div class="dow">${x}</div>`).join('');
    for(let i=0;i<42;i++){const dt=new Date(start);dt.setDate(start.getDate()+i);const iso=localISODate(dt);html+=`<button id="day-${iso}" class="day ${dt.getMonth()!==m?'other':''} ${iso===today?'today':''}" onclick="selectCalendarDay('${iso}',this)"><span class="num">${dt.getDate()}</span><span class="state"><i class="day-dot neutral"></i><span class="day-state-text">…</span></span></button>`;}
    $('calendar-grid').innerHTML=html;calendarDays=[];renderCalendarList();if(!currentProfile)return;
    try{
      const from=localISODate(new Date(y,m,1)),to=localISODate(new Date(y,m+1,0));const d=await post('/api/v2/tim-ngay',{profile:current(),viec:eventCode,tu_ngay:from,den_ngay:to});const rows=arr(d.all_results);calendarMap=new Map(rows.map(x=>[x.date,x]));resultMap=new Map([...resultMap,...calendarMap]);calendarDays=rows.map(x=>({ngay:x.date,label:x.conclusion?.label||'',state:x.conclusion?.state||'',v27:x}));for(const x of calendarDays){const el=$(`day-${x.ngay}`);if(!el)continue;const st=el.querySelector('.state');if(st)st.innerHTML=`<i class="day-dot ${tone(x.v27)}"></i><span class="day-state-text">${safe(x.label)}</span>`;}renderCalendarList();$('calendar-detail').innerHTML='<div class="soft-note">Chọn một ngày để xem kết luận ngắn và mở căn cứ chi tiết.</div>';
    }catch(e){$('calendar-detail').innerHTML=`<div class="notice danger">${safe(e.message)}</div>`;}
  };
  selectCalendarDay=async function(iso,el){
    const eventCode=$('calendar-work')?.value||'';if(!eventCode)return previousSelectCalendarDay(iso,el);document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));el?.classList.add('selected');let r=calendarMap.get(iso);if(!r){const d=await post('/api/v2/tim-ngay',{profile:current(),viec:eventCode,tu_ngay:iso,den_ngay:iso});r=arr(d.all_results||d.results)[0];if(r){calendarMap.set(iso,r);resultMap.set(iso,r);}}if(!r)return;$('calendar-detail').innerHTML=`<div class="t12-context"><small>${safe(eventName())}</small><b>${safe(iso)} · ${safe(r.conclusion?.label||'')}</b><span>${safe(decisionReason(r))}</span><button class="btn" onclick="openTrustDetail('${safe(iso)}','overview')">Xem căn cứ ngày này</button></div>`;
  };
  addStyles();
})();
