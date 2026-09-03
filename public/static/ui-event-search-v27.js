// UI V1.2.1 TRUST FIRST — người dùng hiểu trước, kỹ thuật kiểm sau. Không tự tính lại quyết định engine.
(function(){
  window.TU_BINH_EVENT_SEARCH_UI_VERSION='3.2.1-ui-v1.2.1-trust';
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
  function friendlyDate(v){
    const s=String(v||'');
    const m=s.match(/^(\d{4})-(\d{2})-(\d{2})$/);if(!m)return s;
    const d=new Date(`${s}T12:00:00`);
    const wd=d.toLocaleDateString('vi-VN',{weekday:'long'});
    return `${wd.charAt(0).toUpperCase()+wd.slice(1)} · ${m[3]}/${m[2]}/${m[1]}`;
  }
  function profileName(){const p=current?.()||{};return p.full_name||p.name||p.ten||p.display_name||'người đã chọn';}
  function eventName(){const el=$('work-type');return el?.selectedOptions?.[0]?.textContent?.trim()||'việc đã chọn';}
  function calendarEventName(){const el=$('calendar-work');return el?.selectedOptions?.[0]?.textContent?.trim()||eventName();}
  function evidenceStatusLabel(v){
    if(v==='VERIFIED')return'Đã xác minh';
    if(v==='PROVISIONAL')return'Tạm dùng — còn cần đối chiếu';
    if(v==='PENDING')return'Đang chờ xác minh';
    return v||'Chưa ghi trạng thái';
  }
  function tokenTitle(token){
    const names={'吉期':'Cát Kỳ','五富':'Ngũ Phú','天倉':'Thiên Thương','天馬':'Thiên Mã','驛馬':'Dịch Mã','天醫':'Thiên Y','天后':'Thiên Hậu','除神':'Trừ Thần','王日':'Vương Nhật','官日':'Quan Nhật','相日':'Tướng Nhật','民日':'Dân Nhật','臨日':'Lâm Nhật','月徳':'Nguyệt Đức','月徳合':'Nguyệt Đức Hợp','月恩':'Nguyệt Ân','天赦':'Thiên Xá','天願':'Thiên Nguyện','天喜':'Thiên Hỷ','五合':'Ngũ Hợp','大耗':'Đại Hao','月破':'Nguyệt Phá','月刑':'Nguyệt Hình','月厭':'Nguyệt Yếm','劫煞':'Kiếp Sát','災煞':'Tai Sát','月煞':'Nguyệt Sát'};
    return names[token]||token;
  }
  function tokenMeaning(token,polarity){
    const good={
      '吉期':'Hỗ trợ tiến hành việc quan trọng khi quy tắc này được xác minh cho đúng nhóm việc đang chọn.',
      '五富':'Phù hợp hơn với các việc liên quan tài lộc, kinh doanh và giao dịch trong phạm vi đã xác minh.',
      '天倉':'Phù hợp hơn với việc thu tiền, nhận tiền, gom tài hoặc nạp tài trong phạm vi đã xác minh.',
      '天馬':'Phù hợp hơn với di chuyển, xuất hành hoặc thay đổi nơi chốn trong phạm vi đã xác minh.',
      '驛馬':'Phù hợp hơn với xuất hành, di chuyển hoặc chuyển nơi ở trong phạm vi đã xác minh.',
      '天醫':'Hỗ trợ nhóm việc điều trị, chăm sóc sức khỏe trong phạm vi đã xác minh.',
      '天后':'Hỗ trợ cầu y, chữa bệnh trong phạm vi đã xác minh.',
      '除神':'Hỗ trợ nhóm việc điều trị trong phạm vi đã xác minh.',
      '王日':'Là căn cứ thuận cho nhóm việc đã được xác minh trong engine.',
      '官日':'Hỗ trợ nhậm chức hoặc công việc công vụ trong phạm vi đã xác minh.',
      '相日':'Hỗ trợ nhậm chức trong phạm vi đã xác minh.',
      '民日':'Hỗ trợ một số việc dân sinh, giao dịch trong phạm vi đã xác minh.',
      '臨日':'Hỗ trợ nhậm chức trong phạm vi đã xác minh.',
      '月徳':'Là tín hiệu cát hỗ trợ; không có quyền cứu một ngày đã bị chặn.',
      '月徳合':'Là tín hiệu cát hỗ trợ; không có quyền cứu một ngày đã bị chặn.',
      '月恩':'Là tín hiệu cát hỗ trợ trong lớp ngày.',
      '天赦':'Là tín hiệu cát mạnh nhưng vẫn phải tuân theo điều kiện chặn của sự kiện.',
      '天願':'Là tín hiệu cát hỗ trợ trong phạm vi ngày.',
      '天喜':'Là tín hiệu cát hỗ trợ trong phạm vi đã xác minh.',
      '五合':'Là tín hiệu hợp trợ trong phạm vi ngày.'
    };
    const bad={
      '大耗':'Có ý nghĩa hao tán; app dùng như cảnh báo và tự nó không tạo HARD_BLOCK.',
      '月破':'Là tín hiệu phá, được dùng ở lớp cần tránh.',
      '月刑':'Là tín hiệu hình, được dùng như cảnh báo.',
      '月厭':'Là tín hiệu cần thận trọng ở lớp sự kiện.',
      '劫煞':'Là tín hiệu sát, được dùng như cảnh báo.',
      '災煞':'Là tín hiệu sát, được dùng như cảnh báo.',
      '月煞':'Là tín hiệu sát, được dùng như cảnh báo.'
    };
    return (polarity==='JI'?bad[token]:good[token])||`${polarity==='JI'?'Là căn cứ cần tránh':'Là căn cứ hỗ trợ'} được engine dùng cho đúng việc đã chọn.`;
  }
  function visibleEvidence(r){return arr(r?.technical?.matched_evidence);}
  function yi(r){return arr(r?.technical?.matched_yi_tokens);}
  function ji(r){return arr(r?.technical?.matched_ji_tokens);}
  function personalData(r){return r?.personal_context||r?.personal_v1_1||r?.technical?.personal_context||{};}
  function personalRaw(r){const p=personalData(r);return p?.headline||r?.personal_explanation||p?.decision_effect||r?.technical?.personal_state||'';}
  function personalSummary(r){
    const raw=String(personalRaw(r)||'').trim();
    if(!raw)return'Chưa có căn cứ cá nhân đủ rõ để nâng hoặc hạ kết luận của ngày này.';
    if(/trung tính|neutral/i.test(raw))return'Lá số hiện không làm ngày này tốt hơn cũng không làm xấu đi; kết luận chủ yếu đến từ lớp ngày và việc đang chọn.';
    if(/thuận|support|favorable/i.test(raw))return'Lớp cá nhân đang hỗ trợ thêm cho ngày này, nhưng không thay thế kết luận của lớp sự kiện.';
    if(/nghịch|caution|bất lợi|adverse/i.test(raw))return'Lớp cá nhân có yếu tố cần thận trọng, vì vậy nên xem kỹ phần căn cứ trước khi chọn.';
    return raw;
  }
  function confidence(r){return r?.confidence_state||'Chưa đủ căn cứ';}
  function primarySignal(r){
    const token=yi(r)[0]||ji(r)[0];
    if(!token)return'';
    return `${tokenTitle(token)} — ${tokenMeaning(token,ji(r).includes(token)?'JI':'YI')}`;
  }
  function decisionReason(r){
    if(r?.event_context?.hard_block)return'Ngày này bị chặn ở lớp sự kiện. Các yếu tố thuận khác không được dùng để đảo ngược kết luận.';
    const y=yi(r),j=ji(r),primary=primarySignal(r);
    if(y.length&&!j.length)return `${primary||'Có căn cứ thuận cho việc đang chọn.'} Không ghi nhận quy tắc kiêng trực tiếp trong payload hiện tại.`;
    if(y.length&&j.length)return `${primary||'Có căn cứ hỗ trợ.'} Đồng thời ngày này còn có căn cứ cần tránh, nên phải đọc cả hai phía trước khi quyết định.`;
    if(j.length)return `${primary||'Có căn cứ cần tránh cho việc đang chọn.'}`;
    return r?.plain_explanation||'Chưa có căn cứ trực tiếp đủ rõ để giải thích mạnh hơn.';
  }
  function trustBadge(r){
    const ev=visibleEvidence(r),verified=ev.filter(x=>x.evidence_status==='VERIFIED').length,total=ev.length;
    const text=total?`${verified}/${total} căn cứ trực tiếp đã xác minh`:confidence(r);
    return `<span class="t12-trust">Căn cứ: <b>${safe(text)}</b></span>`;
  }
  function tokenLines(r,limit=4){
    const rows=[...yi(r).map(x=>({x,p:'YI'})),...ji(r).map(x=>({x,p:'JI'}))].slice(0,limit);
    if(!rows.length)return'<div class="t12-empty">Chưa có quy tắc trực tiếp nổi bật trong ngày này.</div>';
    return rows.map(o=>`<div class="t12-signal ${o.p==='JI'?'bad':'good'}"><span>${o.p==='JI'?'−':'+'}</span><p><b>${safe(tokenTitle(o.x))}</b><small>${safe(tokenMeaning(o.x,o.p))}</small></p></div>`).join('');
  }
  function topHero(r){
    return `<section class="t12-hero ${tone(r)}"><div class="t12-kicker">LỰA CHỌN ĐẦU TIÊN · ${safe(eventName().toUpperCase())}</div><div class="t12-hero-head"><div><h2>${safe(friendlyDate(r?.date||'—'))}</h2><strong>Nhóm ${safe(r?.conclusion?.label||'Chưa đủ căn cứ')}</strong></div>${trustBadge(r)}</div><div class="t12-why"><b>Vì sao ngày này được đưa lên đầu?</b><p>${safe(decisionReason(r))}</p></div><div class="t12-signals">${tokenLines(r,4)}</div><div class="t12-personal"><b>Riêng với ${safe(profileName())}</b><span>${safe(personalSummary(r))}</span></div><button class="t12-primary" onclick="openTrustDetail('${safe(r?.date||'')}','overview')">Xem đầy đủ căn cứ ngày này</button></section>`;
  }
  function topCard(r,index){
    const signal=yi(r)[0]||ji(r)[0];
    const sig=signal?`${tokenTitle(signal)} · ${ji(r).includes(signal)?'cần tránh':'căn cứ thuận'}`:'Chưa có quy tắc nổi bật';
    return `<button class="t12-compare-card ${tone(r)}" onclick="openTrustDetail('${safe(r?.date||'')}','overview')"><span class="t12-rank">#${index+1}</span><b>${safe(shortDate(r?.date))} · ${safe(r?.conclusion?.label||'')}</b><small>${safe(sig)}</small><div class="t12-mini">${safe(personalSummary(r))}</div></button>`;
  }
  function compactRow(r){return `<button class="t12-row" onclick="openTrustDetail('${safe(r?.date||'')}','overview')"><b>${safe(shortDate(r?.date))}</b><span><strong>${safe(r?.conclusion?.label||'Chưa đủ căn cứ')}</strong><small>${safe(primarySignal(r)||r?.plain_explanation||'Xem chi tiết căn cứ')}</small></span><em>›</em></button>`;}
  function groupKey(r){
    const label=String(r?.conclusion?.label||'');
    if(/Bị chặn|HARD_BLOCK/i.test(label)||r?.event_context?.hard_block)return'blocked';
    if(/Không ưu tiên/i.test(label))return'avoid';
    if(/Cân nhắc|Thận trọng/i.test(label))return'consider';
    if(/Ưu tiên|Khá thuận/i.test(label))return'priority';
    return'other';
  }
  function groupedDays(all){
    const defs=[['priority','Nên xem trước','Những ngày engine xếp vào nhóm ưu tiên.'],['consider','Có thể cân nhắc','Có thể dùng khi cần thêm lựa chọn, nhưng nên đọc kỹ căn cứ.'],['avoid','Không ưu tiên','Nên xem các ngày ở nhóm trên trước.'],['blocked','Bị chặn','Có điều kiện chặn ở lớp sự kiện; tín hiệu thuận khác không đảo được kết luận.'],['other','Chưa phân nhóm','Kết quả chưa nằm trong bốn nhóm chính.']];
    return defs.map(([key,title,note])=>{const rows=all.filter(r=>groupKey(r)===key);if(!rows.length)return'';return `<details class="t12-group" ${key==='priority'?'open':''}><summary><span><b>${title}</b><small>${note}</small></span><em>${rows.length}</em></summary><div class="t12-list">${rows.map(compactRow).join('')}</div></details>`;}).join('');
  }
  function evidenceHtml(r){
    const ev=visibleEvidence(r);
    if(!ev.length)return'<div class="t12-empty">Ngày này chưa có evidence chi tiết gắn trực tiếp trong payload.</div>';
    return ev.map(x=>`<article class="t12-proof"><div><b>${safe(tokenTitle(x.token||x.rule_id||'Quy tắc'))}</b><span class="${x.polarity==='JI'?'bad':'good'}">${x.polarity==='JI'?'Cần tránh':'Hỗ trợ'}</span></div><p>${safe(tokenMeaning(x.token||x.rule_id,x.polarity))}</p><dl><div><dt>Trạng thái</dt><dd>${safe(evidenceStatusLabel(x.evidence_status))}</dd></div><div><dt>Nguồn</dt><dd>${safe(x.source_location||x.source_id||'Chưa ghi vị trí nguồn')}</dd></div></dl></article>`).join('');
  }
  function overviewTab(r){return `<section class="t12-detail-section"><div class="t12-detail-verdict ${tone(r)}"><small>KẾT LUẬN CHO ${safe(eventName().toUpperCase())}</small><h2>${safe(r?.conclusion?.label||'')}</h2><p>${safe(decisionReason(r))}</p></div><h3>Căn cứ làm nên kết quả</h3>${tokenLines(r,99)}<div class="t12-boundary"><b>Cách đọc</b><span>Đây không phải phép cộng điểm. UI chỉ diễn giải dữ liệu engine; HARD_BLOCK luôn thắng lớp sự kiện và cá nhân.</span></div></section>`;}
  function personalTab(r){
    const p=personalData(r),facts=arr(p?.branch_impacts||p?.technical_facts),raw=personalRaw(r);
    return `<section class="t12-detail-section"><h3>Riêng với ${safe(profileName())}</h3><p class="t12-lead">${safe(personalSummary(r))}</p>${raw?`<details class="t12-tech"><summary>Xem lý do Tử Bình</summary><p>${safe(raw)}</p>${facts.length?`<ul>${facts.map(x=>`<li>${safe(x)}</li>`).join('')}</ul>`:''}</details>`:'<div class="t12-empty">Engine chưa trả về chi tiết cá nhân đủ rõ cho ngày này.</div>'}<div class="t12-boundary"><b>Cách hiểu đúng</b><span>Nếu lớp cá nhân chưa đủ căn cứ, app nói thẳng là chưa đủ; không giả vờ cá nhân hóa. Lớp cá nhân không cứu ngày bị HARD_BLOCK.</span></div></section>`;
  }
  function hourTab(r){const t=r?.technical||{};const h=r?.hour_context||r?.personal_hour||t?.hour_context||{};const items=arr(h?.items||h?.hours||h?.recommendations);return `<section class="t12-detail-section"><h3>Giờ tham khảo có căn cứ hiện tại</h3>${items.length?items.map(x=>`<div class="t12-hour"><b>${safe(x.label||x.hour||x.name||'Giờ')}</b><span>${safe(x.reason||x.state||'')}</span></div>`).join(''):'<div class="t12-empty">Chưa đủ dữ liệu giờ cá nhân để đề xuất giờ cụ thể cho ngày này.</div>'}<div class="t12-boundary"><b>Chưa phải “giờ tốt/xấu cá nhân hoàn chỉnh”</b><span>Engine hiện vẫn khóa phạm vi giờ; ngày/sự kiện luôn được xét trước và giờ không được đảo HARD_BLOCK.</span></div></section>`;}
  function sourceTab(r){const t=r?.technical||{};return `<section class="t12-detail-section"><h3>Căn cứ cổ thư & trạng thái xác minh</h3>${evidenceHtml(r)}<details class="t12-tech"><summary>Dành cho người muốn kiểm tra kỹ thuật</summary><p><b>Rule ID:</b> ${arr(r?.rules).map(safe).join(' · ')||'—'}</p><p><b>Source ID:</b> ${arr(r?.sources).map(safe).join(' · ')||'—'}</p><p><b>Decision authority:</b> ${safe(t.decision_authority||'—')}</p><p><b>Coverage:</b> ${safe(t.coverage||'—')}</p><p><b>Hiệp Kỷ:</b> ${safe(t.hiep_ky_extension||'—')}</p></details></section>`;}
  function ensureSheet(){
    if(document.getElementById('t12-sheet'))return;
    const el=document.createElement('div');el.id='t12-sheet';el.className='t12-sheet';
    el.innerHTML=`<div class="t12-backdrop" onclick="closeTrustDetail()"></div><div class="t12-panel"><header><div><small>CHI TIẾT NGÀY</small><h2 id="t12-date">—</h2></div><button onclick="closeTrustDetail()">×</button></header><nav><button data-tab="overview" onclick="switchTrustTab('overview')">Kết luận</button><button data-tab="personal" onclick="switchTrustTab('personal')">Cá nhân</button><button data-tab="hour" onclick="switchTrustTab('hour')">Giờ</button><button data-tab="source" onclick="switchTrustTab('source')">Căn cứ</button></nav><main id="t12-body"></main></div>`;
    document.body.appendChild(el);
  }
  function renderDetail(){const r=resultMap.get(activeDate)||calendarMap.get(activeDate);if(!r)return;document.getElementById('t12-date').textContent=friendlyDate(activeDate);document.getElementById('t12-body').innerHTML=activeTab==='personal'?personalTab(r):activeTab==='hour'?hourTab(r):activeTab==='source'?sourceTab(r):overviewTab(r);document.querySelectorAll('#t12-sheet nav button').forEach(b=>b.classList.toggle('active',b.dataset.tab===activeTab));}
  window.openTrustDetail=function(date,tab='overview'){ensureSheet();activeDate=date;activeTab=tab;renderDetail();document.getElementById('t12-sheet').classList.add('open');document.body.classList.add('t12-lock');};
  window.closeTrustDetail=function(){document.getElementById('t12-sheet')?.classList.remove('open');document.body.classList.remove('t12-lock');};
  window.switchTrustTab=function(tab){activeTab=tab;renderDetail();};

  function addStyles(){
    if(document.getElementById('t12-style'))return;
    const s=document.createElement('style');s.id='t12-style';s.textContent=`
      .t12-context{padding:14px 16px;border-radius:16px;background:var(--soft,#f2f6f4);display:grid;gap:4px}.t12-context b{font-size:16px}.t12-context small,.t12-context span{color:var(--muted,#64748b)}
      .t12-hero{border:1px solid var(--line,#d8e3df);border-radius:20px;padding:18px;background:var(--card,#fff);display:grid;gap:14px}.t12-hero.good{border-top:5px solid #15836e}.t12-hero.warn{border-top:5px solid #c58a20}.t12-hero.bad{border-top:5px solid #b94b48}.t12-kicker{font-size:11px;font-weight:900;letter-spacing:.05em;color:var(--muted,#64748b)}.t12-hero-head{display:flex;justify-content:space-between;gap:12px;align-items:start}.t12-hero h2{margin:0;font-size:26px}.t12-hero strong{display:block;margin-top:4px;font-size:16px}.t12-trust{font-size:11px;background:var(--soft,#f2f6f4);padding:7px 9px;border-radius:999px}.t12-lead{font-size:15px;line-height:1.55;margin:0}.t12-why{display:grid;gap:5px;padding:12px 0}.t12-why p{margin:0;line-height:1.55}.t12-signals{display:grid;gap:7px}.t12-signal{display:grid;grid-template-columns:24px 1fr;gap:8px;padding:10px;border-radius:12px;background:var(--soft,#f5f7f6)}.t12-signal>span{font-size:18px;font-weight:900}.t12-signal.good>span{color:#14745f}.t12-signal.bad>span{color:#a23f3b}.t12-signal p{margin:0;display:grid;gap:2px}.t12-signal small{color:var(--muted,#64748b);line-height:1.4}.t12-personal{padding:12px;border-left:3px solid #6b7f79;background:var(--soft,#f5f7f6);display:grid;gap:4px}.t12-personal span{font-size:13px;line-height:1.45}.t12-primary{border:0;border-radius:12px;padding:12px 14px;background:#0f766e;color:white;font-weight:800}
      .t12-section-title{margin:18px 0 8px}.t12-section-title h3{margin:0}.t12-section-title p{margin:3px 0;color:var(--muted,#64748b);font-size:13px}.t12-compare{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.t12-compare-card{border:1px solid var(--line,#d8e3df);border-radius:14px;background:var(--card,#fff);padding:12px;text-align:left;display:grid;gap:5px}.t12-compare-card.good{border-top:3px solid #15836e}.t12-compare-card.warn{border-top:3px solid #c58a20}.t12-compare-card.bad{border-top:3px solid #b94b48}.t12-rank{font-size:10px;font-weight:900;color:var(--muted,#64748b)}.t12-compare-card small{line-height:1.35;color:var(--muted,#64748b)}.t12-mini{font-size:11px;margin-top:4px;color:var(--muted,#64748b)}
      .t12-groups{display:grid;gap:10px}.t12-group{border:1px solid var(--line,#d8e3df);border-radius:15px;background:var(--card,#fff);overflow:hidden}.t12-group>summary{cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;list-style:none}.t12-group>summary::-webkit-details-marker{display:none}.t12-group>summary span{display:grid;gap:2px}.t12-group>summary small{color:var(--muted,#64748b)}.t12-group>summary em{font-style:normal;font-weight:900;background:var(--soft,#f2f6f4);min-width:30px;text-align:center;padding:4px 8px;border-radius:999px}.t12-list{border-top:1px solid var(--line,#d8e3df)}.t12-row{width:100%;border:0;border-bottom:1px solid var(--line,#e5ece9);background:var(--card,#fff);display:grid;grid-template-columns:58px 1fr 20px;gap:10px;padding:11px 13px;text-align:left;align-items:center}.t12-row:last-child{border-bottom:0}.t12-row>span{display:grid;gap:2px}.t12-row small{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--muted,#64748b)}.t12-row em{font-size:22px;font-style:normal;color:var(--muted,#64748b)}.t12-empty{padding:12px;border-radius:12px;background:var(--soft,#f5f7f6);color:var(--muted,#64748b);font-size:13px}
      .t12-sheet{position:fixed;inset:0;z-index:9999;display:none}.t12-sheet.open{display:block}.t12-backdrop{position:absolute;inset:0;background:rgba(15,23,42,.42)}.t12-panel{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(720px,92vw);max-height:88vh;background:var(--card,#fff);border-radius:20px;overflow:hidden;display:grid;grid-template-rows:auto auto 1fr;box-shadow:0 24px 80px rgba(0,0,0,.24)}.t12-panel>header{display:flex;justify-content:space-between;padding:16px 18px 10px}.t12-panel>header h2{margin:2px 0}.t12-panel>header button{border:0;background:var(--soft,#f2f6f4);width:36px;height:36px;border-radius:50%;font-size:22px}.t12-panel>nav{display:flex;gap:6px;padding:0 14px 10px;overflow:auto}.t12-panel>nav button{border:0;background:transparent;padding:9px 11px;border-radius:999px;white-space:nowrap}.t12-panel>nav button.active{background:#0f766e;color:#fff}.t12-panel>main{overflow:auto;padding:0 18px 22px}.t12-detail-section{display:grid;gap:12px}.t12-detail-verdict{padding:15px;border-radius:15px;background:var(--soft,#f5f7f6)}.t12-detail-verdict h2{margin:4px 0}.t12-proof{border:1px solid var(--line,#d8e3df);border-radius:14px;padding:12px}.t12-proof>div:first-child{display:flex;justify-content:space-between;gap:8px}.t12-proof span.good{color:#14745f}.t12-proof span.bad{color:#a23f3b}.t12-proof p{font-size:13px;line-height:1.45}.t12-proof dl{display:grid;gap:5px;margin:0}.t12-proof dl>div{display:grid;grid-template-columns:90px 1fr;gap:8px;font-size:12px}.t12-proof dt{color:var(--muted,#64748b)}.t12-boundary{padding:12px;border-radius:12px;background:#fff7e7;display:grid;gap:4px;font-size:12px}.t12-hour{padding:12px;border-radius:12px;background:var(--soft,#f5f7f6);display:grid;gap:3px}.t12-tech{border-top:1px solid var(--line,#d8e3df);padding-top:10px}.t12-lock{overflow:hidden}
      @media(max-width:640px){.t12-compare{grid-template-columns:1fr}.t12-hero-head{display:grid}.t12-panel{left:0;top:auto;bottom:0;transform:none;width:100%;max-height:94vh;border-radius:18px 18px 0 0}.t12-row{grid-template-columns:50px 1fr 18px}.t12-context{border-radius:14px}.t12-hero{padding:15px;border-radius:16px}.t12-hero h2{font-size:22px}}
    `;document.head.appendChild(s);
  }

  findDates=async function(){
    if(!needProfile())return;
    $('work-result').innerHTML='<div class="card">Đang đối chiếu ngày, cá nhân và căn cứ…</div>';
    try{
      const d=await post('/api/v2/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
      const top=arr(d.results),all=arr(d.all_results).length?arr(d.all_results):top;resultMap=new Map(all.map(x=>[x.date,x]));
      const best=top[0];
      $('work-result').innerHTML=`${d.safety_note?`<div class="notice danger"><b>Lưu ý an toàn</b>${safe(d.safety_note)}</div>`:''}<div class="t12-context"><small>ĐANG XEM CHO</small><b>${safe(profileName())}</b><strong>${safe(eventName())}</strong><span>${safe($('work-from').value)} → ${safe($('work-to').value)} · đã xét ${safe(d.result_count??all.length)} ngày</span></div>${best?topHero(best):'<div class="card">Chưa có kết quả.</div>'}<div class="t12-section-title"><h3>Các lựa chọn đầu</h3><p>Các ngày có thể cùng một nhóm kết luận. Thứ tự #1–#3 lấy nguyên từ engine, không phải phép cộng số lượng sao hay điểm số.</p></div><div class="t12-compare">${top.map((r,i)=>topCard(r,i)).join('')}</div><div class="t12-section-title"><h3>Tất cả ngày đã xét</h3><p>Đã gom theo kết luận để dễ quét. Bấm một ngày để xem kết luận, cá nhân, giờ và căn cứ.</p></div><div class="t12-groups">${groupedDays(all)}</div>`;
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
    const eventCode=$('calendar-work')?.value||'';if(!eventCode)return previousSelectCalendarDay(iso,el);document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));el?.classList.add('selected');let r=calendarMap.get(iso);if(!r){const d=await post('/api/v2/tim-ngay',{profile:current(),viec:eventCode,tu_ngay:iso,den_ngay:iso});r=arr(d.all_results||d.results)[0];if(r){calendarMap.set(iso,r);resultMap.set(iso,r);}}if(!r)return;$('calendar-detail').innerHTML=`<div class="t12-context"><small>${safe(calendarEventName())}</small><b>${safe(friendlyDate(iso))} · ${safe(r.conclusion?.label||'')}</b><span>${safe(decisionReason(r))}</span><button class="btn" onclick="openTrustDetail('${safe(iso)}','overview')">Xem căn cứ ngày này</button></div>`;
  };
  addStyles();
})();
