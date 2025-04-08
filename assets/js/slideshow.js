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
    // Initialize all slideshows
    const slideshows = document.querySelectorAll('.slideshow-container');
    slideshows.forEach(initSlideshow);

    // Image popup functionality
    const popup = document.getElementById('image-popup');
    const popupImage = popup.querySelector('.popup-image');
    const popupDescription = popup.querySelector('.popup-description');
    const closePopup = popup.querySelector('.close-popup');

    // Add click event to all slideshow images
    document.querySelectorAll('.slideshow-image').forEach(img => {
        img.addEventListener('click', function() {
            popupImage.src = this.src;
            popupImage.alt = this.alt;
            
            // Get the description from the slide
            const description = this.nextElementSibling;
            if (description && description.classList.contains('slide-description')) {
                popupDescription.innerHTML = description.innerHTML;
            }
            
            popup.classList.add('active');
        });
    });

    // Close popup when clicking the close button
    closePopup.addEventListener('click', function() {
        popup.classList.remove('active');
    });

    // Close popup when clicking outside the image
    popup.addEventListener('click', function(e) {
        if (e.target === popup) {
            popup.classList.remove('active');
        }
    });

    // Close popup with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && popup.classList.contains('active')) {
            popup.classList.remove('active');
        }
    });
}); 