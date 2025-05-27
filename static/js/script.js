function moveCategories(direction) {
    const container = document.querySelector('.categories-section');
    const cardWidth = document.querySelector('.category-card').offsetWidth + 20;
    container.scrollBy({
        left: direction * cardWidth,
        behavior: 'smooth'
    });
}
