// static/js/scripts.js

// Elimina los mensajes después de que la animación termine
document.addEventListener('DOMContentLoaded', function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.remove();  // Elimina el mensaje del DOM
        }, 5000);  // 5 segundos
    });

    // Limpiar inputs en caso de error
    let form = document.getElementById('registroForm');
    let inputs = form.querySelectorAll('input, textarea, select');

    if (document.querySelector('.alert-error')) {
        inputs.forEach(function(input) {
            if (input.type !== 'submit' && input.type !== 'hidden') {
                input.value = '';  // Limpia el valor del input
            }
        });
    }
});