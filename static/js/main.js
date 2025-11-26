// JavaScript global para todas las páginas
console.log("UHO Sistema Académico cargado");

// Funciones globales
function showLoading() {
    // Mostrar spinner de carga global
    console.log("Loading...");
}

function hideLoading() {
    // Ocultar spinner de carga global
    console.log("Loading complete");
}

// Inicializaciones globales
document.addEventListener('DOMContentLoaded', function() {
    console.log("Página cargada completamente");
});