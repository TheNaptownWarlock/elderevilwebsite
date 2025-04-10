// Popup functionality
let currentImageIndex = 0;
let currentImageSet = [];

function showPopup(imageSrc, description, imageSet) {
    const popup = document.getElementById('image-popup');
    const popupImage = popup.querySelector('.popup-image');
    const popupDescription = popup.querySelector('.popup-description');
    
    if (!popup || !popupImage || !popupDescription) {
        console.error('Popup elements not found');
        return;
    }
    
    popupImage.src = imageSrc;
    popupDescription.innerHTML = description;
    popup.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    currentImageSet = imageSet;
    currentImageIndex = imageSet.findIndex(img => img.src === imageSrc);
}

function closePopup() {
    const popup = document.getElementById('image-popup');
    if (popup) {
        popup.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function navigateImage(direction) {
    if (currentImageSet.length === 0) return;
    
    if (direction === 'prev') {
        currentImageIndex = (currentImageIndex - 1 + currentImageSet.length) % currentImageSet.length;
    } else {
        currentImageIndex = (currentImageIndex + 1) % currentImageSet.length;
    }
    
    const nextImage = currentImageSet[currentImageIndex];
    showPopup(nextImage.src, nextImage.description, currentImageSet);
}

// Auto-scroll functionality for slide descriptions
function setupAutoScroll() {
    const slides = document.querySelectorAll('.slide');
    
    slides.forEach(slide => {
        const description = slide.querySelector('.slide-description');
        if (!description) return;
        
        let scrollInterval;
        
        slide.addEventListener('mouseenter', () => {
            if (description.scrollHeight > description.clientHeight) {
                let scrollPosition = 0;
                const scrollStep = 1;
                const scrollDuration = 15; // seconds
                const totalSteps = (scrollDuration * 1000) / 16; // assuming 60fps
                
                scrollInterval = setInterval(() => {
                    scrollPosition += (description.scrollHeight - description.clientHeight) / totalSteps;
                    description.scrollTop = scrollPosition;
                    
                    if (scrollPosition >= description.scrollHeight - description.clientHeight) {
                        scrollPosition = 0;
                    }
                }, 16); // approximately 60fps
            }
        });
        
        slide.addEventListener('mouseleave', () => {
            if (scrollInterval) {
                clearInterval(scrollInterval);
                description.scrollTop = 0;
            }
        });
    });
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    setupAutoScroll();
    
    const popup = document.getElementById('image-popup');
    if (!popup) {
        console.error('Popup element not found');
        return;
    }

    const closeButton = popup.querySelector('.close-popup');
    const prevButton = popup.querySelector('.nav-button.prev');
    const nextButton = popup.querySelector('.nav-button.next');
    const necronomiconSound = document.getElementById('necronomicon-sound');
    
    if (closeButton) {
        closeButton.addEventListener('click', closePopup);
    }
    
    if (prevButton) {
        prevButton.addEventListener('click', () => navigateImage('prev'));
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', () => navigateImage('next'));
    }
    
    popup.addEventListener('click', function(e) {
        if (e.target === popup) {
            closePopup();
        }
    });
    
    // Add click events to all portfolio and slideshow images
    const images = document.querySelectorAll('.portfolio-item img, .slideshow img');
    images.forEach(img => {
        img.addEventListener('click', function() {
            const parentContainer = this.closest('.slideshow-container') || this.closest('.portfolio-item');
            if (!parentContainer) return;
            
            // Check if this is the Necro-NOM-icon slideshow
            if (parentContainer.id === 'necro-nom-icon-slideshow' && necronomiconSound) {
                necronomiconSound.currentTime = 0; // Reset the sound to start
                necronomiconSound.play().catch(error => {
                    console.error('Error playing sound:', error);
                });
            }
            
            const imageSet = Array.from(parentContainer.querySelectorAll('.slide'))
                .map(slide => {
                    const img = slide.querySelector('img');
                    const description = slide.querySelector('.slide-description');
                    return {
                        src: img.src,
                        description: description ? description.innerHTML : ''
                    };
                });
            
            const currentSlide = this.closest('.slide');
            const currentDescription = currentSlide ? currentSlide.querySelector('.slide-description').innerHTML : '';
            
            showPopup(this.src, currentDescription, imageSet);
        });
    });
}); 