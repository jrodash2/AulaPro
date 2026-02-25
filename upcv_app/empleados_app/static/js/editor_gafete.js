(function () {
  const cfg = window.editorConfig;
  if (!cfg) return;
  const canvas = document.getElementById('canvas');
  const select = document.getElementById('layer-select');
  const sizeInput = document.getElementById('font-size');
  const colorInput = document.getElementById('font-color');
  const alignInput = document.getElementById('font-align');
  let layers = cfg.capas || [];
  let active = 0;

  function render() {
    canvas.querySelectorAll('.layer-text').forEach((n) => n.remove());
    select.innerHTML = '';
    layers.forEach((l, i) => {
      const text = document.createElement('div');
      text.className = 'layer-text';
      text.dataset.i = i;
      text.textContent = cfg.example[l.key] || l.key;
      text.style.cssText = `position:absolute;left:${l.x}px;top:${l.y}px;font-size:${l.font_size}px;font-family:${l.font_family};font-weight:${l.font_weight};color:${l.color};cursor:move;user-select:none;text-align:${l.align};`;
      text.addEventListener('mousedown', startDrag);
      canvas.appendChild(text);
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = l.key;
      select.appendChild(opt);
    });
    select.value = active;
    syncInputs();
  }

  function syncInputs() {
    const l = layers[active];
    if (!l) return;
    sizeInput.value = l.font_size;
    colorInput.value = l.color;
    alignInput.value = l.align;
  }

  function startDrag(e) {
    active = Number(e.target.dataset.i);
    const layer = layers[active];
    const rect = canvas.getBoundingClientRect();
    const startX = e.clientX - layer.x;
    const startY = e.clientY - layer.y;
    function move(ev) {
      layer.x = Math.max(0, Math.min(Math.round(ev.clientX - rect.left - startX), rect.width));
      layer.y = Math.max(0, Math.min(Math.round(ev.clientY - rect.top - startY), rect.height));
      render();
    }
    function up() {
      document.removeEventListener('mousemove', move);
      document.removeEventListener('mouseup', up);
    }
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  }

  select.addEventListener('change', () => { active = Number(select.value); syncInputs(); });
  sizeInput.addEventListener('input', () => { layers[active].font_size = Number(sizeInput.value || 18); render(); });
  colorInput.addEventListener('input', () => { layers[active].color = colorInput.value; render(); });
  alignInput.addEventListener('change', () => { layers[active].align = alignInput.value; render(); });

  document.getElementById('save-design').addEventListener('click', async () => {
    const res = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf },
      body: JSON.stringify({ capas: layers })
    });
    if (res.ok) alert('Diseño guardado correctamente'); else alert('No se pudo guardar el diseño');
  });

  render();
})();
