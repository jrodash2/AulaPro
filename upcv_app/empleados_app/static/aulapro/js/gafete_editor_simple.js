(function () {
  const cfg = window.gafeteEditorSimple;
  if (!cfg) return;

  const H_SIZE = { width: 1011, height: 639 };
  const V_SIZE = { width: 639, height: 1011 };

  const canvas = document.getElementById('editor-canvas');
  const scaleWrapper = document.getElementById('gafete-scale-wrapper');
  if (!canvas) return;

  const layout = JSON.parse(document.getElementById('layout-data').textContent || '{}');
  const defaultLayout = JSON.parse(document.getElementById('default-layout-data').textContent || '{}');

  const activeKeyLabel = document.getElementById('active-key');
  const hint = document.getElementById('coords-hint');
  const textProps = document.getElementById('text-props');
  const photoProps = document.getElementById('photo-props');
  const checklist = document.getElementById('enabled-fields-checklist');
  const orientH = document.getElementById('orient-h');
  const orientV = document.getElementById('orient-v');

  const colorInput = document.getElementById('prop-color');
  const colorText = document.getElementById('prop-color-text');
  const sizeInput = document.getElementById('prop-size');
  const weightInput = document.getElementById('prop-weight');

  const shapeRounded = document.getElementById('shape-rounded');
  const shapeCircle = document.getElementById('shape-circle');
  const photoBorder = document.getElementById('photo-border');
  const photoBorderWidth = document.getElementById('photo-border-width');
  const photoBorderColor = document.getElementById('photo-border-color');
  const photoW = document.getElementById('photo-w');
  const photoH = document.getElementById('photo-h');
  const photoRadius = document.getElementById('photo-radius');

  const items = Array.from(canvas.querySelectorAll('.gafete-item[data-key]'));
  let activeEl = null;
  let dragState = null;

  if (!Array.isArray(layout.enabled_fields)) {
    layout.enabled_fields = Object.keys(layout.items || {});
  }

  function canvasSizeByOrientation(orientation) {
    return orientation === 'V' ? V_SIZE : H_SIZE;
  }

  function syncCanvasSizeFromLayout() {
    const orientation = (layout.canvas && layout.canvas.orientation) || 'H';
    const size = canvasSizeByOrientation(orientation);
    layout.canvas = { width: size.width, height: size.height, orientation };
    canvas.dataset.canvasWidth = size.width;
    canvas.dataset.canvasHeight = size.height;
    canvas.style.width = `${size.width}px`;
    canvas.style.height = `${size.height}px`;
  }

  function fitScale() {
    if (!scaleWrapper || !layout.canvas) return;
    const viewport = scaleWrapper.parentElement;
    const availableW = viewport.clientWidth || layout.canvas.width;
    const availableH = window.innerHeight * 0.65;
    const scale = Math.min(1, availableW / layout.canvas.width, availableH / layout.canvas.height);
    scaleWrapper.style.transform = `scale(${scale})`;
    scaleWrapper.style.transformOrigin = 'top left';
    scaleWrapper.style.width = `${layout.canvas.width}px`;
    scaleWrapper.style.height = `${layout.canvas.height}px`;
    viewport.style.minHeight = `${Math.round(layout.canvas.height * scale)}px`;
  }

  function getScale() {
    const displayed = canvas.getBoundingClientRect().width || 1;
    const real = parseFloat(layout.canvas?.width || 1011);
    return displayed / real;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function itemCfg(key) {
    return layout.items && layout.items[key] ? layout.items[key] : null;
  }

  function isEnabled(key) {
    return layout.enabled_fields.includes(key);
  }

  function applyStyle(el, cfgItem, key) {
    el.style.left = `${cfgItem.x || 0}px`;
    el.style.top = `${cfgItem.y || 0}px`;
    el.style.display = isEnabled(key) && cfgItem.visible !== false ? 'block' : 'none';

    if (key === 'photo') {
      el.style.width = `${cfgItem.w || 250}px`;
      el.style.height = `${cfgItem.h || 350}px`;
      el.style.border = cfgItem.border ? `${cfgItem.border_width || 4}px solid ${cfgItem.border_color || '#ffffff'}` : 'none';
      el.style.borderRadius = cfgItem.shape === 'circle' ? '50%' : `${cfgItem.radius || 20}px`;
      return;
    }

    el.style.fontSize = `${cfgItem.font_size || 24}px`;
    el.style.fontWeight = `${cfgItem.font_weight || '400'}`;
    el.style.color = cfgItem.color || '#111111';
    el.style.textAlign = cfgItem.align || 'left';
  }

  function renderChecklist() {
    checklist.innerHTML = '';
    const labels = {
      photo: 'Foto', nombres: 'Nombres', apellidos: 'Apellidos', codigo_alumno: 'Código alumno',
      grado: 'Grado', grado_descripcion: 'Descripción grado', cui: 'CUI', telefono: 'Teléfono emergencia', establecimiento: 'Establecimiento', sitio_web: 'Sitio web',
    };
    Object.keys(layout.items || {}).forEach((key) => {
      const id = `field-${key}`;
      const wrap = document.createElement('div');
      wrap.className = 'form-check';
      wrap.innerHTML = `<input class="form-check-input" type="checkbox" id="${id}" ${isEnabled(key) ? 'checked' : ''}><label class="form-check-label" for="${id}">${labels[key] || key}</label>`;
      wrap.querySelector('input').addEventListener('change', (ev) => {
        if (ev.target.checked) {
          if (!layout.enabled_fields.includes(key)) layout.enabled_fields.push(key);
          layout.items[key].visible = true;
        } else {
          layout.enabled_fields = layout.enabled_fields.filter((f) => f !== key);
          layout.items[key].visible = false;
        }
        const el = items.find((i) => i.dataset.key === key);
        if (el) applyStyle(el, layout.items[key], key);
      });
      checklist.appendChild(wrap);
    });
  }

  function setActive(el) {
    items.forEach((i) => i.classList.remove('is-active'));
    activeEl = el;
    if (!activeEl) {
      activeKeyLabel.textContent = 'Elemento activo: ninguno';
      textProps.classList.add('d-none');
      photoProps.classList.add('d-none');
      return;
    }

    activeEl.classList.add('is-active');
    const key = activeEl.dataset.key;
    const cfgItem = itemCfg(key);
    if (!cfgItem) return;
    activeKeyLabel.textContent = `Elemento activo: ${key}`;

    if (key === 'photo') {
      textProps.classList.add('d-none');
      photoProps.classList.remove('d-none');
      shapeRounded.checked = (cfgItem.shape || 'rounded') === 'rounded';
      shapeCircle.checked = cfgItem.shape === 'circle';
      photoBorder.checked = cfgItem.border !== false;
      photoBorderWidth.value = cfgItem.border_width || 4;
      photoBorderColor.value = cfgItem.border_color || '#ffffff';
      photoW.value = cfgItem.w || 250;
      photoH.value = cfgItem.h || 350;
      photoRadius.value = cfgItem.radius || 20;
      return;
    }

    photoProps.classList.add('d-none');
    textProps.classList.remove('d-none');
    colorInput.value = cfgItem.color || '#111111';
    colorText.value = cfgItem.color || '#111111';
    sizeInput.value = cfgItem.font_size || 24;
    weightInput.value = String(cfgItem.font_weight || '400');
  }

  function applyTextProps() {
    if (!activeEl) return;
    const key = activeEl.dataset.key;
    if (key === 'photo') return;
    const cfgItem = itemCfg(key);
    if (!cfgItem) return;
    cfgItem.color = colorInput.value;
    cfgItem.font_size = parseInt(sizeInput.value || '24', 10);
    cfgItem.font_weight = weightInput.value;
    applyStyle(activeEl, cfgItem, key);
  }

  function applyPhotoProps() {
    if (!activeEl || activeEl.dataset.key !== 'photo') return;
    const cfgItem = itemCfg('photo');
    if (!cfgItem) return;
    cfgItem.shape = shapeCircle.checked ? 'circle' : 'rounded';
    cfgItem.border = !!photoBorder.checked;
    cfgItem.border_width = parseInt(photoBorderWidth.value || '4', 10);
    cfgItem.border_color = photoBorderColor.value || '#ffffff';
    cfgItem.w = parseInt(photoW.value || '250', 10);
    cfgItem.h = parseInt(photoH.value || '350', 10);
    cfgItem.radius = parseInt(photoRadius.value || '20', 10);
    applyStyle(activeEl, cfgItem, 'photo');
  }

  function applyAllStyles() {
    items.forEach((el) => {
      const key = el.dataset.key;
      const cfgItem = itemCfg(key);
      if (cfgItem) applyStyle(el, cfgItem, key);
    });
  }

  function changeOrientation(orientation) {
    const oldW = layout.canvas.width;
    const oldH = layout.canvas.height;
    const next = canvasSizeByOrientation(orientation);

    Object.keys(layout.items || {}).forEach((key) => {
      const cfgItem = layout.items[key];
      cfgItem.x = Math.round((cfgItem.x || 0) * (next.width / oldW));
      cfgItem.y = Math.round((cfgItem.y || 0) * (next.height / oldH));
      if (key === 'photo') {
        cfgItem.w = Math.round((cfgItem.w || 250) * (next.width / oldW));
        cfgItem.h = Math.round((cfgItem.h || 350) * (next.height / oldH));
      }
    });

    layout.canvas.orientation = orientation;
    syncCanvasSizeFromLayout();
    applyAllStyles();
    fitScale();
  }

  syncCanvasSizeFromLayout();
  renderChecklist();
  applyAllStyles();
  fitScale();
  window.addEventListener('resize', fitScale);

  if ((layout.canvas.orientation || 'H') === 'V') orientV.checked = true;
  else orientH.checked = true;

  orientH.addEventListener('change', () => orientH.checked && changeOrientation('H'));
  orientV.addEventListener('change', () => orientV.checked && changeOrientation('V'));

  items.forEach((el) => {
    const key = el.dataset.key;

    el.addEventListener('click', function (ev) {
      ev.stopPropagation();
      setActive(el);
    });

    el.addEventListener('pointerdown', function (ev) {
      if (!isEnabled(key)) return;
      setActive(el);
      const scale = getScale();
      const cfgItem = itemCfg(key);
      if (!cfgItem) return;

      dragState = { key, startX: ev.clientX, startY: ev.clientY, baseX: cfgItem.x || 0, baseY: cfgItem.y || 0, scale };
      el.setPointerCapture(ev.pointerId);
      ev.preventDefault();
    });

    el.addEventListener('pointermove', function (ev) {
      if (!dragState || dragState.key !== key) return;
      const cfgItem = itemCfg(key);
      if (!cfgItem) return;
      const dx = (ev.clientX - dragState.startX) / dragState.scale;
      const dy = (ev.clientY - dragState.startY) / dragState.scale;

      const itemW = key === 'photo' ? (cfgItem.w || el.offsetWidth) : el.offsetWidth;
      const itemH = key === 'photo' ? (cfgItem.h || el.offsetHeight) : el.offsetHeight;
      cfgItem.x = clamp(Math.round(dragState.baseX + dx), 0, Math.max(0, layout.canvas.width - itemW));
      cfgItem.y = clamp(Math.round(dragState.baseY + dy), 0, Math.max(0, layout.canvas.height - itemH));
      applyStyle(el, cfgItem, key);
      hint.textContent = `x: ${cfgItem.x}, y: ${cfgItem.y}`;
    });

    el.addEventListener('pointerup', function () { dragState = null; });
  });

  canvas.addEventListener('click', function () { setActive(null); });
  document.getElementById('refresh-size').addEventListener('click', fitScale);

  colorInput.addEventListener('input', function () { colorText.value = colorInput.value; applyTextProps(); });
  colorText.addEventListener('input', function () { if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) { colorInput.value = colorText.value; applyTextProps(); } });
  sizeInput.addEventListener('input', applyTextProps);
  weightInput.addEventListener('change', applyTextProps);
  [shapeRounded, shapeCircle, photoBorder, photoBorderWidth, photoBorderColor, photoW, photoH, photoRadius].forEach((input) => {
    input.addEventListener('input', applyPhotoProps);
    input.addEventListener('change', applyPhotoProps);
  });

  document.getElementById('save-layout').addEventListener('click', async function () {
    const res = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf, 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({ layout }),
    });
    alert(res.ok ? 'Diseño guardado' : 'No se pudo guardar el diseño');
  });

  document.getElementById('reset-layout').addEventListener('click', function () {
    layout.canvas = JSON.parse(JSON.stringify(defaultLayout.canvas));
    layout.enabled_fields = JSON.parse(JSON.stringify(defaultLayout.enabled_fields || []));
    layout.items = JSON.parse(JSON.stringify(defaultLayout.items || {}));
    renderChecklist();
    applyAllStyles();
    orientH.checked = (layout.canvas.orientation || 'H') === 'H';
    orientV.checked = (layout.canvas.orientation || 'H') === 'V';
    syncCanvasSizeFromLayout();
    fitScale();
    setActive(null);
    hint.textContent = 'Restablecido a valores por defecto';
  });
})();
