document.addEventListener('DOMContentLoaded', () => {
    const scroller = document.querySelector('.scrolling-track');

    // Si no hay carrusel en la página, no hacemos nada.
    if (!scroller) {
        return;
    }

    // 1. Clonar los elementos para crear el efecto infinito
    const scrollerContent = Array.from(scroller.children);
    scrollerContent.forEach(item => {
        const duplicatedItem = item.cloneNode(true);
        duplicatedItem.setAttribute('aria-hidden', true); // Ocultar los clones a lectores de pantalla
        scroller.appendChild(duplicatedItem);
    });

    // 2. Variable para controlar si el usuario tiene el cursor encima
    let isPaused = false;
    // Usamos el contenedor '.scrolling-wrapper' para pausar, es más grande y fiable.
    const wrapper = document.querySelector('.scrolling-wrapper');
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
    const scrollSpeed = 0.5; // Puedes ajustar este valor (más bajo = más lento)

    function animate() {
        if (!isPaused) {
            scrollPosition += scrollSpeed;
            
            // Si hemos desplazado todo el contenido original, reseteamos a 0 sin que se note
            if (scrollPosition >= scroller.scrollWidth / 2) {
                scrollPosition = 0;
            }
            scroller.style.transform = `translateX(-${scrollPosition}px)`;
        }
        
        // Llamamos al siguiente frame de la animación
        requestAnimationFrame(animate);
    }

    // ¡Iniciamos la animación!
    requestAnimationFrame(animate);
});