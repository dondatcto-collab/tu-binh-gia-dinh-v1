const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[<>&"']/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':'&quot;',"'":'&#39;'}[c]));
let profiles=[], currentProfile=null, editingId=null, chosenAvatar='adult-male';
let calCursor=new Date();
let calendarDays=[];
let calendarView='month';
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
const DB_VERSION=2;
const APP_VERSION='0.3.0';
const STORE='profiles';
function openLocalDB(){return new Promise((resolve,reject)=>{const req=indexedDB.open(DB_NAME,DB_VERSION);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'profile_id'})};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function dbAll(){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readonly');const req=tx.objectStore(STORE).getAll();req.onsuccess=()=>resolve(req.result||[]);req.onerror=()=>reject(req.error);tx.oncomplete=()=>db.close()})}
async function dbPut(p){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(p);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function dbDelete(id){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).delete(id);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function dbClear(){const db=await openLocalDB();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).clear();tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
function newId(){return 'P-'+(crypto.randomUUID?crypto.randomUUID().replace(/-/g,'').slice(0,10):Date.now().toString(36)+Math.random().toString(36).slice(2,6))}
function getAvatar(id){return profiles.find(p=>p.profile_id===id)?.avatar||'adult-male'}
function current(){return profiles.find(p=>p.profile_id===currentProfile)||null}

function normalizeGender(v){const x=String(v||'').trim().toUpperCase();if(['NAM','MALE','M'].includes(x))return'NAM';if(['NU','NỮ','FEMALE','F'].includes(x))return'NU';return x}
function normalizeProfile(p={}){const b=p.birth||{};const out={...p,profile_id:p.profile_id||newId(),full_name:String(p.full_name||p.name||'').trim(),gender:normalizeGender(p.gender),birth:{year:Number(b.year??p.birth_year),month:Number(b.month??p.birth_month),day:Number(b.day??p.birth_day),hour:Number(b.hour??p.birth_hour??0),minute:Number(b.minute??p.birth_minute??0)},birth_place_text:String(p.birth_place_text||p.birth_place||p.place||'').trim(),timezone_name:p.timezone_name||p.timezone||'Asia/Ho_Chi_Minh',time_certainty:p.time_certainty||'KNOWN',note:p.note??null,avatar:p.avatar||'adult-male',created_at:p.created_at||new Date().toISOString(),updated_at:p.updated_at||new Date().toISOString()};return out}
function apiProfile(p){const x=normalizeProfile(p);return{profile_id:x.profile_id,full_name:x.full_name,gender:x.gender,birth:x.birth,birth_place_text:x.birth_place_text,timezone_name:x.timezone_name,time_certainty:x.time_certainty,note:x.note}}
function friendlyError(status,d={}){const code=d.error_code?` (${d.error_code})`:'';const stage=d.error_stage?` [${d.error_stage}]`:'';if(status===422)return`Hồ sơ đang dùng dữ liệu từ phiên bản cũ hoặc thiếu trường bắt buộc. Hãy mở Hồ sơ → Sửa → Lưu lại.${code}`;if(status===408||status===429)return`Máy chủ đang bận. Hãy thử lại sau vài giây.${code}`;if(status>=500)return`Engine chưa xử lý được yêu cầu${stage}. Hãy thử lại; nếu lặp lại, gửi mã lỗi này.${code}`;return`${d.detail||'Yêu cầu chưa thực hiện được.'}${code}`}
async function api(url,opt={}){let lastErr;for(let attempt=0;attempt<2;attempt++){const ctl=new AbortController();const timer=setTimeout(()=>ctl.abort(),25000);try{const r=await fetch(url,{...opt,signal:ctl.signal,cache:'no-store'});clearTimeout(timer);let d={};try{d=await r.json()}catch{}if(!r.ok){const e=new Error(friendlyError(r.status,d));e.status=r.status;if(r.status>=500&&attempt===0){lastErr=e;await new Promise(res=>setTimeout(res,700));continue}throw e}return d}catch(e){clearTimeout(timer);lastErr=e;if(attempt===0&&(e.name==='AbortError'||!e.status)){await new Promise(res=>setTimeout(res,700));continue}if(e.name==='AbortError')throw new Error('Máy chủ phản hồi quá lâu. Hãy kiểm tra mạng và thử lại.');throw e}}throw lastErr||new Error('Không thể kết nối Engine.')}
async function post(url,body){const payload={...body};if(payload.profile)payload.profile=apiProfile(payload.profile);return api(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})}

function applySettings(){
 const theme=localStorage.getItem('xemngay-theme')||'light';
 const font=localStorage.getItem('xemngay-font')||'normal';
 document.documentElement.dataset.theme=theme;document.documentElement.dataset.font=font;
 const fs=$('font-size');if(fs)fs.value=font;renderThemes(theme);updateBackupState();
}
function renderThemes(selected){
 const grid=$('theme-grid');if(!grid)return;
 grid.innerHTML=themes.map(([id,name,desc,sw])=>`<button class="theme ${id===selected?'selected':''}" onclick="chooseTheme('${id}')"><div class="swatch" style="background:${sw}"></div><b>${name}</b><small>${desc}</small>${id===selected?'<span class="theme-check">✓ Đang dùng</span>':''}</button>`).join('');
 const cur=$('theme-current');const found=themes.find(x=>x[0]===selected);if(cur&&found)cur.textContent=found[1];
}
function chooseTheme(id){localStorage.setItem('xemngay-theme',id);applySettings()}
function toggleThemePanel(){const el=$('theme-panel');if(el)el.hidden=!el.hidden}
function saveSettings(){localStorage.setItem('xemngay-font',$('font-size').value);applySettings()}
function navTo(name){
 document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));const target=$('screen-'+name);if(target)target.classList.add('active');
 document.querySelectorAll('.nav-btn').forEach(x=>x.classList.toggle('active',x.dataset.nav===name));window.scrollTo(0,0);
 if(name==='home')loadHomeDashboard();if(name==='calendar')renderCalendar();if(name==='profile')renderProfiles();if(name==='settings')updateBackupState();
}
async function loadStatus(){
 return api('/api/tinh-trang').then(()=>{const el=$('status-banner');if(el)el.innerHTML=`<div class="trust-line"><span>✓ Có nguồn</span><span>✓ Có truy nguyên</span><span>✓ Không tạo điểm giả</span></div>`})
}
function profileOptions(){return profiles.length?profiles.map(p=>`<option value="${p.profile_id}" ${p.profile_id===currentProfile?'selected':''}>${esc(p.full_name)}</option>`).join(''):'<option value="">— Chưa có hồ sơ —</option>'}
function syncProfileSelectors(){['profile-select','calendar-profile','work-profile'].forEach(id=>{const el=$(id);if(el){el.innerHTML=profileOptions();el.value=currentProfile||''}})}
function selectProfileFrom(id){
 const el=$(id);currentProfile=el?.value||null;localStorage.setItem('xemngay-profile',currentProfile||'');syncProfileSelectors();updateHomeTitle();
 if(id==='calendar-profile')renderCalendar();loadHomeDashboard();if($('screen-profile')?.classList.contains('active'))renderProfiles();
}
async function loadProfiles(){
 const raw=await dbAll();profiles=[];
 for(const item of raw){const p=normalizeProfile(item);const valid=p.full_name&&['NAM','NU'].includes(p.gender)&&Number.isInteger(p.birth.year)&&Number.isInteger(p.birth.month)&&Number.isInteger(p.birth.day);if(!valid)continue;profiles.push(p);if(JSON.stringify(p)!==JSON.stringify(item))await dbPut(p)}
 profiles.sort((a,b)=>(a.created_at||'').localeCompare(b.created_at||'')||a.full_name.localeCompare(b.full_name,'vi'));
 const saved=localStorage.getItem('xemngay-profile');if(saved&&profiles.some(p=>p.profile_id===saved))currentProfile=saved;else currentProfile=profiles[0]?.profile_id||null;
 syncProfileSelectors();const homeSel=$('profile-select');if(homeSel)homeSel.onchange=()=>selectProfileFrom('profile-select');updateHomeTitle();renderProfiles();renderFamilyStrip();loadHomeDashboard();
}
function updateHomeTitle(){
 const p=current();const el=$('home-title');if(el)el.textContent=p?p.full_name:'gia đình';
 const av=$('home-avatar');if(av)av.innerHTML=p?avatarHtml(p.avatar||'adult-male'):'<div class="brand-mark">命</div>';
}

function renderFamilyStrip(){
 const el=$('home-family-strip');if(!el)return;
 el.innerHTML=profiles.length?profiles.map(p=>`<button class="family-chip ${p.profile_id===currentProfile?'selected':''}" onclick="selectProfileCard('${p.profile_id}')">${avatarHtml(p.avatar||'adult-male')}<small>${esc(p.full_name)}</small></button>`).join('')+`<button class="family-chip add" onclick="openAddProfile()"><span>＋</span><small>Thêm</small></button>`:`<button class="btn" onclick="openAddProfile()">+ Thêm thành viên đầu tiên</button>`;
}
function ordinalMeter(label){const cls=badgeClass(label);return `<div class="ordinal-meter ${cls}"><div class="meter-arc"></div><strong>${esc(label||'Đang đánh giá')}</strong><small>V1-basic</small></div>`}
async function loadHomeDashboard(){
 const monthEl=$('home-month-summary'),todayEl=$('home-today-summary'),cycle=$('home-cycle');renderFamilyStrip();updateHomeTitle();
 if(!currentProfile){if(monthEl)monthEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem tháng này.</div>';if(todayEl)todayEl.innerHTML='<div class="empty-home">Thêm hồ sơ để xem hôm nay.</div>';if(cycle)cycle.textContent='Chọn một người để bắt đầu';return}
 const p=current();if(monthEl)monthEl.innerHTML='<div class="loading-line">Đang tải tổng quan tháng…</div>';if(todayEl)todayEl.innerHTML='<div class="loading-line">Đang tải hôm nay…</div>';
 try{const d=await post('/api/stateless/dashboard',{profile:p});const pos=d.vi_tri||{};if(cycle)cycle.textContent=`Đại vận ${pos.dai_van?.tru||'—'} · ${pos.nam_hien_tai?.vi||'—'} · ${pos.thang_hien_tai?.vi||'—'}`;
  if(monthEl){const m=d.thang||{},s=m.don_gian||{},dg=s.dien_giai||{};monthEl.classList.remove('loading-card');monthEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('month')"><div class="home-card-head"><div><small>THÁNG NÀY CỦA TÔI</small><b>${esc(m.chuyen_sau?.thang?.tru?.vi||'Tháng hiện tại')}</b></div><span>›</span></div><div class="home-month-body">${ordinalMeter(s.tom_tat)}<div class="home-points"><p><i class="good-dot"></i><b>Công việc:</b> ${esc(dg.cong_viec||((s.nen_lam||[])[0]||'Giữ kế hoạch rõ ràng'))}</p><p><i class="warn-dot"></i><b>Quan hệ:</b> ${esc(dg.quan_he||'Chưa có tín hiệu riêng')}</p><p><i class="neutral-dot"></i><b>Việc lớn:</b> ${esc(dg.viec_lon||'Xét riêng theo đúng loại việc')}</p></div></div></button>`}
  if(todayEl){const t=d.hom_nay||{},s=t.don_gian||{},dg=s.dien_giai||{};todayEl.classList.remove('loading-card');const good=(t.gio_trong_ngay||[]).filter(x=>x.relation_level==='POSITIVE').slice(0,3);todayEl.innerHTML=`<button class="home-card-click" onclick="openQuestion('today')"><div class="home-card-head"><div><small>HÔM NAY THẾ NÀO?</small><b class="${badgeClass(s.tom_tat)}-text">${esc(dg.headline||s.tom_tat)}</b></div><span>›</span></div><div class="today-compact"><span class="today-check">✓</span><div><p><b>Công việc:</b> ${esc(dg.cong_viec||s.vi_sao||'Chưa có tín hiệu riêng')}</p><p><b>Quan hệ:</b> ${esc(dg.quan_he||'Chưa có tín hiệu riêng')}</p>${good.length?`<small>Giờ tham khảo theo hồ sơ: ${good.map(x=>esc(x.chi_vi)).join(', ')}</small>`:''}</div></div></button>`}
 }catch(e){if(monthEl)monthEl.innerHTML=`<div class="notice danger"><b>Chưa tải được tổng quan tháng</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="loadHomeDashboard()">Thử lại</button></div>`;if(todayEl)todayEl.innerHTML=`<div class="notice danger"><b>Chưa tải được kết quả hôm nay</b>${esc(e.message)}</div>`}
}

function renderProfiles(){
 const list=$('profile-list');if(!list)return;
 list.innerHTML=profiles.length?`<div class="family-tabs-scroll">${profiles.map(p=>`<button class="profile-tab ${p.profile_id===currentProfile?'active':''}" onclick="selectProfileCard('${p.profile_id}')">${avatarHtml(p.avatar||'adult-male')}<span>${esc(p.full_name)}</span></button>`).join('')}<button class="profile-tab add" onclick="openAddProfile()"><span class="plus-round">＋</span><span>Thêm</span></button></div>`:'<div class="card muted">Chưa có thành viên. Bấm “Thêm người”.</div>';
 loadProfileInsight();
}
function selectProfileCard(id){currentProfile=id;localStorage.setItem('xemngay-profile',id);syncProfileSelectors();updateHomeTitle();renderFamilyStrip();renderProfiles();loadHomeDashboard()}
async function loadProfileInsight(){
 const el=$('profile-insight');if(!el)return;if(!currentProfile){el.innerHTML='';return}
 const p=current();el.innerHTML='<div class="card muted">Đang tải thông tin sinh mệnh…</div>';
 try{
  const d=await post('/api/stateless/toi-dang-o-dau',{profile:p});const pillars=Object.values(d.tu_tru||{}).map(x=>x.vi).join(' · ');const dv=d.dai_van;const stage=dv?.nam_thu_may<=3?'Giai đoạn đầu vận':(dv?.nam_thu_may<=7?'Giai đoạn giữa vận':'Giai đoạn cuối vận');
  el.innerHTML=`<div class="profile-hero-a"><div class="profile-hero-inner">${avatarHtml(p.avatar||'adult-male')}<div class="grow"><h2>${esc(p.full_name)}</h2><p>${p.gender==='NAM'?'Nam':'Nữ'} · ${String(p.birth.day).padStart(2,'0')}/${String(p.birth.month).padStart(2,'0')}/${p.birth.year}</p><p>${String(p.birth.hour).padStart(2,'0')}:${String(p.birth.minute).padStart(2,'0')} · ${esc(p.birth_place_text)}</p></div><button class="hero-edit" onclick="editProfile('${p.profile_id}')">✎</button></div></div>
  <div class="card destiny-card"><div class="destiny-title"><h3>TỔNG QUAN MỆNH LÝ</h3><span>Tóm tắt</span></div><div class="destiny-row"><span>Tứ Trụ</span><b>${esc(pillars||'—')}</b></div><div class="destiny-row"><span>Đại vận hiện tại</span><b>${esc(dv?.tru||'—')}<small>${dv?`${esc(stage)} · khoảng ${esc(dv.nam_bat_dau)}–${esc(dv.nam_ket_thuc)}`:''}</small></b></div><div class="destiny-row"><span>Năm / Tháng</span><b>${esc(d.nam_hien_tai?.vi||'—')} · ${esc(d.thang_hien_tai?.vi||'—')}</b></div><div class="destiny-row"><span>Yếu tố cân bằng</span><b class="muted">Chưa dùng trong kết luận V1</b></div></div>
  <div class="profile-actions-a"><button onclick="openQuestion('long')"><span>◷</span><b>Đồng thời gian</b><small>Xem vận hiện tại</small></button><button onclick="exportBackup()"><span>☁</span><b>Sao lưu hồ sơ</b><small>Lưu dữ liệu an toàn</small></button><button onclick="loadProfileWhy()"><span>▤</span><b>Giải thích</b><small>Xem cách tính & nguồn</small></button><button class="danger-lite" onclick="deleteProfile('${p.profile_id}')"><span>⌫</span><b>Xóa hồ sơ</b><small>Chỉ trên thiết bị</small></button></div>
  <div id="profile-why"></div>${dv?.canh_bao?.length?`<details class="tech-details"><summary>Độ chính xác mốc Đại vận</summary><div class="soft-note">Mốc chuyển vận hiện là mốc dự kiến, có thể sai lệch vài tháng.<br><small>${dv.canh_bao.map(esc).join('<br>')}</small></div></details>`:''}`;
 }catch(e){el.innerHTML=`<div class="notice danger"><b>Chưa tải được thông tin sinh mệnh</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="loadProfileInsight()">Thử lại</button></div>`}
}
async function loadProfileWhy(){
 const el=$('profile-why');if(!el||!needProfile())return;el.innerHTML='<div class="card muted">Đang tải nguồn và quy tắc…</div>';
 try{const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:null});el.innerHTML=`<div class="card expert-box"><h3>Rule & nguồn đang dùng</h3><p class="muted">Đây là tầng chuyên sâu; kết luận gia đình không thay đổi bởi cách trình bày này.</p>${(d.truy_nguoc||[]).slice(0,12).map(r=>`<div class="trace-row"><b>${esc(r.rule_id)} · ${esc(r.name_vi)}</b><div><span class="tag">${esc(r.verification_status)}</span> <span class="tag">${esc(r.confidence)}</span></div><div class="muted">${esc(r.source_title||'Chưa gắn nguồn')}</div></div>`).join('')||'<div class="muted">Chưa có rule truy ngược phù hợp.</div>'}</div>`}catch(e){el.innerHTML=`<div class="notice danger"><b>Chưa tải được phần giải thích</b>${esc(e.message)}</div>`}
}
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
function badgeClass(label=''){if(/Ưu tiên|^Phù hợp$|Khá thuận/i.test(label))return'good';if(/Không ưu tiên/i.test(label))return'bad';if(/Cân nhắc|lưu ý/i.test(label))return'warn';return'neutral'}
function decisionHero(simple,scope){const label=simple.tom_tat||simple.tieu_de||'Đang đánh giá';const cls=badgeClass(label);return `<div class="decision-hero ${cls}"><div class="decision-main"><small>${scope==='month'?'THÁNG NÀY':'HÔM NAY'}</small><strong>${esc(label)}</strong><span>${esc(simple.vi_sao||'Kết luận theo lớp quy tắc V1-basic có truy nguồn.')}</span></div><div class="decision-seal">V1<br><b>BASIC</b></div></div>`}
function adviceHtml(simple){return `<div class="advice-grid"><div class="advice good"><h4>✓ NÊN</h4>${(simple.nen_lam||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Theo kế hoạch bình thường.</p>'}</div><div class="advice warn"><h4>! CÂN NHẮC</h4>${(simple.can_nhac||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Kiểm tra điều kiện thực tế.</p>'}</div><div class="advice bad"><h4>× KHÔNG ƯU TIÊN</h4>${(simple.khong_uu_tien||[]).map(x=>`<p>• ${esc(x)}</p>`).join('')||'<p>• Không có cấm tuyệt đối ở lớp hiện tại.</p>'}</div></div>`}

function impactGrid(s){const d=s?.dien_giai||{};if(!Object.keys(d).length)return '';const rows=[['Công việc',d.cong_viec],['Tài chính',d.tai_chinh],['Quan hệ',d.quan_he],['Việc lớn',d.viec_lon]].filter(x=>x[1]);return `<div class="impact-grid">${rows.map(([k,v])=>`<div class="impact-item"><b>${esc(k)}</b><p>${esc(v)}</p></div>`).join('')}</div>${d.khong_suy_dien?`<div class="interpretation-limit"><b>Giới hạn kết luận:</b> ${esc(d.khong_suy_dien)}</div>`:''}`}
function triggerLine(s){const d=s?.dien_giai||{};return d.trigger?`<div class="trigger-line"><b>Điểm tạo khác biệt:</b> ${esc(d.trigger)}</div>`:''}
function hoursBlock(d){const arr=d.gio_trong_ngay||[];const good=arr.filter(x=>x.relation_level==='POSITIVE').slice(0,4);const caution=arr.filter(x=>x.relation_level==='CAUTION').slice(0,4);return `<div class="hours-card"><h4>GIỜ THAM KHẢO THEO HỒ SƠ</h4><div class="hour-grid good-hours">${good.map(x=>`<span><b>${esc(x.khoang_gio)}</b><small>${esc(x.chi_vi)}</small></span>`).join('')||'<span class="muted">Chưa có giờ nổi bật</span>'}</div><h4>GIỜ CẦN CÂN NHẮC THEO HỒ SƠ</h4><div class="hour-grid bad-hours">${caution.map(x=>`<span><b>${esc(x.khoang_gio)}</b><small>${esc(x.chi_vi)}</small></span>`).join('')||'<span class="muted">Không có cảnh báo giờ đặc biệt</span>'}</div><p class="muted hour-scope-note">${esc(d.gio_note||'Giờ hiện là tham khảo theo hồ sơ; chưa phải giờ tốt đã hợp lưu riêng với ngày.')}</p></div>`}
function renderTodayA(d,p){const s=d.don_gian,deep=d.chuyen_sau;return `<div class="today-a-hero ${badgeClass(s.tom_tat)}"><div><small>TỔNG QUAN HÔM NAY</small><h2>${esc((s.dien_giai||{}).headline||s.tom_tat)}</h2><p>${esc(s.tom_tat)}</p></div><div class="ordinal-disc"><span>V1</span><b>BASIC</b></div></div>${triggerLine(s)}${impactGrid(s)}<div class="action-summary">${adviceHtml(s)}</div>${hoursBlock(d)}<div class="card why-summary"><h3>TẠI SAO HÔM NAY NHƯ VẬY?</h3>${fusionHtml(deep,true)}<p class="muted">Kết luận hợp lưu Đại vận → Năm → Tháng → Ngày. Bấm dưới đây để xem quan hệ kỹ thuật, rule và nguồn.</p><button class="btn full-btn" onclick="loadWhy('day')">Xem chi tiết</button><div id="why-box"></div></div>`}
function renderMonthB(d,p){const s=d.don_gian,deep=d.chuyen_sau;const dg=s.dien_giai||{};const focus=dg.focus||s.nen_lam||[];return `<div class="month-b-timeline">${fusionHtml(deep,false)}</div><div class="month-b-summary"><div class="month-compass">◈</div><div><small>ĐÁNH GIÁ THÁNG</small><h2>${esc(dg.headline||s.tom_tat)}</h2><p>${esc(s.tom_tat)}</p></div></div>${triggerLine(s)}${impactGrid(s)}<div class="card month-focus"><h3>NÊN TẬP TRUNG</h3><div class="focus-chips">${focus.slice(0,4).map((x,i)=>`<span><i>${['◎','▤','♧','◈'][i%4]}</i>${esc(x)}</span>`).join('')||'<span><i>◎</i>Giữ kế hoạch rõ ràng</span>'}</div></div><button class="btn secondary full-btn" onclick="loadWhy('month')">TẠI SAO? · Xem chuyên sâu</button><div id="why-box"></div>`}
async function openQuestion(kind){
 if(!needProfile())return;const p=current();navTo('result');$('result-body').innerHTML='<div class="card">Đang tính…</div>';
 try{
  if(kind==='long'){
   const d=await post('/api/stateless/toi-dang-o-dau',{profile:p});$('result-title').textContent='Vận dài hạn';const dv=d.dai_van;const stage=dv?.nam_thu_may<=3?'Giai đoạn đầu vận':(dv?.nam_thu_may<=7?'Giai đoạn giữa vận':'Giai đoạn cuối vận');
   $('result-body').innerHTML=`<div class="long-hero"><h2>${esc(d.ho_ten)}</h2><div class="fusion"><div class="layer"><small>Đại vận</small><b>${esc(dv?.tru||'—')}</b><span class="subline">${dv?`${esc(stage)} · khoảng ${esc(dv.nam_bat_dau)}–${esc(dv.nam_ket_thuc)}`:'Chưa xác định'}</span></div><div class="layer"><small>Năm</small><b>${esc(d.nam_hien_tai.vi)}</b></div><div class="layer"><small>Tháng</small><b>${esc(d.thang_hien_tai.vi)}</b></div></div></div><div id="profile-why"></div>${dv?.canh_bao?.length?`<details class="tech-details"><summary>Độ chính xác mốc Đại vận</summary><div class="soft-note">Thời điểm bắt đầu Đại vận hiện là mốc dự kiến, có thể sai lệch vài tháng.<br><small>${dv.canh_bao.map(esc).join('<br>')}</small></div></details>`:''}`;return;
  }
  const isMonth=kind==='month';const d=await post(isMonth?'/api/stateless/thang-nay':'/api/stateless/hom-nay',{profile:p});$('result-title').textContent=isMonth?'Tháng này của tôi':'Hôm nay thế nào?';$('result-body').innerHTML=isMonth?renderMonthB(d,p):renderTodayA(d,p);
 }catch(e){$('result-body').innerHTML=`<div class="notice danger"><b>Chưa lấy được kết quả</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="openQuestion('${kind}')">Thử lại</button></div>`}
}

async function loadWhy(scope='day'){
 if(!needProfile())return;
 const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:null});
 const scopeText=scope==='month'?'tháng hiện tại':'ngày đang xem';
 $('why-box').innerHTML=`<div class="card expert-box"><h3>Chuyên sâu · ${scopeText}</h3><p class="muted">Phần này dành cho người muốn kiểm tra cách tính và nguồn. Thuật ngữ kỹ thuật không được dùng để thay thế kết luận ở tầng gia đình.</p>${d.truy_nguoc.length?d.truy_nguoc.map(r=>`<div class="trace-row"><b>${esc(r.rule_id)} · ${esc(r.name_vi)}</b><div><span class="tag">${esc(r.verification_status)}</span> <span class="tag">tin cậy ${esc(r.confidence)}</span></div><div class="muted">${esc(r.source_title||'Chưa gắn nguồn')}${r.source_location?' · '+esc(r.source_location):''}</div>${r.passage_excerpt?`<pre>${esc(r.passage_excerpt)}</pre>`:''}</div>`).join(''):'<div class="muted">Chưa có rule truy ngược phù hợp.</div>'}</div>`
}
function localISODate(d=new Date()){const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${day}`}
function calendarTone(label,state=''){const x=(label||'')+' '+(state||'');if(/Không ưu tiên|JI|CAN_NHAC|xung động/i.test(x))return /Không ưu tiên|JI/i.test(x)?'bad':'warn';if(/Ưu tiên|Phù hợp|THUAN|Khá thuận/i.test(x))return 'good';return 'neutral'}
async function renderCalendar(){
 const y=calCursor.getFullYear(),m=calCursor.getMonth();const title=$('cal-title');if(title)title.textContent=`Tháng ${m+1} / ${y}`;
 const first=new Date(y,m,1),offset=(first.getDay()+6)%7,start=new Date(y,m,1-offset),today=localISODate();let html=['T2','T3','T4','T5','T6','T7','CN'].map(x=>`<div class="dow">${x}</div>`).join('');
 for(let i=0;i<42;i++){const d=new Date(start);d.setDate(start.getDate()+i);const iso=localISODate(d);html+=`<button id="day-${iso}" class="day ${d.getMonth()!==m?'other':''} ${iso===today?'today':''}" onclick="selectCalendarDay('${iso}',this)"><span class="num">${d.getDate()}</span><span class="state"><i class="day-dot neutral"></i><span class="day-state-text">Đang tính</span></span></button>`}
 $('calendar-grid').innerHTML=html;calendarDays=[];renderCalendarList();if(!currentProfile)return;
 try{const r=await post('/api/stateless/lich-thang',{profile:current(),year:y,month:m+1,viec:$('calendar-work')?.value||null});calendarDays=r.days||[];for(const x of calendarDays){const el=$(`day-${x.ngay}`);if(!el)continue;const tone=calendarTone(x.label,x.state);const st=el.querySelector('.state');if(st){st.innerHTML=`<i class="day-dot ${tone}"></i><span class="day-state-text">${esc(x.label)}</span>`;el.title=x.label||''}el.dataset.tone=tone}renderCalendarList()}catch(e){document.querySelectorAll('.day .state').forEach(st=>st.innerHTML='<i class="day-dot neutral"></i>');const detail=$('calendar-detail');if(detail)detail.innerHTML=`<div class="notice danger"><b>Chưa tải được đánh giá tháng</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="renderCalendar()">Thử lại</button></div>`}
}

function setCalendarView(view){calendarView=view;const mv=$('calendar-month-view'),lv=$('calendar-list-view');if(mv)mv.hidden=view!=='month';if(lv)lv.hidden=view!=='list';$('cal-tab-month')?.classList.toggle('active',view==='month');$('cal-tab-list')?.classList.toggle('active',view==='list');if(view==='list')renderCalendarList()}
function renderCalendarList(){const el=$('calendar-list-view');if(!el)return;el.innerHTML=calendarDays.length?calendarDays.map(x=>`<button class="calendar-list-row" onclick="setCalendarView('month');setTimeout(()=>document.getElementById('day-${x.ngay}')?.click(),0)"><b>${esc(x.ngay)}</b><span class="result-label ${calendarTone(x.label,x.state)}">${esc(x.label)}</span><em>›</em></button>`).join(''):'<div class="muted">Đang tải danh sách tháng…</div>'}
function moveMonth(n){calCursor=new Date(calCursor.getFullYear(),calCursor.getMonth()+n,1);renderCalendar()}
function goTodayCalendar(){const n=new Date();calCursor=new Date(n.getFullYear(),n.getMonth(),1);renderCalendar()}
async function selectCalendarDay(iso,el){
 document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));if(el)el.classList.add('selected');if(!needProfile())return;$('calendar-detail').innerHTML='Đang tính…';
 try{const d=await post('/api/stateless/hom-nay',{profile:current(),ngay:iso});const s=d.don_gian;const good=(d.gio_trong_ngay||[]).filter(x=>x.relation_level==='POSITIVE').slice(0,3);$('calendar-detail').innerHTML=`<div class="cal-detail-top"><div class="date-badge">${iso.slice(-2)}</div><div class="grow"><small>CHI TIẾT NGÀY ${esc(iso)}</small><h3>${esc(s.tom_tat)}</h3><p>${esc(s.vi_sao||'')}</p></div><span class="result-label ${badgeClass(s.tom_tat)}">${esc(s.tom_tat)}</span></div>${good.length?`<div class="cal-good-hours"><b>Giờ tham khảo theo hồ sơ:</b> ${good.map(x=>`${esc(x.chi_vi)} (${esc(x.khoang_gio)})`).join(' · ')}</div>`:''}${adviceHtml(s)}<button class="btn full-btn" onclick="loadCalendarWhy('${iso}')">Xem chi tiết & lý do</button><div id="calendar-why"></div>`}catch(e){$('calendar-detail').innerHTML=`<div class="notice danger"><b>Chưa tính được ngày này</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="selectCalendarDay('${iso}',document.getElementById('day-${iso}'))">Thử lại</button></div>`}
}

async function loadCalendarWhy(iso){const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:iso});$('calendar-why').innerHTML=`<ul class="list-clean">${d.truy_nguoc.map(r=>`<li><b>${esc(r.rule_id)}</b> · ${esc(r.name_vi)} · ${esc(r.verification_status)}</li>`).join('')}</ul>`}
async function loadWorkTypes(){const x=await api('/api/loai-viec');const wt=$('work-type');if(wt)wt.innerHTML=x.map(v=>`<option value="${v.code}">${esc(v.ten)}</option>`).join('');const cw=$('calendar-work');if(cw)cw.innerHTML='<option value="">Tất cả việc</option>'+x.map(v=>`<option value="${v.code}">${esc(v.ten)}</option>`).join('');const today=localISODate();if($('work-from'))$('work-from').value=today;const d=new Date();d.setDate(d.getDate()+14);if($('work-to'))$('work-to').value=localISODate(d)}
async function findDates(){
 if(!needProfile())return;$('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
 try{
  const d=await post('/api/stateless/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});const top=d.top||[];
  const hourData=await Promise.all(top.map(x=>post('/api/stateless/hom-nay',{profile:current(),ngay:x.ngay}).catch(()=>null)));
  const rows=top.map((x,i)=>{const hd=hourData[i];const hours=(hd?.gio_trong_ngay||[]).filter(h=>h.relation_level==='POSITIVE').slice(0,3);return {...x,hours}});
  const first=rows[0];$('work-result').innerHTML=`${d.canh_bao_an_toan?`<div class="notice danger"><b>Lưu ý y tế</b>${esc(d.canh_bao_an_toan)}</div>`:''}${first?`<div class="work-winner"><small>NGÀY ƯU TIÊN #1</small><div class="winner-row"><div class="medal">1</div><div class="grow"><h2>${esc(first.ngay)}</h2><strong>${esc(first.label)}</strong><p>${first.hours.length?'Giờ tham khảo theo hồ sơ: '+first.hours.map(h=>`${esc(h.chi_vi)} (${esc(h.khoang_gio)})`).join(' · '):'Giờ hợp lưu riêng theo ngày chưa có trong V1-basic.'}</p></div><span class="ordinal-badge">V1<br>BASIC</span></div></div>`:''}<div class="card work-other"><h3>DANH SÁCH GỢI Ý KHÁC</h3>${rows.slice(1).map((x,i)=>`<div class="work-rank-row"><div class="rank-no">${i+2}</div><div class="grow"><b>${esc(x.ngay)}</b><strong>${esc(x.label)}</strong><small>Trực ${esc(x.truc||'—')} · ${esc(x.personal_relation?.nhan||'')}</small>${x.hours.length?`<p>Giờ tham khảo theo hồ sơ: ${x.hours.map(h=>esc(h.chi_vi)).join(', ')}</p>`:''}</div><span>›</span></div>`).join('')||'<div class="muted">Không có gợi ý khác.</div>'}<div class="soft-note">${esc(d.ghi_chu||'')}</div><div class="work-buttons"><button class="btn secondary" onclick="document.querySelector('.work-search-card')?.scrollIntoView({behavior:'smooth'})">Chỉnh sửa tìm kiếm</button><button class="btn" onclick="toggleResearchDays()">Xem chi tiết tất cả</button></div><div id="research-days" class="research-days" hidden>${(d.cac_ngay||[]).map(x=>`<div class="research-row"><b>${x.ngay}</b> · ${esc(x.tru_ngay)} · <span class="result-label ${badgeClass(x.label)}">${esc(x.label)}</span><div class="muted">Trực ${esc(x.truc||'—')} · ${esc(x.personal_relation?.nhan||'')}</div></div>`).join('')}</div></div>`;
 }catch(e){$('work-result').innerHTML=`<div class="notice danger"><b>Chưa tìm được ngày</b>${esc(e.message)}<button class="btn secondary small retry-btn" onclick="findDates()">Thử lại</button></div>`}
}

function toggleResearchDays(){const el=$('research-days');if(el)el.hidden=!el.hidden}

// ----- Sao lưu / khôi phục -----
function updateBackupState(){const el=$('backup-state');if(!el)return;const last=localStorage.getItem('xemngay-last-backup');if(!last){el.textContent='Chưa có bản sao lưu trên thiết bị này.';return}const days=Math.floor((Date.now()-new Date(last).getTime())/86400000);el.textContent=days>=30?`Đã ${days} ngày chưa sao lưu. Nên tạo bản sao lưu mới.`:`Lần sao lưu gần nhất: ${new Date(last).toLocaleString('vi-VN')}.`}
async function exportBackup(){const data={format:'TU_BINH_GIA_DINH_BACKUP',schema_version:1,exported_at:new Date().toISOString(),profiles:await dbAll(),settings:{theme:localStorage.getItem('xemngay-theme')||'light',font:localStorage.getItem('xemngay-font')||'normal',current_profile:currentProfile}};const text=JSON.stringify(data,null,2),name=`tu-binh-gia-dinh-${localISODate()}.json`;const file=new File([text],name,{type:'application/json'});if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'Sao lưu Tử Bình Gia Đình'});}else{const blob=new Blob([text],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);}localStorage.setItem('xemngay-last-backup',new Date().toISOString());updateBackupState()}
function chooseRestoreFile(){$('restore-file').click()}
async function restoreBackup(input){const file=input.files?.[0];input.value='';if(!file)return;try{const data=JSON.parse(await file.text());if(data.format!=='TU_BINH_GIA_DINH_BACKUP'||data.schema_version!==1||!Array.isArray(data.profiles))throw new Error('File không phải bản sao lưu V1 hợp lệ.');const names=data.profiles.map(p=>p.full_name).filter(Boolean).slice(0,8).join(', ');if(!confirm(`Khôi phục ${data.profiles.length} hồ sơ${names?' ('+names+')':''}? Dữ liệu hồ sơ hiện có trên thiết bị sẽ được thay thế.`))return;await dbClear();for(const p of data.profiles)await dbPut(p);if(data.settings?.theme)localStorage.setItem('xemngay-theme',data.settings.theme);if(data.settings?.font)localStorage.setItem('xemngay-font',data.settings.font);if(data.settings?.current_profile)localStorage.setItem('xemngay-profile',data.settings.current_profile);await loadProfiles();applySettings();alert('Khôi phục dữ liệu thành công.')}catch(e){alert('Không thể khôi phục: '+e.message)}}
async function deleteAllLocal(){if(!confirm('Xóa TOÀN BỘ hồ sơ trên thiết bị này? Hành động này không thể hoàn tác nếu chưa sao lưu.'))return;if(!confirm('Xác nhận lần cuối: xóa toàn bộ dữ liệu cục bộ?'))return;await dbClear();localStorage.removeItem('xemngay-profile');currentProfile=null;await loadProfiles();alert('Đã xóa dữ liệu trên thiết bị này.')}

async function checkConnection(){const el=$('connection-state');try{const h=await api('/api/health');if(el)el.textContent=h.ok?`Engine ${h.engine_version} · kết nối tốt`:`Engine ${h.engine_version} · chưa sẵn sàng (${Object.entries(h.checks||{}).filter(([,v])=>!v).map(([k])=>k).join(', ')||'health'})`;}catch(e){if(el)el.textContent=`Engine chưa phản hồi · ${e.message}`}}
async function boot(){applySettings();populateTimezones();renderAvatarChoices();await loadProfiles();await Promise.allSettled([loadStatus(),loadWorkTypes(),checkConnection()]);renderCalendar()}
boot().catch(e=>{$('status-banner').innerHTML=`<div class="notice danger"><b>Không khởi động được</b>${esc(e.message)}</div>`});

// ----- PWA -----
let deferredInstallPrompt=null;
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredInstallPrompt=e;const b=$('install-button');if(b)b.style.display='block';const st=$('install-state');if(st)st.textContent='Thiết bị này có thể cài ứng dụng trực tiếp.'});
window.addEventListener('appinstalled',()=>{deferredInstallPrompt=null;const b=$('install-button');if(b)b.style.display='none';const st=$('install-state');if(st)st.textContent='Ứng dụng đã được cài trên thiết bị.'});
async function installPWA(){if(!deferredInstallPrompt){alert('iPhone: Safari → Chia sẻ → Thêm vào Màn hình chính. Android: Chrome → menu ⋮ → Cài ứng dụng.');return}deferredInstallPrompt.prompt();await deferredInstallPrompt.userChoice;deferredInstallPrompt=null}
if('serviceWorker' in navigator){window.addEventListener('load',async()=>{try{const reg=await navigator.serviceWorker.register('/service-worker.js?v='+APP_VERSION,{updateViaCache:'none'});await reg.update();if(reg.waiting)reg.waiting.postMessage('SKIP_WAITING');reg.addEventListener('updatefound',()=>{const nw=reg.installing;if(nw)nw.addEventListener('statechange',()=>{if(nw.state==='installed'&&navigator.serviceWorker.controller)nw.postMessage('SKIP_WAITING')})});let reloaded=false;navigator.serviceWorker.addEventListener('controllerchange',()=>{if(reloaded)return;reloaded=true;location.reload()})}catch{}})}
