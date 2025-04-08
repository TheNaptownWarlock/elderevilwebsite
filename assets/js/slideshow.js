function initSlideshow(containerId) {
    const container = document.getElementById(containerId);
    const slides = container.querySelectorAll('.slide');
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    let currentIndex = 0;

    // Initialize all slides
    slides.forEach((slide, index) => {
        if (index === 0) {
            slide.style.opacity = '1';
            slide.classList.add('active');
        } else {
            slide.style.opacity = '0';
            slide.classList.remove('active');
        }
    });

    function showSlide(index) {
        // Hide all slides
        slides.forEach(slide => {
            slide.style.opacity = '0';
            slide.classList.remove('active');
        });
        
        // Show current slide
        slides[index].style.opacity = '1';
        slides[index].classList.add('active');
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(currentIndex);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            currentIndex = (currentIndex + 1) % slides.length;
            showSlide(currentIndex);
        });
    }
}

// Initialize all slideshows when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSlideshow('jester-slideshow');
    initSlideshow('wizard-slideshow');
    initSlideshow('elder-evil-coffee-slideshow');
    initSlideshow('necro-nom-icon-slideshow');
    initSlideshow('elder-cow-slideshow');
}); 