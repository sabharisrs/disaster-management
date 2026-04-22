function initializeLocationPicker(mapElement) {
    const latitudeInput = document.getElementById("latitude");
    const longitudeInput = document.getElementById("longitude");
    const initialLat = parseFloat(mapElement.dataset.lat || "20.5937");
    const initialLng = parseFloat(mapElement.dataset.lng || "78.9629");

    const map = L.map(mapElement).setView([initialLat, initialLng], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    let marker = L.marker([initialLat, initialLng]).addTo(map);

    function updateFields(lat, lng) {
        latitudeInput.value = lat.toFixed(6);
        longitudeInput.value = lng.toFixed(6);
    }

    updateFields(initialLat, initialLng);
    setTimeout(() => map.invalidateSize(), 150);

    map.on("click", function (event) {
        const { lat, lng } = event.latlng;
        marker.setLatLng([lat, lng]);
        updateFields(lat, lng);
    });
}

async function initializeRequestsMap(mapElement) {
    const map = L.map(mapElement).setView([20.5937, 78.9629], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    try {
        const response = await fetch(mapElement.dataset.source);
        const data = await response.json();
        const markers = [];

        data.requests.forEach((item) => {
            const marker = L.marker([item.latitude, item.longitude]).addTo(map);
            marker.bindPopup(
                `<strong>${item.title}</strong><br>${item.disaster_type} | ${item.urgency}<br>Status: ${item.status}`
            );
            markers.push([item.latitude, item.longitude]);
        });

        if (markers.length > 0) {
            map.fitBounds(markers, { padding: [30, 30] });
        }
    } catch (error) {
        console.error("Unable to load map data:", error);
    }

    setTimeout(() => map.invalidateSize(), 150);
}

document.addEventListener("DOMContentLoaded", function () {
    const requestMap = document.getElementById("request-map");
    const requestsMap = document.getElementById("requests-map");

    if (requestMap && typeof L !== "undefined") {
        initializeLocationPicker(requestMap);
    }

    if (requestsMap && typeof L !== "undefined") {
        initializeRequestsMap(requestsMap);
    }

    const navbarCollapse = document.getElementById("mainNavbar");
    if (navbarCollapse) {
        navbarCollapse.querySelectorAll(".nav-link, .btn").forEach((element) => {
            element.addEventListener("click", function () {
                const expanded = window.getComputedStyle(navbarCollapse).display !== "none" && navbarCollapse.classList.contains("show");
                if (expanded && window.innerWidth < 992) {
                    bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
                }
            });
        });
    }
});

// Highlight active navigation link
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link-animated');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.style.color = 'var(--text-main) !important';
            const underline = link.querySelector('.nav-underline');
            if (underline) {
                underline.style.width = '100%';
            }
        }
    });
}

// Initialize cursor follower and letter hover effects when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Highlight active nav link
    highlightActiveNavLink();
    
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (!prefersReducedMotion) {
        try {
            // Initialize cursor follower
            initCursorFollower();
            
            // Initialize letter hover effects
            initLetterHover();
        } catch (error) {
            console.warn('Hero animation initialization failed:', error);
        }
    }
    
    // Password toggle functionality
    const togglePassword = document.getElementById('togglePassword');
    const toggleLoginPassword = document.getElementById('toggleLoginPassword');
    const password = document.getElementById('password');
    const loginPassword = document.getElementById('loginPassword');
    
    if (togglePassword && password) {
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
    
    if (toggleLoginPassword && loginPassword) {
        toggleLoginPassword.addEventListener('click', function() {
            const type = loginPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            loginPassword.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
    
    // Password strength indicator
    if (password) {
        password.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            updatePasswordStrength(strength);
        });
    }
    
    // Form submission with loading states
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const btn = document.getElementById('registerBtn');
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            
            btn.disabled = true;
            btnText.classList.add('d-none');
            btnLoading.classList.remove('d-none');
        });
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const btn = document.getElementById('loginBtn');
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            
            btn.disabled = true;
            btnText.classList.add('d-none');
            btnLoading.classList.remove('d-none');
        });
    }
    
    // Role selection visual feedback
    const roleOptions = document.querySelectorAll('.role-option input[type="radio"]');
    roleOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Remove selected class from all
            document.querySelectorAll('.role-card').forEach(card => {
                card.classList.remove('selected');
            });
            // Add selected class to checked option
            if (this.checked) {
                this.nextElementSibling.classList.add('selected');
            }
        });
    });
});

// Cursor follower functionality
function initCursorFollower() {
    // Check if device supports hover (not touch-only)
    if (window.matchMedia && window.matchMedia('(hover: none)').matches) {
        return; // Don't initialize cursor follower on touch devices
    }

    const cursor = document.createElement('div');
    cursor.className = 'cursor-follower';
    document.body.appendChild(cursor);
    
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    let isActive = false;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        if (!isActive) {
            isActive = true;
        }
    });
    
    document.addEventListener('mouseleave', () => {
        cursor.classList.remove('hover');
    });
    
    function updateCursor() {
        if (isActive) {
            const dx = mouseX - cursorX;
            const dy = mouseY - cursorY;
            
            // Smooth following with easing
            cursorX += dx * 0.12;
            cursorY += dy * 0.12;
            
            cursor.style.left = `${cursorX - 10}px`;
            cursor.style.top = `${cursorY - 10}px`;
        }
        
        requestAnimationFrame(updateCursor);
    }
    
    updateCursor();
    
    // Add hover effects for interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .role-card, .hero-text-animated, .hero-text-animated span');
    
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('hover');
        });
        
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('hover');
        });
    });
}

// Letter hover effects
function initLetterHover() {
    const heroText = document.querySelector('.hero-text-animated');
    if (!heroText) return;
    
    // Clear any existing content first
    heroText.innerHTML = '';
    
    // Get the full text from data attribute
    const text = heroText.getAttribute('data-text') || '';
    
    if (!text) return;
    
    // Split text into individual letters/spaces and create spans
    for (let i = 0; i < text.length; i++) {
        const span = document.createElement('span');
        const char = text[i];
        
        if (char === ' ') {
            // Use regular space, not &nbsp;
            span.textContent = ' ';
            span.style.display = 'inline';
            span.classList.add('space');
        } else {
            span.textContent = char;
            span.style.display = 'inline-block';
        }
        
        heroText.appendChild(span);
    }
}

// Password strength checking function
function checkPasswordStrength(password) {
    let strength = 0;
    const checks = [
        password.length >= 8, // Length
        /[a-z]/.test(password), // Lowercase
        /[A-Z]/.test(password), // Uppercase
        /[0-9]/.test(password), // Numbers
        /[^A-Za-z0-9]/.test(password) // Special characters
    ];
    
    strength = checks.filter(Boolean).length;
    
    if (strength <= 2) return 'weak';
    if (strength <= 3) return 'medium';
    return 'strong';
}

// Update password strength indicator
function updatePasswordStrength(strength) {
    const indicator = document.getElementById('passwordStrength');
    if (!indicator) return;
    
    indicator.className = 'password-strength';
    if (strength) {
        indicator.classList.add(strength);
        if (!indicator.querySelector('.strength-bar')) {
            indicator.innerHTML = '<div class="strength-bar"></div>';
        }
    } else {
        indicator.innerHTML = '';
    }
}
