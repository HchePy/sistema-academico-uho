// JavaScript para Login y Registro

// Función para mostrar notificaciones (toasts)
function showToast(type, title, message) {
    try {
        const toastElement = document.getElementById('notificationToast');
        if (!toastElement) {
            console.warn('Toast element not found, using alert');
            alert(`${title}: ${message}`);
            return;
        }
        
        const toastIcon = document.getElementById('toastIcon');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');

        // Establecer clase según tipo
        toastElement.className = 'toast';
        if (type === 'success') {
            toastElement.classList.add('bg-success', 'text-white');
            if (toastIcon) toastIcon.className = 'fas fa-check-circle text-white';
        } else if (type === 'error') {
            toastElement.classList.add('bg-danger', 'text-white');
            if (toastIcon) toastIcon.className = 'fas fa-exclamation-circle text-white';
        } else if (type === 'warning') {
            toastElement.classList.add('bg-warning', 'text-dark');
            if (toastIcon) toastIcon.className = 'fas fa-exclamation-triangle text-dark';
        } else {
            toastElement.classList.add('bg-info', 'text-white');
            if (toastIcon) toastIcon.className = 'fas fa-info-circle text-white';
        }

        if (toastTitle) toastTitle.textContent = title;
        if (toastMessage) toastMessage.textContent = message;

        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        } else {
            console.warn('Bootstrap not loaded, using alert');
            alert(`${title}: ${message}`);
        }
    } catch (e) {
        console.error('Error showing toast:', e);
        alert(`${title}: ${message}`);
    }
}

function togglePassword(inputId, btn) {
    // btn: el elemento <button> (se pasa con 'this'); inputId: id del input (opcional)
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
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;

            if (username && password) {
                // Enviar login al backend
                fetch('/api/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        remember: remember
                    })
                })
                    .then(r => r.json())
                    .then(data => {
                        if (data.authenticated) {
                            window.location.href = '/base/';
                        } else {
                            showToast('error', 'Error', 'Usuario o contraseña incorrectos');
                        }
                    })
                    .catch(err => {
                        console.error('Error:', err);
                        showToast('error', 'Error', 'Error al iniciar sesión');
                    });
            } else {
                showToast('error', 'Error', 'Por favor complete todos los campos');
            }
        });
    }
});

