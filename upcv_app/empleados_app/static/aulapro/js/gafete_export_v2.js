(function () {
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

      const rect = el.getBoundingClientRect();
      const transform = getComputedStyle(el).transform;
      console.log('[gafete_export_v2] elemento encontrado', el);
      console.log('[gafete_export_v2] rect', rect.width, rect.height, rect);
      console.log('[gafete_export_v2] transform', transform);

      await waitForImages(el);

      const canvas = await html2canvas(el, {
        scale: 1,
        width: 1011,
        height: 639,
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
