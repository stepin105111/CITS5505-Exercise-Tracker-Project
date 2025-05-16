document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function (e) {
        // Skip everything for logout
        if (this.classList.contains('logout-btn')) {
            return; // Do not prevent default, let it redirect to /logout
        }

        e.preventDefault();

        // Remove active class from all menu items
        document.querySelectorAll('.menu-item').forEach(i => {
            i.classList.remove('active');
        });

        // Add active class to clicked menu item
        this.classList.add('active');

        // Hide all content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show the target content section
        const targetSection = this.getAttribute('data-target');
        document.getElementById(targetSection).classList.add('active');
    });
});

// Day selector for workout plan
const dayBtns = document.querySelectorAll('.days-selector .btn');
if (dayBtns.length) {
    dayBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.toggle('btn-primary');
            if (this.classList.contains('btn-primary')) {
                this.style.background = '#3498db';
                this.style.color = 'white';
            } else {
                this.style.background = '#f0f4f8';
                this.style.color = '#333';
            }
        });
    });
}

// flash msg
document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(function (message) {
        // Auto dismiss after 5 seconds
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
});

function togglePasswordVisibility() {
    const passwordField = document.getElementById('password');
    const toggleIcon = document.querySelector('.toggle-password');

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordField.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// Toggle password visibility
    function togglePasswordVisibility(fieldId) {
        const passwordField = document.getElementById(fieldId);
        const toggleIcon = passwordField.nextElementSibling;

        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
    }

    // Password strength checker
    document.getElementById('password').addEventListener('input', function () {
        const password = this.value;
        const meter = document.getElementById('strength-meter');
        const text = document.getElementById('strength-text');

        // Simple strength calculation
        let strength = 0;
        if (password.length > 6) strength += 25;
        if (password.match(/[A-Z]/)) strength += 25;
        if (password.match(/[0-9]/)) strength += 25;
        if (password.match(/[^A-Za-z0-9]/)) strength += 25;

        // Update UI
        meter.style.width = strength + '%';

        if (strength <= 25) {
            meter.style.backgroundColor = '#ff4d4d';
            text.textContent = 'Weak password';
        } else if (strength <= 50) {
            meter.style.backgroundColor = '#ffa64d';
            text.textContent = 'Medium password';
        } else if (strength <= 75) {
            meter.style.backgroundColor = '#99cc00';
            text.textContent = 'Good password';
        } else {
            meter.style.backgroundColor = '#00cc44';
            text.textContent = 'Strong password';
        }
    });

    // Password confirmation validation
    document.getElementById('signup-form').addEventListener('submit', function (e) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        if (password !== confirmPassword) {
            e.preventDefault();
            alert('Passwords do not match!');
        }
    });













