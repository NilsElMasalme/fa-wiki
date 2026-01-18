/**
 * FAForever Wiki - Main JavaScript
 */

(function() {
    'use strict';

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Skip intro animation handling
    function initIntroSkip() {
        const introContainer = document.getElementById('introContainer');
        if (!introContainer) return;

        // Check if already seen
        if (localStorage.getItem('fafWikiIntroSeen') === 'true' || prefersReducedMotion) {
            introContainer.style.display = 'none';
            document.body.classList.add('skip-animation');
            return;
        }

        const skipIntro = () => {
            if (introContainer.classList.contains('fade-out')) return;

            introContainer.classList.add('fade-out');
            document.body.classList.add('animation-skipped');
            localStorage.setItem('fafWikiIntroSeen', 'true');

            // Clean up listeners
            document.removeEventListener('keydown', skipIntro);
            document.removeEventListener('click', skipIntro);
            document.removeEventListener('touchstart', skipIntro);
            document.removeEventListener('wheel', skipIntro);

            // Remove intro after animation
            setTimeout(() => {
                introContainer.remove();
            }, 800);
        };

        // Add skip listeners
        document.addEventListener('keydown', skipIntro);
        document.addEventListener('click', skipIntro);
        document.addEventListener('touchstart', skipIntro);
        document.addEventListener('wheel', skipIntro);

        // Handle video end if present
        const video = introContainer.querySelector('video');
        if (video) {
            video.addEventListener('ended', skipIntro);
        }

        // Auto-skip after timeout
        setTimeout(() => {
            if (!introContainer.classList.contains('fade-out')) {
                skipIntro();
            }
        }, 4000);
    }

    // FAQ toggle functionality
    function initFAQ() {
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', () => {
                const item = question.closest('.faq-item');
                const wasOpen = item.classList.contains('open');

                // Close all others
                document.querySelectorAll('.faq-item.open').forEach(openItem => {
                    if (openItem !== item) {
                        openItem.classList.remove('open');
                    }
                });

                // Toggle current
                item.classList.toggle('open', !wasOpen);
            });
        });
    }

    // Flash message auto-dismiss
    function initFlashMessages() {
        document.querySelectorAll('.flash-message').forEach(msg => {
            setTimeout(() => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateX(100%)';
                setTimeout(() => msg.remove(), 500);
            }, 5000);
        });
    }

    // Smooth scroll for anchor links
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    // HTMX event handlers
    function initHTMX() {
        // Show loading state
        document.body.addEventListener('htmx:beforeRequest', (e) => {
            const target = e.detail.target;
            if (target && target.id === 'editModal') {
                target.innerHTML = `
                    <div class="edit-modal-overlay">
                        <div class="spinner"></div>
                    </div>
                `;
            }
        });

        // Handle errors
        document.body.addEventListener('htmx:responseError', (e) => {
            console.error('HTMX Error:', e.detail);
            const target = e.detail.target;
            if (target) {
                target.innerHTML = `
                    <div class="edit-modal-overlay" onclick="this.remove()">
                        <div class="edit-modal">
                            <div class="edit-modal-body text-center">
                                <p style="color: var(--error);">An error occurred. Please try again.</p>
                                <button class="btn btn-secondary mt-2" onclick="this.closest('.edit-modal-overlay').remove()">Close</button>
                            </div>
                        </div>
                    </div>
                `;
            }
        });

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-modal-overlay')) {
                e.target.remove();
            }
        });

        // Close modal on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.querySelector('.edit-modal-overlay');
                if (modal) modal.remove();
            }
        });
    }

    // Button hover sound effect (optional)
    function initButtonEffects() {
        const buttons = document.querySelectorAll('.nav-button');
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                // Could add subtle hover sound here
            });
        });
    }

    // Initialize everything
    function init() {
        initIntroSkip();
        initFAQ();
        initFlashMessages();
        initSmoothScroll();
        initHTMX();
        initButtonEffects();
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Re-init after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', () => {
        initFAQ();
        initButtonEffects();
    });

})();
