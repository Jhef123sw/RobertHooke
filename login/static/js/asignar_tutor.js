let tutorSeleccionadoId = null;

function mostrarMarcadorSiVacio() {
    const lista = document.getElementById('lista-alumnos-tutor');
    if (lista.children.length === 0) {
        const placeholder = document.createElement('li');
        placeholder.textContent = 'Arrastra alumnos aquí';
        placeholder.style.fontStyle = 'italic';
        placeholder.style.color = '#888';
        placeholder.style.pointerEvents = 'none';
        placeholder.className = 'placeholder';
        lista.appendChild(placeholder);
    } else {
        const placeholder = lista.querySelector('.placeholder');
        if (placeholder) placeholder.remove();
    }
}

function actualizarAlumnosDeTutor() {
    fetch(`/obtener-estudiantes/${tutorSeleccionadoId}/`)
        .then(res => res.json())
        .then(data => {
            const lista = document.getElementById('lista-alumnos-tutor');
            lista.innerHTML = '';
            data.forEach(est => {
                const li = document.createElement('li');
                li.dataset.id = est.ID_Estudiante;
                li.draggable = true;
                li.className = 'estudiante';
                li.innerHTML = `<input type="checkbox" class="select-asignado" /> ${est.usuario} ${est.nombre}`;
                lista.appendChild(li);
            });
            setCheckboxHandlers();
            setDragEvents();
            mostrarMarcadorSiVacio();
        });
}

function actualizarListaGeneral() {
    fetch(`/obtener-todos-estudiantes/`)
        .then(res => res.json())
        .then(data => {
            const lista = document.querySelector('#estudiantes ul');
            lista.innerHTML = '';
            data.forEach(est => {
                const li = document.createElement('li');
                li.dataset.id = est.ID_Estudiante;
                li.className = 'estudiante';
                li.innerHTML = `<input type="checkbox" class="select-estudiante" />
                                ${est.usuario} ${est.nombre}
                                ${est.tutor ? `<span style="font-size: 0.8em; color: #888;">(Asignado ${est.tutor})</span>` : ''}`;
                
                if (!est.tutor) {
                    li.draggable = true;
                } else {
                    li.style.opacity = 0.6;
                    li.style.cursor = 'not-allowed';
                }

                lista.appendChild(li);
            });
            setCheckboxHandlers();
            setDragEvents();
        });
}

function setCheckboxHandlers() {
    document.getElementById('checkAllEstudiantes')?.addEventListener('change', function () {
        document.querySelectorAll('.select-estudiante').forEach(cb => {
            const li = cb.closest('li');
            const visible = li.offsetParent !== null;
            const habilitado = !cb.disabled;
            cb.checked = this.checked && visible && habilitado;
        });
    });

    document.getElementById('checkAllAsignados')?.addEventListener('change', function () {
        document.querySelectorAll('.select-asignado').forEach(cb => cb.checked = this.checked);
    });
}

function setDragEvents() {
    document.querySelectorAll('li.estudiante').forEach(li => {
        li.addEventListener('dragstart', e => {
            const selected = Array.from(document.querySelectorAll('.select-estudiante:checked, .select-asignado:checked'));
            const ids = selected.map(cb => cb.parentElement.dataset.id);
            e.dataTransfer.setData('ids', JSON.stringify(ids));
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tutor').forEach(tutor => {
        tutor.addEventListener('click', function () {
            tutorSeleccionadoId = this.dataset.id;
            document.getElementById('nombre-tutor').innerText = this.innerText;
            actualizarAlumnosDeTutor();
        });
    });

    setCheckboxHandlers();
    setDragEvents();

    const listaGeneral = document.querySelector('#estudiantes ul');
    const listaTutor = document.getElementById('lista-alumnos-tutor');

    listaTutor.addEventListener('dragover', e => e.preventDefault());
    listaTutor.addEventListener('drop', e => {
        e.preventDefault();
        const ids = JSON.parse(e.dataTransfer.getData('ids'));
        Promise.all(ids.map(id =>
            fetch('/asignar-estudiante/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: new URLSearchParams({ estudiante_id: id, tutor_id: tutorSeleccionadoId })
            })
        )).then(() => {
            actualizarAlumnosDeTutor();
            actualizarListaGeneral();
        });
    });

    listaGeneral.addEventListener('dragover', e => e.preventDefault());
    listaGeneral.addEventListener('drop', e => {
        e.preventDefault();
        const ids = JSON.parse(e.dataTransfer.getData('ids'));
        Promise.all(ids.map(id =>
            fetch('/desasignar-estudiante/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: new URLSearchParams({ estudiante_id: id })
            })
        )).then(() => {
            actualizarAlumnosDeTutor();
            actualizarListaGeneral();
        });
    });

    document.getElementById('busqueda-estudiantes').addEventListener('input', aplicarFiltros);
    document.getElementById('filtro-asignados').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-desasignados').addEventListener('change', aplicarFiltros);
});

function aplicarFiltros() {
    const texto = document.getElementById('busqueda-estudiantes').value.toLowerCase();
    const mostrarAsignados = document.getElementById('filtro-asignados').checked;
    const mostrarDesasignados = document.getElementById('filtro-desasignados').checked;

    document.querySelectorAll('#estudiantes ul li').forEach(li => {
        const esAsignado = li.innerHTML.includes('(Asignado');
        const coincideBusqueda = li.textContent.toLowerCase().includes(texto);
        const mostrar = coincideBusqueda && ((esAsignado && mostrarAsignados) || (!esAsignado && mostrarDesasignados));
        li.style.display = mostrar ? 'flex' : 'none';
    });
}
