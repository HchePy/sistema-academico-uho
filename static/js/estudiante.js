/* JavaScript para el Dashboard del Estudiante */

document.addEventListener('DOMContentLoaded', () => {
    // Funcionalidad para expandir/contraer noticias
    const botonesVerMas = document.querySelectorAll('.btn-ver-mas');

    botonesVerMas.forEach(boton => {
        boton.addEventListener('click', (e) => {
            e.preventDefault();
            const noticiaId = boton.dataset.noticiaId;
            const contenedor = document.querySelector(`.noticia-contenido[data-noticia-id="${noticiaId}"]`);
            const contenidoCorto = contenedor.querySelector('.contenido-corto');
            const contenidoCompleto = contenedor.querySelector('.contenido-completo');
            const textoBoton = boton.querySelector('.texto-ver-mas');
            const icono = boton.querySelector('i');

            // Toggle entre corto y completo
            if (contenidoCorto.classList.contains('d-none')) {
                // Mostrar versión corta
                contenidoCorto.classList.remove('d-none');
                contenidoCompleto.classList.add('d-none');
                textoBoton.textContent = 'Leer más';
                icono.classList.remove('fa-chevron-up');
                icono.classList.add('fa-chevron-right');
            } else {
                // Mostrar versión completa
                contenidoCorto.classList.add('d-none');
                contenidoCompleto.classList.remove('d-none');
                textoBoton.textContent = 'Ver menos';
                icono.classList.remove('fa-chevron-right');
                icono.classList.add('fa-chevron-up');
            }
        });
    });
});
