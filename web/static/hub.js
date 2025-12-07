/**
 * HUB.JS — Interactive Landing Page Script
 * Features: Smooth scroll, active nav, scroll animations
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScrollAnimations();
    initMobileNav();
    initTelegramWebApp();
});

/**
 * Navigation: Smooth scroll & active state
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    const sections = document.querySelectorAll('section[id]');
    const nav = document.querySelector('.nav-fixed');

    // Smooth scroll on click
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('data-section');
            const section = document.getElementById(sectionId);

            if (section) {
                const offsetTop = section.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }

            // Close mobile menu
            document.querySelector('.nav-links')?.classList.remove('active');
        });
    });

    // Active state on scroll with Intersection Observer
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                setActiveNav(id);
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });

    // Nav background on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav?.classList.add('scrolled');
        } else {
            nav?.classList.remove('scrolled');
        }
    });
}

function setActiveNav(sectionId) {
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionId) {
            link.classList.add('active');
        }
    });
}

/**
 * Scroll Animations: Fade-in elements on viewport entry
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');

    if (!animatedElements.length) return;

    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -10% 0px',
        threshold: 0.1
    };

    const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    animatedElements.forEach(el => {
        observer.observe(el);
    });

    // Trigger hero animation immediately
    setTimeout(() => {
        document.querySelectorAll('#hero .animate-on-scroll').forEach(el => {
            el.classList.add('visible');
        });
    }, 100);
}

/**
 * Mobile Navigation Toggle
 */
function initMobileNav() {
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (!toggle || !navLinks) return;

    toggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');

        // Animate hamburger
        const spans = toggle.querySelectorAll('span');
        if (navLinks.classList.contains('active')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        }
    });
}

/**
 * Telegram WebApp Integration
 */
function initTelegramWebApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        // Optional: Apply Telegram theme
        if (tg.themeParams && tg.themeParams.bg_color) {
            // Could adjust colors based on Telegram theme
            console.log('Running in Telegram WebApp');
        }
    }
}

/**
 * Utility: Staggered animation for card grids
 */
function animateCards(selector, baseDelay = 100) {
    const cards = document.querySelectorAll(selector);
    cards.forEach((card, index) => {
        card.style.transitionDelay = `${baseDelay * index}ms`;
    });
}

// Initialize card animations
animateCards('.quick-card', 80);
animateCards('.preview-card', 50);
