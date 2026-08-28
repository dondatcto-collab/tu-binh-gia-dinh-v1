// V2.6 Product Consolidation — một điểm bootstrap duy nhất cho các module giao diện.
(function(){
  window.TU_BINH_PRODUCT_UI_VERSION = '2.6';
  const modules = [
    ['work', '/static/ui-work-v21.js?v=2.6'],
    ['finance', '/static/ui-finance-v22.js?v=2.6'],
    ['relationship', '/static/ui-relationship-v23.js?v=2.6'],
    ['hour', '/static/ui-hour-v24.js?v=2.6'],
  ];

  function loadModule(name, src){
    if(document.querySelector(`script[data-v26-module="${name}"]`)) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.dataset.v26Module = name;
      s.onload = resolve;
      s.onerror = () => reject(new Error(`Không tải được module giao diện: ${name}`));
      document.head.appendChild(s);
    });
  }

  async function boot(){
    try{
      for(const [name, src] of modules) await loadModule(name, src);
      window.TU_BINH_UI_READY = true;
      if(typeof loadHomeDashboard === 'function') setTimeout(() => { try{ loadHomeDashboard(); }catch{} }, 0);
    }catch(err){
      window.TU_BINH_UI_READY = false;
      console.error('[V2.6 bootstrap]', err);
    }
  }

  boot();
})();
