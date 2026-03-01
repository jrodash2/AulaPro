(function () {
  const CANVAS_WIDTH = 1011;
  const CANVAS_HEIGHT = 639;

  function waitForImage(img) {
    if (img.complete && img.naturalWidth > 0) return Promise.resolve();
    return new Promise((resolve) => {
      const done = () => resolve();
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
    });
  }

  async function waitForImages(root) {
    await Promise.all(Array.from(root.querySelectorAll('img')).map(waitForImage));
  }

  function sanitizeFilename(name) {
    const base = (name || 'GAFETE_NA_NA_NA.jpg').replace(/\.jpg$/i, '');
    return base
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^A-Za-z0-9_\-]+/g, '_') + '.jpg';
  }

  async function handleDownload(event) {
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
        const msg = `No se encontró el canvas de exportación: ${exportId}`;
        console.error('[gafete_export_v2]', msg);
        alert(msg);
        return;
      }

      el.style.width = `${CANVAS_WIDTH}px`;
      el.style.height = `${CANVAS_HEIGHT}px`;
      el.style.transform = 'none';

      const rect = el.getBoundingClientRect();
      const transform = getComputedStyle(el).transform;
      console.log('[gafete_export_v2] elemento encontrado', el);
      console.log('[gafete_export_v2] export rect:', rect.width, rect.height);
      console.log('[gafete_export_v2] export transform:', transform);

      const bg = el.querySelector('img.gafete-bg');
      if (bg) {
        console.log('[gafete_export_v2] bg natural/rendered:', bg.naturalWidth, bg.naturalHeight, bg.getBoundingClientRect());
      }
      const photo = el.querySelector('img.gafete-photo');
      if (photo) {
        console.log('[gafete_export_v2] photo natural/rendered:', photo.naturalWidth, photo.naturalHeight, photo.getBoundingClientRect());
      }

      const widthOk = Math.abs(rect.width - CANVAS_WIDTH) < 1;
      const heightOk = Math.abs(rect.height - CANVAS_HEIGHT) < 1;
      if (!widthOk || !heightOk) {
        throw new Error('Export canvas no es 1011x639');
      }

      await waitForImages(el);

      const canvas = await html2canvas(el, {
        scale: 1,
        width: CANVAS_WIDTH,
        height: CANVAS_HEIGHT,
        useCORS: true,
        backgroundColor: '#ffffff',
      });

      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/jpeg', 0.95);
      link.download = sanitizeFilename(btn.dataset.filename);
      link.click();
    } catch (error) {
      console.error('[gafete_export_v2] Error exportando', error);
      alert(`Error al descargar JPG: ${error?.message || error}`);
    } finally {
      btn.dataset.busy = '0';
      btn.disabled = false;
    }
  }

  function bind() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', handleDownload);
      btn.addEventListener('click', handleDownload);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
