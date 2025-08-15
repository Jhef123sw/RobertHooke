const nivelInput = document.getElementById("nivel");
const cursoInput = document.getElementById("curso");
const tipoInput = document.getElementById("tipo");

let grafico;

function cargarGrafico() {
  const nivel = nivelInput.value;
  const curso = cursoInput.value;
  const tipo = tipoInput.value;

  if (!nivel || !curso || !tipo) return;

  fetch(`/reportes/api/grafico-por-tipo/?nivel=${nivel}&curso=${curso}&tipo=${tipo}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }

      const labels = data.fechas;
      const datasets = data.series.map(serie => ({
        label: serie.intervalo,
        data: serie.valores,
        fill: false,
        borderColor: serie.color,
        tension: 0.1
      }));

      grafico.data.labels = labels;
      grafico.data.datasets = datasets;
      grafico.update();
    });
}

nivelInput.addEventListener("change", () => {
  cursoInput.disabled = nivelInput.value === "";
  tipoInput.disabled = true;
  tipoInput.value = "";
});

cursoInput.addEventListener("change", () => {
  tipoInput.disabled = cursoInput.value === "";
});

tipoInput.addEventListener("change", cargarGrafico);

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
        title: {
          display: true,
          text: "Evolución por Intervalos"
        },
        legend: {
          position: "top"
        }
      }
    }
  });
});
