document.addEventListener('DOMContentLoaded', function () {
    const formFiltros = document.getElementById('form-filtros');
    const inputBusqueda = document.getElementById('input-busqueda');
    const inputFecha = document.getElementById('fecha');
    const tablaBody = document.getElementById('tabla-asistencias-body');
    const selectAllCheckbox = document.getElementById('select-all');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const checkboxes = document.querySelectorAll('.asistencia-checkbox');
            checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
        });
    }

    function actualizarTabla() {
        const params = new URLSearchParams(new FormData(formFiltros)).toString();
        fetch(`?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            tablaBody.innerHTML = data.html;
            if (selectAllCheckbox) selectAllCheckbox.checked = false;
        });
    }

    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', actualizarTabla);
    }

    if (formFiltros) {
        formFiltros.addEventListener('submit', function (e) {
            e.preventDefault();
            actualizarTabla();
        });
    }

    const tablaAsistenciasBody = document.getElementById('tabla-asistencias-body');

    if (tablaAsistenciasBody) {
        tablaAsistenciasBody.addEventListener('click', function (event) {
            const target = event.target;
            if (target.classList.contains('btn-eliminar')) {
                event.preventDefault();
                const asistenciaId = target.getAttribute('data-id');
                if (confirm("¿Estás seguro de que deseas eliminar esta asistencia?")) {
                    window.location.href = `/asistencias/eliminar/${asistenciaId}/`;
                }
            }
        });
    }

    const formAsistencias = document.getElementById('formAsistenciasSeleccionadas');
    if (formAsistencias) {
        formAsistencias.addEventListener('submit', function (e) {
            const seleccionados = document.querySelectorAll('.asistencia-checkbox:checked');
            if (seleccionados.length === 0) {
                e.preventDefault();
                alert("Por favor selecciona al menos una asistencia.");
            }
        });
    }
});
