document.addEventListener('DOMContentLoaded', function() {
    
    /**
     * Función de Scroll Suave Personalizada
     * @param {number} endY - La posición Y final a la que se debe desplazar.
     * @param {number} duration - La duración de la animación en milisegundos.
     */
    function customSmoothScroll(endY, duration) {
        const startY = window.scrollY;
        const distanceY = endY - startY;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            
            // Fórmula de easing (ease-in-out) para un inicio y final suaves
            const ease = 0.5 * (1 - Math.cos(Math.PI * progress));

            window.scrollTo(0, startY + distanceY * ease);

            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        }

        requestAnimationFrame(animation);
    }

    // --- Lógica Principal (igual que antes, pero ahora usa nuestra función) ---

    const urlParams = new URLSearchParams(window.location.search);
    const urlHash = window.location.hash;

    let targetElement = null;

    if (urlHash) {
        targetElement = document.querySelector(urlHash); 
    } else if (urlParams.has('q') || urlParams.has('categoria')) {
        targetElement = document.getElementById('titulo-eventos');
    }

    if (targetElement) {
        const offset = 20; 
        
        // El timeout sigue siendo útil para evitar el salto inicial del navegador
        setTimeout(() => {
            const bodyRect = document.body.getBoundingClientRect().top;
            const elementRect = targetElement.getBoundingClientRect().top;
            const elementPosition = elementRect - bodyRect;
            const offsetPosition = elementPosition - offset;
            
            // --- LLAMADA A LA NUEVA FUNCIÓN ---
            // Aquí definimos la duración. 800ms es un buen valor para un scroll suave.
            // Puedes cambiarlo a 1000 (1 segundo) para hacerlo aún más lento.
            customSmoothScroll(offsetPosition, 800);

        }, 100);
    }
});