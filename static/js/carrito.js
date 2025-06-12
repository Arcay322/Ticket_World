// static/js/carrito.js

document.addEventListener('DOMContentLoaded', function() {
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    document.querySelectorAll('.input-cantidad').forEach(input => {
        // Usamos el evento 'input' para una respuesta en tiempo real
        input.addEventListener('input', function() {
            const boletoId = this.dataset.boletoId;
            let cantidad = parseInt(this.value);
            const maxStock = parseInt(this.max);

            // Si el usuario escribe algo que no es un número (queda NaN), lo tratamos como 1
            if (isNaN(cantidad)) {
                cantidad = 1;
            }

            // Validamos que la cantidad no exceda el stock máximo
            if (cantidad > maxStock) {
                // Mostramos la alerta profesional
                Swal.fire({
                    icon: 'error',
                    title: 'Stock Insuficiente',
                    text: `La cantidad no puede superar el stock disponible de ${maxStock} boletos.`,
                    confirmButtonColor: '#00acc1'
                });
                // Corregimos el valor en el campo al máximo permitido
                this.value = maxStock;
                return; // Detenemos la ejecución
            }

            // Si el usuario borra el campo o pone 0, lo forzamos a 1
            if (cantidad < 1) {
                this.value = 1;
                // No hacemos nada más, esperamos a que el usuario ponga un número válido
                return;
            }
            
            // Si todo está bien, actualizamos el carrito.
            // Para evitar sobrecargar el servidor con cada tecla, podrías añadir un 'debounce' aquí
            // pero por ahora lo mantenemos simple.
            actualizarCarrito(boletoId, cantidad);
        });
    });

    function actualizarCarrito(boletoId, cantidad) {
        fetch('/tickets/actualizar-carrito/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                'boleto_id': boletoId,
                'cantidad': cantidad
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => Promise.reject(errorData));
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // La recarga es la forma más simple de asegurar que los totales se actualizan.
                // Podríamos hacerlo sin recargar, pero aumenta la complejidad.
                location.reload(); 
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: error.message || 'Ocurrió un error al actualizar el carrito.',
                confirmButtonColor: '#00acc1'
            });
        });
    }
});