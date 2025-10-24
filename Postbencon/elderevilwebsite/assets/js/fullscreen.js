// Fullscreen image popup functionality
document.addEventListener('DOMContentLoaded', function() {
    const fullscreenPopup = document.getElementById('fullscreen-popup');
    const fullscreenImage = document.querySelector('.fullscreen-image');
    const fullscreenDate = document.querySelector('.fullscreen-date');
    const fullscreenText = document.querySelector('.fullscreen-text');
    const closeFullscreen = document.querySelector('.close-fullscreen');

    // Function to show fullscreen popup
    function showFullscreen(imageSrc, date, description) {
        fullscreenImage.src = imageSrc;
        fullscreenDate.textContent = date;
        fullscreenText.textContent = description;
        fullscreenPopup.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    // Function to close fullscreen popup
    function closeFullscreenPopup() {
        fullscreenPopup.style.display = 'none';
        document.body.style.overflow = '';
    }

    // Close fullscreen popup when clicking the close button
    closeFullscreen.addEventListener('click', closeFullscreenPopup);

    // Close fullscreen popup when clicking outside the image
    fullscreenPopup.addEventListener('click', function(e) {
        if (e.target === fullscreenPopup) {
            closeFullscreenPopup();
        }
    });

    // Make the showFullscreen function available globally
    window.showFullscreen = showFullscreen;
}); 