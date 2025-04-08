function initSlideshow(containerId) {
    const container = document.getElementById(containerId);
    const images = container.querySelectorAll('.slide');
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    let currentIndex = 0;

    // Initialize all slides
    images.forEach((img, index) => {
        img.style.opacity = index === 0 ? '1' : '0';
        img.classList.toggle('active', index === 0);
    });

    function showSlide(index) {
        // Remove active class from all slides
        images.forEach(img => {
            img.style.opacity = '0';
            img.classList.remove('active');
        });
        
        // Add active class to current slide
        images[index].style.opacity = '1';
        images[index].classList.add('active');
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event from bubbling to the image
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            showSlide(currentIndex);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event from bubbling to the image
            currentIndex = (currentIndex + 1) % images.length;
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