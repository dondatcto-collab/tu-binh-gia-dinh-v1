// V2.9A Giờ cá nhân — chọn việc -> kiểm cổng ngày -> tham khảo 12 giờ; chưa sinh giờ tốt/xấu.
(function(){
  window.TU_BINH_HOUR_UI_VERSION='2.9A';
  const EVENTS=[
    ['','— Chọn việc để kiểm tra cổng ngày —'],
    ['AN_TANG','An táng'],['CAU_TAI','Cầu tài'],['CUOI_HOI','Cưới hỏi'],['DAM_PHAN','Đàm phán'],
    ['DIEU_TRI','Điều trị'],['DONG_THO','Động thổ'],['KHAI_TRUONG','Khai trương'],['KY_HOP_DONG','Ký hợp đồng'],
    ['MUA_TAI_SAN','Mua tài sản'],['NHAM_CHUC','Nhậm chức'],['NHAP_TRACH','Nhập trạch'],['XUAT_HANH','Xuất hành']
  ];
  function options(selected=''){return EVENTS.map(([code,label])=>`<option value="${esc(code)}" ${code===selected?'selected':''}>${esc(label)}</option>`).join('')}
  async function fetchHours(eventCode=''){
    const body={profile:current()};
    if(eventCode)body.viec=eventCode;
    return post('/api/v2/gio-ca-nhan',body);
  }
  function hourGateText(x){
    if(x?.day_gate==='HARD_BLOCK')return 'Không xét — ngày đã bị chặn';
    if(x?.day_gate==='PASS_TO_HOUR_RULES')return 'Qua cổng ngày · chờ rule giờ VERIFIED';
    return 'Tham khảo cấu trúc';
  }
  function tone(r){return r?.conclusion?.state==='BLOCKED_BY_DAY'?'bad':(r?.event_code?'warn':'neutral')}
  function card(r){
    const hours=r?.hours||[],selected=r?.event_code||'',day=r?.event_day||{};
    return `<div class="card v24-hour-card ${tone(r)}" data-hour-card>
      <small>GIỜ TRONG NGÀY · V2.9A</small>
      <h3>${esc(r?.conclusion?.title||'Tham khảo cấu trúc giờ')}</h3>
      <p>${esc(r?.plain_explanation||'')}</p>
      <div class="v29-hour-event"><label for="v29-hour-event-select"><b>Xét giờ theo việc</b></label><select id="v29-hour-event-select" onchange="reloadPersonalHoursV29(this.value)">${options(selected)}</select></div>
      <div class="v24-hour-note"><b>Trạng thái:</b> ${esc(r?.conclusion?.label||'Tham khảo cấu trúc')} · <b>Mức căn cứ:</b> ${esc(r?.confidence_state||'Chưa đủ căn cứ')}</div>
      ${day?.conclusion?`<div class="v29-day-gate ${day.hard_block?'bad':'neutral'}"><b>Cổng ngày:</b> ${esc(day.conclusion.label||day.conclusion.state||'Đã xét')}${day.hard_block?' · HARD_BLOCK':''}</div>`:'<div class="soft-note">Chọn một loại việc để app kiểm tra ngày trước khi xét lớp giờ.</div>'}
      <details><summary>Xem 12 khoảng giờ</summary><div class="v24-hour-grid">${hours.map(x=>`<div class="v24-hour-item"><b>${esc(x.time_range||'')}</b> · ${esc(x.chi_vi||x.chi||'')}<br><span>${esc(x.relation_label||'Không có quan hệ trực tiếp trong lớp hiện tại')}</span><small>${esc(hourGateText(x))}</small></div>`).join('')}</div></details>
      <div class="soft-note"><b>Giới hạn:</b> Chưa phải giờ tốt/xấu cá nhân. Giờ không được cứu một ngày HARD_BLOCK. Nhãn giờ chỉ được mở ở V2.9B sau khi rule giờ có nguồn và trạng thái VERIFIED.</div>
    </div>`
  }
  function styles(){
    if(document.getElementById('v24-hour-style'))return;
    const s=document.createElement('style');s.id='v24-hour-style';s.textContent=`
      .v24-hour-card{border-left:5px solid #82918e}.v24-hour-card.bad{border-left-color:#b94a48}.v24-hour-card.warn{border-left-color:#c38b22}.v24-hour-card h3{margin:5px 0 8px}.v24-hour-note{margin:10px 0;font-size:13px}.v29-hour-event{display:grid;gap:6px;margin:12px 0}.v29-hour-event select{width:100%;padding:10px;border:1px solid var(--line,#d7e2de);border-radius:10px;background:var(--card,#fff);color:inherit}.v29-day-gate{padding:9px 11px;border-radius:10px;background:var(--soft,#f4f7f6);font-size:13px;margin:8px 0}.v29-day-gate.bad{background:#fdebea;color:#9a3d3a}.v24-hour-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}.v24-hour-item{border:1px solid var(--line,#d7e2de);border-radius:12px;padding:10px;font-size:13px;line-height:1.4}.v24-hour-item span{display:block;color:var(--muted,#64748b)}.v24-hour-item small{display:block;margin-top:5px;font-weight:700}@media(max-width:640px){.v24-hour-grid{grid-template-columns:1fr}}
    `;document.head.appendChild(s)
  }
  window.reloadPersonalHoursV29=async function(eventCode=''){
    const old=document.querySelector('[data-hour-card]');
    if(old)old.outerHTML='<div class="card" data-hour-card>Đang kiểm tra cổng ngày và 12 giờ…</div>';
    try{
      const html=card(await fetchHours(eventCode));
      const target=document.querySelector('[data-hour-card]');
      if(target)target.outerHTML=html;
    }catch(e){const target=document.querySelector('[data-hour-card]');if(target)target.outerHTML=`<div class="notice danger" data-hour-card><b>Chưa tải được mục Giờ trong ngày</b>${esc(e.message)}</div>`}
  };
  window.openPersonalHoursV24=async function(){
    if(!needProfile())return;navTo('result');$('result-title').textContent='Giờ trong ngày';$('result-body').innerHTML='<div class="card" data-hour-card>Đang đọc cấu trúc giờ…</div>';
    try{$('result-body').innerHTML=card(await fetchHours())}catch(e){$('result-body').innerHTML=`<div class="notice danger"><b>Chưa tải được mục Giờ trong ngày</b>${esc(e.message)}</div>`}
  };
  const previousQuestion=openQuestion;openQuestion=async function(kind){await previousQuestion(kind);if(kind!=='today')return;try{const body=$('result-body');if(body)body.insertAdjacentHTML('beforeend',card(await fetchHours()))}catch{}}
  styles();
})();
