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
    
    slideshows.forEach(slideshow => {
        const slides = slideshow.querySelectorAll('.slide');
        const prevBtn = slideshow.querySelector('.prev-btn');
        const nextBtn = slideshow.querySelector('.next-btn');
        let currentSlide = 0;

        // Add click event to images for fullscreen
        slides.forEach(slide => {
            const img = slide.querySelector('img');
            img.addEventListener('click', function() {
                const popup = document.getElementById('image-popup');
                const popupImg = popup.querySelector('.popup-image');
                const popupDesc = popup.querySelector('.popup-description');
                
                popupImg.src = this.src;
                popupImg.alt = this.alt;
                popupDesc.innerHTML = slide.querySelector('.slide-description').innerHTML;
                
                popup.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            });
        });

        // Close popup when clicking the close button
        const closePopup = document.querySelector('.close-popup');
        closePopup.addEventListener('click', function() {
            const popup = document.getElementById('image-popup');
            popup.style.display = 'none';
            document.body.style.overflow = 'auto';
        });

        // Close popup when clicking outside the image
        const popup = document.getElementById('image-popup');
        popup.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });

        // Show initial slide
        showSlide(currentSlide);

        // Previous button click handler
        prevBtn.addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        });

        // Next button click handler
        nextBtn.addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        });

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.style.display = i === index ? 'block' : 'none';
            });
        }
    });
}); 