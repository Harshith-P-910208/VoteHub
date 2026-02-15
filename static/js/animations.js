// UI Animations and Interactions

// Candidate Selection
document.addEventListener('DOMContentLoaded', function () {
    // Candidate card selection
    const candidateCards = document.querySelectorAll('.candidate-card');
    const candidateInput = document.querySelector('input[name="candidate_id"]');

    candidateCards.forEach(card => {
        card.addEventListener('click', function () {
            // Remove selected class from all cards
            candidateCards.forEach(c => c.classList.remove('selected'));

            // Add selected class to clicked card
            this.classList.add('selected');

            // Set hidden input value
            const candidateId = this.dataset.candidateId;
            if (candidateInput) {
                candidateInput.value = candidateId;
            }

            // Update submit button state
            if (typeof updateSubmitButton === 'function') {
                updateSubmitButton();
            }

            // Play selection sound (optional)
            playSelectionSound();
        });
    });

    // Smooth scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.glass-card, .card, .election-card, .stat-card').forEach(card => {
        observer.observe(card);
    });

    // Form validation animations
    const formInputs = document.querySelectorAll('.form-input, .form-textarea, .form-select');
    formInputs.forEach(input => {
        input.addEventListener('invalid', function (e) {
            e.preventDefault();
            this.classList.add('error-shake');
            setTimeout(() => {
                this.classList.remove('error-shake');
            }, 500);
        });

        input.addEventListener('input', function () {
            if (this.validity.valid) {
                this.style.borderColor = 'var(--success)';
            } else {
                this.style.borderColor = 'var(--danger)';
            }
        });
    });

    // Confetti animation on confirmation page
    if (document.querySelector('.confirmation-container')) {
        createConfetti();
    }

    // Progress bar animations on results page
    animateProgressBars();

    // Staggered Animations for Cards
    const cards = document.querySelectorAll('.election-card, .stat-card, .candidate-card, .result-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.classList.add('animate-slide-up');
        card.style.animationDelay = `${index * 0.1}s`;

        // Add hover lift effect
        card.classList.add('hover-lift');
    });

    // Animate Statistics Counters
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.innerText);
        if (!isNaN(finalValue)) {
            animateCounter(stat, 0, finalValue, 2000);
        }
    });

    // Add float effect to main headings
    const headings = document.querySelectorAll('h1');
    headings.forEach(h1 => {
        h1.classList.add('animate-scale-in');
    });

    // Upgraded 3D Tilt Animation with Dynamic Glare
    const tiltCards = document.querySelectorAll('.glass-card, .election-card, .stat-card, .candidate-card, .result-card');

    tiltCards.forEach(card => {
        // Ensure card has relative positioning for glare
        card.style.position = 'relative';
        card.style.overflow = 'hidden';

        // Create glare element dynamically
        const glare = document.createElement('div');
        glare.className = 'card-glare';
        glare.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            background: radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.2) 0%, transparent 60%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 5;
        `;
        card.appendChild(glare);

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -15; // Increased tilt
            const rotateY = ((x - centerX) / centerX) * 15;

            // 3D Transform with enhanced scale
            card.style.transform = `
                perspective(1200px) 
                rotateX(${rotateX}deg) 
                rotateY(${rotateY}deg) 
                scale3d(1.05, 1.05, 1.05)
            `;

            // Internal Parallax for children (icons, values, titles)
            const children = card.querySelectorAll('.stat-icon, .stat-value, .election-title, .portal-icon, .candidate-icon');
            children.forEach(child => {
                const moveX = ((x - centerX) / centerX) * 10;
                const moveY = ((y - centerY) / centerY) * 10;
                child.style.transform = `translateZ(50px) translateX(${moveX}px) translateY(${moveY}px)`;
                child.style.transition = 'none';
            });

            // Dynamic shadow related to mouse
            const shadowX = (centerX - x) / 8;
            const shadowY = (centerY - y) / 8;
            card.style.boxShadow = `
                ${shadowX}px ${shadowY}px 35px rgba(0, 0, 0, 0.4), 
                0 0 25px rgba(102, 126, 234, 0.3)
            `;

            // Glare position calculation
            glare.style.opacity = '1';
            glare.style.background = `
                radial-gradient(circle at ${(x / rect.width) * 100}% ${(y / rect.height) * 100}%, 
                rgba(255, 255, 255, 0.25) 0%, transparent 70%)
            `;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1200px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            card.style.boxShadow = '';
            card.style.transition = 'transform 0.6s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.6s ease';
            glare.style.opacity = '0';

            // Reset children
            const children = card.querySelectorAll('.stat-icon, .stat-value, .election-title, .portal-icon, .candidate-icon');
            children.forEach(child => {
                child.style.transform = 'translateZ(0) translateX(0) translateY(0)';
                child.style.transition = 'transform 0.6s ease';
            });
        });

        card.addEventListener('mouseenter', () => {
            card.style.transition = 'transform 0.1s ease, box-shadow 0.2s ease';
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Counter Animation Function
function animateCounter(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        // Easing function for smooth counting
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);

        obj.innerHTML = Math.floor(easeOutQuart * (end - start) + start);

        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Play selection sound
function playSelectionSound() {
    // Create a subtle click sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

// Create confetti animation
function createConfetti() {
    const colors = ['#667eea', '#764ba2', '#f5576c', '#00f2fe', '#10b981'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
        document.body.appendChild(confetti);

        // Remove after animation
        setTimeout(() => {
            confetti.remove();
        }, 6000);
    }
}

// Animate progress bars
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');

    progressBars.forEach(bar => {
        const targetWidth = bar.dataset.percentage || '0';
        bar.style.width = '0%';

        setTimeout(() => {
            bar.style.width = targetWidth + '%';
        }, 100);
    });
}

// Add error shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes error-shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .error-shake {
        animation: error-shake 0.5s ease;
    }
`;
document.head.appendChild(style);

// Smooth page transitions
window.addEventListener('beforeunload', function () {
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.95)';
});

// Image preview modal for voter images
function showImageModal(imageSrc) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: pointer;
    `;

    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: 1rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    `;

    modal.appendChild(img);
    document.body.appendChild(modal);

    modal.addEventListener('click', function () {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.remove();
        }, 300);
    });

    // Animate in
    modal.style.opacity = '0';
    setTimeout(() => {
        modal.style.opacity = '1';
        modal.style.transition = 'opacity 0.3s ease';
    }, 10);
}

// Add click handlers for voter image thumbnails
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('voter-image-thumb')) {
        showImageModal(e.target.src);
    }
});

// Form submission loading state
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function (e) {
        const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
        }
    });
});

// Delete confirmation
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn-delete') || e.target.classList.contains('delete-candidate-btn')) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    }
});

// Real-time form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

const emailInputs = document.querySelectorAll('input[type="email"]');
emailInputs.forEach(input => {
    input.addEventListener('blur', function () {
        if (this.value && !validateEmail(this.value)) {
            this.setCustomValidity('Please enter a valid email address');
            this.reportValidity();
        } else {
            this.setCustomValidity('');
        }
    });
});
