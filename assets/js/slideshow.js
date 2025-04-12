function initSlideshow(containerId) {
    console.log(`Initializing slideshow: ${containerId}`);
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return;
    }
    console.log('Container found:', container);
    const slides = container.querySelectorAll('.slide');
    console.log('Number of slides:', slides.length);
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    let currentIndex = 0;

    // Initialize all slides
    slides.forEach((slide, index) => {
        console.log(`Initializing slide ${index}`);
        if (index === 0) {
            slide.style.opacity = '1';
            slide.classList.add('active');
            console.log('First slide set to active');
        } else {
            slide.style.opacity = '0';
            slide.classList.remove('active');
        }
    });

    function showSlide(index) {
        console.log(`Showing slide ${index}`);
        // Hide all slides
        slides.forEach(slide => {
            slide.style.opacity = '0';
            slide.classList.remove('active');
        });
        
        // Show current slide
        slides[index].style.opacity = '1';
        slides[index].classList.add('active');
        console.log('Slide shown:', slides[index]);
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
    console.log('DOM Content Loaded - Initializing slideshows');
    initSlideshow('jester-slideshow');
    initSlideshow('wizard-slideshow');
    initSlideshow('elder-evil-coffee-slideshow');
    initSlideshow('necro-nom-icon-slideshow');
    initSlideshow('elder-cow-slideshow');
    initSlideshow('boozin-slideshow');
    initSlideshow('merch-slideshow');
}); 