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
  const propW = document.getElementById('prop-w');
  const propH = document.getElementById('prop-h');
  const propAlign = document.getElementById('prop-align');
  const propEmptyState = document.getElementById('prop-empty-state');
  const propInputs = Array.from(document.querySelectorAll('.prop-input'));

  const colorInput = document.getElementById('prop-color');
  const colorText = document.getElementById('prop-color-text');
  const sizeInput = document.getElementById('prop-size');
  const weightInput = document.getElementById('prop-weight');
  const textProps = document.getElementById('text-props');
  const photoProps = document.getElementById('photo-props');
  const imageProps = document.getElementById('image-props');
  const imageFit = document.getElementById('image-fit');
  const imageSrc = document.getElementById('image-src');
  const addTextBtn = document.getElementById('add-text-btn');
  const addImageBtn = document.getElementById('add-image-btn');
  const addImageInput = document.getElementById('add-image-input');
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
    image: 'Imagen',
  };

  const faceData = () => layout[currentFace] || { enabled_fields: [], items: {} };
  const items = () => Array.from(canvases[currentFace].querySelectorAll('.gafete-item[data-key]'));
  const getCfg = (key) => (faceData().items || {})[key];
  const isEnabled = (key) => (faceData().enabled_fields || []).includes(key);
  const isTextKey = (key) => key && key !== 'photo' && !key.startsWith('image');
  const isImageKey = (key) => key && key.startsWith('image');
  const isCustomTextKey = (key) => key && key.startsWith('texto_libre_');
  const isPlaceholder = (key) => ['texto_libre_1', 'texto_libre_2', 'texto_libre_3', 'image'].includes(key);

  function labelForKey(key) {
    if (labelsMap[key]) return labelsMap[key];
    if (key.startsWith('texto_libre_')) return `Texto ${key.replace('texto_libre_', '')}`;
    if (key.startsWith('image')) return `Imagen ${key.replace('image_', '') || ''}`.trim();
    return key;
  }

  function allowedInCurrentFace(key) {
    if (currentFace === 'front') return true;
    if (isCustomTextKey(key) || isImageKey(key)) return true;
    return BACK_TEXT_KEYS.has(key);
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
    if (isImageKey(key)) {
      el.style.width = `${itemCfg.w || 220}px`;
      el.style.height = `${itemCfg.h || 220}px`;
      el.style.objectFit = itemCfg.object_fit || 'contain';
      return;
    }
    if (key === 'photo') {
      el.style.width = `${itemCfg.w || 220}px`;
      el.style.height = `${itemCfg.h || 220}px`;
      el.style.border = itemCfg.border ? `${itemCfg.border_width || 4}px solid ${itemCfg.border_color || '#ffffff'}` : 'none';
      el.style.borderRadius = itemCfg.shape === 'circle' ? '50%' : `${itemCfg.radius || 20}px`;
      return;
    }
    if (itemCfg.w != null) {
      el.style.width = `${itemCfg.w}px`;
      el.style.whiteSpace = 'normal';
      el.style.overflow = 'hidden';
    } else {
      el.style.width = key === 'grado' ? '470px' : '';
      el.style.whiteSpace = key === 'grado' ? 'normal' : 'nowrap';
      el.style.overflow = key === 'grado' ? 'hidden' : '';
    }
    if (itemCfg.h != null) el.style.height = `${itemCfg.h}px`; else el.style.height = '';
    el.style.fontSize = `${itemCfg.font_size || 24}px`;
    el.style.fontWeight = `${itemCfg.font_weight || '400'}`;
    el.style.color = itemCfg.color || '#111111';
    el.style.textAlign = itemCfg.align || (key === 'grado' ? 'center' : 'left');
    if (isCustomTextKey(key) && textContentInput && el.textContent !== itemCfg.text) {
      el.textContent = itemCfg.text || '';
    }
  }

  function renderLayers() {
    if (!layersList) return;
    const face = faceData();
    const enabled = face.enabled_fields || [];
    const allKeys = Object.keys(face.items || {}).filter((key) => {
      if (!allowedInCurrentFace(key)) return false;
      const cfg = face.items[key] || {};
      if (!isPlaceholder(key)) return true;
      if ((face.enabled_fields || []).includes(key)) return true;
      if (key.startsWith('texto_libre_')) return !!(cfg.text || '').trim();
      if (key.startsWith('image')) return !!cfg.src;
      return false;
    });
    const orderedKeys = [
      ...enabled.filter((key) => allKeys.includes(key)),
      ...allKeys.filter((key) => !enabled.includes(key)),
    ];
    layersList.innerHTML = '';
    orderedKeys.forEach((key, idx) => {
      const itemCfg = (face.items || {})[key];
      if (!itemCfg) return;
      const isVisible = enabled.includes(key) && itemCfg.visible !== false;
      const row = document.createElement('button');
      row.type = 'button';
      row.className = `layer-item ${activeKey === key ? 'is-active' : ''} ${isVisible ? '' : 'is-hidden'}`;
      row.dataset.key = key;
      row.innerHTML = `
        <span class="layer-name"><i class="fa ${isVisible ? 'fa-eye text-success' : 'fa-eye-slash text-muted'}"></i>${labelForKey(key)}</span>
        <span class="d-flex align-items-center gap-2">
          <small class="layer-meta">${isVisible ? 'Visible' : 'Oculto'}</small>
          <span class="form-check form-switch m-0">
            <input class="form-check-input layer-visible-toggle" type="checkbox" data-key="${key}" ${isVisible ? 'checked' : ''}>
          </span>
        </span>
      `;
      layersList.appendChild(row);
    });
  }

  function refreshItems() {
    syncCanvasNodes();
    items().forEach((el) => applyStyle(el, getCfg(el.dataset.key), el.dataset.key));
    renderLayers();
    ensureResizeHandle();
  }

  function syncCanvasNodes() {
    const canvas = canvases[currentFace];
    const faceItems = faceData().items || {};
    const existing = new Set(items().map((el) => el.dataset.key));
    Object.entries(faceItems).forEach(([key, cfg]) => {
      if (existing.has(key)) return;
      if (!allowedInCurrentFace(key)) return;
      if (!isCustomTextKey(key) && !isImageKey(key)) return;
      createCanvasItem(key, cfg);
    });
    items().forEach((el) => {
      if (!faceItems[el.dataset.key]) el.remove();
    });
  }

  function ensureEnabled(key) {
    const face = faceData();
    if (!face.enabled_fields.includes(key)) face.enabled_fields.push(key);
  }

  function nextKey(prefix) {
    const used = new Set(Object.keys(faceData().items || {}));
    let idx = 1;
    while (used.has(`${prefix}_${idx}`)) idx += 1;
    return `${prefix}_${idx}`;
  }

  function createCanvasItem(key, itemCfg) {
    const canvas = canvases[currentFace];
    const el = isImageKey(key) ? document.createElement('img') : document.createElement('div');
    el.className = `gafete-item ${isImageKey(key) ? 'free-image' : 'free-text'}`;
    if (!isImageKey(key)) el.textContent = itemCfg.text || '';
    if (isImageKey(key)) {
      el.src = itemCfg.src || '';
      el.alt = labelForKey(key);
    }
    el.dataset.key = key;
    canvas.appendChild(el);
    return el;
  }

  function ensureResizeHandle() {
    document.querySelectorAll('.resize-handle').forEach((h) => h.remove());
    if (!activeKey || activeKey === 'photo') return;
    const target = canvases[currentFace].querySelector(`.gafete-item[data-key="${activeKey}"]`);
    if (!target) return;
    const handle = document.createElement('span');
    handle.className = 'resize-handle';
    handle.dataset.resizeKey = activeKey;
    target.appendChild(handle);
  }

  function setActive(key) {
    activeKey = key;
    items().forEach((el) => el.classList.toggle('is-active', el.dataset.key === key));
    ensureResizeHandle();
    if (!key) {
      activeKeyLabel.textContent = `Elemento activo (${currentFace}): ninguno`;
      textProps.classList.add('d-none');
      photoProps.classList.add('d-none');
      imageProps.classList.add('d-none');
      setPropsEnabled(false);
      return;
    }
    const itemCfg = getCfg(key);
    if (!itemCfg) {
      setPropsEnabled(false);
      return;
    }
    setPropsEnabled(true);
    activeKeyLabel.textContent = `Elemento activo (${currentFace}): ${labelForKey(key)}`;
    propX.value = itemCfg.x || 0;
    propY.value = itemCfg.y || 0;
    propW.value = itemCfg.w || (key === 'photo' ? 250 : '');
    propH.value = itemCfg.h || (key === 'photo' ? 350 : '');
    if (key === 'photo' && currentFace === 'front') {
      textProps.classList.add('d-none');
      photoProps.classList.remove('d-none');
      imageProps.classList.add('d-none');
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

    if (isImageKey(key)) {
      photoProps.classList.add('d-none');
      textProps.classList.add('d-none');
      imageProps.classList.remove('d-none');
      imageFit.value = itemCfg.object_fit || 'contain';
      imageSrc.value = itemCfg.src || '';
      return;
    }

    photoProps.classList.add('d-none');
    imageProps.classList.add('d-none');
    textProps.classList.remove('d-none');
    colorInput.value = itemCfg.color || '#111111';
    colorText.value = itemCfg.color || '#111111';
    sizeInput.value = itemCfg.font_size || 24;
    weightInput.value = String(itemCfg.font_weight || '400');
    propAlign.value = itemCfg.align || (key === 'grado' ? 'center' : 'left');
    textContentInput.value = isCustomTextKey(key) ? (itemCfg.text || '') : '';
    textContentInput.disabled = !isCustomTextKey(key);
  }

  layersList?.addEventListener('click', (e) => {
    const toggle = e.target.closest('.layer-visible-toggle');
    if (toggle) {
      const key = toggle.dataset.key;
      const itemCfg = getCfg(key);
      if (!itemCfg) return;
      itemCfg.visible = !!toggle.checked;
      if (itemCfg.visible) ensureEnabled(key);
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
    let resize = null;
    canvasEl.addEventListener('pointerdown', (e) => {
      if (canvases[currentFace] !== canvasEl) return;
      const handle = e.target.closest('.resize-handle');
      if (handle) {
        const key = handle.dataset.resizeKey;
        const itemCfg = getCfg(key);
        const item = canvasEl.querySelector(`.gafete-item[data-key="${key}"]`);
        if (!item || !itemCfg) return;
        setActive(key);
        resize = {
          key,
          item,
          pointerId: e.pointerId,
          startW: itemCfg.w || item.offsetWidth || 120,
          startH: itemCfg.h || item.offsetHeight || 60,
          sx: e.clientX,
          sy: e.clientY,
        };
        handle.setPointerCapture(e.pointerId);
        e.preventDefault();
        return;
      }
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
      if (resize && e.pointerId === resize.pointerId) {
        const itemCfg = getCfg(resize.key);
        if (!itemCfg) return;
        const dw = Math.round(e.clientX - resize.sx);
        const dh = Math.round(e.clientY - resize.sy);
        itemCfg.w = Math.max(40, resize.startW + dw);
        itemCfg.h = Math.max(30, resize.startH + dh);
        applyStyle(resize.item, itemCfg, resize.key);
        if (activeKey === resize.key) {
          propW.value = itemCfg.w;
          propH.value = itemCfg.h;
        }
        hint.textContent = `Cara ${currentFace} · w: ${itemCfg.w}, h: ${itemCfg.h}`;
        return;
      }
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
    canvasEl.addEventListener('pointerup', (e) => {
      if (resize && e.pointerId === resize.pointerId) {
        syncLayoutInput();
        resize = null;
      }
      if (drag) {
        syncLayoutInput();
        drag = null;
      }
    });
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
    const newW = parseInt(propW.value, 10);
    const newH = parseInt(propH.value, 10);
    if (Number.isFinite(newW)) itemCfg.w = Math.max(40, newW);
    else if (activeKey === 'photo' || isImageKey(activeKey) || itemCfg.w != null) itemCfg.w = itemCfg.w || (activeKey === 'photo' ? 250 : 220);
    else delete itemCfg.w;
    if (Number.isFinite(newH)) itemCfg.h = Math.max(30, newH);
    else if (activeKey === 'photo' || isImageKey(activeKey) || itemCfg.h != null) itemCfg.h = itemCfg.h || (activeKey === 'photo' ? 350 : 220);
    else delete itemCfg.h;
    refreshItems();
    setActive(activeKey);
    syncLayoutInput();
  }
  [propX, propY, propW, propH].forEach((el) => {
    el?.addEventListener('input', applyCommonPositionProps);
    el?.addEventListener('change', applyCommonPositionProps);
  });

  function applyTextProps() {
    if (!activeKey || activeKey === 'photo' || isImageKey(activeKey)) return;
    const itemCfg = getCfg(activeKey);
    if (!itemCfg) return;
    itemCfg.color = colorInput.value;
    itemCfg.font_size = Number.isFinite(parseInt(sizeInput.value, 10)) ? parseInt(sizeInput.value, 10) : (itemCfg.font_size || 24);
    itemCfg.font_weight = weightInput.value;
    itemCfg.align = propAlign.value || (activeKey === 'grado' ? 'center' : 'left');
    if (isCustomTextKey(activeKey)) itemCfg.text = textContentInput.value || '';
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

  function applyImageProps() {
    if (!activeKey || !isImageKey(activeKey)) return;
    const itemCfg = getCfg(activeKey);
    if (!itemCfg) return;
    itemCfg.object_fit = imageFit.value || 'contain';
    refreshItems();
    setActive(activeKey);
    syncLayoutInput();
  }
  imageFit?.addEventListener('change', applyImageProps);

  addTextBtn?.addEventListener('click', () => {
    const key = nextKey('texto_libre');
    const face = faceData();
    face.items[key] = {
      x: 120, y: 120, w: 320, h: 80, font_size: 26, font_weight: '400', color: '#111111', align: 'left', visible: true, text: 'Nuevo texto',
    };
    labelsMap[key] = `Texto libre ${key.replace('texto_libre_', '')}`;
    ensureEnabled(key);
    createCanvasItem(key, face.items[key]);
    refreshItems();
    setActive(key);
    activateTab('props');
    syncLayoutInput();
  });

  addImageBtn?.addEventListener('click', () => addImageInput?.click());

  addImageInput?.addEventListener('change', async () => {
    const file = addImageInput.files?.[0];
    if (!file) return;
    if (!/^image\/(png|jpe?g|webp|svg\+xml)$/i.test(file.type)) {
      alert('Formato no permitido. Use PNG, JPG, WEBP o SVG.');
      addImageInput.value = '';
      return;
    }
    const formData = new FormData();
    formData.append('image', file);
    const res = await fetch(cfg.uploadUrl, {
      method: 'POST',
      headers: { 'X-CSRFToken': cfg.csrf, 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok || !data.url) {
      alert(data.error || 'No se pudo subir la imagen.');
      addImageInput.value = '';
      return;
    }
    const key = nextKey('image');
    const face = faceData();
    face.items[key] = {
      x: 80, y: 80, w: 220, h: 220, src: data.url, object_fit: 'contain', visible: true,
    };
    labelsMap[key] = `Imagen ${key.replace('image_', '')}`;
    ensureEnabled(key);
    createCanvasItem(key, face.items[key]);
    refreshItems();
    setActive(key);
    activateTab('props');
    syncLayoutInput();
    addImageInput.value = '';
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
