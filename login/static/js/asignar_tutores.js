
        let tutorSeleccionadoId = null;

        document.querySelectorAll('.tutor').forEach(tutor => {
            tutor.addEventListener('click', function() {
                tutorSeleccionadoId = this.dataset.id;
                document.getElementById('nombre-tutor').innerText = this.innerText;
                fetch(`/obtener-estudiantes/${tutorSeleccionadoId}/`)
                    .then(res => res.json())
                    .then(data => {
                        const lista = document.getElementById('lista-alumnos-tutor');
                        lista.innerHTML = '';
                        data.forEach(est => {
                            const li = document.createElement('li');
                            li.innerText = est.nombre;
                            li.dataset.id = est.ID_Estudiante;
                            li.draggable = true;
                            li.className = 'estudiante';
                            lista.appendChild(li);
                        });
                    });
            });
        });

        function addDragEvents(element) {
            element.addEventListener('dragstart', e => {
                e.dataTransfer.setData('id', element.dataset.id);
            });
        }

        document.querySelectorAll('.estudiante').forEach(addDragEvents);

        const listaGeneral = document.querySelector('#estudiantes ul');
        const listaTutor = document.getElementById('lista-alumnos-tutor');

        listaTutor.addEventListener('dragover', e => e.preventDefault());
        listaTutor.addEventListener('drop', e => {
            e.preventDefault();
            const id = e.dataTransfer.getData('id');
            fetch('/asignar-estudiante/', {
                method: 'POST',
                headers: {'X-CSRFToken': '{{ csrf_token }}'},
                body: new URLSearchParams({ estudiante_id: id, tutor_id: tutorSeleccionadoId })
            }).then(() => location.reload());
        });

        listaGeneral.addEventListener('dragover', e => e.preventDefault());
        listaGeneral.addEventListener('drop', e => {
            e.preventDefault();
            const id = e.dataTransfer.getData('id');
            fetch('/desasignar-estudiante/', {
                method: 'POST',
                headers: {'X-CSRFToken': '{{ csrf_token }}'},
                body: new URLSearchParams({ estudiante_id: id })
            }).then(() => location.reload());
        });