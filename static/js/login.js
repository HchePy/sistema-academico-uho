// JavaScript para Login y Registro

function togglePassword(inputId, btn) {
    btn = btn || (typeof event !== 'undefined' && event.currentTarget);
    const input = inputId ? document.getElementById(inputId)
        : (btn && (btn.previousElementSibling || btn.closest('.input-group').querySelector('input')));
    if (!input) return;
    const icon = btn ? btn.querySelector('i') : null;
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) { icon.classList.remove('fa-eye'); icon.classList.add('fa-eye-slash'); }
    } else {
        input.type = 'password';
        if (icon) { icon.classList.remove('fa-eye-slash'); icon.classList.add('fa-eye'); }
    }
}

// Función para abrir el modal de registro
function mostrarRegistroModal() {
    const registroModal = new bootstrap.Modal(document.getElementById('registroModal'));
    registroModal.show();
}

// Validar que las contraseñas coincidan en el modal
function validarPasswordsRegistro() {
    const pass1 = document.getElementById('reg_password1');
    const pass2 = document.getElementById('reg_password2');

    if (pass1 && pass2) {
        if (pass1.value !== pass2.value) {
            pass2.style.borderColor = '#dc3545'; // Rojo si no coinciden
            return false;
        } else {
            pass2.style.borderColor = '#28a745'; // Verde si coinciden
        }
    }
    return true;
}

// Función para enviar el registro al backend
function registrarUsuario() {
    if (!validarPasswordsRegistro()) {
        showToast('error', 'Error', 'Las contraseñas no coinciden');
        return;
    }

    const username = (document.getElementById('reg_username') || {}).value || '';
    const email = (document.getElementById('reg_email') || {}).value || '';
    const password = (document.getElementById('reg_password1') || {}).value || '';
    const carrera_id = (document.getElementById('reg_carrera') || {}).value || '';
    const anio = (document.getElementById('reg_anio') || {}).value || '';

    if (!username.trim() || !email.trim() || !password || !carrera_id) {
        showToast('error', 'Error', 'Por favor complete todos los campos de registro');
        return;
    }

    fetch('/api/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username.trim(),
            email: email.trim(),
            password: password,
            carrera_id: carrera_id,
            año: anio
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Éxito', 'Usuario creado exitosamente. Rol: ' + (data.role || ''));
                const modalEl = document.getElementById('registroModal');
                const registroModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                registroModal.hide();
            } else {
                showToast('error', 'Error', data.error || 'Error en el registro');
            }
        })
        .catch(err => {
            console.error(err);
            showToast('error', 'Error', 'Error en la solicitud de registro');
        });
}

// Configurar validación cuando cargue la página
document.addEventListener('DOMContentLoaded', function () {
    const pass1 = document.getElementById('reg_password1');
    const pass2 = document.getElementById('reg_password2');

    if (pass1 && pass2) {
        pass1.addEventListener('input', validarPasswordsRegistro);
        pass2.addEventListener('input', validarPasswordsRegistro);
    }

    // Prevenir envío si las contraseñas no coinciden
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            if (!validarPasswordsRegistro()) {
                e.preventDefault();
                alert('Las contraseñas no coinciden');
            }
        });
    }

    // Enviar form

    // Auto-show modal if requested by backend
    if (document.body.dataset.showRegisterModal === "true") {
        var modalEl = document.getElementById('registroModal');
        if (modalEl) {
            var modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    }


});

