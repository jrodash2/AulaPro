(function () {
  function sanitizeFilenamePart(value) {
    return (value || 'NA')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/gi, '_')
      .replace(/^_+|_+$/g, '') || 'NA';
  }

  function waitForImage(img) {
    if (img.complete && img.naturalWidth > 0) return Promise.resolve();
    return new Promise((resolve) => {
      const done = () => resolve();
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
    });
  }

  async function waitForImages(container) {
    const imgs = Array.from(container.querySelectorAll('img'));
    await Promise.all(imgs.map(waitForImage));
  }

  function applyPreviewScaleFor(id) {
    const viewport = document.getElementById(`previewViewport-${id}`);
    const scaleWrap = document.getElementById(`previewScaleWrap-${id}`);
    const canvas = scaleWrap ? scaleWrap.querySelector('.gafete-canvas') : null;
    if (!viewport || !scaleWrap || !canvas) return;

    const canvasWidth = parseInt(canvas.dataset.canvasWidth || '1011', 10);
    const canvasHeight = parseInt(canvas.dataset.canvasHeight || '639', 10);
    const availWidth = viewport.clientWidth - 8;
    const availHeight = viewport.clientHeight - 8;
    const scale = Math.min(1, availWidth / canvasWidth, availHeight / canvasHeight);

    scaleWrap.style.transform = `scale(${scale})`;
    scaleWrap.style.width = `${canvasWidth * scale}px`;
    scaleWrap.style.height = `${canvasHeight * scale}px`;
  }

  function bindPreviewScale() {
    const ids = new Set();
    document.querySelectorAll('[id^="previewScaleWrap-"]').forEach((el) => {
      ids.add(el.id.replace('previewScaleWrap-', ''));
    });

    ids.forEach((id) => applyPreviewScaleFor(id));
    window.addEventListener('resize', () => ids.forEach((id) => applyPreviewScaleFor(id)));

    document.querySelectorAll('.modal[id^="gafeteModal"]').forEach((modal) => {
      modal.addEventListener('shown.bs.modal', () => {
        const modalId = (modal.id || '').replace('gafeteModal', '');
        applyPreviewScaleFor(modalId);
      });
    });
  }

  async function exportGafete(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    if (btn.dataset.busy === '1') return;
    btn.dataset.busy = '1';
    btn.disabled = true;

    try {
      if (typeof html2canvas === 'undefined') {
        alert('html2canvas no cargó');
        return;
      }

      const exportId = btn.dataset.exportId;
      const el = document.getElementById(`gafete-export-canvas-${exportId}`);
      if (!el) {
        const msg = `No se encontró el canvas de exportación para id ${exportId}`;
        console.error('[gafete_export]', msg);
        alert(msg);
        return;
      }

      const rect = el.getBoundingClientRect();
      const transform = getComputedStyle(el).transform;
      console.log('[gafete_export] element', el);
      console.log('[gafete_export] rect', rect.width, rect.height, rect);
      console.log('[gafete_export] transform', transform);

      await waitForImages(el);

      const canvas = await html2canvas(el, {
        scale: 1,
        width: 1011,
        height: 639,
        useCORS: true,
        backgroundColor: null,
      });

      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/jpeg', 0.95);
      const rawFilename = btn.dataset.filename || 'GAFETE_NA_NA_NA.jpg';
      link.download = sanitizeFilenamePart(rawFilename.replace(/\.jpg$/i, '')) + '.jpg';
      link.click();
    } catch (err) {
      console.error('[gafete_export] Falló la exportación:', err);
      alert(`Error al descargar JPG: ${err && err.message ? err.message : err}`);
    } finally {
      btn.dataset.busy = '0';
      btn.disabled = false;
    }
  }

  function bindExport() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', exportGafete);
      btn.addEventListener('click', exportGafete);
    });
  }

  function init() {
    bindPreviewScale();
    bindExport();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
