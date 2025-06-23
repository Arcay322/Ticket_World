// static/js/carousel.js

document.addEventListener('DOMContentLoaded', () => {
    // Apuntamos al contenedor que se va a desplazar (el 'track' que contiene las tarjetas)
    const scroller = document.querySelector('.scrolling-track');

    // Si no hay un carrusel de este tipo en la página, no hacemos nada.
    if (!scroller) {
        return;
    }

    // El contenedor que usaremos para detectar el "mouseenter/mouseleave" (el 'wrapper')
    const wrapper = document.querySelector('.scrolling-wrapper');

    // 1. Clonar los elementos para crear el efecto infinito
    // Obtenemos los hijos DIRECTOS del scroller, que son nuestras tarjetas de evento.
    const scrollerContent = Array.from(scroller.children);

    // Es crucial tener suficientes elementos para que el efecto de loop sea suave.
    // Si hay menos de, digamos, 3-4 tarjetas, el loop puede no ser efectivo o verse raro.
    // Puedes ajustar 'minItemsForLoop' basado en cuántas tarjetas se ven simultáneamente.
    const minItemsForLoop = 4; // Si tienes 3-4 visibles, esto asegura al menos una repetición completa.

    // Si la cantidad de elementos originales es insuficiente para un loop continuo,
    // simplemente centramos los elementos y no aplicamos la animación.
    if (scrollerContent.length < minItemsForLoop) {
        if (wrapper) { // Asegúrate de que wrapper existe antes de intentar modificarlo
            wrapper.style.justifyContent = 'center'; // Centra los elementos si no hay suficientes para animar
            wrapper.style.overflowX = 'auto'; // Permite el scroll manual si hay más de los que caben
        }
        return; // Salir, no se necesita animación infinita
    }

    // Si hay suficientes elementos, procedemos a clonarlos.
    scrollerContent.forEach(item => {
        const duplicatedItem = item.cloneNode(true); // Clonamos el nodo y todo su contenido
        duplicatedItem.setAttribute('aria-hidden', true); // Ocultar los clones a lectores de pantalla para accesibilidad
        scroller.appendChild(duplicatedItem); // Añadimos el clon al final del scroller
    });

    // 2. Variable para controlar si el usuario tiene el cursor encima (pausar animación)
    let isPaused = false;
    if (wrapper) {
        wrapper.addEventListener('mouseenter', () => {
            isPaused = true;
        });
        wrapper.addEventListener('mouseleave', () => {
            isPaused = false;
        });
    }

    // 3. La función de animación
    let scrollPosition = 0;
    const scrollSpeed = 0.5; // Velocidad de desplazamiento (más bajo = más lento, más alto = más rápido)

    function animate() {
        if (!isPaused) {
            scrollPosition += scrollSpeed; // Incrementamos la posición de desplazamiento

            // Si hemos desplazado más allá de la longitud del contenido original (la mitad del total de contenido),
            // reseteamos la posición a 0 para crear el efecto infinito sin que el usuario lo note.
            // `scroller.scrollWidth` es el ancho total de TODO el contenido (original + clones).
            // `scroller.scrollWidth / 2` es el ancho del contenido original.
            if (scrollPosition >= scroller.scrollWidth / 2) {
                scrollPosition = 0;
            }
            // Aplicamos la transformación CSS para desplazar el carrusel
            scroller.style.transform = `translateX(-${scrollPosition}px)`;
        }

        // Llamamos al siguiente frame de la animación para mantener el bucle
        requestAnimationFrame(animate);
    }

    // ¡Iniciamos la animación al cargar la página!
    requestAnimationFrame(animate);
});