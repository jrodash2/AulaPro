(function () {
  const SAFETY_MARGIN = 24;

  function applyPreviewScaleFor(id) {
    const viewport = document.getElementById(`vp-${id}`);
    const wrap = document.getElementById(`wrap-${id}`);
    const canvas = document.getElementById(`gafete-canvas-${id}`) || (wrap ? wrap.querySelector('.gafete-canvas-real') : null);
    if (!viewport || !wrap || !canvas) return;

    const viewportRect = viewport.getBoundingClientRect();
    const canvasRect = canvas.getBoundingClientRect();

    const availWidth = Math.max(1, viewport.clientWidth - SAFETY_MARGIN);
    const availHeight = Math.max(1, viewport.clientHeight - SAFETY_MARGIN);
    const canvasW = parseInt(canvas.dataset.w || canvas.dataset.canvasWidth || Math.round(canvas.offsetWidth) || 1011, 10);
    const canvasH = parseInt(canvas.dataset.h || canvas.dataset.canvasHeight || Math.round(canvas.offsetHeight) || 639, 10);
    let scale = Math.min(1, availWidth / canvasW, availHeight / canvasH);

    if (!Number.isFinite(scale) || scale < 0.1) {
      console.error('[gafete_preview] scale inválido, se fuerza a 1', { id, scale, availWidth, availHeight });
      scale = 1;
    }

    wrap.style.transform = `scale(${scale})`;
    wrap.style.width = `${canvasW * scale}px`;
    wrap.style.height = `${canvasH * scale}px`;

    console.log('preview canvas:', canvas);
    console.log('rect:', canvasRect);
    console.log('wrap transform:', getComputedStyle(wrap).transform);
    console.log('viewport rect:', viewportRect);
    console.log('[gafete_preview] scale aplicado', { id, scale, w: canvasW, h: canvasH });
  }

  function bindPreviewScale() {
    const ids = new Set();
    document.querySelectorAll('[id^="wrap-"]').forEach((el) => ids.add(el.id.replace('wrap-', '')));

    ids.forEach((id) => applyPreviewScaleFor(id));
    window.addEventListener('resize', () => ids.forEach((id) => applyPreviewScaleFor(id)));

    document.querySelectorAll('.modal[id^="gafeteModal"]').forEach((modal) => {
      modal.addEventListener('shown.bs.modal', () => {
        const id = (modal.id || '').replace('gafeteModal', '');
        requestAnimationFrame(() => {
          applyPreviewScaleFor(id);
          setTimeout(() => applyPreviewScaleFor(id), 0);
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindPreviewScale);
  } else {
    bindPreviewScale();
  }
})();
