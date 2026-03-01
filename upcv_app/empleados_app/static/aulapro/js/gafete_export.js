(function () {
  function sanitizeFilenamePart(value) {
    return (value || 'alumno').toString().trim().replace(/[^a-z0-9_-]+/gi, '_');
  }

  async function downloadJpg(event) {
    event.preventDefault();

    const btn = event.currentTarget;
    const targetId = btn.dataset.target;
    const width = parseInt(btn.dataset.width || '1011', 10);
    const height = parseInt(btn.dataset.height || '639', 10);
    const name = sanitizeFilenamePart(btn.dataset.name);
    const downloadUrl = btn.dataset.downloadUrl;
    const csrfToken = btn.dataset.csrf;

    if (typeof html2canvas === 'undefined') {
      console.error('[gafete_export] html2canvas no está cargado.');
      return;
    }

    const element = document.getElementById(targetId);
    if (!element) {
      console.error('[gafete_export] No se encontró el contenedor del gafete:', targetId);
      return;
    }

    try {
      const canvas = await html2canvas(element, {
        useCORS: true,
        backgroundColor: '#ffffff',
        scale: 1,
        width,
        height,
      });

      const imageData = canvas.toDataURL('image/jpeg', 0.95);

      if (!downloadUrl) {
        const link = document.createElement('a');
        link.href = imageData;
        link.download = `${name}_gafete.jpg`;
        link.click();
        return;
      }

      const formData = new FormData();
      formData.append('image_data', imageData);
      const response = await fetch(downloadUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[gafete_export] Error al solicitar JPG:', response.status, errorText);
        return;
      }

      const blob = await response.blob();
      const fileUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = `${name}_gafete.jpg`;
      link.click();
      URL.revokeObjectURL(fileUrl);
    } catch (error) {
      console.error('[gafete_export] Falló la descarga del gafete:', error);
    }
  }

  function bindExportButtons() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', downloadJpg);
      btn.addEventListener('click', downloadJpg);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindExportButtons);
  } else {
    bindExportButtons();
  }
})();
