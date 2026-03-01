(function () {
  function sanitizeFilenamePart(value) {
    return (value || 'NA')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/gi, '_')
      .replace(/^_+|_+$/g, '') || 'NA';
  }

  function buildFilename(btn) {
    return `GAFETE_${sanitizeFilenamePart(btn.dataset.apellidos)}_${sanitizeFilenamePart(btn.dataset.nombres)}_${sanitizeFilenamePart(btn.dataset.codigo)}.jpg`;
  }

  async function waitForImages(container) {
    const imgs = Array.from(container.querySelectorAll('img'));
    await Promise.all(imgs.map((img) => {
      if (img.complete && img.naturalWidth > 0) return Promise.resolve();
      return new Promise((resolve) => {
        const done = () => resolve();
        img.addEventListener('load', done, { once: true });
        img.addEventListener('error', done, { once: true });
      });
    }));
  }

  async function exportGafete(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    if (btn.dataset.busy === '1') return;
    btn.dataset.busy = '1';
    btn.disabled = true;

    try {
      if (typeof html2canvas === 'undefined') {
        console.error('[gafete_export] html2canvas no está cargado.');
        return;
      }

      const targetId = btn.dataset.target;
      const el = document.getElementById(targetId);
      if (!el) {
        console.error('[gafete_export] No se encontró canvas de export:', targetId);
        return;
      }

      const width = parseInt(el.dataset.canvasWidth || btn.dataset.width || '1011', 10);
      const height = parseInt(el.dataset.canvasHeight || btn.dataset.height || '639', 10);
      const textEl = el.querySelector('.gafete-item[data-key="nombres"], .gafete-item[data-key="apellidos"]');
      console.log('[gafete_export] target', el, el.getBoundingClientRect());
      console.log('[gafete_export] transform', getComputedStyle(el).transform, 'fontSize', textEl ? getComputedStyle(textEl).fontSize : 'n/a');

      await waitForImages(el);

      const canvas = await html2canvas(el, {
        scale: 1,
        width,
        height,
        backgroundColor: null,
        useCORS: true,
      });

      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/jpeg', 0.95);
      link.download = buildFilename(btn);
      link.click();
    } catch (err) {
      console.error('[gafete_export] Falló la exportación:', err);
    } finally {
      btn.dataset.busy = '0';
      btn.disabled = false;
    }
  }

  function bind() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', exportGafete);
      btn.addEventListener('click', exportGafete);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
