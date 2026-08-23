const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[<>&"']/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':'&quot;',"'":'&#39;'}[c]));
let profiles=[], currentProfile=null, editingId=null, chosenAvatar='adult-male';
let calCursor=new Date();
const themes=[
 ['light','Hiện đại sáng','linear-gradient(135deg,#f7f4ed,#0f766e)'],
 ['dark-calm','Tối thư giãn','linear-gradient(135deg,#13231f,#49c6b4)'],
 ['oriental','Đông phương','linear-gradient(135deg,#f6efe3,#8c4437)'],
 ['dark-premium','Tối cao cấp','linear-gradient(135deg,#121417,#d0a84d)'],
 ['dark-blue','Tối xanh dịu','linear-gradient(135deg,#0d1d2a,#46b8a9)']
];
const avatarDefs={
 'old-male':['Nam lớn tuổi','#6f8fa8','#f1f0eb','M','old'], 'old-female':['Nữ lớn tuổi','#b97886','#f1f0eb','F','old'],
 'adult-male':['Nam trung niên','#347f7a','#283a37','M','adult'], 'adult-female':['Nữ trung niên','#bd7380','#4a332d','F','adult'],
 'youth-male':['Nam thiếu niên','#57a35c','#2e302c','M','youth'], 'youth-female':['Nữ thiếu niên','#f08fa4','#3b3028','F','youth']
};
function avatarSvg(code){
 const [label,shirt,hair,sex,age]=avatarDefs[code]||avatarDefs['adult-male'];
 const female=sex==='F', old=age==='old', youth=age==='youth';
 const face=old?'#e8c2a2':'#f1c9aa';
 const glasses=old?`<g fill="none" stroke="#6b615c" stroke-width="2"><circle cx="41" cy="45" r="7"/><circle cx="59" cy="45" r="7"/><path d="M48 45h4"/></g>`:'';
 const wrinkles=old?`<path d="M38 34h7M55 34h7M47 58c2 1 4 1 6 0" stroke="#c7967b" stroke-width="1.2" fill="none" stroke-linecap="round"/>`:'';
 const blush=youth?`<circle cx="35" cy="52" r="3" fill="#e9a894" opacity=".45"/><circle cx="65" cy="52" r="3" fill="#e9a894" opacity=".45"/>`:'';
 const longHair=female?`<path d="M27 37c-4 14-3 31 5 41l9-10c-5-12-4-24 0-35zM73 37c4 14 3 31-5 41l-9-10c5-12 4-24 0-35z" fill="${hair}"/>`:'';
 const oldHair=old?`<path d="M29 40c1-20 10-30 21-30 14 0 23 11 23 30-6-8-14-12-24-12-8 0-14 4-20 12z" fill="${hair}"/>`:`<path d="M28 41c0-22 12-31 22-31 14 0 24 10 24 30-8-7-16-10-26-10-8 0-14 3-20 11z" fill="${hair}"/>`;
 return `<svg class="avatar-svg" viewBox="0 0 100 100" role="img" aria-label="${label}"><defs><linearGradient id="bg-${code}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f7fbf9"/><stop offset="1" stop-color="#e5f3ee"/></linearGradient></defs><circle cx="50" cy="50" r="47" fill="url(#bg-${code})"/><path d="M18 97c3-25 17-35 32-35s29 10 32 35" fill="${shirt}"/><path d="M43 62h14v12H43z" fill="${face}"/><ellipse cx="50" cy="44" rx="22" ry="25" fill="${face}"/>${longHair}${oldHair}<circle cx="41" cy="45" r="2.1" fill="#2d312f"/><circle cx="59" cy="45" r="2.1" fill="#2d312f"/>${glasses}${wrinkles}${blush}<path d="M43 55c4.5 3.8 9.5 3.8 14 0" fill="none" stroke="#9d5c4a" stroke-width="2" stroke-linecap="round"/></svg>`
}

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
function renderThemes(selected){$('theme-grid').innerHTML=themes.map(([id,name,sw])=>`<button class="theme ${id===selected?'selected':''}" onclick="chooseTheme('${id}')"><div class="swatch" style="background:${sw}"></div><b>${name}</b></button>`).join('')}
function chooseTheme(id){localStorage.setItem('xemngay-theme',id);applySettings()}
function saveSettings(){localStorage.setItem('xemngay-font',$('font-size').value);applySettings()}
function navTo(name){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));$('screen-'+name).classList.add('active');document.querySelectorAll('.nav-btn').forEach(x=>x.classList.toggle('active',x.dataset.nav===name));window.scrollTo(0,0);if(name==='calendar')renderCalendar();if(name==='profile')renderProfiles();if(name==='settings')updateBackupState()}
async function loadStatus(){return api('/api/tinh-trang').then(s=>{$('status-banner').innerHTML=`<div class="engine-status"><div class="engine-row ok"><span class="status-dot"></span><div><b>Lõi tính toán đã chạy</b><small>Lịch pháp, cấu trúc sinh và các tầng thời gian đã được xác định theo rule hiện có.</small></div></div><div class="engine-row pending"><span class="status-dot"></span><div><b>Kết luận chỉ hiện khi đủ căn cứ</b><small>${esc(s.canh_bao)}</small></div></div><div class="status-meta"><span class="tag">${s.quy_tac_verified} quy tắc VERIFIED</span><span class="tag">Hồ sơ lưu riêng trên thiết bị</span></div></div>`})}
async function loadProfiles(){profiles=(await dbAll()).sort((a,b)=>(a.created_at||'').localeCompare(b.created_at||'')||a.full_name.localeCompare(b.full_name,'vi'));const saved=localStorage.getItem('xemngay-profile');if(saved&&profiles.some(p=>p.profile_id===saved))currentProfile=saved;else currentProfile=profiles[0]?.profile_id||null;$('profile-select').innerHTML=profiles.length?profiles.map(p=>`<option value="${p.profile_id}" ${p.profile_id===currentProfile?'selected':''}>${esc(p.full_name)}</option>`).join(''):'<option value="">— Chưa có hồ sơ —</option>';$('profile-select').onchange=e=>{currentProfile=e.target.value||null;localStorage.setItem('xemngay-profile',currentProfile||'');updateHomeTitle()};updateHomeTitle();renderProfiles()}
function updateHomeTitle(){const p=current();$('home-title').textContent=p?`Hôm nay của ${p.full_name}`:'Chào gia đình'}
function renderProfiles(){if(!$('profile-list'))return;$('profile-list').innerHTML=profiles.length?profiles.map(p=>`<div class="card profile-row">${avatarSvg(p.avatar||'adult-male')}<div class="grow"><b>${esc(p.full_name)}</b><div class="muted">Sinh (Dương lịch) ${String(p.birth.day).padStart(2,'0')}/${String(p.birth.month).padStart(2,'0')}/${p.birth.year} · ${String(p.birth.hour).padStart(2,'0')}:${String(p.birth.minute).padStart(2,'0')}</div><div class="muted">${esc(p.birth_place_text)}</div></div><div class="row-actions"><button class="btn secondary small" onclick="editProfile('${p.profile_id}')">Sửa</button><button class="btn danger small" onclick="deleteProfile('${p.profile_id}')">Xóa</button></div></div>`).join(''):'<div class="card muted">Chưa có thành viên. Bấm “Thêm người”.</div>'}
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
function renderAvatarChoices(){const current=chosenAvatar;$('avatar-grid').innerHTML=Object.entries(avatarDefs).map(([id,[label]])=>`<button type="button" class="avatar-option ${id===current?'selected':''}" onclick="chooseAvatar('${id}')">${avatarSvg(id)}<small>${label}</small></button>`).join('')}
function chooseAvatar(code){chosenAvatar=code;renderAvatarChoices()}
function openAddProfile(){editingId=null;chosenAvatar='adult-male';$('profile-form-title').textContent='Thêm người';['p-name','p-date','p-time','p-place'].forEach(id=>$(id).value='');$('p-gender').value='NAM';$('p-timezone').value='Asia/Ho_Chi_Minh';$('profile-error').textContent='';renderAvatarChoices();$('profile-modal').classList.add('open')}
function editProfile(id){const p=profiles.find(x=>x.profile_id===id);if(!p)return;editingId=id;chosenAvatar=p.avatar||'adult-male';$('profile-form-title').textContent='Sửa hồ sơ';$('p-name').value=p.full_name;$('p-gender').value=p.gender;$('p-date').value=`${p.birth.year}-${String(p.birth.month).padStart(2,'0')}-${String(p.birth.day).padStart(2,'0')}`;$('p-time').value=`${String(p.birth.hour).padStart(2,'0')}:${String(p.birth.minute).padStart(2,'0')}`;$('p-place').value=p.birth_place_text;$('p-timezone').value=p.timezone_name||'Asia/Ho_Chi_Minh';$('profile-error').textContent='';renderAvatarChoices();$('profile-modal').classList.add('open')}
function closeProfileModal(){$('profile-modal').classList.remove('open')}
async function saveProfile(){try{const d=$('p-date').value,t=$('p-time').value;if(!$('p-name').value.trim()||!d||!t||!$('p-place').value.trim())throw new Error('Hãy nhập đủ tên, ngày giờ sinh và nơi sinh.');const old=editingId?profiles.find(x=>x.profile_id===editingId):null;const p={profile_id:editingId||newId(),full_name:$('p-name').value.trim(),gender:$('p-gender').value,birth:{year:+d.slice(0,4),month:+d.slice(5,7),day:+d.slice(8,10),hour:+t.slice(0,2),minute:+t.slice(3,5)},birth_place_text:$('p-place').value.trim(),timezone_name:$('p-timezone').value,time_certainty:'KNOWN',note:old?.note||null,avatar:chosenAvatar,created_at:old?.created_at||new Date().toISOString(),updated_at:new Date().toISOString()};await dbPut(p);currentProfile=p.profile_id;localStorage.setItem('xemngay-profile',currentProfile);closeProfileModal();await loadProfiles();navTo('profile')}catch(e){$('profile-error').textContent=e.message}}
async function deleteProfile(id){const p=profiles.find(x=>x.profile_id===id);if(!confirm(`Xóa hồ sơ ${p?.full_name||''}? Dữ liệu chỉ bị xóa trên thiết bị này.`))return;await dbDelete(id);if(currentProfile===id)localStorage.removeItem('xemngay-profile');await loadProfiles()}
function needProfile(){if(!currentProfile){alert('Hãy thêm và chọn một thành viên trước.');return false}return true}
function fusionHtml(deep,includeDay=false){if(!deep)return'';const layers=[['Đại vận',deep.dai_van?.tru||'Chưa xác định'],['Năm',deep.nam?.tru?.vi||'—'],['Tháng',deep.thang?.tru?.vi||'—']];if(includeDay)layers.push(['Ngày',deep.ngay?.tru_ngay||'—']);return `<div class="fusion">${layers.map(([a,b])=>`<div class="layer"><small>${a}</small><b>${esc(b)}</b></div>`).join('')}</div>`}
async function openQuestion(kind){
 if(!needProfile())return;
 const p=current();navTo('result');$('result-body').innerHTML='<div class="card">Đang tính…</div>';
 try{
  if(kind==='long'){
   const d=await post('/api/stateless/toi-dang-o-dau',{profile:p});
   $('result-title').textContent='Vận dài hạn';
   $('result-body').innerHTML=`<div class="card"><h3>${esc(d.ho_ten)}</h3><div class="fusion"><div class="layer"><small>Đại vận</small><b>${esc(d.dai_van?.tru||'—')}</b><span class="subline">${d.dai_van?`Năm ${d.dai_van.nam_thu_may}/10 · ${d.dai_van.nam_bat_dau}–${d.dai_van.nam_ket_thuc}`:'Chưa xác định'}</span></div><div class="layer"><small>Năm</small><b>${esc(d.nam_hien_tai.vi)}</b></div><div class="layer"><small>Tháng</small><b>${esc(d.thang_hien_tai.vi)}</b></div></div></div><div class="decision-state pending"><b>Đang chờ đủ căn cứ để kết luận thuận/nghịch</b><span>Lõi tính toán đã xác định vị trí thời gian. App không tự gán tốt/xấu khi nhóm quy tắc quyết định tương ứng chưa đủ trạng thái xác minh.</span></div>${d.dai_van?.canh_bao?.length?`<div class="notice danger"><b>Cảnh báo mốc Đại vận</b>${d.dai_van.canh_bao.map(esc).join('<br>')}</div>`:''}`;
   return;
  }
  const isMonth=kind==='month';
  const d=await post(isMonth?'/api/stateless/thang-nay':'/api/stateless/hom-nay',{profile:p});
  const simple=d.don_gian,deep=d.chuyen_sau;
  $('result-title').textContent=isMonth?`Tháng này của ${p.full_name}`:'Hôm nay thế nào?';
  const scopeLabel=isMonth?'tháng':'ngày';
  $('result-body').innerHTML=`<div class="card result-overview"><div class="result-kicker">Hợp lưu ${isMonth?'Đại vận → Năm → Tháng':'Đại vận → Năm → Tháng → Ngày'}</div>${fusionHtml(deep,!isMonth)}<div class="decision-state pending"><b>Chưa đủ căn cứ để kết luận ${scopeLabel} thuận hay nghịch</b><span>${esc(simple.vi_sao_chua_cham_diem)}</span></div></div><div class="card"><h3>Đã xác định</h3><ul class="list-clean">${simple.he_thong_biet_gi.map(x=>`<li class="known-item"><span>✓</span>${esc(x)}</li>`).join('')}</ul></div><div class="card"><h3>Chưa đủ căn cứ để kết luận</h3><ul class="list-clean">${simple.he_thong_chua_biet_gi.map(x=>`<li class="pending-item"><span>•</span>${esc(x)}</li>`).join('')}</ul></div><button class="btn secondary" onclick="loadWhy('${isMonth?'month':'day'}')">TẠI SAO? · Xem chuyên sâu</button><div id="why-box"></div>`;
 }catch(e){$('result-body').innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}
}
async function loadWhy(scope='day'){
 if(!needProfile())return;
 const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:null});
 const scopeText=scope==='month'?'tháng hiện tại':'ngày đang xem';
 $('why-box').innerHTML=`<div class="card expert-box"><h3>Chuyên sâu · ${scopeText}</h3><p class="muted">Phần này dành cho người muốn kiểm tra rule và nguồn. Thuật ngữ kỹ thuật không được dùng để thay thế kết luận ở tầng gia đình.</p>${d.truy_nguoc.length?d.truy_nguoc.map(r=>`<div class="trace-row"><b>${esc(r.rule_id)} · ${esc(r.name_vi)}</b><div><span class="tag">${esc(r.verification_status)}</span> <span class="tag">tin cậy ${esc(r.confidence)}</span></div><div class="muted">${esc(r.source_title||'Chưa gắn nguồn')}${r.source_location?' · '+esc(r.source_location):''}</div>${r.passage_excerpt?`<pre>${esc(r.passage_excerpt)}</pre>`:''}</div>`).join(''):'<div class="muted">Chưa có rule truy ngược phù hợp.</div>'}</div>`
}
function localISODate(d=new Date()){const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${day}`}
function renderCalendar(){const y=calCursor.getFullYear(),m=calCursor.getMonth();$('cal-title').textContent=`Tháng ${m+1}/${y}`;const first=new Date(y,m,1),start=new Date(y,m,1-first.getDay());const today=localISODate();let html=['CN','T2','T3','T4','T5','T6','T7'].map(x=>`<div class="dow">${x}</div>`).join('');for(let i=0;i<42;i++){const d=new Date(start);d.setDate(start.getDate()+i);const iso=localISODate(d);html+=`<button class="day ${d.getMonth()!==m?'other':''} ${iso===today?'today':''}" onclick="selectCalendarDay('${iso}',this)"><span class="num">${d.getDate()}</span><span class="state">chưa kết luận</span></button>`}$('calendar-grid').innerHTML=html}
function moveMonth(n){calCursor=new Date(calCursor.getFullYear(),calCursor.getMonth()+n,1);renderCalendar()}
async function selectCalendarDay(iso,el){document.querySelectorAll('.day').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');if(!needProfile())return;$('calendar-detail').innerHTML='Đang tính…';try{const d=await post('/api/stateless/hom-nay',{profile:current(),ngay:iso});$('calendar-detail').innerHTML=`<h3>${iso}</h3><div class="decision-state pending"><b>Chưa đủ căn cứ để kết luận ngày này</b><span>${esc(d.don_gian.vi_sao_chua_cham_diem)}</span></div>${fusionHtml(d.chuyen_sau,true)}<button class="btn secondary small" onclick="loadCalendarWhy('${iso}')">Tại sao?</button><div id="calendar-why"></div>`}catch(e){$('calendar-detail').innerHTML=`<div class="notice danger">${esc(e.message)}</div>`}}
async function loadCalendarWhy(iso){const d=await post('/api/stateless/tai-sao',{profile:current(),ngay:iso});$('calendar-why').innerHTML=`<ul class="list-clean">${d.truy_nguoc.map(r=>`<li><b>${esc(r.rule_id)}</b> · ${esc(r.name_vi)} · ${esc(r.verification_status)}</li>`).join('')}</ul>`}
async function loadWorkTypes(){const x=await api('/api/loai-viec');$('work-type').innerHTML=x.map(v=>`<option value="${v.code}">${esc(v.ten)}</option>`).join('');const today=localISODate();$('work-from').value=today;$('work-to').value=today}
async function findDates(){
 if(!needProfile())return;
 $('work-result').innerHTML='<div class="card">Đang kiểm tra các ngày…</div>';
 try{
  const d=await post('/api/stateless/tim-ngay',{profile:current(),viec:$('work-type').value,tu_ngay:$('work-from').value,den_ngay:$('work-to').value});
  $('work-result').innerHTML=`<div class="decision-state pending"><b>Chưa thể xếp hạng các ngày</b><span>${esc(d.ly_do_khong_xep_hang)}</span></div><div class="card"><h3>Đã kiểm tra ${d.so_ngay_da_quet} ngày</h3><p class="muted">Cấu trúc lịch của từng ngày đã được tính. Danh sách kỹ thuật được ẩn ở tầng thường để tránh tạo cảm giác đây là bảng xếp hạng.</p><button class="btn secondary small" onclick="toggleResearchDays()">Xem chi tiết nghiên cứu</button><div id="research-days" class="research-days" hidden>${d.cac_ngay.map(x=>`<div class="research-row"><b>${x.ngay}</b> · ${esc(x.tru_ngay)}<div class="muted">Quan hệ kỹ thuật với Nhật chủ: ${esc(x.quan_he_voi_ban)} · Điểm: chưa chấm</div></div>`).join('')}</div></div>`;
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
