// Enhanced form interactions for auth pages
document.addEventListener('DOMContentLoaded', function() {
    initializeAuthForms();
    initializeInputAnimations();
    initializePasswordFeatures();
    initializeRoleSelection();
    initializeFloatingLabels();
});

function initializeAuthForms() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.auth-btn');
            if (submitBtn && !submitBtn.classList.contains('loading')) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

function initializeInputAnimations() {
    const inputs = document.querySelectorAll('.auth-input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
        
        // Real-time validation
        input.addEventListener('input', function() {
            if (this.type === 'text' && this.name === 'username') {
                validateUsername(this);
            } else if (this.type === 'email') {
                validateEmail(this);
            } else if (this.type === 'password') {
                validatePassword(this);
            }
        });
    });
}

function initializePasswordFeatures() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    passwordInputs.forEach(input => {
        const container = input.parentElement;
        
        // Create password toggle button
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.innerHTML = '<i class="fas fa-eye"></i>';
        toggle.className = 'password-toggle';
        toggle.setAttribute('aria-label', 'Toggle password visibility');
        
        toggle.addEventListener('click', function() {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            this.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
            this.style.color = isPassword ? '#ffc300' : '#666';
        });
        
        // Create character counter for password
        if (input.name === 'password') {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.textContent = '0';
            
            input.addEventListener('input', function() {
                const length = this.value.length;
                counter.textContent = length;
                
                if (length > 0) {
                    counter.style.color = length >= 8 ? '#51cf66' : '#ff6b6b';
                } else {
                    counter.style.color = '#666';
                }
            });
            
            container.appendChild(counter);
        }
        
        container.appendChild(toggle);
    });
}

function initializeFloatingLabels() {
    const inputs = document.querySelectorAll('.auth-input');
    
    inputs.forEach(input => {
        const label = input.nextElementSibling;
        
        if (label && label.classList.contains('floating-label')) {
            // Check if input has value on page load
            if (input.value) {
                label.classList.add('active');
            }
            
            input.addEventListener('focus', function() {
                label.classList.add('active');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    label.classList.remove('active');
                }
            });
        }
    });
}

function initializeRoleSelection() {
    const roleOptions = document.querySelectorAll('.role-option');
    
    roleOptions.forEach(option => {
        option.addEventListener('click', function() {
            roleOptions.forEach(opt => {
                opt.querySelector('input').checked = false;
            });
            
            const input = this.querySelector('input');
            input.checked = true;
        });
    });
}

// Validation Functions
function validateUsername(input) {
    const value = input.value.trim();
    const isValid = value.length >= 3 && /^[a-zA-Z0-9_]+$/.test(value);
    
    if (value.length > 0) {
        input.style.borderColor = isValid ? '#51cf66' : '#ff6b6b';
    } else {
        input.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}

function validateEmail(input) {
    const value = input.value.trim();
    const isValid = value === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    
    if (value.length > 0) {
        input.style.borderColor = isValid ? '#51cf66' : '#ff6b6b';
    } else {
        input.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}

function validatePassword(input) {
    const value = input.value;
    const isValid = value.length >= 8;
    
    if (value.length > 0) {
        input.style.borderColor = isValid ? '#51cf66' : '#ff6b6b';
    } else {
        input.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
}

console.log('Auth.js loaded successfully!');