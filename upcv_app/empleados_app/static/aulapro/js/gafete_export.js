(function () {
  function sanitizeFilenamePart(value) {
    return (value || 'NA')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/gi, '_')
      .replace(/^_+|_+$/g, '');
  }

  function buildFilename(btn) {
    const apellidos = sanitizeFilenamePart(btn.dataset.apellidos);
    const nombres = sanitizeFilenamePart(btn.dataset.nombres);
    const codigo = sanitizeFilenamePart(btn.dataset.codigo);
    return `GAFETE_${apellidos || 'NA'}_${nombres || 'NA'}_${codigo || 'NA'}.jpg`;
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
      const width = parseInt(btn.dataset.width || '1011', 10);
      const height = parseInt(btn.dataset.height || '639', 10);
      const source = document.getElementById(targetId);
      if (!source) {
        console.error('[gafete_export] No se encontró el canvas real:', targetId);
        return;
      }

      const canvas = await html2canvas(source, {
        scale: 1,
        width,
        height,
        useCORS: true,
        backgroundColor: '#ffffff',
      });

      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/jpeg', 0.95);
      link.download = buildFilename(btn);
      link.click();
    } catch (err) {
      console.error('[gafete_export] Falló la exportación JPG:', err);
    } finally {
      btn.dataset.busy = '0';
      btn.disabled = false;
    }
  }

  function bindExportButtons() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', exportGafete);
      btn.addEventListener('click', exportGafete);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindExportButtons);
  } else {
    bindExportButtons();
  }
})();
