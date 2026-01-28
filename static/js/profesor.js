function toggleSegmentacion() {
    const publicoField = document.getElementById('id_visible_para');
    if (!publicoField) return;

    const publico = publicoField.value;
    const divCarrera = document.getElementById('div_carrera');
    const divAnio = document.getElementById('div_año');

    if (publico === 'todos') {
        divCarrera?.classList.add('d-none');
        divAnio?.classList.add('d-none');
    } else if (publico === 'profesores') {
        divCarrera?.classList.remove('d-none');
        divAnio?.classList.add('d-none');
    } else {
        divCarrera?.classList.remove('d-none');
        divAnio?.classList.remove('d-none');
    }
}

// Inicializar listener para segmentación
document.addEventListener('DOMContentLoaded', function () {
    const publicoField = document.getElementById('id_visible_para');
    if (publicoField) {
        publicoField.addEventListener('change', toggleSegmentacion);
        toggleSegmentacion(); // Inicializar estado
    }
});

// =========================================================
// MÓDULO JEFE DE CARRERA
// =========================================================

// Función para ver detalles de asignatura (estudiantes y notas)
function verDetallesAsignatura(materiaId, materiaNombre) {
    const modal = new bootstrap.Modal(document.getElementById('detallesAsignaturaModal'));
    const titulo = document.getElementById('detalleAsignaturaTitulo');
    const content = document.getElementById('detallesAsignaturaContent');

    titulo.textContent = `Estudiantes - ${materiaNombre}`;
    content.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="small text-muted mt-2">Cargando estudiantes...</p>
        </div>`;

    modal.show();

    // Fetch estudiantes y notas
    fetch(`/api/obtener-estudiantes-notas/${materiaId}/`)
        .then(res => {
            if (!res.ok) throw new Error('Error al cargar datos');
            return res.json();
        })
        .then(data => {
            if (!data.estudiantes || data.estudiantes.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-users-slash fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No hay estudiantes registrados en esta asignatura.</p>
                    </div>`;
                return;
            }

            // Crear tabla con estudiantes y notas
            let html = `
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th><i class="fas fa-user me-1"></i>Estudiante</th>
                                <th class="text-center"><i class="fas fa-star me-1"></i>Nota</th>
                                <th class="text-center"><i class="fas fa-chart-line me-1"></i>Tendencia</th>
                            </tr>
                        </thead>
                        <tbody>`;

            data.estudiantes.forEach(est => {
                const notaDisplay = est.nota !== null ? `${est.nota}/5` : '<span class="text-muted">Sin nota</span>';
                let tendenciaBadge = '';

                if (est.tendencia === 'subio') {
                    tendenciaBadge = '<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="fas fa-arrow-up me-1"></i>Subió</span>';
                } else if (est.tendencia === 'bajo') {
                    tendenciaBadge = '<span class="badge bg-danger-subtle text-danger border border-danger-subtle"><i class="fas fa-arrow-down me-1"></i>Bajó</span>';
                } else if (est.tendencia === 'mantuvo') {
                    tendenciaBadge = '<span class="badge bg-light text-muted border">Mantuvo</span>';
                } else {
                    tendenciaBadge = '<span class="text-muted">-</span>';
                }

                html += `
                    <tr>
                        <td><strong>${est.nombre}</strong></td>
                        <td class="text-center">${notaDisplay}</td>
                        <td class="text-center">${tendenciaBadge}</td>
                    </tr>`;
            });

            html += `
                        </tbody>
                    </table>
                </div>`;

            content.innerHTML = html;
        })
        .catch(err => {
            content.innerHTML = `
                <div class="alert alert-danger m-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al cargar los datos: ${err.message}
                    <button class="btn btn-sm btn-danger mt-2 d-block" onclick="verDetallesAsignatura(${materiaId}, '${materiaNombre}')">
                        Reintentar
                    </button>
                </div>`;
        });
}


function seleccionarProfesorLocal(el) {
    const p = el.dataset;

    document.getElementById('detalleProfesorEmpty').classList.add('d-none');
    document.getElementById('detalleProfesorForm').classList.remove('d-none');

    document.getElementById('editProfesorNombre').textContent = p.nombre;
    document.getElementById('editProfesorEmail').textContent = p.email;
    document.getElementById('editProfesorId').value = p.id;
    document.getElementById('editProfesorNivel').textContent = p.nivel === 'jefe de carrera' ? 'Jefe de Carrera' : 'Profesor';

    const carreraSelect = document.getElementById('editProfesorCarrera');
    carreraSelect.value = p.carrera || "";

    let materiasIds = [];
    try {
        materiasIds = JSON.parse(p.materias || '[]');
    } catch (e) { console.error("Error parseando materias", e); }

    renderMateriasCheckboxes(p.carrera, materiasIds);

    carreraSelect.onchange = () => {
        renderMateriasCheckboxes(carreraSelect.value, []);
    };

    // Listener filtro año
    const filtroAnio = document.getElementById('filtroAnioMateria');
    if (filtroAnio) {
        filtroAnio.value = 'todos'; // reset
        filtroAnio.onchange = () => {
            const anio = filtroAnio.value;
            // Solo ocultar visualmente
            document.querySelectorAll('.materia-item').forEach(m => {
                if (anio === 'todos' || m.dataset.anio === anio) m.classList.remove('d-none');
                else m.classList.add('d-none');
            });
        };
    }
}

function renderMateriasCheckboxes(carreraId, materiasAsignadas) {
    const container = document.getElementById('listaMateriasCheckboxes');
    container.innerHTML = '';

    if (typeof ALL_MATERIAS === 'undefined') {
        console.error("CRÍTICO: ALL_MATERIAS no está definido.");
        container.innerHTML = '<div class="alert alert-danger p-2">Error: Datos de materias no cargados.</div>';
        return;
    }

    if (!carreraId) {
        container.innerHTML = '<div class="text-center text-muted p-3">Selecciona una carrera válida.</div>';
        return;
    }

    // Todas las materias de la carrera (permitir multi-año)
    const materias = ALL_MATERIAS.filter(m => m.carrera_id == carreraId);

    if (materias.length === 0) {
        container.innerHTML = '<div class="text-center text-muted p-3">No hay materias registradas para esta carrera.</div>';
        return;
    }

    // Ordenar materias por año
    materias.sort((a, b) => (a['año'] || 0) - (b['año'] || 0));

    let html = '';
    materias.forEach(m => {
        const anio = m['año'] || m.anio || '?';
        const isChecked = materiasAsignadas.includes(m.id) ? 'checked' : '';

        html += `
        <div class="col-md-6 materia-item" data-anio="${anio}">
            <div class="form-check p-2 border rounded bg-light hover-shadow">
                <input class="form-check-input ms-1" type="checkbox" value="${m.id}" id="mat_${m.id}" ${isChecked}>
                <label class="form-check-label w-100 ps-2 cursor-pointer" for="mat_${m.id}">
                    <span class="fw-bold text-navy d-block">${m.nombre}</span>
                    <span class="badge bg-secondary rounded-pill" style="font-size:0.6em">Año ${anio}</span>
                </label>
            </div>
        </div>`;
    });

    container.innerHTML = html;
}

// =========================================================
// INICIALIZACIÓN (DOMContentLoaded)
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
    // Listeners Generales
    const publicoSelect = document.getElementById('noticia_visible_para');
    if (publicoSelect) {
        toggleSegmentacion();
        publicoSelect.addEventListener('change', toggleSegmentacion);
    }



    // Formulario Noticias
    // El formulario de noticias ahora usa Django Forms (POST estándar).
    // Se ha eliminado el listener antiguo "formNuevaNoticia".

    // Formularios Subir Notas y Horarios ahora usan Django Forms estándar (POST)
    // Se eliminó la lógica AJAX manual.


    // Formulario Asignar Profesores (JEFE)
    const formEditarProf = document.getElementById('formEditarProfesor');
    if (formEditarProf) {
        formEditarProf.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = formEditarProf.querySelector('button[type="submit"]');
            btn.innerHTML = 'Guardando...';
            btn.disabled = true;

            const profesorId = document.getElementById('editProfesorId').value;
            const carreraId = document.getElementById('editProfesorCarrera').value;
            const checkboxes = document.querySelectorAll('#listaMateriasCheckboxes input[type="checkbox"]:checked');
            const materiasIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

            fetch('/api/profesores/asignar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    profesor_id: profesorId,
                    carrera_id: carreraId || null,
                    materias_ids: materiasIds
                })
            }).then(r => {
                if (!r.ok) throw new Error("Error HTTP " + r.status);
                return r.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch {
                        throw new Error("Respuesta inválida servidor");
                    }
                });
            }).then(d => {
                btn.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';
                btn.disabled = false;
                if (d.success) {
                    showToast("success", "Guardado", "Asignaciones actualizadas con éxito");
                    // Opcional: recargar para ver cambios en la lista ppal
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast("error", "Error", d.error);
                }
            }).catch(err => {
                btn.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';
                btn.disabled = false;
                showToast("error", "Error", err.message);
            });
        });
    }

    // Cleanup modales
    document.addEventListener('hidden.bs.modal', function () {
        if (!document.querySelector('.modal.show')) {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
        }
    });

    // Fix: Aplicar anchos de barras de progreso dinámicamente para evitar errores de linter CSS en HTML
    document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
    });
});

// Función para cargar materias en el formulario de notas
function initMateriasNotas() {
    const carreraSel = document.getElementById('notas_carrera');
    const anioSel = document.getElementById('notas_anio');
    const materiaSel = document.getElementById('notas_materia');

    if (!carreraSel || !anioSel || !materiaSel) return;

    function load() {
        const carreraId = carreraSel.value;
        const anio = anioSel.value;

        materiaSel.innerHTML = '<option>Cargando...</option>';

        if (!carreraId || !anio) {
            materiaSel.innerHTML = '<option value="" disabled selected>Seleccione carrera y año...</option>';
            return;
        }

        fetch(`/api/materias/?carrera_id=${carreraId}&anio=${anio}`)
            .then(r => r.json())
            .then(d => {
                materiaSel.innerHTML = '';
                if (d.materias && d.materias.length > 0) {
                    d.materias.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.id;
                        opt.textContent = m.nombre;
                        materiaSel.appendChild(opt);
                    });
                } else {
                    materiaSel.innerHTML = '<option value="" disabled>No hay materias</option>';
                }
            })
            .catch(() => {
                materiaSel.innerHTML = '<option value="" disabled>Error al cargar</option>';
            });
    }

    carreraSel.addEventListener('change', load);
    anioSel.addEventListener('change', load);
}

document.addEventListener('DOMContentLoaded', initMateriasNotas);

// =========================================================
// FUNCIONES MIGRADAS DE HTML (Inline Scripts)
// =========================================================

// Cargar datos de materias al inicio (para Jefe de Carrera)
function initMateriasData() {
    try {
        const scriptTag = document.getElementById('ums-materias-data');
        if (scriptTag) {
            window.ALL_MATERIAS = JSON.parse(scriptTag.textContent);
            console.log("ALL_MATERIAS cargado:", window.ALL_MATERIAS ? window.ALL_MATERIAS.length : 0);
        } else {
            // Solo warn si se esperaba (ej: es jefe de carrera) pero no rompe si no lo es.
            // window.ALL_MATERIAS = []; 
        }
    } catch (e) {
        console.error("Error parsing materias data:", e);
        window.ALL_MATERIAS = [];
    }
}

// Preparar formulario para Editar Noticia
// Se expone globalmente porque se llama desde onclick en HTML
window.prepararEdicion = function (id, titulo, contenido, visiblePara, categoria, carreraId, anio) {
    // Switch tab
    const tabPublicarEl = document.querySelector('#publicar-tab');
    if (tabPublicarEl) {
        const tabPublicar = new bootstrap.Tab(tabPublicarEl);
        tabPublicar.show();
    }

    // Fill form
    const form = document.getElementById('formNoticia');
    if (!form) return;

    form.action = `/noticias/editar/${id}/`;

    if (document.getElementById('id_titulo')) document.getElementById('id_titulo').value = titulo;
    if (document.getElementById('id_contenido')) document.getElementById('id_contenido').value = contenido;
    if (document.getElementById('id_visible_para')) document.getElementById('id_visible_para').value = visiblePara;
    if (document.getElementById('id_categoria')) document.getElementById('id_categoria').value = categoria;

    const carField = document.getElementById('id_carrera');
    const anioField = document.getElementById('id_anio');
    if (carField && carreraId) carField.value = carreraId;
    if (anioField && anio) anioField.value = anio;

    // UI Change
    const btnSubmit = document.getElementById('btnSubmitNoticia');
    if (btnSubmit) btnSubmit.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';

    const btnCancel = document.getElementById('btnCancelarEdicion');
    if (btnCancel) btnCancel.classList.remove('d-none');

    // Trigger generic change event for visibility logic (if any)
    const visField = document.getElementById('id_visible_para');
    if (visField) visField.dispatchEvent(new Event('change'));
};

// Cancelar Edición Noticia
window.cancelarEdicion = function () {
    const form = document.getElementById('formNoticia');
    if (!form) return;

    // Reset action to "Create" 
    // Usamos el data-attribute para obtener la URL limpia
    const createUrl = form.dataset.createUrl || '/noticias/crear/';
    form.action = createUrl;

    form.reset();

    const btnSubmit = document.getElementById('btnSubmitNoticia');
    if (btnSubmit) btnSubmit.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Publicar Ahora';

    const btnCancel = document.getElementById('btnCancelarEdicion');
    if (btnCancel) btnCancel.classList.add('d-none');

    const visField = document.getElementById('id_visible_para');
    if (visField) visField.dispatchEvent(new Event('change'));
};

// Inicialización extra
document.addEventListener('DOMContentLoaded', () => {
    initMateriasData();
});
