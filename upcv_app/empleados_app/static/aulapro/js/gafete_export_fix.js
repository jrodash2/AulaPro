(function () {
  const W = 1011;
  const H = 639;

  function sanitizeFilename(name) {
    const base = (name || 'GAFETE_NA_NA_NA.jpg').replace(/\.jpg$/i, '');
    return base.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Za-z0-9_\-]+/g, '_') + '.jpg';
  }

  function getSandbox() {
    let el = document.getElementById('export-sandbox');
    if (!el) {
      el = document.createElement('div');
      el.id = 'export-sandbox';
      el.style.cssText = 'position:fixed;left:-99999px;top:0;width:0;height:0;overflow:hidden;';
      document.body.appendChild(el);
    }
    return el;
  }

  function waitForImage(img) {
    if (img.complete) return Promise.resolve();
    return new Promise((resolve) => {
      const done = () => resolve();
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
    });
  }

  async function waitImages(root) {
    await Promise.all(Array.from(root.querySelectorAll('img')).map(waitForImage));
  }

  function validateRectAndTransform(el, label) {
    const rect = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    console.log(`${label} selector/id:`, el.id || el.className, el);
    console.log(`${label} rect:`, rect.width, rect.height, rect);
    console.log(`${label} transform:`, cs.transform);
    console.log(`${label} zoom:`, cs.zoom || 'normal');
    if (Math.abs(rect.width - W) > 1 || Math.abs(rect.height - H) > 1) {
      throw new Error('Export canvas NO está en 1011x639');
    }
    if (cs.transform && cs.transform !== 'none') {
      throw new Error('Export canvas tiene transform, no se permite');
    }
  }

  function logImageMetrics(root) {
    const bg = root.querySelector('img.gafete-bg');
    if (bg) {
      console.log('bg natural:', bg.naturalWidth, bg.naturalHeight, 'rendered:', bg.getBoundingClientRect());
    }
    const ph = root.querySelector('img.gafete-photo');
    if (ph) {
      const phStyle = getComputedStyle(ph);
      console.log('photo natural:', ph.naturalWidth, ph.naturalHeight, 'rendered:', ph.getBoundingClientRect());
      console.log('photo objectFit:', phStyle.objectFit, 'photo size:', phStyle.width, phStyle.height);
    }
    const phBg = root.querySelector('.gafete-photo-bg');
    if (phBg) {
      const phBgStyle = getComputedStyle(phBg);
      console.log('photo-bg size:', phBgStyle.width, phBgStyle.height, 'bgSize:', phBgStyle.backgroundSize, 'bgPosition:', phBgStyle.backgroundPosition);
    }
  }

  function buildCloneWrapper(originalCanvas) {
    const clone = originalCanvas.cloneNode(true);
    clone.style.transform = 'none';
    clone.style.zoom = '1';
    clone.style.width = `${W}px`;
    clone.style.height = `${H}px`;

    const wrapper = document.createElement('div');
    wrapper.id = `export-wrapper-${Date.now()}`;
    wrapper.style.width = `${W}px`;
    wrapper.style.height = `${H}px`;
    wrapper.style.position = 'relative';
    wrapper.style.overflow = 'hidden';
    wrapper.style.background = '#fff';
    wrapper.style.transform = 'none';
    wrapper.style.zoom = '1';

    wrapper.appendChild(clone);
    return { wrapper, clone };
  }

  async function exportWithHtml2Canvas(wrapper, filename) {
    const canvas = await html2canvas(wrapper, {
      scale: 1,
      width: W,
      height: H,
      useCORS: true,
      backgroundColor: '#ffffff',
      allowTaint: false,
      removeContainer: true,
    });
    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = sanitizeFilename(filename);
    a.click();
  }

  async function exportWithSvgForeignObject(wrapper, filename) {
    const foreign = `<div xmlns="http://www.w3.org/1999/xhtml" style="width:${W}px;height:${H}px;position:relative;overflow:hidden;background:#fff;">${wrapper.innerHTML}</div>`;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><foreignObject width="100%" height="100%">${foreign}</foreignObject></svg>`;
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        try {
          const c = document.createElement('canvas');
          c.width = W;
          c.height = H;
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#fff';
          ctx.fillRect(0, 0, W, H);
          ctx.drawImage(img, 0, 0);
          const a = document.createElement('a');
          a.href = c.toDataURL('image/jpeg', 0.95);
          a.download = sanitizeFilename(filename);
          a.click();
          resolve();
        } catch (e) {
          reject(e);
        } finally {
          URL.revokeObjectURL(url);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Fallback SVG foreignObject falló'));
      };
      img.src = url;
    });
  }

  async function handleClick(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    if (btn.dataset.busy === '1') return;
    btn.dataset.busy = '1';
    btn.disabled = true;

    try {
      if (typeof html2canvas === 'undefined') {
        throw new Error('html2canvas no cargó');
      }

      const id = btn.dataset.exportId;
      const originalCanvas = document.getElementById(`gafete-export-canvas-${id}`);
      if (!originalCanvas) throw new Error(`No se encontró origen de export: ${id}`);

      const sandbox = getSandbox();
      const { wrapper, clone } = buildCloneWrapper(originalCanvas);
      sandbox.innerHTML = '';
      sandbox.appendChild(wrapper);

      validateRectAndTransform(wrapper, 'EXPORT');
      logImageMetrics(clone);
      await waitImages(clone);

      try {
        await exportWithHtml2Canvas(wrapper, btn.dataset.filename);
      } catch (e) {
        console.error('[gafete_export_fix] html2canvas falló, usando fallback SVG', e);
        await exportWithSvgForeignObject(wrapper, btn.dataset.filename);
      }
    } catch (error) {
      console.error('[gafete_export_fix] error:', error);
      alert(error.message || String(error));
    } finally {
      btn.dataset.busy = '0';
      btn.disabled = false;
    }
  }

  function bind() {
    document.querySelectorAll('.gafete-export-btn').forEach((btn) => {
      btn.removeEventListener('click', handleClick);
      btn.addEventListener('click', handleClick);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
