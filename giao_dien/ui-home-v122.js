// UI V1.2.3 CONTENT FIRST — nói dữ kiện đang thấy trước, kết luận sau.
(function(){
  window.TU_BINH_HOME_UI_VERSION='3.2.3-content-first';
  const GROUP_LABEL={AUTHORITY:'Quy tắc & trách nhiệm',RESOURCE:'Học hỏi & chuẩn bị',OUTPUT:'Thực thi & đầu ra',PEER:'Phối hợp & người ngang vai',WEALTH:'Tài & nguồn lực'};
  const STATE_LABEL={SUPPORT:'đang hỗ trợ',CAUTION:'cần thận trọng',NEUTRAL:'trung tính',DESCRIPTIVE_ONLY:'chỉ đủ mô tả',INSUFFICIENT:'chưa đủ căn cứ'};
  const domainDefs=[
    {key:'work',label:'Công việc',icon:'▣',url:'/api/v2/cong-viec',open:"openWorkDomain('day')"},
    {key:'finance',label:'Tiền bạc',icon:'◈',url:'/api/v2/tai-chinh',open:"openFinanceDomain('day')"},
    {key:'relationship',label:'Quan hệ',icon:'◎',url:'/api/v2/quan-he',open:"openRelationshipDomain('day')"},
  ];
  let cacheKey='',cacheAt=0,cacheData=null;

  function addStyles(){if(document.getElementById('home-v123-style'))return;const s=document.createElement('style');s.id='home-v123-style';s.textContent=`
    #home-work-summary-v21,#home-finance-summary-v22,#home-relationship-summary-v23{display:none!important}
    .home-v123-card{margin-top:12px;border:1px solid var(--line,#d7e2de);border-radius:18px;background:var(--card,#fff);overflow:hidden}
    .home-v123-head{padding:14px 15px 10px}.home-v123-head small{font-size:11px;font-weight:900;letter-spacing:.06em;color:var(--muted,#64748b)}.home-v123-head h3{margin:4px 0;font-size:17px;line-height:1.35}.home-v123-head p{margin:0;color:var(--muted,#64748b);font-size:12px;line-height:1.45}
    .home-v123-signal{margin:0 14px 12px;padding:11px 12px;border-radius:13px;background:var(--soft,#f2f7f5);display:grid;gap:4px}.home-v123-signal b{font-size:13px}.home-v123-signal span{font-size:12px;line-height:1.45;color:var(--muted,#64748b)}
    .home-v123-list{border-top:1px solid var(--line,#e3ebe8)}.home-v123-row{width:100%;border:0;border-bottom:1px solid var(--line,#e3ebe8);background:transparent;padding:12px 14px;display:grid;grid-template-columns:34px minmax(0,1fr) auto 16px;gap:9px;align-items:center;text-align:left;color:inherit}.home-v123-row:last-child{border-bottom:0}
    .home-v123-icon{width:32px;height:32px;border-radius:10px;background:var(--soft,#eef5f2);display:grid;place-items:center;color:#0f766e;font-weight:900}.home-v123-main{min-width:0;display:grid;gap:3px}.home-v123-main b{font-size:14px}.home-v123-main small{font-size:12px;color:var(--muted,#64748b);line-height:1.35}.home-v123-why{font-size:11px;color:#43534f;line-height:1.35}
    .home-v123-state{font-size:11px;font-weight:800;padding:5px 8px;border-radius:999px;background:var(--soft,#eef5f2);white-space:nowrap}.home-v123-state.good{color:#13725f;background:#e9f7f2}.home-v123-state.warn{color:#8b641b;background:#fff4d9}.home-v123-state.neutral{color:#5d6b67}.home-v123-arrow{font-size:18px;color:var(--muted,#64748b)}.home-v123-foot{padding:9px 14px 12px;color:var(--muted,#64748b);font-size:11px;line-height:1.4}
    .home-summary-card,.home-today-card{box-shadow:0 8px 24px rgba(26,55,47,.035)}.home-trust{margin-top:8px!important;opacity:.72}.trust-line{font-size:11px!important}
    @media(max-width:640px){.home-v123-row{grid-template-columns:32px minmax(0,1fr) 16px}.home-v123-state{grid-column:2;justify-self:start;padding:3px 7px}.home-v123-arrow{grid-column:3;grid-row:1 / span 2}.home-v123-icon{grid-row:1 / span 2}}
  `;document.head.appendChild(s)}

  function assessment(r,scope='day'){
    const ev=(r?.evidence||[]).find(x=>x&&x.type==='TEN_GOD_THEME')||{};
    const t=r?.technical||{};
    const dg=t?.[scope==='month'?'thang':'ngay']?.danh_gia||{};
    const theme=ev.theme||t.theme||dg.theme||{};
    const group=ev.theme_group||t.theme_group||theme.theme_group||null;
    const tenGod=ev.ten_god_vi||theme.ten_god_vi||ev.ten_god||theme.ten_god||theme.theme||null;
    const pstate=t.personal_state||dg.state||((r?.conclusion||{}).state)||null;
    const impacts=t.branch_impacts||dg.branch_impacts||[];
    return {group,tenGod,pstate,impacts};
  }
  function tone(r){const s=String(r?.conclusion?.state||'');if(s==='SUPPORT'||s.includes('THUẬN'))return'good';if(s==='CAUTION'||s.includes('THẬN'))return'warn';return'neutral'}
  function seen(a){if(!a.tenGod&&!a.group)return'Chưa có một chủ đề Thập Thần đủ rõ để nêu riêng.';const g=GROUP_LABEL[a.group]||a.group||'chưa phân nhóm';return `Đang nổi bật: ${a.tenGod||g} · nhóm ${g}.`}
  function personalMeaning(a){const st=STATE_LABEL[a.pstate]||String(a.pstate||'chưa xác định').toLowerCase();const rel=a.impacts?.length?` Có ${a.impacts.length} quan hệ Chi đang được ghi nhận làm bằng chứng bổ sung.`:'';return `Nền cá nhân ${st}.${rel}`}
  function domainWhy(key,a,r){
    const g=a.group;const name=a.tenGod||GROUP_LABEL[g]||'chủ đề hiện tại';
    if(key==='finance'&&g!=='WEALTH')return `${name} không thuộc nhóm Tài, nên app không dùng tín hiệu này để suy tiền bạc.`;
    if(key==='relationship'&&g!=='PEER')return `${name} không thuộc nhóm phối hợp/người ngang vai, nên app chưa dùng nó để kết luận quan hệ.`;
    if(key==='work'&&!['AUTHORITY','RESOURCE','OUTPUT','PEER'].includes(g))return `${name} không nằm trong nhóm tín hiệu Công việc đã khóa, nên app không ép kết luận nghề nghiệp.`;
    const meaning={AUTHORITY:'liên quan trách nhiệm, quy tắc và vị trí công việc',RESOURCE:'liên quan học hỏi, hồ sơ, chuẩn bị và nguồn hỗ trợ',OUTPUT:'liên quan thực thi, trình bày và tạo đầu ra',PEER:'liên quan phối hợp, tự chủ và người ngang vai',WEALTH:'liên quan quản lý tài và nguồn lực'}[g];
    return meaning?`${name} ${meaning}. ${r?.plain_explanation||''}`:(r?.plain_explanation||'Bấm để xem căn cứ chi tiết.');
  }
  async function loadConcrete(){
    const p=current();if(!p)return null;const key=p.profile_id||p.full_name||'profile';if(cacheData&&cacheKey===key&&Date.now()-cacheAt<30000)return cacheData;
    const [today,month,...domains]=await Promise.all([
      post('/api/v2/hom-nay',{profile:p}),post('/api/v2/thang-nay',{profile:p}),
      ...domainDefs.map(d=>post(d.url,{profile:p,scope:'day'}))
    ]);
    cacheKey=key;cacheAt=Date.now();cacheData={today,month,domains};return cacheData;
  }
  function renderPeriod(el,r,label,scope,openKind){if(!el||!r)return;const a=assessment(r,scope),c=r.conclusion||{};el.classList.remove('loading-card');el.innerHTML=`<button class="home-card-click" onclick="openQuestion('${openKind}')"><div class="home-card-head"><div><small>${label}</small><b>${esc(a.tenGod?`Nổi bật ${a.tenGod}`:(c.title||c.label||'Chưa đủ căn cứ'))}</b></div><span>›</span></div><div class="home-v123-signal"><b>${esc(seen(a))}</b><span>${esc(personalMeaning(a))}</span></div><div class="v2-meta"><span class="v2-confidence ${tone(r)}">${esc(r.confidence_state||'Chưa đủ căn cứ')}</span></div><span class="v2-home-more">Xem kết luận và căn cứ đầy đủ ›</span></button>`}
  function renderDomains(data){const todayEl=$('home-today-summary');if(!todayEl||!data)return;let box=$('home-domain-overview-v122');if(!box){box=document.createElement('section');box.id='home-domain-overview-v122';todayEl.insertAdjacentElement('afterend',box)}box.className='home-v123-card';box.innerHTML=`<div class="home-v123-head"><small>HÔM NAY THEO TỪNG LĨNH VỰC</small><h3>Cùng một tín hiệu, mỗi lĩnh vực được dùng khác nhau</h3><p>App nêu rõ tín hiệu đang thấy và lý do nó có hoặc không đủ quyền tạo kết luận.</p></div><div class="home-v123-list">${domainDefs.map((d,i)=>{const r=data.domains[i]||{},a=assessment(r),c=r.conclusion||{};return `<button class="home-v123-row" onclick="${d.open}"><span class="home-v123-icon">${d.icon}</span><span class="home-v123-main"><b>${esc(d.label)} · ${esc(a.tenGod||GROUP_LABEL[a.group]||'chưa có chủ đề rõ')}</b><small>${esc(c.title||c.label||'Chưa đủ căn cứ')}</small><span class="home-v123-why">${esc(domainWhy(d.key,a,r))}</span></span><span class="home-v123-state ${tone(r)}">${esc(r.confidence_state||'Chưa đủ căn cứ')}</span><span class="home-v123-arrow">›</span></button>`}).join('')}</div><div class="home-v123-foot">“Chưa đủ căn cứ” giờ luôn đi kèm lý do: tín hiệu nào đang hiện diện và vì sao tín hiệu đó không thuộc phạm vi của lĩnh vực đang xem.</div>`}
  async function refreshContent(){if(!currentProfile)return;try{const d=await loadConcrete();if(!d)return;renderPeriod($('home-month-summary'),d.month,'THÁNG NÀY CỦA TÔI','month','month');renderPeriod($('home-today-summary'),d.today,'HÔM NAY ĐANG NỔI BẬT GÌ?','day','today');renderDomains(d)}catch(e){console.warn('[Home V1.2.3]',e)}}

  const previousHome=loadHomeDashboard;loadHomeDashboard=async function(){await previousHome();await refreshContent()};
  addStyles();window.addEventListener('load',()=>setTimeout(()=>{try{refreshContent()}catch{}},2200));
})();
