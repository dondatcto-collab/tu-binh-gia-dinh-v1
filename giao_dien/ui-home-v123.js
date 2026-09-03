// UI V1.2.3 ACTION FIRST — Trang chủ ưu tiên hành động cụ thể từ payload hiện có.
(function(){
  window.TU_BINH_HOME_ACTION_UI_VERSION='3.2.3-action-first';
  const defs=[
    {key:'work',label:'Công việc',icon:'▣',endpoint:'/api/v2/cong-viec',open:"openWorkDomain('day')"},
    {key:'finance',label:'Tiền bạc',icon:'◈',endpoint:'/api/v2/tai-chinh',open:"openFinanceDomain('day')"},
    {key:'relationship',label:'Quan hệ',icon:'◎',endpoint:'/api/v2/quan-he',open:"openRelationshipDomain('day')"},
  ];
  const cache=new Map();
  function todayKey(){return new Date().toISOString().slice(0,10)}
  function tone(r){const s=String(r?.conclusion?.state||'');if(s==='SUPPORT')return'good';if(s==='CAUTION')return'warn';return'neutral'}
  function firstText(a){return Array.isArray(a)&&a.length?String(a[0]||'').trim():''}
  function summarize(def,r){
    const action=firstText(r?.recommended_actions), caution=firstText(r?.cautions), confidence=String(r?.confidence_state||'Chưa đủ căn cứ');
    let lead='',sub='';
    if(action){lead=`Nên: ${action}`;sub=caution?`Cần lưu ý: ${caution}`:'Không có lưu ý riêng nổi bật trong dữ liệu hiện tại.'}
    else if(caution){lead=`Cần lưu ý: ${caution}`;sub='Chưa có hành động thuận riêng đủ căn cứ để khuyến nghị.'}
    else{lead='Chưa có khuyến nghị riêng cho hôm nay.';sub='Nếu có việc quan trọng, hãy kiểm tra theo đúng loại việc trước khi quyết định.'}
    return {...def,action,caution,confidence,lead,sub,tone:tone(r)};
  }
  function styles(){if(document.getElementById('home-v123-style'))return;const s=document.createElement('style');s.id='home-v123-style';s.textContent=`
    #home-domain-overview-v122{display:none!important}
    .home-v123{margin-top:12px;border:1px solid var(--line,#d7e2de);border-radius:18px;background:var(--card,#fff);overflow:hidden}
    .home-v123-head{padding:14px 15px 10px;border-bottom:1px solid var(--line,#e3ebe8)}
    .home-v123-head small{display:block;font-size:11px;font-weight:900;letter-spacing:.06em;color:var(--muted,#64748b);margin-bottom:3px}
    .home-v123-head b{font-size:18px;line-height:1.25}.home-v123-head p{margin:5px 0 0;font-size:12px;color:var(--muted,#64748b);line-height:1.45}
    .home-v123-row{width:100%;border:0;border-bottom:1px solid var(--line,#e3ebe8);background:transparent;padding:12px 14px;display:grid;grid-template-columns:34px minmax(0,1fr) auto 16px;gap:9px;align-items:start;text-align:left;color:inherit}
    .home-v123-row:last-child{border-bottom:0}.home-v123-icon{width:32px;height:32px;border-radius:10px;background:var(--soft,#eef5f2);display:grid;place-items:center;color:#0f766e;font-weight:900}
    .home-v123-main{display:grid;gap:3px;min-width:0}.home-v123-main>b{font-size:14px}.home-v123-lead{font-size:13px;line-height:1.4;font-weight:700}.home-v123-sub{font-size:11px;line-height:1.4;color:var(--muted,#64748b)}
    .home-v123-state{font-size:10px;font-weight:800;padding:5px 7px;border-radius:999px;background:var(--soft,#eef5f2);white-space:nowrap}.home-v123-state.good{color:#13725f;background:#e9f7f2}.home-v123-state.warn{color:#8b641b;background:#fff4d9}.home-v123-state.neutral{color:#5d6b67}
    .home-v123-arrow{font-size:18px;color:var(--muted,#64748b);padding-top:5px}.home-v123-cta{padding:10px 14px 13px;font-size:11px;line-height:1.45;color:var(--muted,#64748b);background:var(--soft,#f6f8f7)}
    .home-v123-cta b{color:inherit}.home-v123-loading{padding:15px;color:var(--muted,#64748b);font-size:12px}
    @media(max-width:640px){.home-v123-row{grid-template-columns:32px minmax(0,1fr) 16px}.home-v123-state{grid-column:2;justify-self:start}.home-v123-arrow{grid-column:3;grid-row:1 / span 3}.home-v123-icon{grid-row:1 / span 3}}
  `;document.head.appendChild(s)}
  function ensureBox(){const today=$('home-today-summary');if(!today)return null;let box=$('home-action-v123');if(!box){box=document.createElement('section');box.id='home-action-v123';box.className='home-v123';const old=$('home-domain-overview-v122');(old||today).insertAdjacentElement('afterend',box)}return box}
  function render(rows){const box=ensureBox();if(!box)return;box.innerHTML=`<div class="home-v123-head"><small>HÔM NAY NÊN LÀM GÌ?</small><b>Ưu tiên hành động có căn cứ</b><p>Chỉ hiện khuyến nghị thật từ từng lĩnh vực; không có căn cứ thì nói thẳng là chưa có.</p></div>${rows.map(x=>`<button class="home-v123-row" onclick="${x.open}"><span class="home-v123-icon">${x.icon}</span><span class="home-v123-main"><b>${esc(x.label)}</b><span class="home-v123-lead">${esc(x.lead)}</span><span class="home-v123-sub">${esc(x.sub)}</span></span><span class="home-v123-state ${x.tone}">${esc(x.confidence)}</span><span class="home-v123-arrow">›</span></button>`).join('')}<div class="home-v123-cta"><b>Có việc quan trọng?</b> Dùng “Tìm ngày cho một việc” để kiểm theo đúng loại việc thay vì suy từ kết luận chung của hôm nay.</div>`}
  async function load(){if(!currentProfile)return;const box=ensureBox();if(!box)return;box.innerHTML='<div class="home-v123-loading">Đang đọc khuyến nghị cụ thể cho hôm nay…</div>';const p=current();const key=`${p?.profile_id||''}:${todayKey()}`;let data=cache.get(key);if(!data){data=await Promise.all(defs.map(async d=>{try{return summarize(d,await post(d.endpoint,{profile:p,scope:'day'}))}catch(e){return {...d,lead:'Chưa tải được khuyến nghị.',sub:e.message||'Hãy thử lại.',confidence:'Lỗi kết nối',tone:'neutral'}}}));cache.set(key,data)}render(data)}
  const previousHome=loadHomeDashboard;loadHomeDashboard=async function(){await previousHome();await load()};
  styles();window.addEventListener('load',()=>setTimeout(()=>{try{load()}catch{}},2300));
})();
