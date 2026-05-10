/**
 * Modern Room Image Carousel System
 * Airbnb-style immersive image viewing experience
 * Production-ready with clean architecture
 */
class RoomImageCarousel {
    constructor() {
        // State management
        this.currentIndex = 0;
        this.images = [];
        this.isOpen = false;
        
        // Touch gesture tracking
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.touchThreshold = 50;
        
        // Performance optimization
        this.preloadedImages = new Set();
        
        // UI elements cache
        this.modal = null;
        this.imageContainer = null;
        this.imageElement = null;
        this.counterElement = null;
        this.prevButton = null;
        this.nextButton = null;
        this.closeButton = null;
        
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.setupEventListeners();
        this.setupKeyboardSupport();
        this.setupTouchSupport();
    }
    
    cacheElements() {
        this.modal = document.getElementById('roomImageCarousel');
        this.imageContainer = document.getElementById('carouselImageContainer');
        this.imageElement = document.getElementById('carouselImage');
        this.counterElement = document.getElementById('carouselCounter');
        this.prevButton = document.getElementById('carouselPrev');
        this.nextButton = document.getElementById('carouselNext');
        this.closeButton = document.getElementById('carouselClose');
    }
    
    // ========================================
    // CORE CAROUSEL LOGIC
    // ========================================
    
    openModal(imageList, startIndex = 0) {
        if (!imageList || imageList.length === 0) {
            console.warn('No images provided to carousel');
            return;
        }
        
        // Set state
        this.images = imageList;
        this.currentIndex = Math.max(0, Math.min(startIndex, imageList.length - 1));
        this.isOpen = true;
        
        // Update UI
        this.updateImage();
        this.updateCounter();
        this.updateNavigationButtons();
        
        // Show modal
        this.showModal();
        
        // Preload adjacent images
        this.preloadAdjacentImages();
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    closeModal() {
        if (!this.isOpen) return;
        
        this.isOpen = false;
        this.hideModal();
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Clear preloaded images
        this.preloadedImages.clear();
    }
    
    showImage(index) {
        if (index < 0 || index >= this.images.length) return;
        
        this.currentIndex = index;
        this.updateImage();
        this.updateCounter();
        this.updateNavigationButtons();
        this.preloadAdjacentImages();
    }
    
    nextImage() {
        if (this.currentIndex < this.images.length - 1) {
            this.showImage(this.currentIndex + 1);
        }
    }
    
    prevImage() {
        if (this.currentIndex > 0) {
            this.showImage(this.currentIndex - 1);
        }
    }
    
    // ========================================
    // UI UPDATE METHODS
    // ========================================
    
    updateImage() {
        if (!this.imageElement || !this.images[this.currentIndex]) return;
        
        const image = this.images[this.currentIndex];
        
        // Smooth fade transition
        this.imageElement.style.opacity = '0';
        
        setTimeout(() => {
            this.imageElement.src = image.url;
            this.imageElement.alt = `${image.room_code || 'Room'} - Image ${this.currentIndex + 1}`;
            this.imageElement.style.opacity = '1';
        }, 150);
    }
    
    updateCounter() {
        if (!this.counterElement) return;
        this.counterElement.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
    }
    
    updateNavigationButtons() {
        if (!this.prevButton || !this.nextButton) return;
        
        // Previous button state
        this.prevButton.disabled = this.currentIndex === 0;
        this.prevButton.style.opacity = this.currentIndex === 0 ? '0.3' : '0.8';
        
        // Next button state  
        this.nextButton.disabled = this.currentIndex === this.images.length - 1;
        this.nextButton.style.opacity = this.currentIndex === this.images.length - 1 ? '0.3' : '0.8';
    }
    
    showModal() {
        if (!this.modal) return;
        
        this.modal.style.display = 'flex';
        // Trigger reflow for animation
        this.modal.offsetHeight;
        this.modal.classList.add('show');
    }
    
    hideModal() {
        if (!this.modal) return;
        
        this.modal.classList.remove('show');
        setTimeout(() => {
            this.modal.style.display = 'none';
        }, 300);
    }
    
    // ========================================
    // EVENT LISTENERS
    // ========================================
    
    setupEventListeners() {
        // Navigation buttons
        this.prevButton?.addEventListener('click', () => this.prevImage());
        this.nextButton?.addEventListener('click', () => this.nextImage());
        this.closeButton?.addEventListener('click', () => this.closeModal());
        
        // Close on backdrop click
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
    }
    
    setupKeyboardSupport() {
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.prevImage();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextImage();
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.closeModal();
                    break;
            }
        });
    }
    
    setupTouchSupport() {
        if (!this.imageContainer) return;
        
        this.imageContainer.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        this.imageContainer.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    }
    
    handleSwipe() {
        const diff = this.touchStartX - this.touchEndX;
        
        if (Math.abs(diff) > this.touchThreshold) {
            if (diff > 0) {
                // Swipe left - next image
                this.nextImage();
            } else {
                // Swipe right - previous image
                this.prevImage();
            }
        }
    }
    
    // ========================================
    // PERFORMANCE OPTIMIZATIONS
    // ========================================
    
    preloadAdjacentImages() {
        const adjacentIndices = [
            this.currentIndex - 1,
            this.currentIndex + 1
        ];
        
        adjacentIndices.forEach(index => {
            if (index >= 0 && index < this.images.length && !this.preloadedImages.has(index)) {
                const img = new Image();
                img.src = this.images[index].url;
                this.preloadedImages.add(index);
            }
        });
    }
    
    // ========================================
    // CLEANUP
    // ========================================
    
    destroy() {
        this.closeModal();
        
        // Remove event listeners
        this.prevButton?.removeEventListener('click', () => this.prevImage());
        this.nextButton?.removeEventListener('click', () => this.nextImage());
        this.closeButton?.removeEventListener('click', () => this.closeModal());
        
        // Clear cache
        this.preloadedImages.clear();
    }
}

// Global carousel instance
let roomCarousel = null;

// Global function for opening carousel
window.openRoomCarousel = function(roomId, roomCode, images) {
    if (!roomCarousel) {
        roomCarousel = new RoomImageCarousel();
    }
    
    roomCarousel.openModal(images, 0);
    
    // Update room code in UI if needed
    const titleElement = document.getElementById('carouselRoomCode');
    if (titleElement) {
        titleElement.textContent = roomCode;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    roomCarousel = new RoomImageCarousel();
    console.log('Room Image Carousel initialized');
});
