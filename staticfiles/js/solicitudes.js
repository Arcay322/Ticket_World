document.querySelectorAll('.solicitud-header').forEach(header => {
    header.addEventListener('click', () => {
      const detalles = header.nextElementSibling;
      detalles.classList.toggle('visible');
    });
  });
  