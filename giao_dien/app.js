const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[<>&"']/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':'&quot;',"'":'&#39;'}[c]));
let profiles=[], currentProfile=null, editingId=null, chosenAvatar='adult-male';
let calCursor=new Date();
const themes=[
 ['light','Hiện đại sáng','Tươi sáng, dễ đọc','linear-gradient(135deg,#ffffff 0 54%,#0f766e 54% 100%)'],
 ['dark-calm','Tối thư giãn','Dễ chịu, bảo vệ mắt','linear-gradient(135deg,#13231f 0 58%,#49c6b4 58% 100%)'],
 ['oriental','Đông phương','Ấm áp, tinh tế Á Đông','linear-gradient(135deg,#f6efe3 0 58%,#b58b38 58% 78%,#8c4437 78% 100%)'],
 ['dark-premium','Tối cao cấp','Sang trọng, tương phản cao','linear-gradient(135deg,#121417 0 68%,#d0a84d 68% 100%)'],
 ['dark-blue','Tối xanh dịu','Mát mắt, tập trung','linear-gradient(135deg,#0d1d2a 0 58%,#46b8a9 58% 100%)']
];
const avatarDefs={
 'old-male':['Nam lớn tuổi','/avatars/old-male.png'], 'old-female':['Nữ lớn tuổi','/avatars/old-female.png'],
 'adult-male':['Nam trung niên','/avatars/adult-male.png'], 'adult-female':['Nữ trung niên','/avatars/adult-female.png'],
 'youth-male':['Nam thiếu niên','/avatars/youth-male.png'], 'youth-female':['Nữ thiếu niên','/avatars/youth-female.png']
};
function avatarHtml(code){const [label,src]=avatarDefs[code]||avatarDefs['adult-male'];return `<img class="avatar-img" src="${src}" alt="${label}" loading="lazy">`}

// ----- Kho hồ sơ cục bộ: IndexedDB -----
const DB_NAME='tu-binh-gia-dinh-v1';
const DB_VERSION=1;
const STORE='profiles';
function openLocalDB(){return new Promise((resolve,reject)=>{const req=indexedDB.open(DB_NAME,DB_VERSION);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'profile_id'})};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function dbAll(){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readonly');const req=tx.objectStore(STORE).getAll();req.onsuccess=()=>resolve(req.result||[]);req.onerror=()=>reject(req.error);tx.oncomplete=()=>db.close()})}
async function dbPut(p){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(p);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function dbDelete(id){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).delete(id);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function dbClear(){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).clear();tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
function newId(){return 'P-'+(crypto.randomUUID?crypto.randomUUID().replace(/-/g,'').slice(0,10):Date.now().toString(36)+Math.random().toString(36).slice(2,6))}
function getAvatar(id){return profiles.find(p=>p.profile_id===id)?.avatar||'adult-male'}
function current(){return profiles.find(p=>p.profile_id===currentProfile)||null}

async function api(url,opt={}){const r=await fetch(url,opt);let d;try{d=await r.json()}catch{d={}}if(!r.ok)throw new Error(d.detail||'Không thể thực hiện.');return d}
async function post(url,body){return api(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}

function applySettings(){const theme=localStorage.getItem('xemngay-theme')||'light';const font=localStorage.getItem('xemngay-font')||'normal';document.documentElement.dataset.theme=theme;document.documentElement.dataset.font=font;$('font-size').value=font;renderThemes(theme);updateBackupState()}
function renderThemes(selected){$('theme-grid').innerHTML=themes.map(([id,name,desc,sw])=>`<button class="theme ${id===selected?'selected':''}" onclick="chooseTheme('${id}')"><div class="swatch" style="background:${sw}"></div><b>${name}</b><small>${desc}</small>${id===selected?'<span class="theme-check">✓ Đang dùng</span>':''}</button>`).join('')}
function chooseTheme(id){localStorage.setItem('xemngay-theme',id);applySettings()}
function saveSettings(){localStorage.setItem('xemngay-font',$('font-size').value);applySettings()}
function navTo(name){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));$('screen-'+name).classList.add('active');document.querySelectorAll('.nav-btn').forEach(x=>x.classList.toggle('active',x.dataset.nav===name));window.scrollTo(0,0);if(name==='calendar')renderCalendar();if(name==='profile')renderProfiles();if(name==='settings')updateBackupState()}
async function loadStatus(){return api('/api/tinh-trang').then(s=>{$('status-banner').innerHTML=`<div class="engine-status compact"><div class="engine-row ok"><span class="status-dot"></span><div><b>Kết luận V1 có căn cứ</b><small>Tháng, ngày và tìm ngày theo việc đã có lớp kết luận cơ bản. Dữ liệu hồ sơ chỉ lưu trên thiết bị của bạn.</small></div></div><div class="status-meta"><span class="tag">Có nguồn</span><span class="tag">Có truy nguyên</span><span class="tag">Không tạo điểm giả</span></div></div>`})}
function profileOptions(){return profiles.length?profiles.map(p=>`<option value="${p.profile_id}" ${p.profile_id===currentProfile?'selected':''}>${esc(p.full_name)}</option>`).join(''):'<option value="">— Chưa có hồ sơ —</option>'}
function syncProfileSelectors(){['profile-select','calendar-profile','work-profile'].forEach(id=>{const el=$(id);if(el){el.innerHTML=profileOptions();el.value=currentProfile||''}})}
function selectProfileFrom(id){const el=$(id);currentProfile=el?.value||null;localStorage.setItem('xemngay-profile',currentProfile||'');syncProfileSelectors();updateHomeTitle();if(id==='calendar-profile')renderCalendar()}
async function loadProfiles(){profiles=(await dbAll()).sort((a,b)=>(a.created_at||'').localeCompare(b.created_at||'')||a.full_name.localeCompare(b.full_name,'vi'));const saved=localStorage.getItem('xemngay-profile');if(saved&&profiles.some(p=>p.profile_id===saved))currentProfile=saved;else currentProfile=profiles[0]?.profile_id||null;syncProfileSelectors();const homeSel=$('profile-select');if(homeSel)homeSel.onchange=()=>selectProfileFrom('profile-select');updateHomeTitle();renderProfiles()}
function updateHomeTitle(){const p=current();$('home-title').textContent=p?`Hôm nay của ${p.full_name}`:'Chào gia đình'}
function renderProfiles(){if(!$('profile-list'))return;$('profile-list').innerHTML=profiles.length?profiles.map(p=>`<div class="card profile-row ${p.profile_id===currentProfile?'selected-profile':''}" onclick="selectProfileCard('${p.profile_id}')">${avatarHtml(p.avatar||'adult-male')}<div class="grow"><b>${esc(p.full_name)}</b><div class="muted">Sinh (Dương lịch) ${String(p.birth.day).padStart(2,'0')}/${String(p.birth.month).padStart(2,'0')}/${p.birth.year} · ${String(p.birth.hour).padStart(2,'0')}:${String(p.birth.minute).padStart(2,'0')}</div><div class="muted">${esc(p.birth_place_text)}</div></div><div class="row-actions"><button class="btn secondary small" onclick="event.stopPropagation();editProfile('${p.profile_id}')">Sửa</button><button class="btn danger small" onclick="event.stopPropagation();deleteProfile('${p.profile_id}')">Xóa</button></div></div>`).join(''):'<div class="card muted">Chưa có thành viên. Bấm “Thêm người”.</div>';loadProfileInsight()}
function selectProfileCard(id){currentProfile=id;localStorage.setItem('xemngay-profile',id);syncProfileSelectors();updateHomeTitle();renderProfiles()}
async function loadProfileInsight(){const el=$('profile-insight');if(!el)return;if(!currentProfile){el.innerHTML='';return}el.innerHTML='<div class="card muted">Đang tải thông tin sinh mệnh…</div>';try{const d=await post('/api/stateless/toi-dang-o-dau',{profile:current()});const pillars=Object.values(d.tu_tru||{}).map(x=>x.vi).join(' · ');el.innerHTML=`<div class="card birth-summary"><div class="section-title"><h3>Thông tin sinh mệnh <span class="muted">(thu gọn)</span></h3><span class="tag">${esc(d.ho_ten)}</span></div><div class="birth-table"><div><span>Tứ Trụ</span><b>${esc(pillars||'—')}</b></div><div><span>Đại vận hiện tại</span><b>${esc(d.dai_van?.tru||'—')}</b><small>${d.dai_van?`${esc(d.dai_van.ngay_bat_dau||d.dai_van.nam_bat_dau)} → ${esc(d.dai_van.ngay_ket_thuc||d.dai_van.nam_ket_thuc)} · năm ${d.dai_van.nam_thu_may}/10`:''}</small></div><div><span>Năm / Tháng</span><b>${esc(d.nam_hien_tai?.vi||'—')} · ${esc(d.thang_hien_tai?.vi||'—')}</b></div><div><span>Dụng / Hỷ / Kỵ</span><b class="muted">Chưa dùng để kết luận ở V1-basic</b></div></div>${d.dai_van?.canh_bao?.length?`<div class="soft-note">${d.dai_van.canh_bao.map(esc).join('<br>')}</div>`:''}</div>`}catch(e){el.innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}}
function populateTimezones(){
 const vn='Asia/Ho_Chi_Minh';
 let zones=[];
 try{if(Intl.supportedValuesOf)zones=Intl.supportedValuesOf('timeZone')}catch{}
 if(!zones.length)zones=['Asia/Bangkok','Asia/Singapore','Asia/Shanghai','Asia/Tokyo','Europe/London','America/New_York','America/Los_Angeles','UTC'];
 zones=[...new Set(zones.filter(z=>z!==vn))];
 const select=$('p-timezone');
 select.innerHTML=`<option value="${vn}">🇻🇳 Việt Nam — ${vn} (GMT+7)</option><optgroup label="Múi giờ khác">${zones.map(z=>`<option value="${z}">${z}</option>`).join('')}</optgroup>`;
 select.value=vn;
}
function renderAvatarChoices(){const current=chosenAvatar;$('avatar-grid').innerHTML=Object.entries(avatarDefs).map(([id,[label]])=>`<button type="button" class="avatar-option ${id===current?'selected':''}" onclick="chooseAvatar('${id}')">${avatarHtml(id)}<small>${label}</small></button>`).join('')}
function chooseAvatar(code){chosenAvatar=code;renderAvatarChoices()}
function openAddProfile(){editingId=null;chosenAvatar='adult-male';$('profile-form-title').textContent='Thêm người';['p-name','p-date','p-time','p-place'].forEach(id=>$(id).value='');$('p-gender').value='NAM';$('p-timezone').value='Asia/Ho_Chi_Minh';$('profile-error').textContent='';renderAvatarChoices();$('profile-modal').classList.add('open')}
function editProfile(id){const p=profiles.find(x=>x.profile_id===id);if(!p)return;editingId=id;chosenAvatar=p.avatar||'adult-male';$('profile-form-title').textContent='Sửa hồ sơ';$('p-name').value=p.full_name;$('p-gender').value=p.gender;$('p-date').value=`${p.birth.year}-${String(p.birth.month).padStart(2,'0')}-${String(p.birth.day).padStart(2,'0')}`;$('p-time').value=`${String(p.birth.hour).padStart(2,'0')}:${String(p.birth.minute).padStart(2,'0')}`;$('p-place').value=p.birth_place_text;$('p-timezone').value=p.timezone_name||'Asia/Ho_Chi_Minh';$('profile-error').textContent='';renderAvatarChoices();$('profile-modal').classList.add('open')}
function closeProfileModal(){$('profile-modal').classList.remove('open')}
async function saveProfile(){try{const d=$('p-date').value,t=$('p-time').value;if(!$('p-name').value.trim()||!d||!t||!$('p-place').value.trim())throw new Error('Hãy nhập đủ tên, ngày giờ sinh và nơi sinh.');const old=editingId?profiles.find(x=>x.profile_id===editingId):null;const p={profile_id:editingId||newId(),full_name:$('p-name').value.trim(),gender:$('p-gender').value,birth:{year:+d.slice(0,4),month:+d.slice(5,7),day:+d.slice(8,10),hour:+t.slice(0,2),minute:+t.slice(3,5)},birth_place_text:$('p-place').value.trim(),timezone_name:$('p-timezone').value,time_certainty:'KNOWN',note:old?.note||null,avatar:chosenAvatar,created_at:old?.created_at||new Date().toISOString(),updated_at:new Date().toISOString()};await dbPut(p);currentProfile=p.profile_id;localStorage.setItem('xemngay-profile',currentProfile);closeProfileModal();await loadProfiles();navTo('profile')}catch(e){$('profile-error').textContent=e.message}}
async function deleteProfile(id){const p=profiles.find(x=>x.profile_id===id);if(!confirm(`Xóa hồ sơ ${p?.full_name||''}? Dữ liệu chỉ bị xóa trên thiết bị này.`))return;await dbDelete(id);if(currentProfile===id)localStorage.removeItem('xemngay-profile');await loadProfiles()}
function needProfile(){if(!currentProfile){alert('Hãy thêm và chọn một thành viên trước.');return false}return true}
function fusionHtml(deep,includeDay=false){if(!deep)return'';const layers=[['Đại vận',deep.dai_van?.tru||'Chưa xác định'],['Năm',deep.nam?.tru?.vi||'—'],['Tháng',deep.thang?.tru?.vi||'—']];if(includeDay)layers.push(['Ngày',deep.ngay?.tru_ngay||'—']);return `<div class="fusion">${layers.map(([a,b])=>`<div class="layer"><small>${a}</small><b>${esc(b)}</b></div>`).join('')}</div>`}
function badgeClass(label=''){if(/Rất phù hợp|^Phù hợp$|hòa hợp|Khá thuận/i.test(label))return'good';if(/Không ưu tiên/i.test(label))return'bad';if(/Cân nhắc|xung động|lưu ý/i.test(label))return'warn';return'neutral'}
function decisionHero(simple,scope){const label=simple.tom_tat||simple.tieu_de||'Đang đánh giá';const cls=badgeClass(label);return `<div class="decision-hero ${cls}"><div class="decision-main"><small>${scope==='month'?'THÁNG NÀY':'HÔM NAY'}</small><strong>${esc(label)}</strong><span>${esc(simple.vi_sao||'Kết luận theo lớp quy tắc V1-basic có truy nguồn.')}</span></div><div class="decision-seal">V1<br><b>BASIC</b></div></div>`}
function adviceHtml(simple){return `<div class="advice-grid"><div class="advice good"><h4>✓ NÊN</h4>${(simple.nen_lam||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Theo kế hoạch bình thường.</p>'}</div><div class="advice warn"><h4>! CÂN NHẮC</h4>${(simple.can_nhac||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Kiểm tra điều kiện thực tế.</p>'}</div><div class="advice bad"><h4>× KHÔNG ƯU TIÊN</h4>${(simple.khong_uu_tien||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Không có cấm tuyệt đối ở lớp hiện tại.</p>'}</div></div>`}
async function openQuestion(kind){
 if(!needProfile())return;
 const p=current();navTo('result');$('result-body').innerHTML='<div class="card">Đang tính…</div>';
 try{
  if(kind==='long'){
   const d=await post('/api/stateless/toi-dang-o-dau',{profile:p});
   $('result-title').textContent='Vận dài hạn';
   $('result-body').innerHTML=`<div class="card profile-summary"><h3>${esc(d.ho_ten)}</h3><div class="fusion"><div class="layer"><small>Đại vận</small><b>${esc(d.dai_van?.tru||'—')}</b><span class="subline">${d.dai_van?`Năm ${d.dai_van.nam_thu_may}/10 · ${d.dai_van.ngay_bat_dau||d.dai_van.nam_bat_dau} → ${d.dai_van.ngay_ket_thuc||d.dai_van.nam_ket_thuc}`:'Chưa xác định'}</span></div><div class="layer"><small>Năm</small><b>${esc(d.nam_hien_tai.vi)}</b></div><div class="layer"><small>Tháng</small><b>${esc(d.thang_hien_tai.vi)}</b></div></div></div>${d.dai_van?.canh_bao?.length?`<div class="notice danger"><b>Mốc Đại vận còn PROVISIONAL</b>${d.dai_van.canh_bao.map(esc).join('<br>')}</div>`:''}`;
   return;
  }
  const isMonth=kind==='month';
  const d=await post(isMonth?'/api/stateless/thang-nay':'/api/stateless/hom-nay',{profile:p});
  const simple=d.don_gian,deep=d.chuyen_sau;
  $('result-title').textContent=isMonth?`Tháng này của ${p.full_name}`:`Hôm nay của ${p.full_name}`;
  $('result-body').innerHTML=`${decisionHero(simple,isMonth?'month':'day')}<div class="card result-overview"><div class="result-kicker">HỢP LƯU ${isMonth?'Đại vận → Năm → Tháng':'Đại vận → Năm → Tháng → Ngày'}</div>${fusionHtml(deep,!isMonth)}</div>${adviceHtml(simple)}<div class="card"><h3>Vì sao?</h3><ul class="list-clean">${simple.he_thong_biet_gi.map(x=>`<li class="known-item"><span>✓</span>${esc(x)}</li>`).join('')}</ul>${simple.he_thong_chua_biet_gi.length?`<div class="soft-note">${simple.he_thong_chua_biet_gi.map(x=>`<div>• ${esc(x)}</div>`).join('')}</div>`:''}</div><button class="btn secondary" onclick="loadWhy('${isMonth?'month':'day'}')">TẠI SAO? · Xem chuyên sâu</button><div id="why-box"></div>`;
 }catch(e){$('result-body').innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}
}

async function loadWhy(scope='day'){
 if(!needProfile())return;
 const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:null});
 const scopeText=scope==='month'?'tháng hiện tại':'ngày đang xem';
 $('why-box').innerHTML=`<div class="card expert-box"><h3>Chuyên sâu · ${scopeText}</h3><p class="muted">Phần này dành cho người muốn kiểm tra rule và nguồn. Thuật ngữ kỹ thuật không được dùng để thay thế kết luận ở tầng gia đình.</p>${d.truy_nguoc.length?d.truy_nguoc.map(r=>`<div class="trace-row"><b>${esc(r.rule_id)} · ${esc(r.name_vi)}</b><div><span class="tag">${esc(r.verification_status)}</span> <span class="tag">tin cậy ${esc(r.confidence)}</span></div><div class="muted">${esc(r.source_title||'Chưa gắn nguồn')}${r.source_location?' · '+esc(r.source_location):''}</div>${r.passage_excerpt?`<pre>${esc(r.passage_excerpt)}</pre>`:''}</div>`).join(''):'<div class="muted">Chưa có rule truy ngược phù hợp.</div>'}</div>`
}
function localISODate(d=new Date()){const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${day}`}
function calendarTone(label,state=''){const x=(label||'')+' '+(state||'');if(/Không ưu tiên|JI|CAN_NHAC|xung động/i.test(x))return /Không ưu tiên|JI/i.test(x)?'bad':'warn';if(/Rất phù hợp|Phù hợp|Khá phù hợp|THUAN|hòa hợp/i.test(x))return 'good';return 'neutral'}
async function renderCalendar(){
 const y=calCursor.getFullYear(),m=calCursor.getMonth();$('cal-title').textContent=`Tháng ${m+1}/${y}`;const first=new Date(y,m,1),start=new Date(y,m,1-first.getDay());const today=localISODate();let html=['CN','T2','T3','T4','T5','T6','T7'].map(x=>`<div class="dow">${x}</div>`).join('');
 for(let i=0;i<42;i++){const d=new Date(start);d.setDate(start.getDate()+i);const iso=localISODate(d);html+=`<button id="day-${iso}" class="day ${d.getMonth()!==m?'other':''} ${iso===today?'today':''}" onclick="selectCalendarDay('${iso}',this)"><span class="num">${d.getDate()}</span><span class="state"><i class="day-dot neutral"></i>Đang tính</span></button>`}
 $('calendar-grid').innerHTML=html;
 if(!currentProfile)return;
 try{const r=await post('/api/stateless/lich-thang',{profile:current(),year:y,month:m+1,viec:$('calendar-work')?.value||null});for(const x of r.days||[]){const el=$(`day-${x.ngay}`);if(!el)continue;const tone=calendarTone(x.label,x.state);const st=el.querySelector('.state');if(st)st.innerHTML=`<i class="day-dot ${tone}"></i>${esc(x.label)}`;el.dataset.tone=tone}}catch(e){document.querySelectorAll('.day .state').forEach(st=>st.textContent='Chạm để xem')}
}
function moveMonth(n){calCursor=new Date(calCursor.getFullYear(),calCursor.getMonth()+n,1);renderCalendar()}
function goTodayCalendar(){const n=new Date();calCursor=new Date(n.getFullYear(),n.getMonth(),1);renderCalendar()}
async function selectCalendarDay(iso,el){document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');if(!needProfile())return;$('calendar-detail').innerHTML='Đang tính…';try{const d=await post('/api/stateless/hom-nay',{profile:current(),ngay:iso});const s=d.don_gian;$('calendar-detail').innerHTML=`<div class="calendar-result"><div><small>${iso}</small><h3>${esc(s.tom_tat)}</h3><p>${esc(s.vi_sao||'')}</p></div><span class="result-label ${badgeClass(s.tom_tat)}">${esc(s.tom_tat)}</span></div>${adviceHtml(s)}${fusionHtml(d.chuyen_sau,true)}<button class="btn secondary small" onclick="loadCalendarWhy('${iso}')">Tại sao?</button><div id="calendar-why"></div>`}catch(e){$('calendar-detail').innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}}

async function loadCalendarWhy(iso){const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:iso});$('calendar-why').innerHTML=`<ul class="list-clean">${d.truy_nguoc.map(r=>`<li><b>${esc(r.rule_id)}</b> · ${esc(r.name_vi)} · ${esc(r.verification_status)}</li>`).join('')}</ul>`}
async function loadWorkTypes(){const x=await api('/api/loai-viec');$('work-type').innerHTML=x.map(v=>`<option value="${v.code}">${esc(v.ten)}</option>`).join('');const cw=$('calendar-work');if(cw)cw.innerHTML='<option value="">Xem nhịp cá nhân</option>'+x.map(v=>`<option value="${v.code}">${esc(v.ten)}</option>`).join('');const today=localISODate();$('work-from').value=today;const d=new Date();d.setDate(d.getDate()+14);$('work-to').value=localISODate(d)}
async function findDates(){
 if(!needProfile())return;
 $('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
 try{
  const d=await post('/api/stateless/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
  const top=d.top||[];
  $('work-result').innerHTML=`<div class="card"><div class="result-kicker">KẾT QUẢ GỢI Ý · TOP ${top.length}</div>${d.canh_bao_an_toan?`<div class="notice danger"><b>Lưu ý y tế</b>${esc(d.canh_bao_an_toan)}</div>`:''}${top.map((x,i)=>`<div class="rank-card ${badgeClass(x.label)}"><div class="rank-no">${i+1}</div><div class="grow"><b>${esc(x.ngay)} · ${esc(x.tru_ngay)}</b><strong>${esc(x.label)}</strong><small>Trực ${esc(x.truc||'—')} · ${esc(x.personal_relation?.nhan||'')}</small>${(x.reasons||[]).slice(0,3).map(r=>`<p>• ${esc(r)}</p>`).join('')}${x.event_note?`<p class="mapping-note">${esc(x.event_note)}</p>`:''}</div></div>`).join('')||'<div class="muted">Không có ngày trong khoảng đã chọn.</div>'}<div class="soft-note"><b>Phạm vi V1-basic:</b> ${esc(d.ghi_chu||'')}</div><button class="btn secondary small" onclick="toggleResearchDays()">Xem toàn bộ ${d.so_ngay_da_quet} ngày</button><div id="research-days" class="research-days" hidden>${(d.cac_ngay||[]).map(x=>`<div class="research-row"><b>${x.ngay}</b> · ${esc(x.tru_ngay)} · <span class="result-label ${badgeClass(x.label)}">${esc(x.label)}</span><div class="muted">Trực ${esc(x.truc||'—')} · ${esc(x.personal_relation?.nhan||'')}</div></div>`).join('')}</div></div>`;
 }catch(e){$('work-result').innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}
}

function toggleResearchDays(){const el=$('research-days');if(el)el.hidden=!el.hidden}

// ----- Sao lưu / khôi phục -----
function updateBackupState(){const el=$('backup-state');if(!el)return;const last=localStorage.getItem('xemngay-last-backup');if(!last){el.textContent='Chưa có bản sao lưu trên thiết bị này.';return}const days=Math.floor((Date.now()-new Date(last).getTime())/86400000);el.textContent=days>=30?`Đã ${days} ngày chưa sao lưu. Nên tạo bản sao lưu mới.`:`Lần sao lưu gần nhất: ${new Date(last).toLocaleString('vi-VN')}.`}
async function exportBackup(){const data={format:'TU_BINH_GIA_DINH_BACKUP',schema_version:1,exported_at:new Date().toISOString(),profiles:await dbAll(),settings:{theme:localStorage.getItem('xemngay-theme')||'light',font:localStorage.getItem('xemngay-font')||'normal',current_profile:currentProfile}};const text=JSON.stringify(data,null,2),name=`tu-binh-gia-dinh-${localISODate()}.json`;const file=new File([text],name,{type:'application/json'});if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'Sao lưu Tử Bình Gia Đình'});}else{const blob=new Blob([text],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);}localStorage.setItem('xemngay-last-backup',new Date().toISOString());updateBackupState()}
function chooseRestoreFile(){$('restore-file').click()}
async function restoreBackup(input){const file=input.files?.[0];input.value='';if(!file)return;try{const data=JSON.parse(await file.text());if(data.format!=='TU_BINH_GIA_DINH_BACKUP'||data.schema_version!==1||!Array.isArray(data.profiles))throw new Error('File không phải bản sao lưu V1 hợp lệ.');const names=data.profiles.map(p=>p.full_name).filter(Boolean).slice(0,8).join(', ');if(!confirm(`Khôi phục ${data.profiles.length} hồ sơ${names?' ('+names+')':''}? Dữ liệu hồ sơ hiện có trên thiết bị sẽ được thay thế.`))return;await dbClear();for(const p of data.profiles)await dbPut(p);if(data.settings?.theme)localStorage.setItem('xemngay-theme',data.settings.theme);if(data.settings?.font)localStorage.setItem('xemngay-font',data.settings.font);if(data.settings?.current_profile)localStorage.setItem('xemngay-profile',data.settings.current_profile);await loadProfiles();applySettings();alert('Khôi phục dữ liệu thành công.')}catch(e){alert('Không thể khôi phục: '+e.message)}}
async function deleteAllLocal(){if(!confirm('Xóa TOÀN BỘ hồ sơ trên thiết bị này? Hành động này không thể hoàn tác nếu chưa sao lưu.'))return;if(!confirm('Xác nhận lần cuối: xóa toàn bộ dữ liệu cục bộ?'))return;await dbClear();localStorage.removeItem('xemngay-profile');currentProfile=null;await loadProfiles();alert('Đã xóa dữ liệu trên thiết bị này.')}

async function boot(){applySettings();populateTimezones();renderAvatarChoices();await loadStatus();await loadProfiles();await loadWorkTypes();renderCalendar()}
boot().catch(e=>{$('status-banner').innerHTML=`<div class="notice danger"><b>Không khởi động được</b>${esc(e.message)}</div>`});

// ----- PWA -----
let deferredInstallPrompt=null;
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredInstallPrompt=e;const b=$('install-button');if(b)b.style.display='block';const st=$('install-state');if(st)st.textContent='Thiết bị này có thể cài ứng dụng trực tiếp.'});
window.addEventListener('appinstalled',()=>{deferredInstallPrompt=null;const b=$('install-button');if(b)b.style.display='none';const st=$('install-state');if(st)st.textContent='Ứng dụng đã được cài trên thiết bị.'});
async function installPWA(){if(!deferredInstallPrompt){alert('iPhone: Safari → Chia sẻ → Thêm vào Màn hình chính. Android: Chrome → menu ⋮ → Cài ứng dụng.');return}deferredInstallPrompt.prompt();await deferredInstallPrompt.userChoice;deferredInstallPrompt=null}
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/service-worker.js').catch(()=>{}));}
