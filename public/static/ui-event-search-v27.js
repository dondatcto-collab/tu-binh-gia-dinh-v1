// UI Decision V1 trên nền Event Search V2.7/V2.8 — chỉ trình bày dữ liệu engine, không tự tính lại quyết định.
(function(){
  window.TU_BINH_EVENT_SEARCH_UI_VERSION = '3.0-ui-v1';
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
    if(r?.event_context?.hard_block) return 'Ngày này bị chặn ở lớp sự kiện. Các tín hiệu thuận khác không được dùng để đảo ngược điều kiện chặn.';
    const label=r?.conclusion?.label||'';
    if(label==='Ưu tiên') return 'Ngày này được xếp nhóm ưu tiên theo kết luận đã trả về từ engine trong phạm vi quy tắc đang hoạt động.';
    if(label==='Có thể cân nhắc') return 'Không có điều kiện chặn, nhưng còn tín hiệu cần cân nhắc hoặc mức căn cứ chưa đủ để xếp ưu tiên.';
    if(label==='Không ưu tiên') return 'Có tín hiệu cần thận trọng; nên xem các ngày xếp hạng cao hơn trước.';
    return r?.plain_explanation||'Chưa có căn cứ đủ mạnh để xếp vào nhóm ưu tiên.';
  }
  function arr(v){return Array.isArray(v)?v:[]}
  function listHtml(items, emptyText){return items.length?`<ul>${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:`<p class="muted">${esc(emptyText)}</p>`}
  function evidenceLabel(status){
    if(status==='VERIFIED') return 'Đã xác minh';
    if(status==='PROVISIONAL') return 'Tạm dùng / cần đối chiếu thêm';
    if(status==='PENDING') return 'Đang chờ xác minh';
    return status||'Chưa ghi trạng thái';
  }
  function confidenceBasisHtml(r){
    const basis=arr(r?.confidence_basis);
    if(!basis.length)return '';
    return `<div class="v28-confidence-basis"><b>Vì sao mức căn cứ là ${esc(r?.confidence_state||'Chưa đủ căn cứ')}?</b>${listHtml(basis,'Chưa có diễn giải mức căn cứ.')}</div>`;
  }
  function decisionLayerHtml(r){
    const label=r?.conclusion?.label||'Chưa đủ căn cứ';
    return `<section class="ui-v1-layer ui-v1-decision"><div class="ui-v1-layer-title"><span>1</span><b>Kết luận</b></div><div class="ui-v1-decision-row"><strong class="v27-label ${tone(r)}">${esc(label)}</strong>${confidence(r)}</div><p>${esc(r?.plain_explanation||whyText(r))}</p>${r?.event_context?.hard_block?'<div class="ui-v1-block-note">Điều kiện chặn đang có hiệu lực. Tín hiệu thuận ở lớp khác không được đảo ngược kết luận này.</div>':''}</section>`;
  }
  function reasonLayerHtml(r){
    const tech=r?.technical||{};
    const yi=arr(tech.matched_yi_tokens), ji=arr(tech.matched_ji_tokens);
    const reasons=arr(r?.reasons);
    return `<section class="ui-v1-layer"><div class="ui-v1-layer-title"><span>2</span><b>Vì sao?</b></div><p>${esc(whyText(r))}</p><div class="ui-v1-two-col"><div><b>Yếu tố hỗ trợ</b>${yi.length?listHtml(yi,''): '<p class="muted">Chưa ghi nhận rule hỗ trợ trực tiếp cho việc này.</p>'}</div><div><b>Yếu tố cần tránh</b>${ji.length?listHtml(ji,''): '<p class="muted">Chưa ghi nhận rule cảnh báo trực tiếp cho việc này.</p>'}</div></div>${reasons.length?`<details><summary>Diễn giải đầy đủ từ engine</summary>${listHtml(reasons,'')}</details>`:''}${confidenceBasisHtml(r)}</section>`;
  }
  function personalLayerHtml(r){
    const p=r?.personal_context||r?.personal_v1_1||r?.technical?.personal_context||{};
    const headline=p?.headline||r?.personal_explanation||'';
    const impacts=arr(p?.branch_impacts||p?.technical_facts);
    const effect=p?.decision_effect||r?.technical?.personal_state||'';
    return `<section class="ui-v1-layer"><div class="ui-v1-layer-title"><span>3</span><b>Cá nhân Tử Bình</b></div>${headline?`<p>${esc(headline)}</p>`:'<p class="muted">Không có diễn giải cá nhân bổ sung cho kết quả này.</p>'}${effect?`<p><b>Vai trò trong quyết định:</b> ${esc(effect)}</p>`:''}${impacts.length?listHtml(impacts,''):''}<p class="ui-v1-policy-note">Lớp cá nhân chỉ bổ sung bối cảnh; không được cứu ngày đã bị HARD_BLOCK hoặc đảo tín hiệu kiêng ở lớp sự kiện.</p></section>`;
  }
  function sourceLayerHtml(r){
    const evidence=arr(r?.technical?.matched_evidence);
    const rules=arr(r?.rules), sources=arr(r?.sources);
    const rows=evidence.map(x=>`<div class="ui-v1-source-row"><div><b>${esc(x.token||x.rule_id||'Quy tắc')}</b><small>${esc(x.polarity==='JI'?'Cần tránh':'Hỗ trợ')}</small></div><div><span>${esc(evidenceLabel(x.evidence_status))}</span><small>${esc(x.source_location||x.source_id||'')}</small></div></div>`).join('');
    return `<section class="ui-v1-layer"><div class="ui-v1-layer-title"><span>4</span><b>Nguồn & quy tắc</b></div>${rows||'<p class="muted">Không có evidence chi tiết gắn trực tiếp với ngày này.</p>'}${rules.length?`<p><b>Rule ID:</b> ${rules.map(esc).join(' · ')}</p>`:''}${sources.length?`<p><b>Source ID:</b> ${sources.map(esc).join(' · ')}</p>`:''}</section>`;
  }
  function technicalLayerHtml(r){
    const t=r?.technical||{};
    return `<details class="ui-v1-technical"><summary>5 · Chi tiết kỹ thuật</summary><div class="ui-v1-tech-grid"><div><b>Thẩm quyền quyết định</b><span>${esc(t.decision_authority||'—')}</span></div><div><b>Tín hiệu sự kiện</b><span>${esc(t.event_signal_v25||'—')}</span></div><div><b>Trạng thái V1</b><span>${esc(t.event_state_v1||'—')}</span></div><div><b>Trực</b><span>${esc(t.truc||'—')}</span></div><div><b>Coverage</b><span>${esc(t.coverage||'—')}</span></div><div><b>Hiệp Kỷ extension</b><span>${esc(t.hiep_ky_extension||'—')}</span></div></div><p class="muted">Không hiển thị điểm tổng hợp: engine đang khóa numeric score và dùng thứ bậc HARD_BLOCK → sự kiện → cá nhân.</p></details>`;
  }
  function layeredResultHtml(r){return `<div class="ui-v1-stack">${decisionLayerHtml(r)}${reasonLayerHtml(r)}${personalLayerHtml(r)}${sourceLayerHtml(r)}${technicalLayerHtml(r)}</div>`}
  function traceHtml(r){return `<details class="v27-trace"><summary>Xem 5 lớp căn cứ</summary>${layeredResultHtml(r)}</details>`}
  function resultCard(r,index,top=false){
    return `<article class="v27-day-card ${tone(r)}"><div class="v27-day-head"><div><small>${top?`GỢI Ý #${index+1}`:'NGÀY ĐÃ XÉT'}</small><h3>${esc(r?.date||'—')}</h3></div><span class="v27-label ${tone(r)}">${esc(r?.conclusion?.label||'Chưa đủ căn cứ')}</span></div><p><b>${esc(r?.conclusion?.title||'')}</b></p><p>${esc(r?.plain_explanation||'')}</p><div class="v27-meta">${confidence(r)}${r?.event_context?.hard_block?'<span>Điều kiện chặn</span>':''}</div>${traceHtml(r)}</article>`;
  }
  function addStyles(){
    if(document.getElementById('v27-event-style'))return;
    const s=document.createElement('style');s.id='v27-event-style';s.textContent=`
      .v27-summary{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 14px}.v27-summary span{font-size:12px;padding:6px 9px;border-radius:999px;background:var(--soft,#edf3f1)}
      .v27-day-card{padding:16px;border:1px solid var(--line,#d7e2de);border-radius:16px;margin:10px 0;background:var(--card,#fff)}.v27-day-card.good{border-left:4px solid #16856f}.v27-day-card.warn{border-left:4px solid #c38b22}.v27-day-card.bad{border-left:4px solid #b94a48}.v27-day-card.neutral{border-left:4px solid #82918e}
      .v27-day-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.v27-day-head small{font-size:11px;font-weight:800;color:var(--muted,#64748b)}.v27-day-head h3{margin:3px 0}.v27-label,.v27-confidence{font-size:12px;font-weight:800;padding:5px 9px;border-radius:999px;background:#edf3f1}.v27-label.good,.v27-confidence.good{background:#e7f6f0;color:#13725f}.v27-label.warn,.v27-confidence.warn{background:#fff4db;color:#8c6414}.v27-label.bad,.v27-confidence.bad{background:#fdebea;color:#9a3d3a}.v27-meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.v27-meta>span{font-size:12px}.v27-trace{margin-top:12px;border-top:1px solid var(--line,#d7e2de);padding-top:10px}.v27-trace>summary{cursor:pointer;font-weight:800}.v27-all summary{cursor:pointer;font-weight:800;padding:8px 0}.v27-calendar-note{margin:8px 0 12px;font-size:12px;color:var(--muted,#64748b)}
      .v28-confidence-basis{margin:10px 0;padding:10px 12px;border-radius:12px;background:var(--soft,#f4f7f6)}.v28-confidence-basis b{font-size:13px}.v28-confidence-basis ul{margin:6px 0 0;padding-left:20px}.v28-confidence-basis li{margin:4px 0;font-size:12px}
      .ui-v1-stack{margin-top:12px;display:grid;gap:10px}.ui-v1-layer,.ui-v1-technical{border:1px solid var(--line,#d7e2de);border-radius:14px;padding:13px;background:var(--card,#fff)}.ui-v1-layer-title{display:flex;align-items:center;gap:8px;margin-bottom:8px}.ui-v1-layer-title>span{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--soft,#edf3f1);font-size:12px;font-weight:900}.ui-v1-decision-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.ui-v1-two-col{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}.ui-v1-two-col>div{padding:10px;border-radius:12px;background:var(--soft,#f4f7f6)}.ui-v1-layer ul{margin:6px 0;padding-left:20px}.ui-v1-layer li{margin:4px 0}.ui-v1-policy-note,.ui-v1-block-note{padding:9px 11px;border-radius:10px;background:var(--soft,#f4f7f6);font-size:12px}.ui-v1-block-note{background:#fdebea;color:#893936;font-weight:700}.ui-v1-source-row{display:grid;grid-template-columns:1fr 1.2fr;gap:10px;padding:9px 0;border-bottom:1px solid var(--line,#e5ece9)}.ui-v1-source-row:last-child{border-bottom:0}.ui-v1-source-row div{display:flex;flex-direction:column;gap:2px}.ui-v1-source-row small{color:var(--muted,#64748b)}.ui-v1-technical>summary{cursor:pointer;font-weight:800}.ui-v1-tech-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.ui-v1-tech-grid>div{display:flex;flex-direction:column;padding:9px;border-radius:10px;background:var(--soft,#f4f7f6)}.ui-v1-tech-grid span{font-size:12px;word-break:break-word}@media(max-width:640px){.ui-v1-two-col,.ui-v1-tech-grid,.ui-v1-source-row{grid-template-columns:1fr}}
    `;document.head.appendChild(s);
  }

  findDates=async function(){
    if(!needProfile())return;
    $('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
      const top=arr(d.results), all=arr(d.all_results).length?arr(d.all_results):top;
      const counts=d.group_counts||{};
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${esc(d.safety_note)}</div>`:''}<div class="card"><span class="v2-kicker">3 lựa chọn nên xem trước</span><p class="muted">Kết luận lấy trực tiếp từ engine theo HARD_BLOCK → sự kiện → cá nhân; UI không tự cộng điểm hay tự suy lại kết quả. App đã xét ${esc(d.result_count??all.length)} ngày.</p><div class="v27-summary">${Object.entries(counts).map(([k,v])=>`<span>${esc(k)}: <b>${esc(v)}</b></span>`).join('')}</div>${top.map((r,i)=>resultCard(r,i,true)).join('')||'<div class="muted">Chưa có kết quả.</div>'}<details class="v27-all"><summary>Xem tất cả ${esc(all.length)} ngày đã xét</summary><p class="muted">Ngày bị chặn hoặc không ưu tiên vẫn được hiển thị để biết rõ nguyên nhân.</p>${all.map((r,i)=>resultCard(r,i,false)).join('')}</details></div>`;
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
      const rows=arr(r.all_results);eventCalendarMap=new Map(rows.map(x=>[x.date,x]));
      calendarDays=rows.slice().sort((a,b)=>String(a.date).localeCompare(String(b.date))).map(x=>({ngay:x.date,label:x.conclusion?.label||'Chưa đủ căn cứ',state:x.conclusion?.state||'',v27:x}));
      for(const x of calendarDays){const el=$(`day-${x.ngay}`);if(!el)continue;const t=tone(x.v27),st=el.querySelector('.state');if(st)st.innerHTML=`<i class="day-dot ${t}"></i><span class="day-state-text">${esc(x.label)}</span>`;el.dataset.tone=t;el.title=x.label}
      renderCalendarList();
      const detail=$('calendar-detail');if(detail)detail.innerHTML=`<div class="v27-calendar-note">Lịch dùng cùng engine Event Search 43-rule. Chọn một ngày để xem 5 lớp căn cứ: kết luận, lý do, cá nhân, nguồn và kỹ thuật.</div>`;
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
      $('calendar-detail').innerHTML=`<div class="v2-hero ${tone(r)}"><small>CHI TIẾT NGÀY ${esc(iso)} · THEO VIỆC ĐÃ CHỌN</small><h2>${esc(r.conclusion?.title||r.conclusion?.label||'Chưa đủ căn cứ')}</h2><p>${esc(r.plain_explanation||'')}</p><div class="v27-meta">${confidence(r)}<span>${esc(r.conclusion?.label||'')}</span>${r.event_context?.hard_block?'<span>Điều kiện chặn</span>':''}</div></div>${layeredResultHtml(r)}`;
    }catch(e){$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tính được ngày này theo việc đã chọn</b>${esc(e.message)}</div>`}
  };

  addStyles();
})();
