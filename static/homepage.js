// Slideshow functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for necessary elements before initializing
    if (document.querySelector('.slideshow-container')) {
        initializeSlideshow();
    }
    initializeAnimations();
    // Smooth scrolling remains active regardless of other features
    initializeSmoothScroll();
});

/**
 * Initializes the main product slideshow functionality.
 */
function initializeSlideshow() {
    // Use the container to ensure we select elements specific to this slideshow
    const container = document.querySelector('.slideshow-container');
    if (!container) return;

    const slides = container.querySelectorAll('.slide');
    const indicators = container.querySelectorAll('.indicator');
    const prevBtn = container.querySelector('.prev-btn');
    const nextBtn = container.querySelector('.next-btn');
    const slideshowWrapper = container.querySelector('.slideshow-wrapper');

    // Early exit if controls or slides are missing
    if (slides.length === 0 || !prevBtn || !nextBtn) return;
    
    let currentSlide = 0;
    let slideInterval;
    const intervalTime = 5000; // 5 seconds

    /** Shows the slide at the given index, handling cycling. */
    function showSlide(index) {
        // Ensure index is within bounds
        if (index < 0) {
            index = slides.length - 1;
        } else if (index >= slides.length) {
            index = 0;
        }

        // Apply classes for the active state
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
        indicators.forEach((indicator, i) => {
            indicator.classList.toggle('active', i === index);
        });
        
        currentSlide = index;
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    function prevSlide() {
        showSlide(currentSlide - 1);
    }

    function startInterval() {
        // Clear any existing interval before starting a new one
        clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, intervalTime);
    }

    function resetInterval() {
        // Call startInterval, which handles the necessary clearInterval internally
        startInterval();
    }

    // --- Event Listeners ---
    prevBtn.addEventListener('click', () => {
        prevSlide();
        resetInterval();
    });
    
    nextBtn.addEventListener('click', () => {
        nextSlide();
        resetInterval();
    });

    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            showSlide(index);
            resetInterval();
        });
    });

    // Pause on hover
    slideshowWrapper.addEventListener('mouseenter', () => {
        clearInterval(slideInterval);
    });

    slideshowWrapper.addEventListener('mouseleave', () => {
        startInterval();
    });
    
    // Start the slideshow
    startInterval();
}

/**
 * Initializes IntersectionObserver for feature card animations on scroll.
 */
function initializeAnimations() {
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length === 0) return;

    const observerOptions = {
        // Triggers when 10% of the element is visible
        threshold: 0.1, 
        // Loads elements 50px before they enter the bottom of the viewport
        rootMargin: '0px 0px -50px 0px' 
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add 'visible' class to trigger CSS animation
                entry.target.classList.add('visible');
                // Stop observing once visible
                obs.unobserve(entry.target); 
            }
        });
    }, observerOptions);

    featureCards.forEach(card => {
        // Ensure a transition exists in CSS for the 'visible' state, 
        // no need for inline JS style for transition here.
        observer.observe(card);
    });
    
    // **Removed Redundant Hover Effects:** // The hover effects (transform: translateY(-10px) on mouseenter/mouseleave) 
    // should be managed entirely by the CSS you provided for better performance 
    // and separation of concerns.
    
}


/**
 * Initializes smooth scrolling for local anchor links.
 */
function initializeSmoothScroll() {
    // Removed the 'a[href^="#"]' selector to put it in its own function
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}