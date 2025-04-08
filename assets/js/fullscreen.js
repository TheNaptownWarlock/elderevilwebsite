document.addEventListener('DOMContentLoaded', function() {
    const fullscreenPopup = document.getElementById('fullscreen-popup');
    const fullscreenImage = document.querySelector('.fullscreen-image');
    const fullscreenDate = document.querySelector('.fullscreen-date');
    const fullscreenText = document.querySelector('.fullscreen-text');
    const closeFullscreen = document.querySelector('.close-fullscreen');

    // Add click event to all slideshow images
    document.querySelectorAll('.slide img').forEach(img => {
        img.addEventListener('click', function() {
            const slide = this.closest('.slide');
            const date = slide.querySelector('.image-date').textContent;
            const description = slide.querySelector('.slide-description p:not(.image-date)').textContent;

            fullscreenImage.src = this.src;
            fullscreenImage.alt = this.alt;
            fullscreenDate.textContent = date;
            fullscreenText.textContent = description;
            fullscreenPopup.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    // Close fullscreen popup
    closeFullscreen.addEventListener('click', function() {
        fullscreenPopup.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close when clicking outside the image
    fullscreenPopup.addEventListener('click', function(e) {
        if (e.target === fullscreenPopup) {
            fullscreenPopup.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Close with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && fullscreenPopup.classList.contains('active')) {
            fullscreenPopup.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}); 