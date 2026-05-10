/**
 * Simple Room Gallery Component
 * Handles primary photo and additional images with basic navigation
 */
class SimpleRoomGallery {
    constructor() {
        this.currentImages = [];
        this.currentIndex = 0;
        this.touchStartX = 0;
        this.touchEndX = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardControls();
        this.setupTouchControls();
    }
    
    // Open gallery with images
    open(images, startIndex = 0) {
        this.currentImages = images;
        this.currentIndex = Math.max(0, Math.min(startIndex, images.length - 1));
        
        if (images.length === 0) {
            alert('No images available for this room.');
            return;
        }
        
        this.updateGallery();
        this.showModal();
    }
    
    // Update gallery display
    updateGallery() {
        if (!this.currentImages.length) return;
        
        const image = this.currentImages[this.currentIndex];
        
        // Update main image
        const mainImage = document.getElementById('galleryMainImage');
        if (mainImage) {
            mainImage.src = image.url;
            mainImage.alt = `${image.room_code || 'Room'} - Image ${this.currentIndex + 1}`;
        }
        
        // Update counter
        const currentIndexEl = document.getElementById('galleryCurrentIndex');
        const totalImagesEl = document.getElementById('galleryTotalImages');
        if (currentIndexEl) currentIndexEl.textContent = this.currentIndex + 1;
        if (totalImagesEl) totalImagesEl.textContent = this.currentImages.length;
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    // Update navigation button states
    updateNavigationButtons() {
        const prevBtn = document.getElementById('galleryPrev');
        const nextBtn = document.getElementById('galleryNext');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentIndex === 0;
            prevBtn.style.opacity = this.currentIndex === 0 ? '0.3' : '0.8';
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentIndex === this.currentImages.length - 1;
            nextBtn.style.opacity = this.currentIndex === this.currentImages.length - 1 ? '0.3' : '0.8';
        }
    }
    
    // Navigation methods
    next() {
        if (this.currentIndex < this.currentImages.length - 1) {
            this.currentIndex++;
            this.updateGallery();
        }
    }
    
    previous() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateGallery();
        }
    }
    
    // Modal management
    showModal() {
        const modal = document.getElementById('roomGalleryModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }
    
    hideModal() {
        const modal = document.getElementById('roomGalleryModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
    
    // Event listeners
    setupEventListeners() {
        // Navigation buttons
        document.getElementById('galleryPrev')?.addEventListener('click', () => this.previous());
        document.getElementById('galleryNext')?.addEventListener('click', () => this.next());
    }
    
    // Keyboard controls
    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            const modal = document.getElementById('roomGalleryModal');
            if (!modal || !modal.classList.contains('show')) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previous();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.next();
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.hideModal();
                    break;
            }
        });
    }
    
    // Touch controls
    setupTouchControls() {
        const mainImage = document.getElementById('galleryMainImage');
        if (!mainImage) return;
        
        mainImage.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        mainImage.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    }
    
    handleSwipe() {
        const swipeThreshold = 50;
        const diff = this.touchStartX - this.touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next image
                this.next();
            } else {
                // Swipe right - previous image
                this.previous();
            }
        }
    }
}

// Global gallery instance
window.roomGallery = new SimpleRoomGallery();

// Global function for opening gallery
window.openRoomGallery = function(roomId, roomCode, images) {
    window.roomGallery.open(images, 0);
    
    // Update gallery title
    const titleEl = document.getElementById('galleryRoomCode');
    if (titleEl) {
        titleEl.textContent = roomCode;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple Room Gallery initialized');
});
