document.addEventListener("DOMContentLoaded", function () {
    const inputBusqueda = document.getElementById('input-busqueda');
    const tablaBody = document.getElementById('tabla-estudiantes-body');
    const btnDescargar = document.getElementById('btn-descargar-reportes');
    const btnEliminar = document.getElementById('btn-eliminar-estudiantes');
    const btnEstudiantesExcel = document.getElementById('btn-descargar-estudiantes');
    const selectAllCheckbox = document.getElementById('select-all');

    function actualizarEstadoBotones() {
        const checkboxes = tablaBody.querySelectorAll('.estudiante-checkbox');
        const algunoSeleccionado = Array.from(checkboxes).some(cb => cb.checked);
        btnDescargar.disabled = !algunoSeleccionado;
        btnEliminar.disabled = !algunoSeleccionado;
        btnEstudiantesExcel.disabled = !algunoSeleccionado;
    }

    inputBusqueda.addEventListener('input', function () {
        const query = this.value;
        fetch(`?q=${encodeURIComponent(query)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            tablaBody.innerHTML = data.html;

            const nuevosCheckboxes = tablaBody.querySelectorAll('.estudiante-checkbox');
            nuevosCheckboxes.forEach(cb => {
                cb.addEventListener('change', actualizarEstadoBotones);
            });

            selectAllCheckbox.checked = false;
            actualizarEstadoBotones();
        });
    });

    selectAllCheckbox.addEventListener('change', function () {
        const checkboxes = tablaBody.querySelectorAll('.estudiante-checkbox');
        checkboxes.forEach(cb => cb.checked = this.checked);
        actualizarEstadoBotones();
    });

    tablaBody.querySelectorAll('.estudiante-checkbox').forEach(cb => {
        cb.addEventListener('change', actualizarEstadoBotones);
    });

    actualizarEstadoBotones();

    tablaBody.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('btn-eliminar')) {
            event.preventDefault();
            const estudianteId = target.getAttribute('data-id');
            if (confirm("¿Estás seguro de que deseas eliminar este estudiante?")) {
                window.location.href = `/estudiantes/eliminar/${estudianteId}/`;
            }
        }
    });
});
