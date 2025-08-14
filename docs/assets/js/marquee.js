/**
 * Marquee functionality
 * Efficient infinite scroll carousel for database and model icons
 */
class MarqueeController {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupMarqueeClickHandlers();
        this.setupModelsClickHandlers();
    }
    
    
    setupMarqueeClickHandlers() {
        const marqueeItems = document.querySelectorAll('.db-marquee-item');
        
        marqueeItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const dbType = item.dataset.db;
                if (dbType) {
                    window.location.href = `documentation/databases/${dbType}/`;
                }
            });
            
            // Add keyboard navigation
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const dbType = item.dataset.db;
                    if (dbType) {
                        window.location.href = `documentation/databases/${dbType}/`;
                    }
                }
            });
            
            // Make items focusable for accessibility
            item.setAttribute('tabindex', '0');
            item.setAttribute('role', 'button');
            item.setAttribute('aria-label', `Learn more about ${item.querySelector('img').alt}`);
        });
    }
    
    setupModelsClickHandlers() {
        const modelsItems = document.querySelectorAll('.models-marquee-item');
        
        modelsItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const modelType = item.dataset.model;
                if (modelType) {
                    window.location.href = `documentation/ai_models/${modelType}/`;
                }
            });
            
            // Add keyboard navigation
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const modelType = item.dataset.model;
                    if (modelType) {
                        window.location.href = `documentation/ai_models/${modelType}/`;
                    }
                }
            });
            
            // Make items focusable for accessibility
            item.setAttribute('tabindex', '0');
            item.setAttribute('role', 'button');
            item.setAttribute('aria-label', `Learn more about ${item.querySelector('img').alt}`);
        });
    }
    
    
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const marquee = new MarqueeController();
    
    // Initialize marquees with bulletproof infinite scroll
    function initializeMarquees() {
        const dbTrack = document.querySelector('.db-marquee-track');
        const modelsTrack = document.querySelector('.models-marquee-track');
        
        // Proven infinite scroll marquee setup
        function setupInfiniteMarquee(track, direction = 'left', speed = 5) {
            if (!track) return;
            
            // Clone all items multiple times for seamless loop
            const originalItems = Array.from(track.children);
            const cloneCount = 3; // Clone 3 times for safety
            
            for (let i = 0; i < cloneCount; i++) {
                originalItems.forEach(item => {
                    const clone = item.cloneNode(true);
                    track.appendChild(clone);
                });
            }
            
            // Re-setup click handlers for all items (including clones)
            const allItems = Array.from(track.children);
            allItems.forEach(item => {
                // Remove any existing listeners to avoid duplicates
                item.replaceWith(item.cloneNode(true));
            });
            
            // Get fresh references after cloning
            const freshItems = Array.from(track.children);
            freshItems.forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    const dbType = item.dataset.db;
                    const modelType = item.dataset.model;
                    
                    if (dbType) {
                        window.location.href = `documentation/databases/${dbType}/`;
                    } else if (modelType) {
                        window.location.href = `documentation/ai_models/${modelType}/`;
                    }
                });
                
                // Add keyboard navigation
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        const dbType = item.dataset.db;
                        const modelType = item.dataset.model;
                        
                        if (dbType) {
                            window.location.href = `documentation/databases/${dbType}/`;
                        } else if (modelType) {
                            window.location.href = `documentation/ai_models/${modelType}/`;
                        }
                    }
                });
                
                // Make items focusable for accessibility
                item.setAttribute('tabindex', '0');
                item.setAttribute('role', 'button');
                const img = item.querySelector('img');
                if (img) {
                    item.setAttribute('aria-label', `Learn more about ${img.alt}`);
                }
            });
            
            // Use transform animation with JavaScript for perfect control
            let position = 0;
            const itemWidth = 108; // 48px icon + 60px gap
            const totalOriginalWidth = originalItems.length * itemWidth;
            
            function animate() {
                if (direction === 'left') {
                    position -= speed;
                    if (position <= -totalOriginalWidth) {
                        position = 0; // Reset to start
                    }
                } else {
                    position += speed;
                    if (position >= totalOriginalWidth) {
                        position = 0; // Reset to start
                    }
                }
                
                track.style.transform = `translateX(${position}px)`;
                requestAnimationFrame(animate);
            }
            
            // Start animation
            requestAnimationFrame(animate);
            
            // Pause on hover
            const marqueeContainer = track.parentElement;
            marqueeContainer.addEventListener('mouseenter', () => {
                track.style.animationPlayState = 'paused';
            });
            marqueeContainer.addEventListener('mouseleave', () => {
                track.style.animationPlayState = 'running';
            });
        }
        
        setupInfiniteMarquee(dbTrack, 'left', 0.25);
        setupInfiniteMarquee(modelsTrack, 'right', 0.25);
    }
    
    // Call initialization
    setTimeout(initializeMarquees, 100);
    
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-quad',
            once: false,
            mirror: true,
            offset: 120,
            delay: 0,
            anchorPlacement: 'top-bottom',
            disable: false,
            startEvent: 'DOMContentLoaded',
            initClassName: 'aos-init',
            animatedClassName: 'aos-animate',
            useClassNames: false,
            disableMutationObserver: false,
            debounceDelay: 50,
            throttleDelay: 99
        });
        
        window.addEventListener('resize', () => {
            AOS.refresh();
        });
        
        setTimeout(() => {
            AOS.refresh();
        }, 100);
    }
    
    // Expose to global scope for potential external control
    window.MarqueeController = marquee;
});