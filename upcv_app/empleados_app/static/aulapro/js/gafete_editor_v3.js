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
  const layersList = document.getElementById('layers-list');
  const textContentInput = document.getElementById('prop-text-content');
  const propX = document.getElementById('prop-x');
  const propY = document.getElementById('prop-y');
  const propVisible = document.getElementById('prop-visible');
  const propAlign = document.getElementById('prop-align');

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

  const labelsMap = {};
  checklist?.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
    const lbl = input.closest('.form-check')?.querySelector('label');
    labelsMap[input.dataset.field] = lbl ? lbl.textContent.trim() : input.dataset.field;
  });

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

  function refreshChecklist() {
    checklist?.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      const key = input.dataset.field;
      const itemCfg = getCfg(key);
      input.checked = !!itemCfg && isEnabled(key) && itemCfg.visible !== false;
      input.closest('.form-check').style.display = allowedInCurrentFace(key) ? '' : 'none';
    });
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
      return;
    }
    const itemCfg = getCfg(key);
    activeKeyLabel.textContent = `Elemento activo (${currentFace}): ${labelsMap[key] || key}`;
    propX.value = itemCfg.x || 0;
    propY.value = itemCfg.y || 0;
    propVisible.checked = itemCfg.visible !== false;

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

  checklist?.querySelectorAll('.field-toggle[data-field]').forEach((input) => input.addEventListener('change', () => {
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

  layersList?.addEventListener('click', (e) => {
    const toggle = e.target.closest('.layer-visible-toggle');
    if (toggle) {
      const key = toggle.dataset.key;
      const itemCfg = getCfg(key);
      if (!itemCfg) return;
      itemCfg.visible = !!toggle.checked;
      if (itemCfg.visible && !faceData().enabled_fields.includes(key)) faceData().enabled_fields.push(key);
      if (!itemCfg.visible) faceData().enabled_fields = faceData().enabled_fields.filter((f) => f !== key);
      refreshChecklist();
      refreshItems();
      syncLayoutInput();
      e.stopPropagation();
      return;
    }
    const row = e.target.closest('.layer-item[data-key]');
    if (!row) return;
    setActive(row.dataset.key);
    renderLayers();
  });

  document.querySelectorAll('.face-switch').forEach((btn) => btn.addEventListener('click', () => showFace(btn.dataset.face)));

  document.querySelectorAll('.editor-tab-btn').forEach((btn) => btn.addEventListener('click', () => {
    document.querySelectorAll('.editor-tab-btn').forEach((b) => b.classList.toggle('active', b === btn));
    document.getElementById('tab-layers')?.classList.toggle('d-none', btn.dataset.tab !== 'layers');
    document.getElementById('tab-props')?.classList.toggle('d-none', btn.dataset.tab !== 'props');
  }));

  function bindCanvas(canvasEl) {
    let drag = null;
    canvasEl.addEventListener('pointerdown', (e) => {
      if (canvases[currentFace] !== canvasEl) return;
      const item = e.target.closest('.gafete-item[data-key]');
      if (!item) return;
      const key = item.dataset.key;
      if (!allowedInCurrentFace(key) || !isEnabled(key)) return;
      setActive(key);
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
      renderLayers();
    });
  }

  [frontCanvas, backCanvas].forEach(bindCanvas);

  function applyCommonPositionProps() {
    if (!activeKey) return;
    const itemCfg = getCfg(activeKey);
    itemCfg.x = parseInt(propX.value || '0', 10);
    itemCfg.y = parseInt(propY.value || '0', 10);
    itemCfg.visible = !!propVisible.checked;
    refreshItems();
    syncLayoutInput();
  }
  [propX, propY, propVisible].forEach((el) => {
    el?.addEventListener('input', applyCommonPositionProps);
    el?.addEventListener('change', applyCommonPositionProps);
  });

  function applyTextProps() {
    if (!activeKey || activeKey === 'photo') return;
    const itemCfg = getCfg(activeKey);
    itemCfg.color = colorInput.value;
    itemCfg.font_size = parseInt(sizeInput.value || '24', 10);
    itemCfg.font_weight = weightInput.value;
    itemCfg.align = propAlign.value || 'left';
    itemCfg.visible = !!propVisible.checked;
    if (activeKey.startsWith('texto_libre_')) itemCfg.text = textContentInput.value || '';
    refreshItems();
    syncLayoutInput();
  }
  colorInput.addEventListener('input', applyTextProps);
  colorText.addEventListener('input', () => { if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) { colorInput.value = colorText.value; applyTextProps(); } });
  sizeInput.addEventListener('input', applyTextProps);
  weightInput.addEventListener('change', applyTextProps);
  textContentInput?.addEventListener('input', applyTextProps);
  propAlign?.addEventListener('change', applyTextProps);

  function applyPhotoProps() {
    if (activeKey !== 'photo') return;
    const itemCfg = getCfg('photo');
    itemCfg.shape = shapeCircle.checked ? 'circle' : 'rounded';
    itemCfg.border = !!photoBorder.checked;
    itemCfg.border_width = parseInt(photoBorderWidth.value || '4', 10);
    itemCfg.border_color = photoBorderColor.value || '#ffffff';
    itemCfg.w = parseInt(photoW.value || '250', 10);
    itemCfg.h = parseInt(photoH.value || '350', 10);
    itemCfg.radius = parseInt(photoRadius.value || '20', 10);
    itemCfg.visible = !!propVisible.checked;
    refreshItems();
    syncLayoutInput();
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

  refreshItems();
  showFace('front');
  syncLayoutInput();
})();
