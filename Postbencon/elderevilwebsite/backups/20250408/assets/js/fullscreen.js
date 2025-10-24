document.addEventListener('DOMContentLoaded', function() {
    const imagePopup = document.getElementById('image-popup');
    const popupImage = document.querySelector('.popup-image');
    const popupDate = document.querySelector('.popup-description .image-date');
    const popupText = document.querySelector('.popup-description .image-text');
    const closePopup = document.querySelector('.close-popup');
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');

    let currentSlideIndex = 0;
    let slides = [];

    // Initialize slides array
    document.querySelectorAll('.slide').forEach(slide => {
        slides.push({
            image: slide.querySelector('img').src,
            alt: slide.querySelector('img').alt,
            date: slide.querySelector('.image-date').textContent,
            text: slide.querySelector('.slide-description p:not(.image-date)').textContent
        });
    });

    function updatePopupContent(index) {
        const slide = slides[index];
        popupImage.src = slide.image;
        popupImage.alt = slide.alt;
        popupDate.textContent = slide.date;
        popupText.textContent = slide.text;
    }

    function showNextSlide() {
        currentSlideIndex = (currentSlideIndex + 1) % slides.length;
        updatePopupContent(currentSlideIndex);
    }

    function showPrevSlide() {
        currentSlideIndex = (currentSlideIndex - 1 + slides.length) % slides.length;
        updatePopupContent(currentSlideIndex);
    }

    // Add click event to all slideshow images
    document.querySelectorAll('.slide img').forEach((img, index) => {
        img.addEventListener('click', function() {
            currentSlideIndex = index;
            updatePopupContent(currentSlideIndex);
            imagePopup.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    // Navigation buttons
    prevButton.addEventListener('click', showPrevSlide);
    nextButton.addEventListener('click', showNextSlide);

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (imagePopup.classList.contains('active')) {
            if (e.key === 'ArrowLeft') {
                showPrevSlide();
            } else if (e.key === 'ArrowRight') {
                showNextSlide();
            } else if (e.key === 'Escape') {
                imagePopup.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });

    // Close popup
    closePopup.addEventListener('click', function() {
        imagePopup.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close when clicking outside the popup content
    imagePopup.addEventListener('click', function(e) {
        if (e.target === imagePopup) {
            imagePopup.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}); 