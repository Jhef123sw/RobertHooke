// static/js/filtrar_estudiante.js

document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("kk-usuario-select");
    if (!select) return;

    const searchBox = document.createElement("input");
    searchBox.type = "text";
    searchBox.className = "form-control mb-2";
    searchBox.placeholder = "Filtrar estudiante...";

    select.parentNode.insertBefore(searchBox, select);

    searchBox.addEventListener("input", function () {
        const filtro = this.value.toLowerCase();
        const opciones = select.options;
        for (let i = 0; i < opciones.length; i++) {
            const texto = opciones[i].text.toLowerCase();
            opciones[i].style.display = texto.includes(filtro) ? "" : "none";
        }
    });
});
