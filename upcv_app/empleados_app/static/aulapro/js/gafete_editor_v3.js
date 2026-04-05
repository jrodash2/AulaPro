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
  const layersList = document.getElementById('layers-list');
  const textContentInput = document.getElementById('prop-text-content');
  const propX = document.getElementById('prop-x');
  const propY = document.getElementById('prop-y');
  const propAlign = document.getElementById('prop-align');
  const propEmptyState = document.getElementById('prop-empty-state');
  const propInputs = Array.from(document.querySelectorAll('.prop-input'));

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

  const labelsMap = {
    photo: 'Foto',
    nombres: 'Nombres',
    apellidos: 'Apellidos',
    codigo_alumno: 'Código alumno',
    grado: 'Grado',
    grado_descripcion: 'Descripción grado',
    cui: 'CUI',
    telefono: 'Teléfono',
    establecimiento: 'Establecimiento',
    sitio_web: 'Sitio web',
    texto_libre_1: 'Texto libre 1',
    texto_libre_2: 'Texto libre 2',
    texto_libre_3: 'Texto libre 3',
  };

  const faceData = () => layout[currentFace] || { enabled_fields: [], items: {} };
  const items = () => Array.from(canvases[currentFace].querySelectorAll('.gafete-item[data-key]'));
  const getCfg = (key) => (faceData().items || {})[key];
  const isEnabled = (key) => (faceData().enabled_fields || []).includes(key);

  function allowedInCurrentFace(key) {
    return currentFace === 'front' ? true : BACK_TEXT_KEYS.has(key);
  }

  function syncLayoutInput() { layoutInput.value = JSON.stringify({ layout }); }

  function setPropsEnabled(enabled) {
    propInputs.forEach((el) => { el.disabled = !enabled; });
    if (propEmptyState) propEmptyState.classList.toggle('d-none', enabled);
  }

  function activateTab(tab) {
    document.querySelectorAll('.editor-tab-btn').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
    document.getElementById('tab-layers')?.classList.toggle('d-none', tab !== 'layers');
    document.getElementById('tab-props')?.classList.toggle('d-none', tab !== 'props');
  }

  function showFace(face) {
    currentFace = face === 'back' ? 'back' : 'front';
    frontCanvas.style.display = currentFace === 'front' ? '' : 'none';
    backCanvas.style.display = currentFace === 'back' ? '' : 'none';
    document.querySelectorAll('.face-switch').forEach((b) => b.classList.toggle('active', b.dataset.face === currentFace));
    activeKey = null;
    setActive(null);
    refreshItems();
  }

  function applyStyle(el, itemCfg, key) {
    if (!itemCfg) return;
    const face = faceData();
    el.style.left = `${itemCfg.x || 0}px`;
    el.style.top = `${itemCfg.y || 0}px`;
    el.style.display = (allowedInCurrentFace(key) && isEnabled(key) && itemCfg.visible !== false) ? '' : 'none';
    el.style.zIndex = String(Math.max(5, (face.enabled_fields || []).indexOf(key) + 6));
    if (key === 'photo') {
      el.style.width = `${itemCfg.w || 220}px`;
      el.style.height = `${itemCfg.h || 220}px`;
      el.style.border = itemCfg.border ? `${itemCfg.border_width || 4}px solid ${itemCfg.border_color || '#ffffff'}` : 'none';
      el.style.borderRadius = itemCfg.shape === 'circle' ? '50%' : `${itemCfg.radius || 20}px`;
      return;
    }
    el.style.fontSize = `${itemCfg.font_size || 24}px`;
    el.style.fontWeight = `${itemCfg.font_weight || '400'}`;
    el.style.color = itemCfg.color || '#111111';
    el.style.textAlign = itemCfg.align || 'left';
    if (key.startsWith('texto_libre_') && textContentInput && el.textContent !== itemCfg.text) {
      el.textContent = itemCfg.text || '';
    }
  }

  function renderLayers() {
    if (!layersList) return;
    const face = faceData();
    const enabled = face.enabled_fields || [];
    layersList.innerHTML = '';
    enabled.forEach((key, idx) => {
      const itemCfg = (face.items || {})[key];
      if (!itemCfg || !allowedInCurrentFace(key)) return;
      const row = document.createElement('button');
      row.type = 'button';
      row.className = `layer-item ${activeKey === key ? 'is-active' : ''}`;
      row.dataset.key = key;
      row.innerHTML = `
        <span class="layer-name"><i class="fa ${key === 'photo' ? 'fa-image' : 'fa-font'}"></i>${labelsMap[key] || key}</span>
        <span class="d-flex align-items-center gap-2">
          <small class="layer-meta">#${idx + 1}</small>
          <span class="form-check form-switch m-0">
            <input class="form-check-input layer-visible-toggle" type="checkbox" data-key="${key}" ${itemCfg.visible !== false ? 'checked' : ''}>
          </span>
        </span>
      `;
      layersList.appendChild(row);
    });
  }

  function refreshItems() {
    items().forEach((el) => applyStyle(el, getCfg(el.dataset.key), el.dataset.key));
    renderLayers();
  }

  function setActive(key) {
    activeKey = key;
    items().forEach((el) => el.classList.toggle('is-active', el.dataset.key === key));
    if (!key) {
      activeKeyLabel.textContent = `Elemento activo (${currentFace}): ninguno`;
      textProps.classList.add('d-none');
      photoProps.classList.add('d-none');
      setPropsEnabled(false);
      return;
    }
    const itemCfg = getCfg(key);
    if (!itemCfg) {
      setPropsEnabled(false);
      return;
    }
    setPropsEnabled(true);
    activeKeyLabel.textContent = `Elemento activo (${currentFace}): ${labelsMap[key] || key}`;
    propX.value = itemCfg.x || 0;
    propY.value = itemCfg.y || 0;
    if (key === 'photo' && currentFace === 'front') {
      textProps.classList.add('d-none');
      photoProps.classList.remove('d-none');
      shapeRounded.checked = (itemCfg.shape || 'rounded') === 'rounded';
      shapeCircle.checked = itemCfg.shape === 'circle';
      photoBorder.checked = itemCfg.border !== false;
      photoBorderWidth.value = itemCfg.border_width || 4;
      photoBorderColor.value = itemCfg.border_color || '#ffffff';
      photoW.value = itemCfg.w || 250;
      photoH.value = itemCfg.h || 350;
      photoRadius.value = itemCfg.radius || 20;
      return;
    }

    photoProps.classList.add('d-none');
    textProps.classList.remove('d-none');
    colorInput.value = itemCfg.color || '#111111';
    colorText.value = itemCfg.color || '#111111';
    sizeInput.value = itemCfg.font_size || 24;
    weightInput.value = String(itemCfg.font_weight || '400');
    propAlign.value = itemCfg.align || 'left';
    textContentInput.value = key.startsWith('texto_libre_') ? (itemCfg.text || '') : '';
    textContentInput.disabled = !key.startsWith('texto_libre_');
  }

  layersList?.addEventListener('click', (e) => {
    const toggle = e.target.closest('.layer-visible-toggle');
    if (toggle) {
      const key = toggle.dataset.key;
      const itemCfg = getCfg(key);
      if (!itemCfg) return;
      itemCfg.visible = !!toggle.checked;
      if (itemCfg.visible && !faceData().enabled_fields.includes(key)) faceData().enabled_fields.push(key);
      if (!itemCfg.visible) faceData().enabled_fields = faceData().enabled_fields.filter((f) => f !== key);
      refreshItems();
      syncLayoutInput();
      e.stopPropagation();
      return;
    }
    const row = e.target.closest('.layer-item[data-key]');
    if (!row) return;
    setActive(row.dataset.key);
    activateTab('props');
    renderLayers();
  });

  document.querySelectorAll('.face-switch').forEach((btn) => btn.addEventListener('click', () => showFace(btn.dataset.face)));

  document.querySelectorAll('.editor-tab-btn').forEach((btn) => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));

  function bindCanvas(canvasEl) {
    let drag = null;
    canvasEl.addEventListener('pointerdown', (e) => {
      if (canvases[currentFace] !== canvasEl) return;
      const item = e.target.closest('.gafete-item[data-key]');
      if (!item) return;
      const key = item.dataset.key;
      if (!allowedInCurrentFace(key) || !isEnabled(key)) return;
      setActive(key);
      activateTab('props');
      const itemCfg = getCfg(key);
      const rect = canvasEl.getBoundingClientRect();
      drag = { item, key, pointerId: e.pointerId, sx: e.clientX - rect.left - (itemCfg.x || 0), sy: e.clientY - rect.top - (itemCfg.y || 0) };
      item.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    canvasEl.addEventListener('pointermove', (e) => {
      if (!drag || e.pointerId !== drag.pointerId) return;
      const itemCfg = getCfg(drag.key);
      const rect = canvasEl.getBoundingClientRect();
      itemCfg.x = Math.max(0, Math.round(e.clientX - rect.left - drag.sx));
      itemCfg.y = Math.max(0, Math.round(e.clientY - rect.top - drag.sy));
      applyStyle(drag.item, itemCfg, drag.key);
      if (activeKey === drag.key) {
        propX.value = itemCfg.x;
        propY.value = itemCfg.y;
      }
      hint.textContent = `Cara ${currentFace} · x: ${itemCfg.x}, y: ${itemCfg.y}`;
    });
    canvasEl.addEventListener('pointerup', () => { if (drag) { syncLayoutInput(); drag = null; } });
    canvasEl.addEventListener('click', (e) => {
      const item = e.target.closest('.gafete-item[data-key]');
      setActive(item ? item.dataset.key : null);
      if (item) activateTab('props');
      renderLayers();
    });
  }

  [frontCanvas, backCanvas].forEach(bindCanvas);

  function applyCommonPositionProps() {
    if (!activeKey) return;
    const itemCfg = getCfg(activeKey);
    if (!itemCfg) return;
    itemCfg.x = Number.isFinite(parseInt(propX.value, 10)) ? parseInt(propX.value, 10) : (itemCfg.x || 0);
    itemCfg.y = Number.isFinite(parseInt(propY.value, 10)) ? parseInt(propY.value, 10) : (itemCfg.y || 0);
    refreshItems();
    setActive(activeKey);
    syncLayoutInput();
  }
  [propX, propY].forEach((el) => {
    el?.addEventListener('input', applyCommonPositionProps);
    el?.addEventListener('change', applyCommonPositionProps);
  });

  function applyTextProps() {
    if (!activeKey || activeKey === 'photo') return;
    const itemCfg = getCfg(activeKey);
    if (!itemCfg) return;
    itemCfg.color = colorInput.value;
    itemCfg.font_size = Number.isFinite(parseInt(sizeInput.value, 10)) ? parseInt(sizeInput.value, 10) : (itemCfg.font_size || 24);
    itemCfg.font_weight = weightInput.value;
    itemCfg.align = propAlign.value || 'left';
    if (activeKey.startsWith('texto_libre_')) itemCfg.text = textContentInput.value || '';
    refreshItems();
    setActive(activeKey);
    syncLayoutInput();
  }
  colorInput?.addEventListener('input', applyTextProps);
  colorText?.addEventListener('input', () => { if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) { colorInput.value = colorText.value; applyTextProps(); } });
  sizeInput?.addEventListener('input', applyTextProps);
  weightInput?.addEventListener('change', applyTextProps);
  textContentInput?.addEventListener('input', applyTextProps);
  propAlign?.addEventListener('change', applyTextProps);

  function applyPhotoProps() {
    if (activeKey !== 'photo') return;
    const itemCfg = getCfg('photo');
    if (!itemCfg) return;
    itemCfg.shape = shapeCircle.checked ? 'circle' : 'rounded';
    itemCfg.border = !!photoBorder.checked;
    itemCfg.border_width = Number.isFinite(parseInt(photoBorderWidth.value, 10)) ? parseInt(photoBorderWidth.value, 10) : (itemCfg.border_width || 4);
    itemCfg.border_color = photoBorderColor.value || '#ffffff';
    itemCfg.w = Number.isFinite(parseInt(photoW.value, 10)) ? parseInt(photoW.value, 10) : (itemCfg.w || 250);
    itemCfg.h = Number.isFinite(parseInt(photoH.value, 10)) ? parseInt(photoH.value, 10) : (itemCfg.h || 350);
    itemCfg.radius = Number.isFinite(parseInt(photoRadius.value, 10)) ? parseInt(photoRadius.value, 10) : (itemCfg.radius || 20);
    refreshItems();
    setActive(activeKey);
    syncLayoutInput();
  }
  [shapeRounded, shapeCircle, photoBorder, photoBorderWidth, photoBorderColor, photoW, photoH, photoRadius].forEach((el) => {
    el?.addEventListener('input', applyPhotoProps);
    el?.addEventListener('change', applyPhotoProps);
  });

  document.getElementById('reset-layout')?.addEventListener('click', () => {
    Object.assign(layout, JSON.parse(JSON.stringify(defaultLayout)));
    showFace('front');
    refreshItems();
    syncLayoutInput();
  });
  document.getElementById('reset-layout-top')?.addEventListener('click', () => document.getElementById('reset-layout')?.click());

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

  activateTab('layers');
  refreshItems();
  showFace('front');
  setPropsEnabled(false);
  syncLayoutInput();
})();
