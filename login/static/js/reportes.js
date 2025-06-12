document.addEventListener("DOMContentLoaded", function () {
    const btnGenerar = document.getElementById("btn-generar");
    const barra = document.getElementById("barra-progreso");
    const mensaje = document.getElementById("mensaje-progreso");
    const contenedorProgreso = document.getElementById("progreso-container");

    if (btnGenerar) {
        btnGenerar.addEventListener("click", function () {
            fetch(btnGenerar.dataset.url)
                .then(response => response.json())
                .then(data => {
                    const taskId = data.task_id;
                    localStorage.setItem("task_reporte_id", taskId);
                    contenedorProgreso.style.display = "block";
                    verificarEstado(taskId);
                });
        });
    }

    const taskId = localStorage.getItem("task_reporte_id");
    if (taskId) {
        contenedorProgreso.style.display = "block";
        verificarEstado(taskId);
    }

    function verificarEstado(taskId) {
        const urlEstado = btnGenerar.dataset.estadoUrl.replace('REEMPLAZAR_ID', taskId);

        fetch(urlEstado)
            .then(response => response.json())
            .then(data => {
                if (data.state === 'PENDING') {
                    barra.style.width = '10%';
                    barra.textContent = 'Esperando...';
                    mensaje.textContent = 'Tarea en cola...';
                } else if (data.state === 'PROGRESO') {
                    const progreso = data.info.progress || 0;
                    const step = data.info.step || 'Trabajando...';
                    barra.style.width = progreso + '%';
                    barra.textContent = progreso + '%';
                    mensaje.textContent = step;
                } else if (data.state === 'SUCCESS') {
                    barra.style.width = '100%';
                    barra.textContent = '100%';
                    mensaje.textContent = '¡Tarea completada con éxito!';
                    localStorage.removeItem("task_reporte_id");
                    return;
                } else if (data.state === 'FAILURE') {
                    barra.style.background = 'red';
                    barra.textContent = 'Error';
                    mensaje.textContent = data.info.exc || 'Error inesperado';
                    localStorage.removeItem("task_reporte_id");
                    return;
                }

                setTimeout(() => verificarEstado(taskId), 2000);
            });
    }
});
