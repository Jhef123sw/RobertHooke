document.addEventListener('DOMContentLoaded', function () {
    const tablaBody = document.querySelector('tbody');

    tablaBody.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('btn-eliminar')) {
            event.preventDefault();
            const estudianteId = target.getAttribute('data-id');
            if (confirm("¿Estás seguro de que deseas eliminar este tutor?")) {
                window.location.href = `/estudiantes/eliminar/${estudianteId}/`;
            }
        }
    });
});
