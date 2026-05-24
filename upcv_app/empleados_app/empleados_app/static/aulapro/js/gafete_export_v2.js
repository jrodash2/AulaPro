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
      const container = document.getElementById(`gafete-export-${exportId}`);
      const el = document.getElementById(`gafete-export-canvas-${exportId}`);
      if (!container || !el) {
        const msg = `No se encontró el canvas de exportación: ${exportId}`;
        console.error('[gafete_export_v2]', msg);
        alert(msg);
        return;
      }

      container.style.width = `${CANVAS_WIDTH}px`;
      container.style.height = `${CANVAS_HEIGHT}px`;
      container.style.transform = 'none';
      el.style.width = `${CANVAS_WIDTH}px`;
      el.style.height = `${CANVAS_HEIGHT}px`;
      el.style.transform = 'none';

      const rect = container.getBoundingClientRect();
      const transform = getComputedStyle(container).transform;
      console.log('EXPORT rect:', rect.width, rect.height);
      console.log('EXPORT transform:', transform);

      const bg = el.querySelector('img.gafete-bg');
      if (bg) {
        console.log('bg natural:', bg.naturalWidth, bg.naturalHeight, 'rendered:', bg.getBoundingClientRect());
      }
      const photo = el.querySelector('img.gafete-photo');
      if (photo) {
        console.log('photo natural:', photo.naturalWidth, photo.naturalHeight, 'rendered:', photo.getBoundingClientRect());
      }

      const widthOk = Math.abs(rect.width - CANVAS_WIDTH) <= 1;
      const heightOk = Math.abs(rect.height - CANVAS_HEIGHT) <= 1;
      if (!widthOk || !heightOk) {
        throw new Error('Export canvas NO está en 1011x639');
      }
      if (transform !== 'none') {
        throw new Error('Export canvas tiene transform, no se permite');
      }

      await waitForImages(el);

      const canvas = await html2canvas(container, {
        scale: 1,
        width: CANVAS_WIDTH,
        height: CANVAS_HEIGHT,
        useCORS: true,
        backgroundColor: '#ffffff',
        removeContainer: true,
      });

      const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
      const link = document.createElement('a');
      link.href = dataUrl;
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
