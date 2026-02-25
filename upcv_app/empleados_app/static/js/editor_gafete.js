(function(){
  const cfg = window.gafeteEditorData;
  if(!cfg) return;
  const items = Array.from(document.querySelectorAll('.layer-item'));
  const select = document.getElementById('layer-select');
  const classInput = document.getElementById('layer-class');
  const layers = (cfg.layout && cfg.layout.layers) ? cfg.layout.layers : {};
  let active = null;

  items.forEach((el, idx) => {
    const key = el.dataset.layer;
    const layerCfg = layers[key] || {};
    if(layerCfg.class){ el.className = `layer-item ${layerCfg.class}`; }
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = key;
    select.appendChild(opt);

    let startX=0,startY=0,baseX=0,baseY=0;
    const style = window.getComputedStyle(el);
    baseX = parseInt(style.left || 0, 10) || 0;
    baseY = parseInt(style.top || 0, 10) || 0;
    el.addEventListener('mousedown', function(e){
      active = key;
      select.value = key;
      classInput.value = (layers[key] && layers[key].class) || el.className.replace('layer-item','').trim();
      startX = e.clientX; startY = e.clientY;
      const initialX = parseInt(window.getComputedStyle(el).left || 0,10) || 0;
      const initialY = parseInt(window.getComputedStyle(el).top || 0,10) || 0;
      function move(ev){
        el.style.left = `${initialX + (ev.clientX - startX)}px`;
        el.style.top = `${initialY + (ev.clientY - startY)}px`;
      }
      function up(){
        document.removeEventListener('mousemove', move);
        document.removeEventListener('mouseup', up);
      }
      document.addEventListener('mousemove', move);
      document.addEventListener('mouseup', up);
    });
    if(idx===0){active=key;}
  });

  select.addEventListener('change', function(){
    active = this.value;
    const el = document.querySelector(`.layer-item[data-layer='${active}']`);
    classInput.value = (layers[active] && layers[active].class) || (el ? el.className.replace('layer-item','').trim() : '');
  });

  classInput.addEventListener('input', function(){
    if(!active) return;
    layers[active] = layers[active] || {};
    layers[active].class = this.value.trim();
    const el = document.querySelector(`.layer-item[data-layer='${active}']`);
    if(el) el.className = `layer-item ${this.value.trim()}`;
  });

  document.getElementById('save-layout').addEventListener('click', async function(){
    items.forEach((el)=>{
      const key = el.dataset.layer;
      layers[key] = layers[key] || {};
      layers[key].class = el.className.replace('layer-item','').trim();
    });
    const res = await fetch(cfg.saveUrl, {
      method:'POST',
      headers:{'Content-Type':'application/json','X-CSRFToken':cfg.csrf},
      body: JSON.stringify({layers})
    });
    if(res.ok){ alert('Diseño guardado'); } else { alert('Error al guardar'); }
  });
})();
