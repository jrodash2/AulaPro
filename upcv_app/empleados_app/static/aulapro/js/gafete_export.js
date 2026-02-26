(function () {
  if (typeof html2canvas === 'undefined') return;

  document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
    btn.addEventListener('click', async function () {
      const targetId = btn.dataset.target;
      const width = parseInt(btn.dataset.width || '1011', 10);
      const height = parseInt(btn.dataset.height || '639', 10);
      const name = btn.dataset.name || 'alumno';
      const element = document.getElementById(targetId);
      if (!element) return;

      const canvas = await html2canvas(element, {
        useCORS: true,
        backgroundColor: null,
        scale: 1,
        width,
        height,
      });

      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/jpeg', 0.95);
      link.download = `${name}_gafete.jpg`;
      link.click();
    });
  });
})();
