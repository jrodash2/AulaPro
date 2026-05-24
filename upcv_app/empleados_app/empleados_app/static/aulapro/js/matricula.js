(function () {
  const cfg = window.matriculaConfig;
  if (!cfg) return;

  const form = document.getElementById('buscar-form');
  const codigoInput = document.getElementById('codigo-input');
  const cicloInput = document.getElementById('id_ciclo');
  const estadoInput = document.getElementById('id_estado');
  const resultBox = document.getElementById('alumno-result');
  const alertBox = document.getElementById('matricula-alert');

  function showAlert(type, text) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const codigo = (codigoInput.value || '').trim();
    if (!codigo) {
      showAlert('warning', 'Ingrese un código para buscar.');
      return;
    }

    const res = await fetch(`${cfg.buscarUrl}?codigo=${encodeURIComponent(codigo)}`);
    const data = await res.json();

    if (!res.ok || !data.ok) {
      resultBox.classList.add('d-none');
      showAlert('danger', data.error || 'Alumno no encontrado.');
      return;
    }

    const a = data.alumno;
    resultBox.classList.remove('d-none');
    resultBox.innerHTML = `
      <div class="card">
        <div class="card-body d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-1">${a.apellidos}, ${a.nombres}</h6>
            <div class="text-muted">Código: ${a.codigo || '-'} · CUI: ${a.cui || '-'}</div>
          </div>
          <button class="btn btn-primary btn-sm" id="btn-matricular">Matricular</button>
        </div>
      </div>
    `;

    document.getElementById('btn-matricular').addEventListener('click', async function () {
      const body = new URLSearchParams({
        codigo_personal: codigo,
        ciclo: cicloInput.value,
        estado: estadoInput.value,
      });
      const r = await fetch(cfg.matricularUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': cfg.csrfToken,
        },
        body: body.toString(),
      });
      const d = await r.json();
      if (!r.ok || !d.ok) {
        showAlert('warning', d.error || 'No se pudo matricular.');
        return;
      }
      showAlert('success', 'Alumno matriculado correctamente.');
      window.location.reload();
    });
  });
})();
