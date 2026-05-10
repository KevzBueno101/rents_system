/**
 * Inline carousel for room Edit and View Details modals.
 * One image is displayed at a time; navigation updates the existing DOM.
 */
(function () {
    class RoomInlineCarousel {
        constructor(container, images, options = {}) {
            this.container = container;
            this.images = Array.isArray(images) ? images : [];
            this.roomCode = options.roomCode || 'Room';
            this.height = options.height || '240px';
            this.currentIndex = Math.max(0, Math.min(options.startIndex || 0, this.images.length - 1));
            this.touchStartX = 0;
            this.touchEndX = 0;
            this.touchThreshold = 45;
            this.preloadedImages = new Set();
            this.boundDocumentKeydown = this.handleDocumentKeydown.bind(this);

            this.render();
            this.cacheElements();
            this.bindEvents();
            this.showImage(this.currentIndex);
        }

        render() {
            if (!this.container) return;

            if (!this.images.length) {
                this.container.innerHTML = `
                    <div class="room-inline-carousel room-inline-carousel-empty" style="height:${this.height};">
                        <div class="text-center text-muted">
                            <i class="bi bi-image" style="font-size:36px;"></i>
                            <div class="small mt-2">No room photos yet</div>
                        </div>
                    </div>
                `;
                return;
            }

            this.container.innerHTML = `
                <div class="room-inline-carousel" style="height:${this.height};" tabindex="0" role="region" aria-label="${this.roomCode} image gallery">
                    <img class="room-inline-carousel-image" alt="${this.roomCode} photo">
                    <button type="button" class="room-inline-carousel-nav room-inline-carousel-prev" aria-label="Previous image">
                        <i class="bi bi-chevron-left"></i>
                    </button>
                    <button type="button" class="room-inline-carousel-nav room-inline-carousel-next" aria-label="Next image">
                        <i class="bi bi-chevron-right"></i>
                    </button>
                    <div class="room-inline-carousel-counter" aria-live="polite">1 / ${this.images.length}</div>
                </div>
            `;
        }

        cacheElements() {
            this.root = this.container?.querySelector('.room-inline-carousel');
            this.imageElement = this.container?.querySelector('.room-inline-carousel-image');
            this.counterElement = this.container?.querySelector('.room-inline-carousel-counter');
            this.prevButton = this.container?.querySelector('.room-inline-carousel-prev');
            this.nextButton = this.container?.querySelector('.room-inline-carousel-next');
        }

        bindEvents() {
            this.prevButton?.addEventListener('click', (event) => {
                event.stopPropagation();
                this.prevImage();
            });
            this.nextButton?.addEventListener('click', (event) => {
                event.stopPropagation();
                this.nextImage();
            });

            this.root?.addEventListener('keydown', (event) => {
                if (event.key === 'ArrowLeft') {
                    event.preventDefault();
                    this.prevImage();
                } else if (event.key === 'ArrowRight') {
                    event.preventDefault();
                    this.nextImage();
                } else if (event.key === 'Escape') {
                    const modalElement = this.root.closest('.modal');
                    const modal = modalElement ? bootstrap.Modal.getInstance(modalElement) : null;
                    modal?.hide();
                }
            });

            this.root?.addEventListener('touchstart', (event) => {
                this.touchStartX = event.changedTouches[0].screenX;
            }, { passive: true });

            this.root?.addEventListener('touchend', (event) => {
                this.touchEndX = event.changedTouches[0].screenX;
                this.handleSwipe();
            }, { passive: true });

            document.addEventListener('keydown', this.boundDocumentKeydown);
        }

        showImage(index) {
            if (!this.images.length || index < 0 || index >= this.images.length || !this.imageElement) return;

            this.currentIndex = index;
            const image = this.images[index];
            this.imageElement.classList.add('is-changing');

            window.setTimeout(() => {
                this.imageElement.src = image.url;
                this.imageElement.alt = `${this.roomCode} photo ${index + 1}`;
                this.imageElement.classList.remove('is-changing');
                this.updateCounter();
                this.updateNavigationButtons();
                this.preloadAdjacentImages();
            }, 120);
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

        updateCounter() {
            if (this.counterElement) {
                this.counterElement.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
            }
        }

        updateNavigationButtons() {
            if (!this.prevButton || !this.nextButton) return;
            this.prevButton.disabled = this.currentIndex === 0;
            this.nextButton.disabled = this.currentIndex === this.images.length - 1;
            this.prevButton.hidden = this.images.length <= 1;
            this.nextButton.hidden = this.images.length <= 1;
        }

        handleSwipe() {
            const diff = this.touchStartX - this.touchEndX;
            if (Math.abs(diff) <= this.touchThreshold) return;
            if (diff > 0) {
                this.nextImage();
            } else {
                this.prevImage();
            }
        }

        preloadAdjacentImages() {
            [this.currentIndex - 1, this.currentIndex + 1].forEach((index) => {
                if (index < 0 || index >= this.images.length || this.preloadedImages.has(index)) return;
                const image = new Image();
                image.src = this.images[index].url;
                this.preloadedImages.add(index);
            });
        }

        handleDocumentKeydown(event) {
            const modalElement = this.root?.closest('.modal');
            if (!modalElement || !modalElement.classList.contains('show')) return;

            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                this.prevImage();
            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                this.nextImage();
            } else if (event.key === 'Escape') {
                const modal = bootstrap.Modal.getInstance(modalElement);
                modal?.hide();
            }
        }

        destroy() {
            document.removeEventListener('keydown', this.boundDocumentKeydown);
            this.preloadedImages.clear();
        }
    }

    window.createRoomInlineCarousel = function (container, images, options) {
        if (container?._roomInlineCarousel) {
            container._roomInlineCarousel.destroy();
        }
        const carousel = new RoomInlineCarousel(container, images, options);
        if (container) {
            container._roomInlineCarousel = carousel;
        }
        return carousel;
    };
})();
