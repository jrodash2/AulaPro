(function () {
  const cfg = window.gafeteEditorSimple;
  if (!cfg) return;

  const canvas = document.getElementById('editor-canvas');
  if (!canvas) return;

  const layout = JSON.parse(document.getElementById('layout-data').textContent || '{}');
  const defaultLayout = JSON.parse(document.getElementById('default-layout-data').textContent || '{}');

  const activeKeyLabel = document.getElementById('active-key');
  const hint = document.getElementById('coords-hint');
  const colorInput = document.getElementById('prop-color');
  const colorText = document.getElementById('prop-color-text');
  const sizeInput = document.getElementById('prop-size');
  const weightInput = document.getElementById('prop-weight');

  const items = Array.from(canvas.querySelectorAll('.gafete-item'));
  let activeEl = null;
  let dragState = null;

  function getScale() {
    const displayed = canvas.getBoundingClientRect().width || 1;
    const real = parseFloat(canvas.dataset.canvasWidth || layout.canvas?.width || 880);
    return displayed / real;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function itemCfg(key) {
    if (!layout.items || !layout.items[key]) return null;
    return layout.items[key];
  }

  function applyStyle(el, cfgItem) {
    el.style.left = `${cfgItem.x}px`;
    el.style.top = `${cfgItem.y}px`;
    el.style.fontSize = `${cfgItem.font_size}px`;
    el.style.fontWeight = `${cfgItem.font_weight}`;
    el.style.color = cfgItem.color;
    el.style.textAlign = cfgItem.align || 'left';
    el.style.display = cfgItem.visible === false ? 'none' : 'block';
  }

  function setActive(el) {
    items.forEach((i) => i.classList.remove('is-active'));
    activeEl = el;
    if (!activeEl) {
      activeKeyLabel.textContent = 'Elemento activo: ninguno';
      return;
    }
    activeEl.classList.add('is-active');
    const key = activeEl.dataset.key;
    const cfgItem = itemCfg(key);
    if (!cfgItem) return;
    activeKeyLabel.textContent = `Elemento activo: ${key}`;
    colorInput.value = cfgItem.color || '#111111';
    colorText.value = cfgItem.color || '#111111';
    sizeInput.value = cfgItem.font_size || 24;
    weightInput.value = String(cfgItem.font_weight || '400');
  }

  function applyProperties() {
    if (!activeEl) return;
    const key = activeEl.dataset.key;
    const cfgItem = itemCfg(key);
    if (!cfgItem) return;
    cfgItem.color = colorInput.value;
    cfgItem.font_size = parseInt(sizeInput.value || '24', 10);
    cfgItem.font_weight = weightInput.value;
    applyStyle(activeEl, cfgItem);
  }

  items.forEach((el) => {
    const key = el.dataset.key;
    const cfgItem = itemCfg(key);
    if (cfgItem) applyStyle(el, cfgItem);

    el.addEventListener('click', function (ev) {
      ev.stopPropagation();
      setActive(el);
    });

    el.addEventListener('pointerdown', function (ev) {
      setActive(el);
      const scale = getScale();
      const key = el.dataset.key;
      const cfgItem = itemCfg(key);
      if (!cfgItem) return;
      dragState = {
        key,
        startX: ev.clientX,
        startY: ev.clientY,
        baseX: cfgItem.x,
        baseY: cfgItem.y,
        scale,
      };
      el.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    });

    el.addEventListener('pointermove', function (ev) {
      if (!dragState || dragState.key !== el.dataset.key) return;
      const cfgItem = itemCfg(dragState.key);
      if (!cfgItem) return;
      const dx = (ev.clientX - dragState.startX) / dragState.scale;
      const dy = (ev.clientY - dragState.startY) / dragState.scale;
      const maxX = (layout.canvas?.width || 880) - el.offsetWidth;
      const maxY = (layout.canvas?.height || 565) - el.offsetHeight;
      cfgItem.x = clamp(Math.round(dragState.baseX + dx), 0, Math.max(0, maxX));
      cfgItem.y = clamp(Math.round(dragState.baseY + dy), 0, Math.max(0, maxY));
      applyStyle(el, cfgItem);
      hint.textContent = `x: ${cfgItem.x}, y: ${cfgItem.y}`;
    });

    el.addEventListener('pointerup', function () {
      dragState = null;
    });
  });

  canvas.addEventListener('click', function () {
    setActive(null);
  });

  colorInput.addEventListener('input', function () {
    colorText.value = colorInput.value;
    applyProperties();
  });
  colorText.addEventListener('input', function () {
    if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) {
      colorInput.value = colorText.value;
      applyProperties();
    }
  });
  sizeInput.addEventListener('input', applyProperties);
  weightInput.addEventListener('change', applyProperties);

  document.getElementById('save-layout').addEventListener('click', async function () {
    const res = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': cfg.csrf,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ layout }),
    });
    if (res.ok) {
      alert('Diseño guardado');
    } else {
      alert('No se pudo guardar el diseño');
    }
  });

  document.getElementById('reset-layout').addEventListener('click', function () {
    layout.canvas = { ...defaultLayout.canvas };
    layout.items = JSON.parse(JSON.stringify(defaultLayout.items || {}));
    items.forEach((el) => {
      const cfgItem = itemCfg(el.dataset.key);
      if (cfgItem) applyStyle(el, cfgItem);
    });
    setActive(null);
    hint.textContent = 'Restablecido a valores por defecto';
  });
})();
