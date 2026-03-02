(function () {
  const cfg = window.gafeteEditorSimple;
  if (!cfg) return;

  console.log('✅ gafete_editor.js cargado');

  const canvas = document.getElementById('editor-gafete-canvas');
  const scaleWrapper = document.getElementById('gafete-scale-wrapper');
  if (!canvas) return;

  console.log('canvas:', canvas);

  const layout = JSON.parse(document.getElementById('layout-data').textContent || '{}');
  const defaultLayout = JSON.parse(document.getElementById('default-layout-data').textContent || '{}');
  const layoutJsonInput = document.getElementById('layout_json');

  const activeKeyLabel = document.getElementById('active-key');
  const hint = document.getElementById('coords-hint');
  const textProps = document.getElementById('text-props');
  const photoProps = document.getElementById('photo-props');
  const checklist = document.getElementById('enabled-fields-checklist');
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

  let items = Array.from(canvas.querySelectorAll('.gafete-item[data-key]'));
  console.log('items:', items.length);

  let activeEl = null;
  let dragState = null;

  if (!layout.items || typeof layout.items !== 'object') layout.items = {};
  if (!Array.isArray(layout.enabled_fields)) layout.enabled_fields = Object.keys(layout.items);

  function syncLayoutJsonField() {
    if (!layoutJsonInput) return;
    layoutJsonInput.value = JSON.stringify({ layout });
  }

  function syncCanvasSizeFromLayout() {
    const width = parseInt(layout.canvas?.width || canvas.dataset.w || 1011, 10);
    const height = parseInt(layout.canvas?.height || canvas.dataset.h || 639, 10);
    const orientation = layout.canvas?.orientation || (height > width ? 'V' : 'H');
    layout.canvas = { width, height, orientation };
    canvas.dataset.w = String(width);
    canvas.dataset.h = String(height);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
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

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const itemCfg = (key) => (layout.items && layout.items[key] ? layout.items[key] : null);
  const isEnabled = (key) => layout.enabled_fields.includes(key);

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

  function updateFieldToggleState() {
    checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      const key = input.dataset.field;
      const cfgItem = itemCfg(key);
      input.checked = !!cfgItem && isEnabled(key) && cfgItem.visible !== false;
    });
  }

  function bindChecklist() {
    checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      input.addEventListener('change', (ev) => {
        const key = ev.target.dataset.field;
        const cfgItem = itemCfg(key);
        if (!cfgItem) return;

        if (ev.target.checked) {
          if (!layout.enabled_fields.includes(key)) layout.enabled_fields.push(key);
          cfgItem.visible = true;
        } else {
          layout.enabled_fields = layout.enabled_fields.filter((f) => f !== key);
          cfgItem.visible = false;
        }

        console.log('toggle field', key, ev.target.checked);
        const el = canvas.querySelector(`.gafete-item[data-key="${key}"]`);
        if (el) applyStyle(el, cfgItem, key);
        syncLayoutJsonField();
      });
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
    syncLayoutJsonField();
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
    syncLayoutJsonField();
  }

  function applyAllStyles() {
    items = Array.from(canvas.querySelectorAll('.gafete-item[data-key]'));
    items.forEach((el) => {
      const key = el.dataset.key;
      const cfgItem = itemCfg(key);
      if (cfgItem) applyStyle(el, cfgItem, key);
    });
    updateFieldToggleState();
  }

  function beginDrag(ev, el) {
    const key = el.dataset.key;
    if (!key || !isEnabled(key)) return;
    const cfgItem = itemCfg(key);
    if (!cfgItem) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = rect.width / (layout.canvas.width || rect.width || 1);
    const scaleY = rect.height / (layout.canvas.height || rect.height || 1);

    const left = parseFloat(cfgItem.x || 0);
    const top = parseFloat(cfgItem.y || 0);
    const pointerX = (ev.clientX - rect.left) / scaleX;
    const pointerY = (ev.clientY - rect.top) / scaleY;

    dragState = {
      key,
      el,
      startX: pointerX,
      startY: pointerY,
      origLeft: left,
      origTop: top,
      moved: false,
      pointerId: ev.pointerId,
      scaleX,
      scaleY,
    };

    setActive(el);
    el.setPointerCapture(ev.pointerId);
    el.classList.add('dragging');
    ev.preventDefault();
  }

  function onDragMove(ev) {
    if (!dragState || ev.pointerId !== dragState.pointerId) return;
    const cfgItem = itemCfg(dragState.key);
    if (!cfgItem) return;

    const rect = canvas.getBoundingClientRect();
    const curX = (ev.clientX - rect.left) / dragState.scaleX;
    const curY = (ev.clientY - rect.top) / dragState.scaleY;
    const dx = curX - dragState.startX;
    const dy = curY - dragState.startY;

    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragState.moved = true;

    const itemW = dragState.key === 'photo' ? (cfgItem.w || dragState.el.offsetWidth) : dragState.el.offsetWidth;
    const itemH = dragState.key === 'photo' ? (cfgItem.h || dragState.el.offsetHeight) : dragState.el.offsetHeight;

    const newLeft = clamp(Math.round(dragState.origLeft + dx), 0, Math.max(0, layout.canvas.width - itemW));
    const newTop = clamp(Math.round(dragState.origTop + dy), 0, Math.max(0, layout.canvas.height - itemH));

    cfgItem.x = newLeft;
    cfgItem.y = newTop;
    applyStyle(dragState.el, cfgItem, dragState.key);
    hint.textContent = `x: ${newLeft}, y: ${newTop}`;
  }

  function endDrag(ev) {
    if (!dragState) return;
    if (ev && ev.pointerId !== dragState.pointerId) return;

    const finishedState = dragState;
    const cfgItem = itemCfg(finishedState.key);
    if (cfgItem) syncLayoutJsonField();
    finishedState.el.classList.remove('dragging');
    try {
      if (finishedState.el.hasPointerCapture(finishedState.pointerId)) finishedState.el.releasePointerCapture(finishedState.pointerId);
    } catch (e) {
      // no-op
    }

    dragState = null;
  }

  syncCanvasSizeFromLayout();
  bindChecklist();
  applyAllStyles();
  fitScale();
  syncLayoutJsonField();
  window.addEventListener('resize', fitScale);

  canvas.addEventListener('pointerdown', (ev) => {
    const target = ev.target.closest('.draggable[data-key]');
    if (!target || !canvas.contains(target)) return;
    beginDrag(ev, target);
  });

  canvas.addEventListener('click', (ev) => {
    if (dragState && dragState.moved) return;
    const target = ev.target.closest('.gafete-item[data-key]');
    if (target) setActive(target);
    else setActive(null);
  });

  items.forEach((el) => {
    el.addEventListener('pointermove', onDragMove);
    el.addEventListener('pointerup', endDrag);
    el.addEventListener('pointercancel', endDrag);
  });

  document.getElementById('refresh-size').addEventListener('click', fitScale);
  colorInput.addEventListener('input', () => { colorText.value = colorInput.value; applyTextProps(); });
  colorText.addEventListener('input', () => { if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) { colorInput.value = colorText.value; applyTextProps(); } });
  sizeInput.addEventListener('input', applyTextProps);
  weightInput.addEventListener('change', applyTextProps);
  [shapeRounded, shapeCircle, photoBorder, photoBorderWidth, photoBorderColor, photoW, photoH, photoRadius].forEach((input) => {
    input.addEventListener('input', applyPhotoProps);
    input.addEventListener('change', applyPhotoProps);
  });

  document.getElementById('save-layout').addEventListener('click', async () => {
    syncLayoutJsonField();
    const res = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf, 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({ layout }),
    });
    alert(res.ok ? 'Diseño guardado' : 'No se pudo guardar el diseño');
  });

  document.getElementById('reset-layout').addEventListener('click', () => {
    layout.canvas = JSON.parse(JSON.stringify(defaultLayout.canvas));
    layout.enabled_fields = JSON.parse(JSON.stringify(defaultLayout.enabled_fields || []));
    layout.items = JSON.parse(JSON.stringify(defaultLayout.items || {}));
    applyAllStyles();
    updateFieldToggleState();
    syncCanvasSizeFromLayout();
    fitScale();
    setActive(null);
    syncLayoutJsonField();
    hint.textContent = 'Restablecido a valores por defecto';
  });
})();
