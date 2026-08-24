// Plain-language interpretation layer V1.2 — presentation only; no decision/ranking logic changes.
(function(){
  function plainStatus(raw){
    const x=String(raw||'').trim();
    if(/Bị chặn|HARD_BLOCK/i.test(x)) return {tone:'bad', short:'Không phù hợp cho việc đang chọn', title:'Không nên chọn thời điểm này cho việc đang xem', meaning:'Có điều kiện chặn ở lớp chọn ngày. Tín hiệu thuận ở lớp cá nhân không được dùng để đảo ngược kết quả này.'};
    if(/^Không ưu tiên$/i.test(x)) return {tone:'bad', short:'Không ưu tiên', title:'Không nên ưu tiên thời điểm này', meaning:'Các yếu tố đang xét chưa ủng hộ việc chọn thời điểm này so với các lựa chọn khác.'};
    if(/Cần thận trọng|CAUTION/i.test(x)) return {tone:'warn', short:'Nên thận trọng hơn', title:'Hôm nay nên chậm lại trước các quyết định quan trọng', meaning:'Nền cá nhân trong thời điểm này kém thuận hơn bình thường. Việc thường ngày vẫn có thể làm; việc quan trọng nên kiểm riêng trước khi quyết định.'};
    if(/Có thể cân nhắc|Cân nhắc/i.test(x)) return {tone:'warn', short:'Có thể cân nhắc', title:'Có thể thực hiện, nhưng nên kiểm kỹ trước việc quan trọng', meaning:'Tín hiệu hiện tại không xấu rõ rệt nhưng cũng chưa đủ mạnh để gọi là thuận.'};
    if(/Thuận nền mệnh|SUPPORT/i.test(x)) return {tone:'good', short:'Khá thuận', title:'Thời điểm này nhìn chung khá thuận với bạn', meaning:'Nền cá nhân đang được hỗ trợ hơn bình thường. Điều này không có nghĩa mọi lĩnh vực đều tốt; việc quan trọng vẫn cần kiểm theo đúng loại việc.'};
    if(/^Ưu tiên$/i.test(x)) return {tone:'good', short:'Nên ưu tiên', title:'Đây là một lựa chọn nên ưu tiên cho việc đang xem', meaning:'Lớp sự kiện và lớp cá nhân đang cùng ủng hộ lựa chọn này trong phạm vi quy tắc đã nghiệm thu.'};
    if(/Trung tính|Cân bằng/i.test(x)) return {tone:'neutral', short:'Tương đối cân bằng', title:'Thời điểm này tương đối cân bằng', meaning:'Chưa có tín hiệu đủ mạnh để gọi là thuận hay nghịch. Có thể tiếp tục việc thường ngày; việc quan trọng nên kiểm riêng.'};
    return {tone:'neutral', short:'Chưa có tín hiệu rõ', title:'Chưa có tín hiệu đủ rõ để kết luận mạnh', meaning:'Ứng dụng chưa có đủ căn cứ để đưa ra kết luận mạnh ở lớp hiện tại.'};
  }

  function actionGuide(raw){
    const p=plainStatus(raw);
    if(p.tone==='good') return {
      yes:['Tiếp tục các kế hoạch đã chuẩn bị rõ ràng.','Ưu tiên xử lý việc thường ngày hoặc việc đã có phương án.','Nếu là việc lớn, chọn đúng loại việc để kiểm ngày riêng.'],
      caution:['Không suy từ “khá thuận” thành chắc chắn có lợi về tiền bạc hay quan hệ.','Không dùng kết luận chung để thay cho kiểm tra một việc cụ thể.']
    };
    if(p.tone==='warn') return {
      yes:['Giữ nhịp sinh hoạt và công việc bình thường.','Kiểm tra kỹ thông tin trước quyết định quan trọng.','Nếu có việc lớn, dùng mục “Tìm ngày cho một việc”.'],
      caution:['Hạn chế quyết định vội chỉ vì cảm giác thời điểm đang thuận.','Không suy kết luận chung thành dự đoán riêng về tiền bạc hay quan hệ.']
    };
    if(p.tone==='bad') return {
      yes:['Ưu tiên phương án khác nếu việc đang chọn có thể dời.','Xem các ngày thay thế trong mục “Tìm ngày cho một việc”.'],
      caution:['Không để tín hiệu cá nhân thuận lật một điều kiện chặn của việc đang chọn.','Không cố chọn giờ để cứu một ngày đã bị chặn.']
    };
    return {
      yes:['Tiếp tục việc thường ngày như bình thường.','Với việc quan trọng, kiểm theo đúng loại việc trước khi quyết định.'],
      caution:['Không xem trạng thái cân bằng là ngày tốt tuyệt đối.','Không tự suy thành kết luận riêng về tiền bạc, quan hệ hoặc sức khỏe.']
    };
  }

  function domainPlain(value,kind){
    const x=String(value||'').trim();
    if(!x || /^(Chưa đủ căn cứ|Chưa có tín hiệu nổi bật|—)$/i.test(x)){
      if(kind==='viec_lon') return 'Chọn một việc cụ thể để kiểm ngày phù hợp.';
      if(kind==='tai_chinh') return 'Chưa có tín hiệu riêng đủ mạnh về tiền bạc.';
      if(kind==='quan_he') return 'Chưa có tín hiệu riêng đủ mạnh về quan hệ.';
      return 'Chưa có tín hiệu riêng đủ mạnh.';
    }
    return x;
  }

  function plainGuideHtml(raw){
    const g=actionGuide(raw);
    return `<div class="plain-guide"><div><h3>Nên làm</h3>${g.yes.map(x=>`<p>✓ ${esc(x)}</p>`).join('')}</div><div><h3>Cần thận trọng</h3>${g.caution.map(x=>`<p>• ${esc(x)}</p>`).join('')}</div></div>`;
  }

  function addPlainStyles(){
    if(document.getElementById('ui-plain-v12-style'))return;
    const s=document.createElement('style');s.id='ui-plain-v12-style';
    s.textContent=`
      .plain-kicker{font-size:12px;font-weight:800;letter-spacing:.04em;color:var(--muted,#64748b);text-transform:uppercase}
      .plain-meaning{margin-top:8px;line-height:1.55;color:var(--text,#18312d)}
      .plain-guide{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.plain-guide>div{padding:16px;border:1px solid var(--line,#d7e2de);border-radius:16px;background:var(--surface,#fff)}.plain-guide h3{margin:0 0 8px;font-size:15px}.plain-guide p{margin:6px 0;line-height:1.45}
      .plain-domains{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}.plain-domain{padding:12px 14px;border:1px solid var(--line,#d7e2de);border-radius:14px;background:var(--surface,#fff)}.plain-domain b{display:block;margin-bottom:4px}.plain-domain span{font-size:13px;line-height:1.4;color:var(--muted,#64748b)}
      .plain-why{margin-top:14px}.plain-why summary{cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:10px;font-weight:800;list-style:none}.plain-why summary::-webkit-details-marker{display:none}.plain-why[open] summary{margin-bottom:12px}.plain-expert{margin-top:12px}.plain-expert summary{cursor:pointer;font-weight:700;color:var(--muted,#64748b)}
      .home-plain-note{display:block;margin-top:7px;font-size:12px;color:var(--muted,#64748b);line-height:1.35}.home-plain-why{display:block;margin-top:7px;font-size:12px;font-weight:800;color:var(--teal,#0f766e)}
      @media(max-width:640px){.plain-guide,.plain-domains{grid-template-columns:1fr}}
    `;document.head.appendChild(s);
  }

  // Home: answer in everyday language first.
  loadHomeDashboard=async function(){
    const monthEl=$('home-month-summary'),todayEl=$('home-today-summary'),cycle=$('home-cycle');renderFamilyStrip();updateHomeTitle();
    if(!currentProfile){if(monthEl)monthEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem tháng này.</div>';if(todayEl)todayEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem hôm nay.</div>';if(cycle)cycle.textContent='Chọn một người để bắt đầu';return}
    const p=current();if(monthEl)monthEl.innerHTML='<div class="loading-line">Đang tải tổng quan tháng…</div>';if(todayEl)todayEl.innerHTML='<div class="loading-line">Đang tải hôm nay…</div>';
    try{
      const d=await post('/api/stateless/dashboard',{profile:p});const pos=d.vi_tri||{};if(cycle)cycle.textContent=`Đại vận ${pos.dai_van?.tru||'—'} · Năm ${pos.nam_hien_tai?.vi||'—'} · Tháng ${pos.thang_hien_tai?.vi||'—'}`;
      if(monthEl){const m=d.thang||{},s=m.don_gian||{},dg=s.dien_giai||{},ps=plainStatus(s.tom_tat);monthEl.classList.remove('loading-card');monthEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('month')"><div class="home-card-head"><div><small>THÁNG NÀY CỦA TÔI</small><b>${esc(m.chuyen_sau?.thang?.tru?.vi||'Tháng hiện tại')}</b></div><span>›</span></div><div class="home-month-body"><div class="ordinal-meter ${ps.tone}"><div class="meter-arc"></div><strong>${esc(ps.short)}</strong><small>Tổng quan tháng</small></div><div class="home-points"><p><b>Nhìn chung:</b> ${esc(ps.title.replace(/^Thời điểm này /,'').replace(/^Hôm nay /,'').replace(/^Tháng này /,''))}</p><p><b>Tiền bạc:</b> ${esc(domainPlain(dg.tai_chinh,'tai_chinh'))}</p><p><b>Quan hệ:</b> ${esc(domainPlain(dg.quan_he,'quan_he'))}</p><p><b>Việc quan trọng:</b> ${esc(domainPlain(dg.viec_lon,'viec_lon'))}</p><span class="home-plain-why">Nhấn để xem nên hiểu thế nào và vì sao ›</span></div></div></button>`}
      if(todayEl){const t=d.hom_nay||{},s=t.don_gian||{},ps=plainStatus(s.tom_tat);todayEl.classList.remove('loading-card');todayEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('today')"><div class="home-card-head"><div><small>HÔM NAY THẾ NÀO?</small><b>${esc(ps.title)}</b></div><span>›</span></div><div class="today-compact"><span class="today-check ${ps.tone}">i</span><div><p>${esc(ps.meaning)}</p><span class="home-plain-why">Nhấn để xem nên làm gì và vì sao ›</span></div></div></button>`}
    }catch(e){if(monthEl)monthEl.innerHTML=`<div class="notice danger"><b>Chưa tải được tổng quan tháng</b>${esc(e.message)}</div>`;if(todayEl)todayEl.innerHTML=`<div class="notice danger"><b>Chưa tải được kết quả hôm nay</b>${esc(e.message)}</div>`}
  };

  // Today: plain conclusion -> practical interpretation -> why -> expert trace.
  renderTodayA=function(d,p){
    const s=d.don_gian||{},deep=d.chuyen_sau||{},ps=plainStatus(s.tom_tat);const dateText=typeof dateVi==='function'?dateVi(d.ngay):(d.ngay||'');
    return `<div class="today-051-hero"><small>${esc(dateText)} · ${esc(p?.full_name||'Hồ sơ đang chọn')}</small><h2>${esc(ps.title)}</h2><p>${esc(ps.meaning)}</p></div>
      <div class="card"><span class="plain-kicker">Gợi ý sử dụng kết quả</span>${plainGuideHtml(s.tom_tat)}</div>
      <details class="card plain-why"><summary><span>Vì sao app đánh giá như vậy?</span><small>Nhấn để xem</small></summary><p class="plain-meaning">Ứng dụng so trạng thái nền của bạn với giai đoạn dài hạn, năm, tháng và ngày hiện tại. Kết luận ở trên chỉ nói mức độ thuận/nghịch chung; nó không tự biến thành dự đoán riêng về tiền bạc, quan hệ hay một việc cụ thể.</p><details class="plain-expert"><summary>Xem phương pháp Tử Bình & dữ liệu kỹ thuật</summary>${fusionHtml(deep,true)}<p class="muted">Đại vận → Năm → Tháng → Ngày được hợp lưu theo cấu trúc. Nếu Cách cục/Hỷ-Kỵ chưa đủ rõ, app hạ về mô tả thay vì ép kết luận.</p><button class="btn full-btn" onclick="loadWhy('day')">Xem nguồn & quy tắc</button><div id="why-box"></div></details></details>
      <details class="card today-051-secondary"><summary>Thông tin tham khảo thêm</summary>${adjacentCompare(d,'day')}${hoursBlock(d)}</details>`;
  };

  // Month: remove jargon from the first screen; technical timeline stays behind an expert disclosure.
  renderMonthB=function(d,p){
    const s=d.don_gian||{},deep=d.chuyen_sau||{},dg=s.dien_giai||{},ps=plainStatus(s.tom_tat);
    return `<div class="card today-051-summary"><span class="plain-kicker">Tổng quan tháng</span><h2>${esc(ps.title.replace(/^Hôm nay /,'').replace(/^Thời điểm này /,'Tháng này '))}</h2><p class="plain-meaning">${esc(ps.meaning.replace(/^Nền cá nhân trong thời điểm này/,'Nền cá nhân trong tháng này'))}</p><div class="plain-domains"><div class="plain-domain"><b>Tiền bạc</b><span>${esc(domainPlain(dg.tai_chinh,'tai_chinh'))}</span></div><div class="plain-domain"><b>Quan hệ</b><span>${esc(domainPlain(dg.quan_he,'quan_he'))}</span></div><div class="plain-domain"><b>Việc quan trọng</b><span>${esc(domainPlain(dg.viec_lon,'viec_lon'))}</span></div><div class="plain-domain"><b>Phạm vi kết luận</b><span>Đây là tổng quan tháng, không phải khẳng định mọi việc đều thuận hoặc nghịch.</span></div></div></div>
      <div class="card"><span class="plain-kicker">Nên hiểu và sử dụng thế nào?</span>${plainGuideHtml(s.tom_tat)}</div>
      <details class="card plain-why"><summary><span>Vì sao app đánh giá tháng như vậy?</span><small>Nhấn để xem</small></summary><p class="plain-meaning">Ứng dụng ghép trạng thái nền của hồ sơ với giai đoạn dài hạn, năm và tháng hiện tại. Khi chưa có quy tắc riêng đủ mạnh cho tiền bạc hay quan hệ, app giữ nguyên là “chưa có tín hiệu riêng” thay vì đoán.</p><details class="plain-expert"><summary>Xem phương pháp Tử Bình & dữ liệu kỹ thuật</summary>${fusionHtml(deep,false)}<button class="btn secondary full-btn" onclick="loadWhy('month')">Xem nguồn & quy tắc</button><div id="why-box"></div></details></details>
      <details class="card today-051-secondary"><summary>So sánh với tháng trước / tháng sau</summary>${adjacentCompare(d,'month')}</details>`;
  };

  addPlainStyles();
  window.addEventListener('load',()=>setTimeout(()=>{try{if(currentProfile)loadHomeDashboard()}catch{}},850));
})();
