(function () {
  const CANVAS_WIDTH = 1011;
  const CANVAS_HEIGHT = 639;
  const SAFETY_MARGIN = 24;

  function applyPreviewScaleFor(id) {
    const viewport = document.getElementById(`vp-${id}`);
    const wrap = document.getElementById(`wrap-${id}`);
    const canvas = wrap ? wrap.querySelector('.gafete-canvas-real') : null;
    if (!viewport || !wrap || !canvas) return;

    const availWidth = Math.max(1, viewport.clientWidth - SAFETY_MARGIN);
    const availHeight = Math.max(1, viewport.clientHeight - SAFETY_MARGIN);
    const scale = Math.min(1, availWidth / CANVAS_WIDTH, availHeight / CANVAS_HEIGHT);

    wrap.style.transform = `scale(${scale})`;
    wrap.style.width = `${CANVAS_WIDTH * scale}px`;
    wrap.style.height = `${CANVAS_HEIGHT * scale}px`;

    console.log('[gafete_preview] scale', id, scale, 'avail', availWidth, availHeight);
    console.log('[gafete_preview] base canvas size', CANVAS_WIDTH, CANVAS_HEIGHT);
  }

  function bindPreviewScale() {
    const ids = new Set();
    document.querySelectorAll('[id^="wrap-"]').forEach((el) => ids.add(el.id.replace('wrap-', '')));

    ids.forEach((id) => applyPreviewScaleFor(id));
    window.addEventListener('resize', () => ids.forEach((id) => applyPreviewScaleFor(id)));

    document.querySelectorAll('.modal[id^="gafeteModal"]').forEach((modal) => {
      modal.addEventListener('shown.bs.modal', () => {
        const id = (modal.id || '').replace('gafeteModal', '');
        requestAnimationFrame(() => applyPreviewScaleFor(id));
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindPreviewScale);
  } else {
    bindPreviewScale();
  }
})();
