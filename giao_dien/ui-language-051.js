// UI language layer 0.5.1 — presentation only, no decision logic changes.
(function(){
  const RAW_MISSING = /^(Chưa đủ căn cứ|Chưa có tín hiệu nổi bật|—)?$/i;

  function statusText(label, compact=false){
    const x=String(label||'').trim();
    if(!x) return compact?'Chưa có tín hiệu':'Chưa có tín hiệu nổi bật';
    if(/Bị chặn|HARD_BLOCK/i.test(x)) return compact?'Bị chặn':'Không nên chọn cho việc này';
    if(/^Không ưu tiên$/i.test(x)) return compact?'Không ưu tiên':'Không nên ưu tiên';
    if(/Cần thận trọng|CAUTION/i.test(x)) return compact?'Thận trọng':'Nên thận trọng hơn';
    if(/Có thể cân nhắc|Cân nhắc/i.test(x)) return compact?'Cân nhắc':'Có thể cân nhắc';
    if(/Thuận nền mệnh|SUPPORT/i.test(x)) return compact?'Khá thuận':'Khá thuận với nền mệnh';
    if(/^Ưu tiên$/i.test(x)) return compact?'Ưu tiên':'Nên ưu tiên';
    if(/Trung tính/i.test(x)) return compact?'Cân bằng':'Tương đối cân bằng';
    return x;
  }

  function domainText(value, kind){
    const x=String(value||'').trim();
    if(!x || RAW_MISSING.test(x)){
      if(kind==='viec_lon') return 'Chọn một việc cụ thể để xem';
      return 'Chưa có tín hiệu riêng nổi bật';
    }
    return x;
  }

  function dateVi(iso){
    if(!iso) return '';
    const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso));
    return m?`${m[3]}/${m[2]}/${m[1]}`:iso;
  }

  function addPolishStyles(){
    if(document.getElementById('ui-language-051-style')) return;
    const s=document.createElement('style');
    s.id='ui-language-051-style';
    s.textContent=`
      .ui-tap-why{display:block;margin-top:8px;font-size:12px;font-weight:700;color:var(--teal,#0f766e)}
      .today-051-hero{padding:22px 24px;border-radius:22px;background:linear-gradient(135deg,#0f766e,#0d8177);color:#fff;box-shadow:var(--shadow,0 10px 30px rgba(0,0,0,.08))}
      .today-051-hero small{display:block;opacity:.82;font-weight:700;margin-bottom:7px}.today-051-hero h2{margin:0;font-size:26px;line-height:1.2}.today-051-hero p{margin:8px 0 0;opacity:.9}
      .today-051-summary{margin-top:14px;padding:18px 20px}.today-051-summary h3{margin:0 0 8px}.today-051-summary p{margin:0;line-height:1.55}
      .today-051-details{margin-top:14px}.today-051-details summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px;font-weight:800}.today-051-details summary::-webkit-details-marker{display:none}.today-051-details summary small{font-weight:500;color:var(--muted,#64748b)}.today-051-details[open] summary{margin-bottom:14px}
      .today-051-secondary{margin-top:12px}.today-051-secondary summary{cursor:pointer;font-weight:700;color:var(--muted,#64748b)}
      .ordinal-meter small{max-width:110px;line-height:1.25}
    `;
    document.head.appendChild(s);
  }

  badgeClass=function(label=''){
    const x=String(label||'');
    if(/Bị chặn|Không ưu tiên|JI|HARD_BLOCK/i.test(x))return'bad';
    if(/Ưu tiên|Phù hợp|Thuận nền mệnh|SUPPORT/i.test(x))return'good';
    if(/Có thể cân nhắc|Cân nhắc|Cần thận trọng|CAUTION|lưu ý/i.test(x))return'warn';
    return'neutral';
  };

  ordinalMeter=function(label){
    const cls=badgeClass(label), shown=statusText(label,true);
    return `<div class="ordinal-meter ${cls}"><div class="meter-arc"></div><strong>${esc(shown)}</strong><small>Tổng quan tháng</small></div>`;
  };

  loadHomeDashboard=async function(){
    const monthEl=$('home-month-summary'),todayEl=$('home-today-summary'),cycle=$('home-cycle');
    renderFamilyStrip();updateHomeTitle();
    if(!currentProfile){
      if(monthEl)monthEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem tháng này.</div>';
      if(todayEl)todayEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem hôm nay.</div>';
      if(cycle)cycle.textContent='Chọn một người để bắt đầu';return;
    }
    const p=current();
    if(monthEl)monthEl.innerHTML='<div class="loading-line">Đang tải tổng quan tháng…</div>';
    if(todayEl)todayEl.innerHTML='<div class="loading-line">Đang tải hôm nay…</div>';
    try{
      const d=await post('/api/stateless/dashboard',{profile:p});const pos=d.vi_tri||{};
      if(cycle)cycle.textContent=`Đại vận ${pos.dai_van?.tru||'—'} · Năm ${pos.nam_hien_tai?.vi||'—'} · Tháng ${pos.thang_hien_tai?.vi||'—'}`;
      if(monthEl){
        const m=d.thang||{},s=m.don_gian||{},dg=s.dien_giai||{};
        monthEl.classList.remove('loading-card');
        monthEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('month')"><div class="home-card-head"><div><small>THÁNG NÀY CỦA TÔI</small><b>${esc(m.chuyen_sau?.thang?.tru?.vi||'Tháng hiện tại')}</b></div><span>›</span></div><div class="home-month-body">${ordinalMeter(s.tom_tat)}<div class="home-points"><p><i class="neutral-dot"></i><b>Xu hướng:</b> ${esc(statusText(s.tom_tat))}</p><p><i class="neutral-dot"></i><b>Tài chính:</b> ${esc(domainText(dg.tai_chinh,'tai_chinh'))}</p><p><i class="neutral-dot"></i><b>Quan hệ:</b> ${esc(domainText(dg.quan_he,'quan_he'))}</p><p><i class="neutral-dot"></i><b>Việc lớn:</b> ${esc(domainText(dg.viec_lon,'viec_lon'))}</p><span class="ui-tap-why">Nhấn để xem vì sao ›</span></div></div></button>`;
      }
      if(todayEl){
        const t=d.hom_nay||{},s=t.don_gian||{};
        todayEl.classList.remove('loading-card');
        todayEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('today')"><div class="home-card-head"><div><small>HÔM NAY THẾ NÀO?</small><b>${esc(statusText(s.tom_tat))}</b></div><span>›</span></div><div class="today-compact"><span class="today-check ${badgeClass(s.tom_tat)}">i</span><div><p>Đánh giá nền cá nhân trong ngày hôm nay.</p><span class="ui-tap-why">Nhấn để xem vì sao ›</span></div></div></button>`;
      }
    }catch(e){
      if(monthEl)monthEl.innerHTML=`<div class="notice danger"><b>Chưa tải được tổng quan tháng</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="loadHomeDashboard()">Thử lại</button></div>`;
      if(todayEl)todayEl.innerHTML=`<div class="notice danger"><b>Chưa tải được kết quả hôm nay</b>${esc(e.message)}</div>`;
    }
  };

  renderTodayA=function(d,p){
    const s=d.don_gian||{},deep=d.chuyen_sau||{},raw=s.tom_tat||'Chưa có tín hiệu nổi bật';
    const headline=statusText(raw);
    const reason=(s.vi_sao&&String(s.vi_sao).length<180)?s.vi_sao:'Kết luận được hợp lưu từ Đại vận, Năm, Tháng và Ngày của hồ sơ.';
    const adjacent=adjacentCompare(d,'day');
    const hours=hoursBlock(d);
    return `<div class="today-051-hero"><small>${esc(dateVi(d.ngay))} · ${esc(p?.full_name||'Hồ sơ đang chọn')}</small><h2>${esc(headline)}</h2><p>${esc(reason)}</p></div>
      <div class="card today-051-summary"><h3>Hôm nay nên hiểu thế nào?</h3><p>${esc(headline)}. Đây là đánh giá nền cá nhân của ngày, không tự suy thành kết luận riêng về tiền bạc, quan hệ hay một việc cụ thể.</p></div>
      <details class="card today-051-details"><summary><span>Vì sao có kết luận này?</span><small>Nhấn để xem</small></summary>${fusionHtml(deep,true)}<p class="muted">Đại vận → Năm → Tháng → Ngày được hợp lưu theo cấu trúc. Trường hợp Cách cục/Hỷ-Kỵ chưa đủ rõ sẽ tự hạ về mô tả, không ép kết luận.</p><button class="btn full-btn" onclick="loadWhy('day')">Xem nguồn & quy tắc</button><div id="why-box"></div></details>
      ${(adjacent||hours)?`<details class="card today-051-secondary"><summary>Thông tin tham khảo thêm</summary>${adjacent}${hours}</details>`:''}`;
  };

  const oldRenderCalendar=renderCalendar;
  renderCalendar=async function(){
    await oldRenderCalendar();
    document.querySelectorAll('.day-state-text').forEach(el=>{el.textContent=statusText(el.textContent,true)});
    document.querySelectorAll('.calendar-list-row .result-label').forEach(el=>{el.textContent=statusText(el.textContent,true)});
    const legend=document.querySelector('.calendar-legend');
    if(legend)legend.innerHTML='<span><i class="dot good"></i>Khá thuận</span><span><i class="dot warn"></i>Thận trọng</span><span><i class="dot bad"></i>Không ưu tiên</span><span><i class="dot neutral"></i>Cân bằng</span>';
  };

  addPolishStyles();
  window.addEventListener('load',()=>setTimeout(()=>{
    try{if(currentProfile)loadHomeDashboard();if($('screen-calendar')?.classList.contains('active'))renderCalendar()}catch{}
  },700));
})();
