(function () {
  const cfg = window.matriculaModalConfig;
  if (!cfg) return;

  const codigoInput = document.getElementById('matricula-codigo');
  const buscarBtn = document.getElementById('matricula-buscar-btn');
  const alertBox = document.getElementById('matricula-modal-alert');
  const resultBox = document.getElementById('matricula-alumno-result');

  let alumnoActual = null;

  function showAlert(type, text) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
  }

  function renderAlumno(alumno) {
    const disabled = cfg.tieneCicloActivo ? '' : 'disabled';
    resultBox.classList.remove('d-none');
    resultBox.innerHTML = `
      <div class="card">
        <div class="card-body d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-1">${alumno.apellidos}, ${alumno.nombres}</h6>
            <div class="text-muted">Código: ${alumno.codigo || '-'} · CUI: ${alumno.cui || '-'}</div>
          </div>
          <button class="btn btn-primary btn-sm" id="btn-confirmar-matricula" ${disabled}>Matricular</button>
        </div>
      </div>
    `;

    const confirmarBtn = document.getElementById('btn-confirmar-matricula');
    confirmarBtn.addEventListener('click', matricularAlumno);
  }

  async function buscarAlumno() {
    const codigo = (codigoInput.value || '').trim();
    if (!codigo) {
      showAlert('warning', 'Ingrese un código personal.');
      resultBox.classList.add('d-none');
      return;
    }

    const response = await fetch(`${cfg.buscarUrl}?codigo=${encodeURIComponent(codigo)}`);
    const data = await response.json();

    if (!response.ok || !data.found) {
      alumnoActual = null;
      resultBox.classList.add('d-none');
      showAlert('warning', data.error || 'Alumno no encontrado.');
      return;
    }

    alumnoActual = data.alumno;
    alertBox.innerHTML = '';
    renderAlumno(alumnoActual);
  }

  async function matricularAlumno() {
    if (!alumnoActual) {
      showAlert('warning', 'Primero seleccione un alumno.');
      return;
    }

    const body = new URLSearchParams({ alumno_id: alumnoActual.id });
    const response = await fetch(cfg.matricularUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': cfg.csrfToken,
      },
      body: body.toString(),
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      showAlert('danger', data.error || 'No se pudo matricular.');
      return;
    }

    showAlert('success', data.message || 'Alumno matriculado correctamente.');
    setTimeout(() => window.location.reload(), 700);
  }

  buscarBtn.addEventListener('click', buscarAlumno);
  codigoInput.addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      buscarAlumno();
    }
  });
})();
