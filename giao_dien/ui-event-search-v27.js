// UI Decision V1.1 — quyết định trước, chi tiết sau. Chỉ trình bày dữ liệu engine, không tự tính lại quyết định.
(function(){
  window.TU_BINH_EVENT_SEARCH_UI_VERSION = '3.1-ui-v1.1';
  const previousRenderCalendar = renderCalendar;
  const previousSelectCalendarDay = selectCalendarDay;
  let eventCalendarMap = new Map();
  let detailMap = new Map();
  let activeDetailDate = '';
  let activeDetailTab = 'overview';

  function arr(v){return Array.isArray(v)?v:[]}
  function tone(r){
    const x=String(r?.conclusion?.label||r?.conclusion?.state||'');
    if(/Bị chặn|Không ưu tiên|HARD_BLOCK/i.test(x)) return 'bad';
    if(/Ưu tiên|Khá thuận|SUPPORT/i.test(x)) return 'good';
    if(/Cân nhắc|Thận trọng|CAUTION/i.test(x)) return 'warn';
    return 'neutral';
  }
  function shortDate(v){
    const s=String(v||''); const m=s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m?`${m[3]}/${m[2]}`:s;
  }
  function evidenceLabel(status){
    if(status==='VERIFIED') return 'Đã xác minh';
    if(status==='PROVISIONAL') return 'Tạm dùng / cần đối chiếu thêm';
    if(status==='PENDING') return 'Đang chờ xác minh';
    return status||'Chưa ghi trạng thái';
  }
  function whyText(r){
    if(r?.event_context?.hard_block) return 'Ngày này có điều kiện chặn ở lớp sự kiện; tín hiệu thuận khác không được dùng để đảo ngược điều kiện chặn.';
    const yi=arr(r?.technical?.matched_yi_tokens), ji=arr(r?.technical?.matched_ji_tokens);
    if(yi.length && !ji.length) return `Có ${yi.slice(0,2).join(', ')} hỗ trợ trực tiếp cho việc đã chọn.`;
    if(yi.length && ji.length) return `Có yếu tố hỗ trợ nhưng đồng thời có ${ji.slice(0,2).join(', ')} cần cân nhắc.`;
    if(ji.length) return `Có ${ji.slice(0,2).join(', ')} cần thận trọng.`;
    return r?.plain_explanation||'Chưa có tín hiệu đủ mạnh để xếp ưu tiên.';
  }
  function reasonChips(r){
    const yi=arr(r?.technical?.matched_yi_tokens).slice(0,2);
    const ji=arr(r?.technical?.matched_ji_tokens).slice(0,2);
    const chips=[...yi.map(x=>`<span class="u11-chip good">+ ${esc(x)}</span>`),...ji.map(x=>`<span class="u11-chip bad">− ${esc(x)}</span>`)];
    return chips.length?chips.join(''):`<span class="u11-chip neutral">${esc(r?.confidence_state||'Chưa đủ căn cứ')}</span>`;
  }
  function compactTopCard(r,index){
    return `<button class="u11-top-card ${tone(r)}" onclick="openDayDetail('${esc(r?.date||'')}','overview')"><span class="u11-rank">#${index+1}</span><span class="u11-top-date">${esc(shortDate(r?.date))}</span><strong>${esc(r?.conclusion?.label||'Chưa đủ căn cứ')}</strong><small>${esc(whyText(r))}</small><span class="u11-open">Xem chi tiết ›</span></button>`;
  }
  function compactRow(r){
    return `<button class="u11-row" onclick="openDayDetail('${esc(r?.date||'')}','overview')"><span class="u11-row-date">${esc(shortDate(r?.date))}</span><span class="u11-row-main"><b>${esc(r?.conclusion?.label||'Chưa đủ căn cứ')}</b><small>${esc(whyText(r))}</small><span class="u11-chips">${reasonChips(r)}</span></span><span class="u11-chevron">›</span></button>`;
  }
  function confidenceBlock(r){
    const basis=arr(r?.confidence_basis);
    return `<div class="u11-note"><b>Mức căn cứ: ${esc(r?.confidence_state||'Chưa đủ căn cứ')}</b>${basis.length?`<ul>${basis.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}</div>`;
  }
  function overviewTab(r){
    const yi=arr(r?.technical?.matched_yi_tokens), ji=arr(r?.technical?.matched_ji_tokens), reasons=arr(r?.reasons);
    return `<div class="u11-detail-hero ${tone(r)}"><small>KẾT LUẬN</small><h2>${esc(r?.conclusion?.label||'Chưa đủ căn cứ')}</h2><p>${esc(r?.plain_explanation||whyText(r))}</p>${r?.event_context?.hard_block?'<div class="u11-block">Điều kiện chặn đang có hiệu lực. Tín hiệu thuận ở lớp khác không được cứu ngày này.</div>':''}</div><section class="u11-section"><h3>Vì sao?</h3><div class="u11-reason-grid"><div><b>Hỗ trợ</b>${yi.length?`<ul>${yi.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:'<p class="muted">Chưa ghi nhận yếu tố hỗ trợ trực tiếp.</p>'}</div><div><b>Cần tránh</b>${ji.length?`<ul>${ji.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:'<p class="muted">Chưa ghi nhận yếu tố cảnh báo trực tiếp.</p>'}</div></div>${reasons.length?`<details><summary>Diễn giải đầy đủ từ engine</summary><ul>${reasons.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>`:''}${confidenceBlock(r)}</section>`;
  }
  function personalTab(r){
    const p=r?.personal_context||r?.personal_v1_1||r?.technical?.personal_context||{};
    const headline=p?.headline||r?.personal_explanation||'';
    const impacts=arr(p?.branch_impacts||p?.technical_facts);
    const effect=p?.decision_effect||r?.technical?.personal_state||'';
    return `<section class="u11-section"><h3>Cá nhân Tử Bình</h3>${headline?`<p>${esc(headline)}</p>`:'<p class="muted">Không có diễn giải cá nhân bổ sung cho ngày này.</p>'}${effect?`<div class="u11-note"><b>Vai trò trong quyết định</b><p>${esc(effect)}</p></div>`:''}${impacts.length?`<ul>${impacts.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}<div class="u11-policy">Lớp cá nhân chỉ bổ sung bối cảnh; không được cứu ngày đã bị HARD_BLOCK hoặc đảo tín hiệu kiêng ở lớp sự kiện.</div></section>`;
  }
  function hourTab(r){
    const t=r?.technical||{};
    const hour=r?.hour_context||r?.personal_hour||t?.hour_context||{};
    const items=arr(hour?.items||hour?.hours||hour?.recommendations);
    const status=hour?.status||t?.personal_hour_status||t?.hour_status||'';
    if(!items.length && !status) return `<section class="u11-section"><h3>Giờ trong ngày</h3><p class="muted">Phiên bản hiện tại chưa có đủ dữ liệu giờ cá nhân để đưa ra lựa chọn giờ cho kết quả này.</p><div class="u11-policy">Ngày/sự kiện luôn được xét trước giờ; giờ không được đảo kết luận HARD_BLOCK của ngày.</div></section>`;
    return `<section class="u11-section"><h3>Giờ trong ngày</h3>${status?`<p><b>Trạng thái:</b> ${esc(status)}</p>`:''}${items.length?`<div class="u11-hour-list">${items.map(x=>`<div><b>${esc(x.label||x.hour||x.name||'Giờ')}</b><span>${esc(x.reason||x.state||'')}</span></div>`).join('')}</div>`:''}<div class="u11-policy">Ngày/sự kiện luôn được xét trước giờ; giờ không được đảo kết luận HARD_BLOCK của ngày.</div></section>`;
  }
  function sourceTab(r){
    const t=r?.technical||{}; const evidence=arr(t.matched_evidence); const rules=arr(r?.rules), sources=arr(r?.sources);
    return `<section class="u11-section"><h3>Nguồn & quy tắc</h3>${evidence.length?evidence.map(x=>`<div class="u11-source"><div><b>${esc(x.token||x.rule_id||'Quy tắc')}</b><small>${esc(x.polarity==='JI'?'Cần tránh':'Hỗ trợ')}</small></div><div><span>${esc(evidenceLabel(x.evidence_status))}</span><small>${esc(x.source_location||x.source_id||'')}</small></div></div>`).join(''):'<p class="muted">Không có evidence chi tiết gắn trực tiếp với ngày này.</p>'}${rules.length?`<p><b>Rule ID:</b> ${rules.map(esc).join(' · ')}</p>`:''}${sources.length?`<p><b>Source ID:</b> ${sources.map(esc).join(' · ')}</p>`:''}<details class="u11-tech"><summary>Chi tiết kỹ thuật</summary><div class="u11-tech-grid"><div><b>Thẩm quyền</b><span>${esc(t.decision_authority||'—')}</span></div><div><b>Tín hiệu sự kiện</b><span>${esc(t.event_signal_v25||'—')}</span></div><div><b>Trạng thái V1</b><span>${esc(t.event_state_v1||'—')}</span></div><div><b>Trực</b><span>${esc(t.truc||'—')}</span></div><div><b>Coverage</b><span>${esc(t.coverage||'—')}</span></div><div><b>Hiệp Kỷ</b><span>${esc(t.hiep_ky_extension||'—')}</span></div></div><p class="muted">Không hiển thị điểm tổng hợp; UI giữ nguyên thứ bậc HARD_BLOCK → sự kiện → cá nhân.</p></details></section>`;
  }
  function detailBody(r,tab){
    if(tab==='personal')return personalTab(r);
    if(tab==='hour')return hourTab(r);
    if(tab==='source')return sourceTab(r);
    return overviewTab(r);
  }
  function ensureDetailSheet(){
    if(document.getElementById('u11-detail-sheet')) return;
    const el=document.createElement('div'); el.id='u11-detail-sheet'; el.className='u11-sheet';
    el.innerHTML=`<div class="u11-backdrop" onclick="closeDayDetail()"></div><div class="u11-panel"><div class="u11-handle"></div><div class="u11-panel-head"><div><small>CHI TIẾT NGÀY</small><h2 id="u11-detail-date">—</h2></div><button class="u11-close" onclick="closeDayDetail()" aria-label="Đóng">×</button></div><div class="u11-tabs"><button data-tab="overview" onclick="switchDayDetailTab('overview')">Tổng quan</button><button data-tab="personal" onclick="switchDayDetailTab('personal')">Cá nhân</button><button data-tab="hour" onclick="switchDayDetailTab('hour')">Giờ</button><button data-tab="source" onclick="switchDayDetailTab('source')">Nguồn</button></div><div id="u11-detail-body" class="u11-panel-body"></div></div>`;
    document.body.appendChild(el);
  }
  window.openDayDetail=function(date,tab='overview'){
    const r=detailMap.get(date)||eventCalendarMap.get(date); if(!r)return;
    ensureDetailSheet(); activeDetailDate=date; activeDetailTab=tab;
    document.getElementById('u11-detail-date').textContent=date;
    document.getElementById('u11-detail-body').innerHTML=detailBody(r,tab);
    document.querySelectorAll('#u11-detail-sheet .u11-tabs button').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));
    document.getElementById('u11-detail-sheet').classList.add('open'); document.body.classList.add('u11-no-scroll');
  };
  window.closeDayDetail=function(){const el=document.getElementById('u11-detail-sheet');if(el)el.classList.remove('open');document.body.classList.remove('u11-no-scroll')};
  window.switchDayDetailTab=function(tab){if(activeDetailDate)openDayDetail(activeDetailDate,tab)};

  function addStyles(){
    if(document.getElementById('u11-style'))return;
    const s=document.createElement('style'); s.id='u11-style'; s.textContent=`
      .u11-result{display:grid;gap:14px}.u11-header{display:flex;justify-content:space-between;gap:10px;align-items:end}.u11-header h3{margin:2px 0}.u11-header small{color:var(--muted,#64748b)}
      .u11-top-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.u11-top-card{appearance:none;text-align:left;border:1px solid var(--line,#d7e2de);border-radius:16px;padding:14px;background:var(--card,#fff);display:flex;flex-direction:column;gap:5px;min-height:150px}.u11-top-card.good{border-top:4px solid #16856f}.u11-top-card.warn{border-top:4px solid #c38b22}.u11-top-card.bad{border-top:4px solid #b94a48}.u11-top-card.neutral{border-top:4px solid #82918e}.u11-rank{font-size:11px;font-weight:900;color:var(--muted,#64748b)}.u11-top-date{font-size:22px;font-weight:900}.u11-top-card strong{font-size:14px}.u11-top-card small{line-height:1.35;color:var(--muted,#64748b);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.u11-open{margin-top:auto;font-size:12px;font-weight:800}
      .u11-list{border:1px solid var(--line,#d7e2de);border-radius:16px;overflow:hidden;background:var(--card,#fff)}.u11-list-title{padding:13px 14px;border-bottom:1px solid var(--line,#d7e2de);display:flex;justify-content:space-between}.u11-row{width:100%;appearance:none;border:0;border-bottom:1px solid var(--line,#e5ece9);background:transparent;padding:12px 14px;display:grid;grid-template-columns:58px 1fr 18px;gap:10px;text-align:left;align-items:center}.u11-row:last-child{border-bottom:0}.u11-row-date{font-size:16px;font-weight:900}.u11-row-main{min-width:0;display:flex;flex-direction:column;gap:3px}.u11-row-main>b{font-size:14px}.u11-row-main>small{color:var(--muted,#64748b);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.u11-chevron{font-size:24px;color:var(--muted,#64748b)}.u11-chips{display:flex;gap:5px;flex-wrap:wrap;margin-top:2px}.u11-chip{font-size:10px;border-radius:999px;padding:3px 6px;background:var(--soft,#edf3f1)}.u11-chip.good{color:#13725f;background:#e7f6f0}.u11-chip.bad{color:#9a3d3a;background:#fdebea}.u11-chip.neutral{color:#64748b}
      .u11-sheet{position:fixed;inset:0;z-index:9999;pointer-events:none;visibility:hidden}.u11-sheet.open{pointer-events:auto;visibility:visible}.u11-backdrop{position:absolute;inset:0;background:rgba(15,23,42,.42);opacity:0;transition:.2s}.u11-sheet.open .u11-backdrop{opacity:1}.u11-panel{position:absolute;left:50%;bottom:0;transform:translate(-50%,105%);width:min(720px,100%);max-height:88vh;background:var(--card,#fff);border-radius:22px 22px 0 0;box-shadow:0 -18px 50px rgba(15,23,42,.18);transition:.24s;display:flex;flex-direction:column}.u11-sheet.open .u11-panel{transform:translate(-50%,0)}.u11-handle{width:42px;height:4px;border-radius:999px;background:#cbd5e1;margin:8px auto 2px}.u11-panel-head{padding:8px 16px 10px;display:flex;justify-content:space-between;align-items:center}.u11-panel-head small{font-size:10px;color:var(--muted,#64748b);font-weight:800}.u11-panel-head h2{margin:2px 0}.u11-close{border:0;background:var(--soft,#edf3f1);width:36px;height:36px;border-radius:50%;font-size:24px}.u11-tabs{display:grid;grid-template-columns:repeat(4,1fr);padding:0 12px;border-bottom:1px solid var(--line,#d7e2de)}.u11-tabs button{border:0;background:transparent;padding:11px 4px;font-weight:700;color:var(--muted,#64748b);border-bottom:3px solid transparent}.u11-tabs button.active{color:inherit;border-bottom-color:#16856f}.u11-panel-body{overflow:auto;padding:14px 16px 28px}.u11-detail-hero{padding:15px;border-radius:16px;background:var(--soft,#f4f7f6);border-left:5px solid #82918e}.u11-detail-hero.good{border-color:#16856f}.u11-detail-hero.warn{border-color:#c38b22}.u11-detail-hero.bad{border-color:#b94a48}.u11-detail-hero h2{margin:4px 0 6px}.u11-section{padding:14px 2px}.u11-section h3{margin:0 0 10px}.u11-reason-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.u11-reason-grid>div,.u11-note,.u11-policy{background:var(--soft,#f4f7f6);border-radius:12px;padding:11px}.u11-block{margin-top:10px;background:#fdebea;color:#893936;padding:9px 11px;border-radius:10px;font-weight:700}.u11-policy{font-size:12px;margin-top:12px}.u11-source{display:grid;grid-template-columns:1fr 1.2fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line,#e5ece9)}.u11-source>div{display:flex;flex-direction:column}.u11-source small{color:var(--muted,#64748b)}.u11-tech{margin-top:14px}.u11-tech summary{font-weight:800}.u11-tech-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.u11-tech-grid>div{display:flex;flex-direction:column;padding:9px;background:var(--soft,#f4f7f6);border-radius:10px}.u11-tech-grid span{font-size:12px;word-break:break-word}.u11-hour-list{display:grid;gap:8px}.u11-hour-list>div{display:flex;justify-content:space-between;gap:10px;padding:10px;background:var(--soft,#f4f7f6);border-radius:10px}.u11-no-scroll{overflow:hidden}
      .u11-calendar-note{font-size:12px;color:var(--muted,#64748b);margin:6px 0 10px}
      @media(max-width:640px){.u11-top-grid{grid-template-columns:1fr}.u11-top-card{min-height:auto;display:grid;grid-template-columns:46px 1fr auto;grid-template-areas:'rank date label' 'reason reason reason' 'open open open';gap:4px 8px}.u11-rank{grid-area:rank}.u11-top-date{grid-area:date;font-size:18px}.u11-top-card strong{grid-area:label}.u11-top-card small{grid-area:reason;-webkit-line-clamp:2}.u11-open{grid-area:open}.u11-panel{max-height:94vh;height:94vh;border-radius:18px 18px 0 0}.u11-reason-grid,.u11-tech-grid,.u11-source{grid-template-columns:1fr}.u11-row{grid-template-columns:52px 1fr 16px}.u11-row-main>small{max-width:calc(100vw - 130px)}}
    `; document.head.appendChild(s);
  }

  findDates=async function(){
    if(!needProfile())return;
    $('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
      const top=arr(d.results), all=arr(d.all_results).length?arr(d.all_results):top;
      detailMap=new Map(all.map(x=>[x.date,x]));
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${esc(d.safety_note)}</div>`:''}<div class="u11-result"><div class="card"><div class="u11-header"><div><small>KẾT QUẢ ƯU TIÊN</small><h3>3 ngày nên xem trước</h3></div><small>Đã xét ${esc(d.result_count??all.length)} ngày</small></div><p class="muted">Chọn nhanh trước; chỉ mở chi tiết khi cần. UI không tự cộng điểm hay tự suy lại kết quả.</p><div class="u11-top-grid">${top.map((r,i)=>compactTopCard(r,i)).join('')||'<div class="muted">Chưa có kết quả.</div>'}</div></div><div class="u11-list"><div class="u11-list-title"><b>Tất cả ngày đã xét</b><small>${esc(all.length)} ngày</small></div>${all.map(compactRow).join('')}</div></div>`;
    }catch(e){$('work-result').innerHTML=`<div class="notice danger"><b>Chưa tìm được ngày</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="findDates()">Thử lại</button></div>`}
  };

  renderCalendar=async function(){
    const eventCode=$('calendar-work')?.value||'';
    if(!eventCode){eventCalendarMap=new Map();return previousRenderCalendar()}
    const y=calCursor.getFullYear(),m=calCursor.getMonth(),title=$('cal-title');if(title)title.textContent=`Tháng ${m+1} / ${y}`;
    const first=new Date(y,m,1),offset=(first.getDay()+6)%7,start=new Date(y,m,1-offset),today=localISODate();
    let html=['T2','T3','T4','T5','T6','T7','CN'].map(x=>`<div class="dow">${x}</div>`).join('');
    for(let i=0;i<42;i++){const d=new Date(start);d.setDate(start.getDate()+i);const iso=localISODate(d);html+=`<button id="day-${iso}" class="day ${d.getMonth()!==m?'other':''} ${iso===today?'today':''}" onclick="selectCalendarDay('${iso}',this)"><span class="num">${d.getDate()}</span><span class="state"><i class="day-dot neutral"></i><span class="day-state-text">Đang tính</span></span></button>`}
    $('calendar-grid').innerHTML=html;calendarDays=[];renderCalendarList();if(!currentProfile)return;
    const from=localISODate(new Date(y,m,1)),to=localISODate(new Date(y,m+1,0));
    try{
      const r=await post('/api/v2/tim-ngay',{profile:current(),viec:eventCode,tu_ngay:from,den_ngay:to});
      const rows=arr(r.all_results);eventCalendarMap=new Map(rows.map(x=>[x.date,x]));detailMap=new Map([...detailMap,...eventCalendarMap]);
      calendarDays=rows.slice().sort((a,b)=>String(a.date).localeCompare(String(b.date))).map(x=>({ngay:x.date,label:x.conclusion?.label||'Chưa đủ căn cứ',state:x.conclusion?.state||'',v27:x}));
      for(const x of calendarDays){const el=$(`day-${x.ngay}`);if(!el)continue;const t=tone(x.v27),st=el.querySelector('.state');if(st)st.innerHTML=`<i class="day-dot ${t}"></i><span class="day-state-text">${esc(x.label)}</span>`;el.dataset.tone=t;el.title=x.label}
      renderCalendarList();
      $('calendar-detail').innerHTML='<div class="u11-calendar-note">Chọn một ngày để xem kết luận ngắn; bấm “Xem chi tiết” để mở Tổng quan · Cá nhân · Giờ · Nguồn.</div>';
    }catch(e){eventCalendarMap=new Map();$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tải được lịch theo việc đã chọn</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="renderCalendar()">Thử lại</button></div>`}
  };

  selectCalendarDay=async function(iso,el){
    const eventCode=$('calendar-work')?.value||'';
    if(!eventCode)return previousSelectCalendarDay(iso,el);
    document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));if(el)el.classList.add('selected');if(!needProfile())return;
    $('calendar-detail').innerHTML='Đang tính…';
    try{
      let r=eventCalendarMap.get(iso);
      if(!r){const d=await post('/api/v2/tim-ngay',{profile:current(),viec:eventCode,tu_ngay:iso,den_ngay:iso});r=(d.all_results||d.results||[])[0]}
      if(!r)throw new Error('Chưa có kết quả cho ngày này.');
      eventCalendarMap.set(iso,r);detailMap.set(iso,r);
      $('calendar-detail').innerHTML=`<div class="u11-detail-hero ${tone(r)}"><small>${esc(iso)} · THEO VIỆC ĐÃ CHỌN</small><h2>${esc(r.conclusion?.label||'Chưa đủ căn cứ')}</h2><p>${esc(whyText(r))}</p><button class="btn full-btn" onclick="openDayDetail('${esc(iso)}','overview')">Xem chi tiết ngày</button></div>`;
    }catch(e){$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tính được ngày này theo việc đã chọn</b>${esc(e.message)}</div>`}
  };

  addStyles(); ensureDetailSheet();
})();
