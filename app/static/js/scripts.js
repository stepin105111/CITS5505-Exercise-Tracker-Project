document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function(e) {
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
        btn.addEventListener('click', function() {
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

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar navigation
    const menuItems = document.querySelectorAll('.menu-item');
    const contentSections = document.querySelectorAll('.content-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const targetSection = this.getAttribute('data-target');
            
            // Remove active class from all menu items and sections
            menuItems.forEach(i => i.classList.remove('active'));
            contentSections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked item and target section
            this.classList.add('active');
            document.getElementById(targetSection).classList.add('active');
        });
    });
    
    // Menu toggle for mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const menu = document.querySelector('.menu');
    if (menuToggle && menu) {
        menuToggle.addEventListener('click', () => {
            menu.classList.toggle('active');
        });
    }
});















