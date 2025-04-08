document.addEventListener('DOMContentLoaded', function() {
    const imagePopup = document.getElementById('image-popup');
    const popupImage = document.querySelector('.popup-image');
    const popupDate = document.querySelector('.popup-description .image-date');
    const popupText = document.querySelector('.popup-description .image-text');
    const closePopup = document.querySelector('.close-popup');

    // Add click event to all slideshow images
    document.querySelectorAll('.slide img').forEach(img => {
        img.addEventListener('click', function() {
            const slide = this.closest('.slide');
            const date = slide.querySelector('.image-date').textContent;
            const description = slide.querySelector('.slide-description p:not(.image-date)').textContent;

            popupImage.src = this.src;
            popupImage.alt = this.alt;
            popupDate.textContent = date;
            popupText.textContent = description;
            imagePopup.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
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

    // Close with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && imagePopup.classList.contains('active')) {
            imagePopup.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}); 