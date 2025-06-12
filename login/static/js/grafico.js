const estudianteInput = document.getElementById("estudiante");
const cursoInput = document.getElementById("curso");
const buscador = document.getElementById("buscador");
const chkCorrectas = document.getElementById("chk_correctas");
const chkIncorrectas = document.getElementById("chk_incorrectas");
const chkBlancas = document.getElementById("chk_blancas");

let grafico;
let datosOriginales;

// apiUrl debe estar definido por la plantilla Django
function cargarDatos() {
    const usuario = estudianteInput.value;
    const curso = cursoInput.value;
    if (!usuario || !curso) return;

    fetch(`/reportes${apiUrl}?usuario=${usuario}&curso=${curso}`)
        .then(res => res.json())
        .then(data => {
            datosOriginales = data;
            actualizarGrafico();
        });
}

function actualizarGrafico() {
    if (!datosOriginales) return;

    const mostrarCorrectas = chkCorrectas.checked;
    const mostrarIncorrectas = chkIncorrectas.checked;
    const mostrarBlancas = chkBlancas.checked;

    const labels = datosOriginales.map(d => d.fecha);
    const datasets = [];

    if (mostrarCorrectas) {
        datasets.push({
            label: 'Correctas',
            data: datosOriginales.map(d => d.correctas),
            borderColor: 'green',
            fill: false
        });
    }

    if (mostrarIncorrectas) {
        datasets.push({
            label: 'Incorrectas',
            data: datosOriginales.map(d => d.incorrectas),
            borderColor: 'red',
            fill: false
        });
    }

    if (mostrarBlancas) {
        datasets.push({
            label: 'En blanco',
            data: datosOriginales.map(d => d.blancas),
            borderColor: 'grey',
            fill: false
        });
    }

    grafico.data.labels = labels;
    grafico.data.datasets = datasets;
    grafico.update();
}

buscador.addEventListener("input", () => {
    const filtro = buscador.value.toLowerCase();
    [...estudianteInput.options].forEach(op => {
        const texto = op.text.toLowerCase();
        op.style.display = texto.includes(filtro) ? "block" : "none";
    });
});

estudianteInput.addEventListener("change", () => {
    cursoInput.disabled = estudianteInput.value === "";
    cargarDatos();
});

cursoInput.addEventListener("change", cargarDatos);
chkCorrectas.addEventListener("change", actualizarGrafico);
chkIncorrectas.addEventListener("change", actualizarGrafico);
chkBlancas.addEventListener("change", actualizarGrafico);

window.addEventListener("load", () => {
    const ctx = document.getElementById("grafico").getContext("2d");
    grafico = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true,
                    text: 'Evolución de Preguntas'
                }
            }
        }
    });
});
