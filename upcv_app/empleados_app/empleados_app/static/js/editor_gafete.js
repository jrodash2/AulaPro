(function () {
  const cfg = window.gafeteEditorData;
  if (!cfg) return;

  const canvas = document.getElementById('editor-canvas');
  if (!canvas) return;

  const select = document.getElementById('field-select');
  const labelInput = document.getElementById('field-label');
  const classInput = document.getElementById('field-class');
  const sizeInput = document.getElementById('field-size');
  const weightInput = document.getElementById('field-weight');
  const alignInput = document.getElementById('field-align');
  const visibleInput = document.getElementById('field-visible');
  const colorPicker = document.getElementById('field-color-picker');
  const colorText = document.getElementById('field-color-text');
  const coords = document.getElementById('field-coords');

  let layout = cfg.layout || { canvas: { width: 880, height: 565 }, fields: [] };
  const defaultLayout = cfg.defaultLayout || layout;
  let activeKey = null;

  function getField(key) {
    return layout.fields.find((f) => f.key === key);
  }

  function fieldElement(key) {
    return canvas.querySelector('.gafete-field[data-key="' + key + '"]');
  }

  function applyFieldStyle(el, field) {
    el.style.left = `${field.x || 0}px`;
    el.style.top = `${field.y || 0}px`;
    el.style.fontSize = `${field.font_size || 24}px`;
    el.style.fontWeight = `${field.font_weight || '400'}`;
    el.style.color = field.color || '#111111';
    el.style.textAlign = field.align || 'left';
    el.style.display = field.visible === false ? 'none' : 'block';
    el.className = `gafete-field ${field.class_css || ''}`.trim();
  }

  function updateToolbox() {
    if (!activeKey) return;
    const field = getField(activeKey);
    if (!field) return;
    labelInput.value = field.label || field.key;
    classInput.value = field.class_css || '';
    sizeInput.value = field.font_size || 24;
    weightInput.value = String(field.font_weight || '400');
    alignInput.value = field.align || 'left';
    visibleInput.value = field.visible === false ? 'false' : 'true';
    colorPicker.value = field.color || '#111111';
    colorText.value = field.color || '#111111';
    coords.textContent = `x:${field.x || 0} y:${field.y || 0}`;
  }

  function bindDrag(el, field) {
    let dragging = false;
    let offsetX = 0;
    let offsetY = 0;

    el.addEventListener('mousedown', function (ev) {
      dragging = true;
      activeKey = field.key;
      select.value = field.key;
      updateToolbox();
      const rect = canvas.getBoundingClientRect();
      offsetX = ev.clientX - rect.left - (field.x || 0);
      offsetY = ev.clientY - rect.top - (field.y || 0);
      ev.preventDefault();
    });

    document.addEventListener('mousemove', function (ev) {
      if (!dragging) return;
      const rect = canvas.getBoundingClientRect();
      field.x = Math.round(ev.clientX - rect.left - offsetX);
      field.y = Math.round(ev.clientY - rect.top - offsetY);
      applyFieldStyle(el, field);
      coords.textContent = `x:${field.x} y:${field.y}`;
    });

    document.addEventListener('mouseup', function () {
      dragging = false;
    });
  }

  layout.fields.forEach((field) => {
    const opt = document.createElement('option');
    opt.value = field.key;
    opt.textContent = field.label || field.key;
    select.appendChild(opt);

    const el = fieldElement(field.key);
    if (el) {
      applyFieldStyle(el, field);
      bindDrag(el, field);
      el.addEventListener('click', function () {
        activeKey = field.key;
        select.value = field.key;
        updateToolbox();
      });
    }
  });

  activeKey = layout.fields.length ? layout.fields[0].key : null;
  if (activeKey) {
    select.value = activeKey;
    updateToolbox();
  }

  select.addEventListener('change', function () {
    activeKey = this.value;
    updateToolbox();
  });

  function patchActive(mutator) {
    if (!activeKey) return;
    const field = getField(activeKey);
    if (!field) return;
    mutator(field);
    const el = fieldElement(activeKey);
    if (el) applyFieldStyle(el, field);
    updateToolbox();
  }

  classInput.addEventListener('input', () => patchActive((f) => (f.class_css = classInput.value.trim())));
  sizeInput.addEventListener('input', () => patchActive((f) => (f.font_size = parseInt(sizeInput.value || '24', 10))));
  weightInput.addEventListener('change', () => patchActive((f) => (f.font_weight = weightInput.value)));
  alignInput.addEventListener('change', () => patchActive((f) => (f.align = alignInput.value)));
  visibleInput.addEventListener('change', () => patchActive((f) => (f.visible = visibleInput.value === 'true')));

  colorPicker.addEventListener('input', function () {
    colorText.value = colorPicker.value;
    patchActive((f) => (f.color = colorPicker.value));
  });
  colorText.addEventListener('input', function () {
    if (/^#[0-9a-fA-F]{6}$/.test(colorText.value)) {
      colorPicker.value = colorText.value;
      patchActive((f) => (f.color = colorText.value));
    }
  });

  document.getElementById('reset-layout').addEventListener('click', function () {
    layout = JSON.parse(JSON.stringify(defaultLayout));
    layout.fields.forEach((field) => {
      const el = fieldElement(field.key);
      if (el) applyFieldStyle(el, field);
    });
    activeKey = layout.fields.length ? layout.fields[0].key : null;
    if (activeKey) {
      select.value = activeKey;
      updateToolbox();
    }
  });

  document.getElementById('save-layout').addEventListener('click', async function () {
    const response = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': cfg.csrf,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ layout }),
    });

    if (!response.ok) {
      alert('Error al guardar diseño');
      return;
    }
    alert('Diseño guardado');
  });
})();
