document.addEventListener('DOMContentLoaded', function() {
    const popup = document.getElementById('image-popup');
    const popupImage = popup.querySelector('.popup-image');
    const popupDescription = popup.querySelector('.popup-description');
    const closeButton = popup.querySelector('.close-popup');

    // Function to open popup
    function openPopup(imageSrc, description) {
        popupImage.src = imageSrc;
        popupImage.alt = description;
        popupDescription.textContent = description;
        popup.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when popup is open
    }

    // Function to close popup
    function closePopup() {
        popup.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }

    // Add click handlers to all slideshow images
    document.querySelectorAll('.slide img').forEach(img => {
        img.addEventListener('click', function(e) {
            e.stopPropagation();
            const description = this.nextElementSibling?.textContent || '';
            openPopup(this.src, description);
        });
    });

    // Close popup when clicking the close button
    closeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        closePopup();
    });

    // Close popup when clicking outside the image
    popup.addEventListener('click', function(e) {
        if (e.target === popup) {
            closePopup();
        }
    });

    // Close popup when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && popup.classList.contains('active')) {
            closePopup();
        }
    });
}); 