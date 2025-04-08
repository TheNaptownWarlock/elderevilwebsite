function initSlideshow(containerId) {
    const container = document.getElementById(containerId);
    const images = container.querySelectorAll('.slide');
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    let currentIndex = 0;

    // Hide all images except the first one
    images.forEach((img, index) => {
        img.style.display = index === 0 ? 'block' : 'none';
    });

    function showSlide(index) {
        images.forEach(img => img.style.display = 'none');
        images[index].style.display = 'block';
        
        // Add fade-in effect
        images[index].classList.add('fade-in');
        setTimeout(() => {
            images[index].classList.remove('fade-in');
        }, 500);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            showSlide(currentIndex);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
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