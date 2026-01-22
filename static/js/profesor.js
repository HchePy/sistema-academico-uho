/* JavaScript para el Dashboard del Profesor */


// Helper para Notificaciones Toast
function showNotification(title, message, type = 'success') {
    const toastEl = document.getElementById('notificationToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    if (!toastEl) {
        // Fallback si no existe el toast en el DOM
        alert(`${title}: ${message}`);
        return;
    }

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Reset classes
    toastIcon.className = 'me-2 fas';

    if (type === 'success') {
        toastIcon.classList.add('fa-check-circle', 'text-success');
    } else if (type === 'error') {
        toastIcon.classList.add('fa-exclamation-circle', 'text-danger');
    } else {
        toastIcon.classList.add('fa-info-circle', 'text-primary');
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// =========================================================
// MÓDULO PUBLICACIONES (NOTICIAS)
// =========================================================
function cargarMisNoticias() {
    const container = document.getElementById('listaNoticias');
    if (!container) return;

    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-2" role="status"></div>
            <p class="small text-muted">Consultando al servidor...</p>
        </div>`;

    fetch('/api/noticias/mias/')
        .then(res => {
            if (!res.ok) throw new Error('Error ' + res.status);
            return res.json();
        })
        .then(data => {
            container.innerHTML = '';

            // Header con refresh
            const header = document.createElement('div');
            header.className = 'bg-light p-2 text-end border-bottom';
            header.innerHTML = `<button class="btn btn-sm btn-link text-decoration-none" id="btnRefrescar"><i class="fas fa-sync-alt me-1"></i>Actualizar</button>`;
            container.appendChild(header);
            header.querySelector('#btnRefrescar').onclick = cargarMisNoticias;

            if (!data.noticias || data.noticias.length === 0) {
                container.innerHTML += '<div class="text-center py-5 text-muted"><p>No has publicado noticias todavía.</p></div>';
                return;
            }

            data.noticias.forEach(n => {
                const badgeClass = n.categoria === 'examen' ? 'bg-danger' : (n.categoria === 'evento' ? 'bg-info' : 'bg-primary');
                const badgeText = n.categoria.charAt(0).toUpperCase() + n.categoria.slice(1);

                const item = document.createElement('div');
                item.className = 'list-group-item p-3';
                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <span class="badge ${badgeClass} rounded-pill small" style="font-size: 0.65rem;">${badgeText}</span>
                                <h6 class="mb-0 fw-bold text-navy">${n.titulo}</h6>
                            </div>
                            <p class="mb-1 small text-secondary">${n.contenido}</p>
                            <small class="text-muted"><i class="far fa-clock me-1"></i>${n.fecha}</small>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary border-0" onclick="editarNoticia(${n.id})">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger border-0" onclick="borrarNoticia(${n.id})">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </div>`;
                container.appendChild(item);
            });
        })
        .catch(err => {
            container.innerHTML = `<div class="alert alert-danger m-3 small">Error al cargar noticias.<br><button class="btn btn-sm btn-danger mt-2" onclick="cargarMisNoticias()">Reintentar</button></div>`;
        });
}

function editarNoticia(id) {
    fetch('/api/noticias/mias/')
        .then(res => res.json())
        .then(data => {
            const noticia = data.noticias.find(n => n.id === id);
            if (!noticia) return;

            document.getElementById('noticia_titulo').value = noticia.titulo;
            document.getElementById('noticia_contenido').value = noticia.contenido;

            toggleSegmentacion();
            const btnPublicar = document.getElementById('btnPublicar');
            btnPublicar.dataset.editingId = id;
            btnPublicar.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';

            document.getElementById('publicar-tab').click();
            new bootstrap.Modal(document.getElementById('noticiaModal')).show();
        });
}

let confirmModalInstance = null;
function borrarNoticia(id) {
    if (!confirmModalInstance) {
        const modalEl = document.getElementById('confirmModal');
        if (modalEl) confirmModalInstance = new bootstrap.Modal(modalEl);
    }

    if (confirmModalInstance) {
        const confirmBtn = document.getElementById('confirmActionBtn');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        document.getElementById('confirmTitle').textContent = '¿Eliminar noticia?';
        document.getElementById('confirmMessage').textContent = 'Esta acción eliminará el aviso de forma permanente.';

        newConfirmBtn.onclick = () => {
            confirmModalInstance.hide();
            doDelete(id);
        };
        confirmModalInstance.show();
    } else {
        if (confirm("¿Eliminar noticia permanentemente?")) doDelete(id);
    }
}

function doDelete(id) {
    fetch('/api/noticias/borrar/' + id + '/', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showNotification("Noticia", "Noticia eliminada correctamente", "success");
                cargarMisNoticias();
            } else {
                showNotification("Error", data.error, "error");
            }
        });
}

function toggleSegmentacion() {
    const publico = document.getElementById('noticia_visible_para').value;
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

    const verTab = document.getElementById('ver-tab');
    if (verTab) {
        verTab.addEventListener('shown.bs.tab', () => cargarMisNoticias());
    }

    // Formulario Noticias
    const formNoticia = document.getElementById('formNuevaNoticia');
    if (formNoticia) {
        formNoticia.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = document.getElementById('btnPublicar');
            const data = {
                titulo: document.getElementById('noticia_titulo').value,
                contenido: document.getElementById('noticia_contenido').value,
                visible_para: document.getElementById('noticia_visible_para').value,
                categoria: document.querySelector('input[name="noticia_categoria"]:checked').value,
                carrera_id: document.getElementById('noticia_carrera').value || null,
                año: document.getElementById('noticia_año').value || null
            };

            const endpoint = btn.dataset.editingId ? `/api/noticias/editar/${btn.dataset.editingId}/` : '/api/noticias/crear/';

            btn.innerHTML = 'Enviando...';
            btn.disabled = true;

            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(r => r.json()).then(d => {
                btn.disabled = false;
                btn.innerHTML = 'Publicar';
                if (d.success) {
                    formNoticia.reset();
                    delete btn.dataset.editingId;
                    cargarMisNoticias();
                    showNotification("Éxito", "Noticia guardada correctamente", "success");
                } else {
                    showNotification("Error", d.error, "error");
                }
            });
        });
    }

    // Formulario Subir Notas
    const formNotas = document.getElementById('formSubirNotas');
    if (formNotas) {
        formNotas.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            // Usar fetch para enviar archivo
            const btn = formNotas.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Subiendo...';
            btn.disabled = true;

            fetch('/subir-notas/', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(d => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    if (d.exito) {
                        showNotification("Éxito", d.exito, "success");
                        const modal = bootstrap.Modal.getInstance(document.getElementById('subirNotasModal'));
                        modal.hide();
                    }
                    else showNotification("Error", d.error || "Falló la subida", "error");
                })
                .catch(e => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    showNotification("Error de Red", e.message, "error");
                });
        });
    }

    // Formulario Subir Horarios
    const formHorarios = document.getElementById('formSubirHorarios');
    if (formHorarios) {
        formHorarios.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const btn = formHorarios.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Subiendo...';
            btn.disabled = true;

            fetch('/subir-horarios/', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(d => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    if (d.exito) {
                        let mensaje = d.exito;
                        // Si hay errores, agregarlos al mensaje
                        if (d.detalles && d.detalles.errores && d.detalles.errores.length > 0) {
                            mensaje += '\n\nErrores encontrados:\n' + d.detalles.errores.join('\n');
                        }
                        showNotification("Éxito", mensaje, "success");
                        const modal = bootstrap.Modal.getInstance(document.getElementById('subirHorariosModal'));
                        modal.hide();
                        formHorarios.reset();
                    }
                    else showNotification("Error", d.error || "Falló la subida", "error");
                })
                .catch(e => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    showNotification("Error de Red", e.message, "error");
                });
        });
    }

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
                headers: { 'Content-Type': 'application/json' },
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
                    showNotification("Guardado", "Asignaciones actualizadas con éxito", "success");
                    // Opcional: recargar para ver cambios en la lista ppal
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification("Error", d.error, "error");
                }
            }).catch(err => {
                btn.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Cambios';
                btn.disabled = false;
                showNotification("Error", err.message, "error");
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
});

// Función global para materia select
function cargarMateriasPorCarrera() {
    const carreraId = document.getElementById('carrera_id')?.value;
    const anio = document.getElementById('anio')?.value;
    const select = document.getElementById('materia_id');
    if (!select || !carreraId || !anio) return;

    select.innerHTML = '<option>Cargando...</option>';
    fetch(`/api/materias/?carrera_id=${carreraId}&anio=${anio}`)
        .then(r => r.json()).then(d => {
            select.innerHTML = '';
            if (d.materias && d.materias.length > 0) {
                d.materias.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id; opt.textContent = m.nombre;
                    select.appendChild(opt);
                });
            } else {
                select.innerHTML = '<option value="" disabled>No hay materias</option>';
            }
        });
}
