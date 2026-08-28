// V2.7 — Event Search hoàn chỉnh: top 3 + toàn bộ ngày; Lịch dùng cùng nguồn quyết định khi chọn việc.
(function(){
  window.TU_BINH_EVENT_SEARCH_UI_VERSION = '2.7';
  const previousRenderCalendar = renderCalendar;
  const previousSelectCalendarDay = selectCalendarDay;
  let eventCalendarMap = new Map();

  function tone(r){
    const x=String(r?.conclusion?.label||r?.conclusion?.state||'');
    if(/Bị chặn|Không ưu tiên|HARD_BLOCK/i.test(x)) return 'bad';
    if(/Ưu tiên|Khá thuận|SUPPORT/i.test(x)) return 'good';
    if(/Cân nhắc|Thận trọng|CAUTION/i.test(x)) return 'warn';
    return 'neutral';
  }
  function confidence(r){return `<span class="v27-confidence ${tone(r)}">${esc(r?.confidence_state||'Chưa đủ căn cứ')}</span>`}
  function whyText(r){
    if(r?.event_context?.hard_block) return 'Bị loại khỏi nhóm ưu tiên vì có điều kiện chặn ở lớp sự kiện.';
    const label=r?.conclusion?.label||'';
    if(label==='Ưu tiên') return 'Được xếp nhóm ưu tiên vì lớp sự kiện và lớp cá nhân cùng ủng hộ trong phạm vi rule đang hoạt động.';
    if(label==='Có thể cân nhắc') return 'Không có điều kiện chặn, nhưng tín hiệu chưa đủ mạnh để xếp vào nhóm ưu tiên.';
    if(label==='Không ưu tiên') return 'Được giữ trong danh sách để đối chiếu, nhưng không nên chọn trước các ngày xếp hạng cao hơn.';
    return r?.plain_explanation||'Chưa có căn cứ đủ mạnh để xếp vào nhóm ưu tiên.';
  }
  function traceHtml(r){
    const rules=Array.isArray(r?.rules)?r.rules:[], sources=Array.isArray(r?.sources)?r.sources:[];
    return `<details class="v27-trace"><summary>Vì sao ngày này được xếp như vậy?</summary><p>${esc(r?.plain_explanation||whyText(r))}</p><p class="muted">${esc(whyText(r))}</p>${rules.length?`<p><b>Rule:</b> ${rules.map(esc).join(' · ')}</p>`:''}${sources.length?`<p><b>Nguồn:</b> ${sources.map(esc).join(' · ')}</p>`:''}<p class="muted">Trực ${esc(r?.technical?.truc||'—')} · phạm vi ${esc(r?.technical?.coverage||'—')}</p></details>`;
  }
  function resultCard(r,index,top=false){
    return `<article class="v27-day-card ${tone(r)}"><div class="v27-day-head"><div><small>${top?`GỢI Ý #${index+1}`:'NGÀY ĐÃ XÉT'}</small><h3>${esc(r?.date||'—')}</h3></div><span class="v27-label ${tone(r)}">${esc(r?.conclusion?.label||'Chưa đủ căn cứ')}</span></div><p><b>${esc(r?.conclusion?.title||'')}</b></p><p>${esc(r?.plain_explanation||'')}</p><div class="v27-meta">${confidence(r)}${r?.event_context?.hard_block?'<span>Điều kiện chặn</span>':''}</div>${traceHtml(r)}</article>`;
  }
  function addStyles(){
    if(document.getElementById('v27-event-style'))return;
    const s=document.createElement('style');s.id='v27-event-style';s.textContent=`
      .v27-summary{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 14px}.v27-summary span{font-size:12px;padding:6px 9px;border-radius:999px;background:var(--soft,#edf3f1)}
      .v27-day-card{padding:16px;border:1px solid var(--line,#d7e2de);border-radius:16px;margin:10px 0;background:var(--card,#fff)}.v27-day-card.good{border-left:4px solid #16856f}.v27-day-card.warn{border-left:4px solid #c38b22}.v27-day-card.bad{border-left:4px solid #b94a48}.v27-day-card.neutral{border-left:4px solid #82918e}
      .v27-day-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.v27-day-head small{font-size:11px;font-weight:800;color:var(--muted,#64748b)}.v27-day-head h3{margin:3px 0}.v27-label,.v27-confidence{font-size:12px;font-weight:800;padding:5px 9px;border-radius:999px;background:#edf3f1}.v27-label.good,.v27-confidence.good{background:#e7f6f0;color:#13725f}.v27-label.warn,.v27-confidence.warn{background:#fff4db;color:#8c6414}.v27-label.bad,.v27-confidence.bad{background:#fdebea;color:#9a3d3a}.v27-meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.v27-meta>span{font-size:12px}.v27-trace{margin-top:10px}.v27-trace summary{cursor:pointer;font-weight:750}.v27-all summary{cursor:pointer;font-weight:800;padding:8px 0}.v27-calendar-note{margin:8px 0 12px;font-size:12px;color:var(--muted,#64748b)}
    `;document.head.appendChild(s);
  }

  findDates=async function(){
    if(!needProfile())return;
    $('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
      const top=Array.isArray(d.results)?d.results:[], all=Array.isArray(d.all_results)?d.all_results:top;
      const counts=d.group_counts||{};
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${esc(d.safety_note)}</div>`:''}<div class="card"><span class="v2-kicker">3 lựa chọn nên xem trước</span><p class="muted">Xếp hạng theo HARD_BLOCK → sự kiện → cá nhân; không dùng điểm số. App đã xét ${esc(d.result_count??all.length)} ngày.</p><div class="v27-summary">${Object.entries(counts).map(([k,v])=>`<span>${esc(k)}: <b>${esc(v)}</b></span>`).join('')}</div>${top.map((r,i)=>resultCard(r,i,true)).join('')||'<div class="muted">Chưa có kết quả.</div>'}<details class="v27-all"><summary>Xem tất cả ${esc(all.length)} ngày đã xét</summary><p class="muted">Danh sách giữ nguyên thứ tự xếp hạng. Ngày bị chặn hoặc không ưu tiên vẫn được hiển thị để biết vì sao bị loại.</p>${all.map((r,i)=>resultCard(r,i,false)).join('')}</details></div>`;
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
      const rows=Array.isArray(r.all_results)?r.all_results:[];eventCalendarMap=new Map(rows.map(x=>[x.date,x]));
      calendarDays=rows.slice().sort((a,b)=>String(a.date).localeCompare(String(b.date))).map(x=>({ngay:x.date,label:x.conclusion?.label||'Chưa đủ căn cứ',state:x.conclusion?.state||'',v27:x}));
      for(const x of calendarDays){const el=$(`day-${x.ngay}`);if(!el)continue;const t=tone(x.v27),st=el.querySelector('.state');if(st)st.innerHTML=`<i class="day-dot ${t}"></i><span class="day-state-text">${esc(x.label)}</span>`;el.dataset.tone=t;el.title=x.label}
      renderCalendarList();
      const detail=$('calendar-detail');if(detail)detail.innerHTML=`<div class="v27-calendar-note">Lịch đang đánh giá theo đúng loại việc đã chọn bằng cùng engine Event Search V2.5. Chọn một ngày để xem lý do.</div>`;
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
      $('calendar-detail').innerHTML=`<div class="v2-hero ${tone(r)}"><small>CHI TIẾT NGÀY ${esc(iso)} · THEO VIỆC ĐÃ CHỌN</small><h2>${esc(r.conclusion?.title||r.conclusion?.label||'Chưa đủ căn cứ')}</h2><p>${esc(r.plain_explanation||'')}</p><div class="v27-meta">${confidence(r)}<span>${esc(r.conclusion?.label||'')}</span>${r.event_context?.hard_block?'<span>Điều kiện chặn</span>':''}</div></div><div class="card">${traceHtml(r)}</div>`;
    }catch(e){$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tính được ngày này theo việc đã chọn</b>${esc(e.message)}</div>`}
  };

  addStyles();
})();
