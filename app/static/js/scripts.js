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