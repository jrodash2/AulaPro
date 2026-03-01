(function () {
  function applyPreviewScaleFor(id) {
    const viewport = document.getElementById(`vp-${id}`);
    const wrap = document.getElementById(`wrap-${id}`);
    const canvas = wrap ? wrap.querySelector('.gafete-canvas-real') : null;
    if (!viewport || !wrap || !canvas) return;

    const canvasWidth = 1011;
    const canvasHeight = 639;
    const scale = Math.min(1, viewport.clientWidth / canvasWidth, viewport.clientHeight / canvasHeight);

    wrap.style.transform = `scale(${scale})`;
    wrap.style.width = `${canvasWidth * scale}px`;
    wrap.style.height = `${canvasHeight * scale}px`;

    const rect = canvas.getBoundingClientRect();
    console.log('[gafete_preview] scale', id, scale);
    console.log('[gafete_preview] real canvas rect (layout)', canvasWidth, canvasHeight, rect);
  }

  function bindPreviewScale() {
    const ids = new Set();
    document.querySelectorAll('[id^="wrap-"]').forEach((el) => ids.add(el.id.replace('wrap-', '')));
    ids.forEach((id) => applyPreviewScaleFor(id));
    window.addEventListener('resize', () => ids.forEach((id) => applyPreviewScaleFor(id)));

    document.querySelectorAll('.modal[id^="gafeteModal"]').forEach((modal) => {
      modal.addEventListener('shown.bs.modal', () => {
        const id = (modal.id || '').replace('gafeteModal', '');
        applyPreviewScaleFor(id);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindPreviewScale);
  } else {
    bindPreviewScale();
  }
})();
