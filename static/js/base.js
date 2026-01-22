// JavaScript global para todas las páginas (Base)

// 1. Función para mostrar toasts de Bootstrap (Global)
function showToast(type, title, message) {
    const toastEl = document.getElementById('notificationToast');
    if (!toastEl) return;

    const toastIcon = document.getElementById('toastIcon');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toastEl.querySelector('.toast-header');

    // Limpiar clases previas
    toastHeader.classList.remove('bg-success', 'bg-danger', 'text-white');
    toastIcon.className = 'me-2';

    if (type === 'success') {
        toastHeader.classList.add('bg-success', 'text-white');
        toastIcon.classList.add('fas', 'fa-check-circle', 'text-white');
        toastTitle.textContent = title || 'Éxito';
    } else if (type === 'error') {
        toastHeader.classList.add('bg-danger', 'text-white');
        toastIcon.classList.add('fas', 'fa-times-circle', 'text-white');
        toastTitle.textContent = title || 'Error';
    }

    toastMessage.textContent = message;

    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
}

// 2. Funciones globales de carga
function showLoading() {
    // Mostrar spinner de carga
}

function hideLoading() {
    // Ocultar spinner de carga
}

// 3. Lógica de Sidebar (Colapso y Persistencia)
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const appWrapper = document.querySelector('.app-wrapper');

    if (!sidebar || !sidebarToggle) return;

    // Recuperar estado previo
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        appWrapper.classList.add('sidebar-collapsed');
    }

    sidebarToggle.addEventListener('click', () => {
        appWrapper.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', appWrapper.classList.contains('sidebar-collapsed'));
    });
}

// Inicializaciones globales
document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
});
