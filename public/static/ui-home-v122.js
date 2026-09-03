// UI V1.2.2 HOME DECISION — Trang chủ để nắm nhanh, chi tiết mở khi cần.
(function(){
  window.TU_BINH_HOME_UI_VERSION='3.2.2-home-decision';

  const domainDefs=[
    {id:'home-work-summary-v21',label:'Công việc',icon:'▣',open:"openWorkDomain('day')"},
    {id:'home-finance-summary-v22',label:'Tiền bạc',icon:'◈',open:"openFinanceDomain('day')"},
    {id:'home-relationship-summary-v23',label:'Quan hệ',icon:'◎',open:"openRelationshipDomain('day')"},
  ];

  function addStyles(){
    if(document.getElementById('home-v122-style'))return;
    const s=document.createElement('style');s.id='home-v122-style';s.textContent=`
      #home-work-summary-v21,#home-finance-summary-v22,#home-relationship-summary-v23{display:none!important}
      .home-v122-overview{margin-top:12px;border:1px solid var(--line,#d7e2de);border-radius:18px;background:var(--card,#fff);overflow:hidden}
      .home-v122-head{padding:14px 15px 9px;display:flex;justify-content:space-between;gap:10px;align-items:end}
      .home-v122-head>div{display:grid;gap:2px}.home-v122-head small{font-size:11px;font-weight:900;letter-spacing:.06em;color:var(--muted,#64748b)}
      .home-v122-head b{font-size:17px}.home-v122-head span{font-size:12px;color:var(--muted,#64748b)}
      .home-v122-list{border-top:1px solid var(--line,#e3ebe8)}
      .home-v122-row{width:100%;border:0;border-bottom:1px solid var(--line,#e3ebe8);background:transparent;padding:11px 14px;display:grid;grid-template-columns:34px minmax(0,1fr) auto 16px;gap:9px;align-items:center;text-align:left;color:inherit}
      .home-v122-row:last-child{border-bottom:0}.home-v122-icon{width:32px;height:32px;border-radius:10px;background:var(--soft,#eef5f2);display:grid;place-items:center;color:#0f766e;font-weight:900}
      .home-v122-main{min-width:0;display:grid;gap:2px}.home-v122-main b{font-size:14px}.home-v122-main small{font-size:12px;color:var(--muted,#64748b);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .home-v122-state{font-size:11px;font-weight:800;padding:5px 8px;border-radius:999px;background:var(--soft,#eef5f2);white-space:nowrap}.home-v122-state.good{color:#13725f;background:#e9f7f2}.home-v122-state.warn{color:#8b641b;background:#fff4d9}.home-v122-state.neutral{color:#5d6b67}
      .home-v122-arrow{font-size:18px;color:var(--muted,#64748b)}
      .home-v122-foot{padding:9px 14px 12px;color:var(--muted,#64748b);font-size:11px;line-height:1.4}
      .home-v122-overview.loading .home-v122-main small{opacity:.65}
      .home-summary-card,.home-today-card{box-shadow:0 8px 24px rgba(26,55,47,.035)}
      .home-trust{margin-top:8px!important;opacity:.72}.trust-line{font-size:11px!important}
      @media(max-width:640px){
        .home-v122-head{align-items:start;display:grid}.home-v122-head span{font-size:11px}.home-v122-row{grid-template-columns:32px minmax(0,1fr) 16px}.home-v122-state{grid-column:2;justify-self:start;padding:3px 7px}.home-v122-arrow{grid-column:3;grid-row:1 / span 2}.home-v122-icon{grid-row:1 / span 2}
      }
    `;document.head.appendChild(s);
  }

  function toneFrom(el){
    if(!el)return'neutral';
    if(el.querySelector('.v2-confidence.good')||el.classList.contains('good'))return'good';
    if(el.querySelector('.v2-confidence.warn')||el.classList.contains('warn'))return'warn';
    return'neutral';
  }
  function domainSnapshot(def){
    const el=$(def.id);
    const title=el?.querySelector('h3')?.textContent?.trim()||'Đang đọc dữ liệu…';
    const confidence=el?.querySelector('.v2-confidence')?.textContent?.trim()||'Đang tải';
    const detail=el?.querySelector('p')?.textContent?.trim()||'Bấm để xem kết luận và căn cứ riêng.';
    return {...def,title,confidence,detail,tone:toneFrom(el),ready:!!el&&!/Đang đọc/.test(title)};
  }
  function renderOverview(){
    const today=$('home-today-summary');if(!today)return;
    let box=$('home-domain-overview-v122');
    if(!box){box=document.createElement('section');box.id='home-domain-overview-v122';box.className='home-v122-overview';today.insertAdjacentElement('afterend',box)}
    const rows=domainDefs.map(domainSnapshot);
    const loading=rows.some(x=>!x.ready);box.classList.toggle('loading',loading);
    box.innerHTML=`<div class="home-v122-head"><div><small>HÔM NAY THEO TỪNG LĨNH VỰC</small><b>Chỉ mở phần anh cần xem</b></div><span>Công việc · Tiền bạc · Quan hệ</span></div><div class="home-v122-list">${rows.map(x=>`<button class="home-v122-row" onclick="${x.open}"><span class="home-v122-icon">${x.icon}</span><span class="home-v122-main"><b>${esc(x.label)}</b><small>${esc(x.title)}</small></span><span class="home-v122-state ${x.tone}">${esc(x.confidence)}</span><span class="home-v122-arrow">›</span></button>`).join('')}</div><div class="home-v122-foot">Trang chủ chỉ tóm tắt. Bấm từng lĩnh vực để xem “nên làm gì”, “cần lưu ý gì” và căn cứ; app không suy kết quả chắc chắn từ một tín hiệu đơn lẻ.</div>`;
  }
  function observeDomains(){
    if(window.__HOME_V122_OBSERVED)return;window.__HOME_V122_OBSERVED=true;
    const root=$('screen-home');if(!root)return;
    let timer=null;new MutationObserver(muts=>{if(!muts.some(m=>m.target?.closest?.('#home-work-summary-v21,#home-finance-summary-v22,#home-relationship-summary-v23')))return;clearTimeout(timer);timer=setTimeout(renderOverview,50)}).observe(root,{subtree:true,childList:true,characterData:true});
  }

  const previousHome=loadHomeDashboard;
  loadHomeDashboard=async function(){await previousHome();renderOverview();observeDomains();};
  addStyles();
  window.addEventListener('load',()=>setTimeout(()=>{try{renderOverview();observeDomains()}catch{}},2100));
})();
