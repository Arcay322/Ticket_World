// static/js/animations.js

document.addEventListener("DOMContentLoaded", function() {
    const sections = document.querySelectorAll('.fade-in-section');

    if (sections.length === 0) return;

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1 // La animación se dispara cuando el 10% de la sección es visible
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Dejamos de observar la sección una vez que es visible
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });
});