(function () {
  if (typeof html2canvas === 'undefined') return;

  document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
    btn.addEventListener('click', async function () {
      const targetId = btn.dataset.target;
      const width = parseInt(btn.dataset.width || '1011', 10);
      const height = parseInt(btn.dataset.height || '639', 10);
      const name = btn.dataset.name || 'alumno';
      const downloadUrl = btn.dataset.downloadUrl;
      const csrfToken = btn.dataset.csrf;
      const element = document.getElementById(targetId);
      if (!element) return;

      const canvas = await html2canvas(element, {
        useCORS: true,
        backgroundColor: null,
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
      if (!response.ok) return;

      const blob = await response.blob();
      const fileUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = `${name}_gafete.jpg`;
      link.click();
      URL.revokeObjectURL(fileUrl);
    });
  });
})();
