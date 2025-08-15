const nivelSelect = document.getElementById("nivel");
const cursoSelect = document.getElementById("curso");
const fechaSelect = document.getElementById("fecha");
const chkCorrectas = document.getElementById("chk_correctas");
const chkIncorrectas = document.getElementById("chk_incorrectas");
const chkBlancas = document.getElementById("chk_blancas");

let grafico;
function mostrarImagenPregunta(nivel, curso, fecha) {
  // Si la fecha viene en formato DD/MM/AAAA, la convertimos a AAAA-MM-DD
  if(curso=="Rv"){
    curso = "Raz_Verbal"
  }else if(curso=="Rm"){
    curso = "Raz_Matemático"
  }else if(curso == "Ar"){
    curso = "Aritmética"
  }else if(curso == "Al"){
    curso = "Álgebra"
  }else if(curso == "Ge"){
    curso = "Geometría"
  }else if(curso == "Tr"){
    curso = "Trigonometría"
  }else if(curso == "Fi"){
    curso = "Física"
  }else if(curso == "Qu"){
    curso = "Química"
  }else if(curso == "Bi"){
    curso = "Biología"
  }else if(curso == "Le"){
    curso = "Lenguaje"
  }else if(curso == "Lit"){
    curso = "Literatura"
  }else if(curso == "Hi"){
    curso = "Historia"
  }else if(curso == "Gf"){
    curso = "Geografía"
  }else if(curso == "Fil"){
    curso = "Filosofía"
  }else if(curso == "Psi"){
    curso = "Psicología"
  }else if(curso == "Ec"){
    curso = "Economía"
  }
  
  if (fecha.includes("/")) {
    const partes = fecha.split("/");
    if (partes.length === 3) {
      // Asumimos DD/MM/AAAA → AAAA-MM-DD
      fecha = `${partes[2]}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}`;
    }
  }

  const carpeta = nivel.toLowerCase() === "pre" ? "pre" : "sem";
  const nombreArchivo = `${nivel.toLowerCase()}_${fecha}_${curso}.png`;
  const rutaImagen = `/media/preguntas/${carpeta}/${nombreArchivo}`;

  const contenedor = document.getElementById("contenedor-imagen-pregunta");
  contenedor.innerHTML = "";

  const img = document.createElement("img");
  img.src = rutaImagen;
  img.alt = "Pregunta del simulacro";
  img.style.width = "100%";
  img.style.height = "auto";
  img.classList.add("img-fluid", "shadow", "rounded", "my-3");

  img.onload = () => {
    contenedor.innerHTML = "";
    contenedor.appendChild(img);
  };
  img.onerror = () => {
    // ➤ Link corregido con formato fecha y curso adecuados
    const btn = document.createElement("a");
    btn.href = `/reportes/subir-preguntas/${nivel.toLowerCase()}/${fecha}/${curso}/`;
    btn.className = "btn btn-outline-primary";
    btn.textContent = "Subir imagen de este simulacro";
    contenedor.appendChild(btn);
  };
}
function mostrarImagenPregunta_respaldo(nivel, curso, fecha) {
  const cursoNombres = (
    "Raz_Verbal",
    "Raz_Matemático",
    "Aritmética",
    "Álgebra",
    "Geometría",
    "Trigonometría",
    "Física",
    "Química",
    "Biología",
    "Lenguaje",
    "Literatura",
    "Historia",
    "Geografía",
    "Filosofía",
    "Psicología",
    "Economía"
  );

  const nombreCurso = cursoNombres[curso] || curso;
  const carpeta = nivel.toLowerCase() === "pre" ? "pre" : "sem";
  const nombreArchivo = `${nivel.toLowerCase()}_${fecha}_${nombreCurso}.png`;
  const rutaImagen = `/media/preguntas/${carpeta}/${nombreArchivo}`;

  const contenedor = document.getElementById("contenedor-imagen-pregunta");
  contenedor.innerHTML = "";

  const img = new Image();
  img.src = rutaImagen;
  img.alt = "Pregunta del simulacro";
  img.classList.add("img-fluid", "shadow", "rounded", "my-3");
  img.onload = () => {
    contenedor.innerHTML = "";
    contenedor.appendChild(img);
  };
  img.onerror = () => {
    const btn = document.createElement("a");
    btn.href = `/subir-preguntas/${nivel.toLowerCase()}/${fecha}/${curso}/`;
    btn.className = "btn btn-outline-primary";
    btn.textContent = "Subir imagen de este simulacro";
    contenedor.appendChild(btn);
  };
}




function inicializarGrafico() {
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
        title: { display: true, text: 'Distribución por Intervalos' }
      }
    }
  });
}

function actualizarGrafico(data) {
  const mostrarCorrectas = chkCorrectas.checked;
  const mostrarIncorrectas = chkIncorrectas.checked;
  const mostrarBlancas = chkBlancas.checked;

  const datasets = [];

  if (mostrarCorrectas) {
    datasets.push({
      label: 'Correctas',
      data: data.correctas,
      borderColor: 'green',
      backgroundColor: 'green',
      fill: false
    });
  }

  if (mostrarIncorrectas) {
    datasets.push({
      label: 'Incorrectas',
      data: data.incorrectas,
      borderColor: 'red',
      backgroundColor: 'red',
      fill: false
    });
  }

  if (mostrarBlancas) {
    datasets.push({
      label: 'En blanco',
      data: data.blancas,
      borderColor: 'gray',
      backgroundColor: 'gray',
      fill: false
    });
  }

  grafico.data.labels = data.intervalos;
  grafico.data.datasets = datasets;
  grafico.update();
}

function cargarFechasDisponibles() {
  const nivel = nivelSelect.value;
  const curso = cursoSelect.value;
  if (!nivel || !curso) return;

  fetch(`/reportes/api/fechas-unicas/?nivel=${nivel}&curso=${curso}`)
  //fetch(`/reportes/api/fechas-unicas/?nivel=${nivel}&curso=${curso}`)
    .then(res => res.json())
    .then(data => {
      fechaSelect.innerHTML = '<option value="">Selecciona una fecha</option>';
      data.fechas.forEach(f => {
        const option = document.createElement('option');
        option.value = f;
        option.textContent = f;
        fechaSelect.appendChild(option);
      });
      fechaSelect.disabled = false;
    });
}

function cargarDistribucion() {
  const nivel = nivelSelect.value;
  const curso = cursoSelect.value;
  const fecha = fechaSelect.value;
  mostrarImagenPregunta(nivel, curso, fecha);
  if (!nivel || !curso || !fecha) return;


  fetch(`/reportes/api/distribucion-por-fecha/?nivel=${nivel}&curso=${curso}&fecha=${fecha}`)
  //fetch(`/reportes/api/distribucion-por-fecha/?nivel=${nivel}&curso=${curso}&fecha=${fecha}`)
    .then(res => res.json())
    .then(data => actualizarGrafico(data));
}

nivelSelect.addEventListener("change", () => {
  cursoSelect.disabled = nivelSelect.value === "";
  fechaSelect.disabled = true;
  cargarDistribucion();
});

cursoSelect.addEventListener("change", () => {
  if (cursoSelect.value !== "") {
    cargarFechasDisponibles();
  }
});

fechaSelect.addEventListener("change", cargarDistribucion);
chkCorrectas.addEventListener("change", cargarDistribucion);
chkIncorrectas.addEventListener("change", cargarDistribucion);
chkBlancas.addEventListener("change", cargarDistribucion);

window.addEventListener("load", inicializarGrafico);
