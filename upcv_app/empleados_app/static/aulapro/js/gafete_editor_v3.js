(function () {
  const cfg = window.gafeteEditorSimple || {};
  console.log('✅ editor gafete js loaded v3');

  const canvas = document.getElementById('editorCanvas');
  const layoutInput = document.getElementById('layout_json');
  const saveForm = document.getElementById('editorForm');
  const saveBtn = document.getElementById('btnGuardar') || document.querySelector('#editorForm button[type="submit"]');
  const scaleWrapper = document.getElementById('gafete-scale-wrapper');
  const items = () => Array.from(document.querySelectorAll('#editorCanvas .gafete-item[data-key]'));

  console.log({ canvas, layoutInput, saveBtn, items: document.querySelectorAll('.gafete-item').length });
  if (!canvas || !layoutInput) return;

  const activeKeyLabel = document.getElementById('active-key');
  const hint = document.getElementById('coords-hint');
  const checklist = document.getElementById('enabled-fields-checklist');

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

  function parseLayout() {
    try {
      const raw = document.getElementById('layout-data')?.textContent?.trim();
      if (raw) return JSON.parse(raw);
    } catch (e) {
      console.error('layout-data parse error', e);
    }
    try {
      const v = layoutInput.value?.trim();
      if (v) {
        const data = JSON.parse(v);
        return data.layout || data;
      }
    } catch (e) {
      console.error('layout_json parse error', e);
    }
    return { canvas: { width: 1011, height: 639, orientation: 'H' }, enabled_fields: [], items: {} };
  }

  function parseDefaultLayout() {
    try {
      const raw = document.getElementById('default-layout-data')?.textContent?.trim();
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  const layout = parseLayout();
  const defaultLayout = parseDefaultLayout();
  if (!layout.items || typeof layout.items !== 'object') layout.items = {};
  if (!Array.isArray(layout.enabled_fields)) layout.enabled_fields = Object.keys(layout.items);

  function syncLayoutInput() {
    layoutInput.value = JSON.stringify({ layout });
  }

  function getItemCfg(key) {
    return layout.items && layout.items[key] ? layout.items[key] : null;
  }

  function isEnabled(key) {
    return Array.isArray(layout.enabled_fields) && layout.enabled_fields.includes(key);
  }

  function applyStyle(el, cfgItem, key) {
    el.style.left = `${cfgItem.x || 0}px`;
    el.style.top = `${cfgItem.y || 0}px`;
    el.style.display = isEnabled(key) && cfgItem.visible !== false ? '' : 'none';

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

  function refreshItems() {
    items().forEach((el) => {
      const key = el.dataset.key;
      const cfgItem = getItemCfg(key);
      if (cfgItem) applyStyle(el, cfgItem, key);
    });
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

  let activeKey = null;
  function setActive(key) {
    activeKey = key;
    items().forEach((el) => el.classList.toggle('is-active', el.dataset.key === key));

    if (!key) {
      activeKeyLabel.textContent = 'Elemento activo: ninguno';
      textProps.classList.add('d-none');
      photoProps.classList.add('d-none');
      return;
    }

    const cfgItem = getItemCfg(key);
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

  function bindFieldToggles() {
    checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      input.addEventListener('change', () => {
        const key = input.dataset.field;
        const cfgItem = getItemCfg(key);
        if (!cfgItem) return;

        if (input.checked) {
          if (!layout.enabled_fields.includes(key)) layout.enabled_fields.push(key);
          cfgItem.visible = true;
        } else {
          layout.enabled_fields = layout.enabled_fields.filter((f) => f !== key);
          cfgItem.visible = false;
        }

        const el = canvas.querySelector(`.gafete-item[data-key="${key}"]`);
        if (el) applyStyle(el, cfgItem, key);
        syncLayoutInput();
      });
    });
  }

  function applyTextProps() {
    if (!activeKey || activeKey === 'photo') return;
    const cfgItem = getItemCfg(activeKey);
    const el = canvas.querySelector(`.gafete-item[data-key="${activeKey}"]`);
    if (!cfgItem || !el) return;

    cfgItem.color = colorInput.value;
    cfgItem.font_size = parseInt(sizeInput.value || '24', 10);
    cfgItem.font_weight = weightInput.value;
    applyStyle(el, cfgItem, activeKey);
    colorText.value = cfgItem.color;
    syncLayoutInput();
  }

  function applyPhotoProps() {
    if (activeKey !== 'photo') return;
    const cfgItem = getItemCfg('photo');
    const el = canvas.querySelector('.gafete-item[data-key="photo"]');
    if (!cfgItem || !el) return;

    cfgItem.shape = shapeCircle.checked ? 'circle' : 'rounded';
    cfgItem.border = !!photoBorder.checked;
    cfgItem.border_width = parseInt(photoBorderWidth.value || '4', 10);
    cfgItem.border_color = photoBorderColor.value || '#ffffff';
    cfgItem.w = parseInt(photoW.value || '250', 10);
    cfgItem.h = parseInt(photoH.value || '350', 10);
    cfgItem.radius = parseInt(photoRadius.value || '20', 10);
    applyStyle(el, cfgItem, 'photo');
    syncLayoutInput();
  }

  let drag = null;
  function getScale() {
    const rect = canvas.getBoundingClientRect();
    return {
      x: rect.width / (layout.canvas?.width || rect.width || 1),
      y: rect.height / (layout.canvas?.height || rect.height || 1),
      rect,
    };
  }

  canvas.addEventListener('pointerdown', (e) => {
    const item = e.target.closest('.gafete-item[data-key]');
    if (!item || !canvas.contains(item)) return;
    const key = item.dataset.key;
    if (!isEnabled(key)) return;

    setActive(key);
    const cfgItem = getItemCfg(key);
    if (!cfgItem) return;

    const { x, y, rect } = getScale();
    drag = {
      key,
      item,
      pointerId: e.pointerId,
      startX: (e.clientX - rect.left) / x,
      startY: (e.clientY - rect.top) / y,
      origX: parseFloat(cfgItem.x || 0),
      origY: parseFloat(cfgItem.y || 0),
      moved: false,
      scaleX: x,
      scaleY: y,
    };

    item.classList.add('dragging');
    item.setPointerCapture(e.pointerId);
    e.preventDefault();
  });

  canvas.addEventListener('pointermove', (e) => {
    if (!drag || e.pointerId !== drag.pointerId) return;
    const cfgItem = getItemCfg(drag.key);
    if (!cfgItem) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / drag.scaleX;
    const y = (e.clientY - rect.top) / drag.scaleY;
    const dx = x - drag.startX;
    const dy = y - drag.startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) drag.moved = true;

    const w = drag.key === 'photo' ? (cfgItem.w || drag.item.offsetWidth) : drag.item.offsetWidth;
    const h = drag.key === 'photo' ? (cfgItem.h || drag.item.offsetHeight) : drag.item.offsetHeight;
    const maxX = Math.max(0, (layout.canvas?.width || rect.width) - w);
    const maxY = Math.max(0, (layout.canvas?.height || rect.height) - h);
    const nextX = Math.max(0, Math.min(maxX, Math.round(drag.origX + dx)));
    const nextY = Math.max(0, Math.min(maxY, Math.round(drag.origY + dy)));

    cfgItem.x = nextX;
    cfgItem.y = nextY;
    drag.item.style.left = `${nextX}px`;
    drag.item.style.top = `${nextY}px`;
    hint.textContent = `x: ${nextX}, y: ${nextY}`;
  });

  function stopDrag(e) {
    if (!drag || (e && e.pointerId !== drag.pointerId)) return;
    const d = drag;
    d.item.classList.remove('dragging');
    try { if (d.item.hasPointerCapture(d.pointerId)) d.item.releasePointerCapture(d.pointerId); } catch (_) {}
    syncLayoutInput();
    drag = null;
  }

  canvas.addEventListener('pointerup', stopDrag);
  canvas.addEventListener('pointercancel', stopDrag);

  canvas.addEventListener('click', (e) => {
    if (drag && drag.moved) return;
    const item = e.target.closest('.gafete-item[data-key]');
    setActive(item ? item.dataset.key : null);
  });

  colorInput.addEventListener('input', applyTextProps);
  colorText.addEventListener('input', () => {
    if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) {
      colorInput.value = colorText.value;
      applyTextProps();
    }
  });
  sizeInput.addEventListener('input', applyTextProps);
  weightInput.addEventListener('change', applyTextProps);
  [shapeRounded, shapeCircle, photoBorder, photoBorderWidth, photoBorderColor, photoW, photoH, photoRadius].forEach((el) => {
    el.addEventListener('input', applyPhotoProps);
    el.addEventListener('change', applyPhotoProps);
  });

  document.getElementById('refresh-size')?.addEventListener('click', fitScale);
  document.getElementById('reset-layout')?.addEventListener('click', () => {
    if (!defaultLayout) return;
    layout.canvas = JSON.parse(JSON.stringify(defaultLayout.canvas || layout.canvas));
    layout.enabled_fields = JSON.parse(JSON.stringify(defaultLayout.enabled_fields || []));
    layout.items = JSON.parse(JSON.stringify(defaultLayout.items || {}));
    refreshItems();

    checklist.querySelectorAll('.field-toggle[data-field]').forEach((input) => {
      const cfgItem = getItemCfg(input.dataset.field);
      input.checked = !!cfgItem && isEnabled(input.dataset.field) && cfgItem.visible !== false;
    });

    setActive(null);
    fitScale();
    syncLayoutInput();
    hint.textContent = 'Restablecido a valores por defecto';
  });

  if (saveForm) {
    saveForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      syncLayoutInput();
      saveBtn && (saveBtn.disabled = true);
      try {
        const res = await fetch(cfg.saveUrl || saveForm.action, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': cfg.csrf || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: JSON.stringify({ layout }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        alert('Diseño guardado');
      } catch (err) {
        console.error('save error', err);
        alert('No se pudo guardar el diseño');
      } finally {
        saveBtn && (saveBtn.disabled = false);
      }
    });
  }

  bindFieldToggles();
  refreshItems();
  fitScale();
  syncLayoutInput();
  setActive(null);
  window.addEventListener('resize', fitScale);
})();
