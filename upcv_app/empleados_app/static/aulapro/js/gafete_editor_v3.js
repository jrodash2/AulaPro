(function () {
  const cfg = window.gafeteEditorSimple || {};
  const frontCanvas = document.getElementById('editorCanvasFront');
  const backCanvas = document.getElementById('editorCanvasBack');
  const layoutInput = document.getElementById('layout_json');
  const saveForm = document.getElementById('editorForm');
  if (!frontCanvas || !backCanvas || !layoutInput || !saveForm) return;

  const canvases = { front: frontCanvas, back: backCanvas };
  let currentFace = 'front';
  let activeKey = null;

  const BACK_TEXT_KEYS = new Set(['nombres', 'apellidos', 'codigo_alumno', 'grado', 'grado_descripcion', 'cui', 'telefono', 'establecimiento', 'sitio_web', 'texto_libre_1', 'texto_libre_2', 'texto_libre_3']);

  const activeKeyLabel = document.getElementById('active-key');
  const hint = document.getElementById('coords-hint');
  const checklist = document.getElementById('enabled-fields-checklist');
  const textContentInput = document.getElementById('prop-text-content');

  const colorInput = document.getElementById('prop-color');
  const colorText = document.getElementById('prop-color-text');
  const sizeInput = document.getElementById('prop-size');
  const weightInput = document.getElementById('prop-weight');
  const textProps = document.getElementById('text-props');
  const photoProps = document.getElementById('photo-props');
  const shapeRounded = document.getElementById('shape-rounded');
  const shapeCircle = document.getElementById('shape-circle');
  const photoBorder = document.getElementById('photo-border');
  const photoBorderWidth = document.getElementById('photo-border-width');
  const photoBorderColor = document.getElementById('photo-border-color');
  const photoW = document.getElementById('photo-w');
  const photoH = document.getElementById('photo-h');
  const photoRadius = document.getElementById('photo-radius');

  const layout = JSON.parse(document.getElementById('layout-data').textContent || '{}');
  const defaultLayout = JSON.parse(document.getElementById('default-layout-data').textContent || '{}');

  const faceData = () => layout[currentFace] || { enabled_fields: [], items: {} };
  const items = () => Array.from(canvases[currentFace].querySelectorAll('.gafete-item[data-key]'));
  const getCfg = (key) => (faceData().items || {})[key];
  const isEnabled = (key) => (faceData().enabled_fields || []).includes(key);

  function allowedInCurrentFace(key) {
    return currentFace === 'front' ? true : BACK_TEXT_KEYS.has(key);
  }

  function syncLayoutInput() { layoutInput.value = JSON.stringify({ layout }); }

  function showFace(face) {
    currentFace = face === 'back' ? 'back' : 'front';
    frontCanvas.style.display = currentFace === 'front' ? '' : 'none';
    backCanvas.style.display = currentFace === 'back' ? '' : 'none';
    document.querySelectorAll('.face-switch').forEach((b) => b.classList.toggle('active', b.dataset.face === currentFace));
    activeKey = null;
    refreshChecklist();
    setActive(null);
  }

  function applyStyle(el, cfg, key) {
    if (!cfg) return;
    el.style.left = `${cfg.x || 0}px`;
    el.style.top = `${cfg.y || 0}px`;
    el.style.display = (allowedInCurrentFace(key) && isEnabled(key) && cfg.visible !== false) ? '' : 'none';
    if (key === 'photo') {
      el.style.width = `${cfg.w || 220}px`;
      el.style.height = `${cfg.h || 220}px`;
      el.style.border = cfg.border ? `${cfg.border_width || 4}px solid ${cfg.border_color || '#ffffff'}` : 'none';
      el.style.borderRadius = cfg.shape === 'circle' ? '50%' : `${cfg.radius || 20}px`;
      return;
    }
    el.style.fontSize = `${cfg.font_size || 24}px`;
    el.style.fontWeight = `${cfg.font_weight || '400'}`;
    el.style.color = cfg.color || '#111111';
    el.style.textAlign = cfg.align || 'left';
    if (key.startsWith('texto_libre_') && textContentInput && el.textContent !== cfg.text) {
      el.textContent = cfg.text || '';
    }
  }

  function refreshChecklist() {
    checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      const key = input.dataset.field;
      const cfg = getCfg(key);
      input.checked = !!cfg && isEnabled(key) && cfg.visible !== false;
      input.closest('.form-check').style.display = allowedInCurrentFace(key) ? '' : 'none';
    });
  }

  function refreshItems() {
    items().forEach((el) => applyStyle(el, getCfg(el.dataset.key), el.dataset.key));
  }

  function setActive(key) {
    activeKey = key;
    items().forEach((el) => el.classList.toggle('is-active', el.dataset.key === key));
    if (!key) {
      activeKeyLabel.textContent = `Elemento activo (${currentFace}): ninguno`;
      textProps.classList.add('d-none');
      photoProps.classList.add('d-none');
      return;
    }
    const cfg = getCfg(key);
    activeKeyLabel.textContent = `Elemento activo (${currentFace}): ${key}`;
    if (key === 'photo' && currentFace === 'front') {
      textProps.classList.add('d-none');
      photoProps.classList.remove('d-none');
      shapeRounded.checked = (cfg.shape || 'rounded') === 'rounded';
      shapeCircle.checked = cfg.shape === 'circle';
      photoBorder.checked = cfg.border !== false;
      photoBorderWidth.value = cfg.border_width || 4;
      photoBorderColor.value = cfg.border_color || '#ffffff';
      photoW.value = cfg.w || 250;
      photoH.value = cfg.h || 350;
      photoRadius.value = cfg.radius || 20;
      return;
    }
    photoProps.classList.add('d-none');
    textProps.classList.remove('d-none');
    colorInput.value = cfg.color || '#111111';
    colorText.value = cfg.color || '#111111';
    sizeInput.value = cfg.font_size || 24;
    weightInput.value = String(cfg.font_weight || '400');
    textContentInput.value = key.startsWith('texto_libre_') ? (cfg.text || '') : '';
    textContentInput.disabled = !key.startsWith('texto_libre_');
  }

  checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => input.addEventListener('change', () => {
    const key = input.dataset.field;
    if (!allowedInCurrentFace(key)) return;
    const face = faceData();
    if (!face.items[key]) return;
    if (input.checked) {
      if (!face.enabled_fields.includes(key)) face.enabled_fields.push(key);
      face.items[key].visible = true;
    } else {
      face.enabled_fields = face.enabled_fields.filter((f) => f !== key);
      face.items[key].visible = false;
    }
    refreshItems();
    syncLayoutInput();
  }));

  document.querySelectorAll('.face-switch').forEach((btn) => btn.addEventListener('click', () => showFace(btn.dataset.face)));

  function bindCanvas(canvasEl) {
    let drag = null;
    canvasEl.addEventListener('pointerdown', (e) => {
      if (canvases[currentFace] !== canvasEl) return;
      const item = e.target.closest('.gafete-item[data-key]');
      if (!item) return;
      const key = item.dataset.key;
      if (!allowedInCurrentFace(key) || !isEnabled(key)) return;
      setActive(key);
      const cfg = getCfg(key);
      const rect = canvasEl.getBoundingClientRect();
      drag = { item, key, pointerId: e.pointerId, sx: e.clientX - rect.left - (cfg.x || 0), sy: e.clientY - rect.top - (cfg.y || 0) };
      item.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    canvasEl.addEventListener('pointermove', (e) => {
      if (!drag || e.pointerId !== drag.pointerId) return;
      const cfg = getCfg(drag.key);
      const rect = canvasEl.getBoundingClientRect();
      cfg.x = Math.max(0, Math.round(e.clientX - rect.left - drag.sx));
      cfg.y = Math.max(0, Math.round(e.clientY - rect.top - drag.sy));
      applyStyle(drag.item, cfg, drag.key);
      hint.textContent = `Cara ${currentFace} · x: ${cfg.x}, y: ${cfg.y}`;
    });
    canvasEl.addEventListener('pointerup', () => { if (drag) { syncLayoutInput(); drag = null; } });
    canvasEl.addEventListener('click', (e) => {
      const item = e.target.closest('.gafete-item[data-key]');
      setActive(item ? item.dataset.key : null);
    });
  }

  [frontCanvas, backCanvas].forEach(bindCanvas);

  function applyTextProps() {
    if (!activeKey || activeKey === 'photo') return;
    const cfg = getCfg(activeKey);
    cfg.color = colorInput.value;
    cfg.font_size = parseInt(sizeInput.value || '24', 10);
    cfg.font_weight = weightInput.value;
    if (activeKey.startsWith('texto_libre_')) cfg.text = textContentInput.value || '';
    refreshItems();
    syncLayoutInput();
  }
  colorInput.addEventListener('input', applyTextProps);
  colorText.addEventListener('input', () => { if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) { colorInput.value = colorText.value; applyTextProps(); } });
  sizeInput.addEventListener('input', applyTextProps);
  weightInput.addEventListener('change', applyTextProps);
  textContentInput?.addEventListener('input', applyTextProps);

  function applyPhotoProps() {
    if (activeKey !== 'photo') return;
    const cfg = getCfg('photo');
    cfg.shape = shapeCircle.checked ? 'circle' : 'rounded';
    cfg.border = !!photoBorder.checked;
    cfg.border_width = parseInt(photoBorderWidth.value || '4', 10);
    cfg.border_color = photoBorderColor.value || '#ffffff';
    cfg.w = parseInt(photoW.value || '250', 10);
    cfg.h = parseInt(photoH.value || '350', 10);
    cfg.radius = parseInt(photoRadius.value || '20', 10);
    refreshItems(); syncLayoutInput();
  }
  [shapeRounded, shapeCircle, photoBorder, photoBorderWidth, photoBorderColor, photoW, photoH, photoRadius].forEach((el) => {
    el.addEventListener('input', applyPhotoProps);
    el.addEventListener('change', applyPhotoProps);
  });

  document.getElementById('reset-layout')?.addEventListener('click', () => {
    Object.assign(layout, JSON.parse(JSON.stringify(defaultLayout)));
    showFace('front');
    refreshItems();
    syncLayoutInput();
  });

  saveForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    syncLayoutInput();
    const res = await fetch(cfg.saveUrl || saveForm.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf, 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({ layout }),
    });
    alert(res.ok ? 'Diseño guardado' : 'No se pudo guardar el diseño');
  });

  refreshItems();
  showFace('front');
  syncLayoutInput();
})();
