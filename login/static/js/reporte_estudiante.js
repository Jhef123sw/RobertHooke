function filtrarGraficos() {
    let cursoSeleccionado = document.getElementById("filtro-curso").value;
    let fechaSeleccionada = document.getElementById("filtro-fecha").value;
    let graficos = document.querySelectorAll(".grafico");

    graficos.forEach(grafico => {
        let curso = grafico.dataset.curso;
        let fecha = grafico.dataset.fecha;

        let mostrarPorCurso = (cursoSeleccionado === "todos" || curso === cursoSeleccionado);
        let mostrarPorFecha = (fechaSeleccionada === "todas" || fecha === fechaSeleccionada);

        grafico.style.display = (mostrarPorCurso && mostrarPorFecha) ? "block" : "none";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("filtro-curso").addEventListener("change", filtrarGraficos);
    document.getElementById("filtro-fecha").addEventListener("change", filtrarGraficos);
});
